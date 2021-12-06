#!/usr/bin/python3

import csv
import json
import os
from pathlib import Path
import shutil
import traceback
import xml.etree.ElementTree as ET


def get_ids_and_pub_numbers(csvpath):
    '''Retrieves identifiers and Proquest pub numbers from report'''
    with open(csvpath, 'r', encoding='utf8') as csvfile:
        csvreader = csv.reader(csvfile)
        header_row = next(csvreader)
        ids_and_pub_numbers = {row[0]: row[1] for row in csvreader}
        return ids_and_pub_numbers

def get_pub_numbers(csvpath):
    '''Retrieves Proquest pub numbers from report'''
    with open(csvpath, 'r', encoding='utf8') as csvfile:
        csvreader = csv.reader(csvfile)
        header_row = next(csvreader)
        pub_numbers = [row[1] for row in csvreader]
        return pub_numbers

def get_unique_names(dirlist):
    '''Loops through extracted file directory (2 files for each) and gets all unique submissions'''
    dirset = set()
    for filename in dirlist:
        if filename != '.DS_Store':
            base_name = filename.replace('_DATA.xml', '').replace('.pdf', '')
            dirset.add(base_name)
    return dirset

def create_submission_directories(extracted_file_path):
    '''Creates a directory for each submission, moves
    Proquest XML and PDFs into submission directories'''
    dirlist = os.listdir(extracted_file_path)
    unique_names = get_unique_names(dirlist)
    for unique_name in unique_names:
        full_path = f"{extracted_file_path}/{unique_name}"
        Path(full_path).mkdir(parents=True, exist_ok=True)
        # this loops through the dirlist for each unique name...
        move_extracted_files(dirlist, unique_name, extracted_file_path, full_path)

def move_extracted_files(dirlist, unique_name, source_path, dest_path):
    '''Moves Proquest XML files and PDF files into directories, one
    for each submission'''
    for filename in dirlist:
        if unique_name in filename and filename != '.DS_Store':
            full_path_old = f"{source_path}/{filename}"
            full_path_new = f"{dest_path}/{filename}"
            shutil.move(full_path_old, full_path_new)

def match_files(extracted_file_path, marcxml_path, report_path):
    '''Matches MARCXML files with submission directories, moves
    MARCXML files into the appropriate submission directory'''
    extracted_file_dirs = os.listdir(extracted_file_path)
    ids_and_pub_nums = get_ids_and_pub_numbers(report_path)
    for extract_dir in extracted_file_dirs:
        for key, value in ids_and_pub_nums.items():
            if key in extract_dir:
                marc_path = f"{marcxml_path}/{value}.xml"
                new_path = f"{extracted_file_path}/{extract_dir}/{value}.xml"
                shutil.move(marc_path, new_path)

def fix_excel_mangling(row):
    bad_key = '\ufeffID'
    good_key = 'ID'
    row[good_key] = row.pop(bad_key)
    return row

def convert_csv_to_json(report_path):
    '''Converts each row of the Proquest dissertation report to a dict 
    and adds to a dict of dicts'''
    dict_of_dicts = {}
    with open(report_path, 'r', encoding='utf8') as csvfile:
        csvdict = csv.DictReader(csvfile)
        for row in csvdict:
            row = fix_excel_mangling(row)
            dict_of_dicts[row.get('ID')] = row
    return dict_of_dicts

def add_json_to_submission_folders(report_path, extracted_file_path):
    '''Takes the dict of dicts above, matches with the submission directories
    based on identifier, stores the JSON file in the submission directory'''
    csv_to_json = convert_csv_to_json(report_path)
    extracted_file_dirs = [item for item in os.listdir(extracted_file_path) if item != '.DS_Store']
    for key, value in csv_to_json.items():
        for extracted_file_dir in extracted_file_dirs:
            if key in extracted_file_dir:
                output_path = f"{extracted_file_path}/{extracted_file_dir}/{key}.json"
                with open(output_path, 'w', encoding='utf8') as jsonfile: 
                    json.dump(value, jsonfile, sort_keys=True, indent=4)

def move_new_xml_files(source_path, dest_path, pub_numbers):
    '''Moves all Spring 2021 MARCXML files into a directory'''
    files_in_source = os.listdir(source_path)
    for filename in files_in_source:
        if filename.replace('xml', '') in pub_numbers:
            full_path_old = f"{source_path}/{filename}"
            full_path_new = f"{dest_path}/{filename}"
            shutil.move(full_path_old, full_path_new)

def split_xml_files(file_path):
    '''Splits individual MARCXML files out of combined XML document'''
    ET.register_namespace('', "http://www.loc.gov/MARC21/slim")
    context = ET.iterparse(f'{file_path}/etd_marc.xml', events=('end', ))
    for event, elem in context:
        if elem.tag == '{http://www.loc.gov/MARC21/slim}record':
            title = elem.findall(".//{http://www.loc.gov/MARC21/slim}controlfield[@tag='001']")[0].text
            title = title.replace('AAI', '')
            filename = f'{fp}/split_xml_files/{title}.xml'
            with open(filename, 'wb') as f:
                f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(b'<collection xmlns="http://www.loc.gov/MARC21/slim">\n')
                f.write(ET.tostring(elem).replace(b' xmlns="http://www.loc.gov/MARC21/slim"', b''))
                f.write(b"</collection>")

def extract_zip_files(diss_fp):
    '''Extracts Proquest zip files (containing XML and PDF files) into a directory'''
    diss_dirlist = os.listdir(f"{diss_fp}/zip_files")
    for item in tqdm(diss_dirlist):
        if item.endswith('.zip'):
            full_path = f"{diss_fp}/zip_files/{item}"
            destination_path = f"{diss_fp}/extracted_files"
            shutil.unpack_archive(full_path, destination_path)


def copy_select_files(new_dirpath, old_dirpath, report_path):
    '''Using a list of identifiers as input, copies dissertation files to a directory'''
    folder_data = {item.replace('.pdf', ''): f"{old_dirpath}/{item}" for item in os.listdir(old_dirpath)}
    with open(report_path, 'r', encoding='utf8') as datafile:
        reader = csv.reader(datafile)
        next(reader)
        for row in reader:
            pub_number = row[1]
            print(pub_number)
            if pub_number in folder_data:
                old_file_path = folder_data[pub_number]
                new_file_path = f"{new_dirpath}/{pub_number}.pdf"
                shutil.copy(old_file_path, new_file_path)

def main():
    with open('config.json') as cfg_fp:
        cfg = json.load(cfg_fp)
        report_path = cfg.get('report_path')
        marcxml_path = cfg.get('marcxml_path')
        extracted_file_path = cfg.get('extracted_file_path')
        new_pdf_dirpath = cfg.get('new_pdf_folder_path')
        all_pdf_dirpath = cfg.get('all_pdf_folder_path')
        copy_select_files(new_pdf_dirpath, all_pdf_dirpath, report_path)
        # add_json_to_submission_folders(report_path, extracted_file_path)

if __name__ == "__main__":
    main()