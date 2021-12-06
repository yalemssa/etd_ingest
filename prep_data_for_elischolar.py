#!/usr/bin/python3

import csv
import json
from lxml import etree
import os
import shutil
from tqdm import tqdm
from utilities import utilities as u


def get_author_data(element):
    '''Checks whether there is an additional author type besides primary - catches multiple authors. However it is unlikely there will be more than one, and anyhow only one can 
    be recorded in EliScholar via bulk upload'''
    if element.tag == 'DISS_author':
        if element.attrib.get('type') != 'primary':
            print('More than one author')

def get_titles(element):
    return element.find(".//DISS_description/DISS_title").text

def get_first_name(element):
    return element.find(".//DISS_authorship/DISS_author/DISS_name/DISS_fname").text

def get_middle_name(element):
    return element.find(".//DISS_authorship/DISS_author/DISS_name/DISS_middle").text

def get_last_name(element):
    return element.find(".//DISS_authorship/DISS_author/DISS_name/DISS_surname").text

def get_suffix(element):
    return element.find(".//DISS_authorship/DISS_author/DISS_name/DISS_suffix").text

def get_email(element):
    return element.find(".//DISS_authorship/DISS_author/DISS_contact/DISS_email").text

def get_institution(element):
    return element.find(".//DISS_description/DISS_institution/DISS_inst_name").text

def get_keywords(element):
    # there is also a keywords element - should I use that??
    return element.find(".//DISS_description/DISS_categorization/DISS_category/DISS_cat_desc").text

def get_degree(element):
    return element.find(".//DISS_description/DISS_degree").text

def get_department(element):
    return element.find(".//DISS_description/DISS_institution/DISS_inst_contact").text

def get_advisor(element):
    first_name = element.find(".//DISS_description/DISS_advisor/DISS_name/DISS_fname").text
    last_name = element.find(".//DISS_description/DISS_advisor/DISS_name/DISS_surname").text
    return f"{last_name}, {first_name}"

def get_pub_date(element):
    return element.find(".//DISS_description/DISS_dates/DISS_accept_date").text

def get_abstract(element):
    data = [e.text for e in element.findall(".//DISS_content/DISS_abstract/DISS_para")]
    return '\n\n'.join(data)

def get_embargo(element):
    # the date is in the "remove" attribute in the 
    return element.find("")

def get_full_text_url(item):
    file_name = item.replace('.xml', '.pdf')
    return f"https://mssa.altfindingaids.library.yale.edu/gsas_etds_2021_spring/{file_name}"

# NOT INCLUDING THE DISCIPLINES OR COMMENTS FIELDS UNTIL I KNOW WHAT SHOULD GO THERE; SHOULD ALSO # ASK ABOUT THE KEYWORDS AND DEPARTMENT FIELDS. ALSO NOT INCLUDING THE COMMITTEE MEMBERS, BUT WILL
# ASK ABOUT THAT TOO; ONLY PUT IN THE FIRST ADVISOR

def extract_xml_data(diss_fp, csvoutfile):
    full_text_urls = get_url_chunk()
    extracted_files = [item for item in os.listdir(diss_fp) if item != '.DS_Store']
    for submission_directory in tqdm(extracted_files):
        full_dir = f"{diss_fp}/{submission_directory}"
        submission_files = [item for item in os.listdir(full_dir) if item != '.DS_Store']
        for item in submission_files:
            full_path = f"{full_dir}/{item}"
            if item.endswith('.json'):
                with open(full_path) as jsonfile:
                    json_data = json.load(jsonfile)
                    pub_date = json_data.get('Date of last event', '')
            if item.endswith('_DATA.xml'):
                parsed_data = etree.parse(full_path)
                title = get_titles(parsed_data)
                # full_text_url = get_full_text_url(item)
                first_name = get_first_name(parsed_data)
                middle_name = get_middle_name(parsed_data)
                last_name = get_last_name(parsed_data)
                suffix = get_suffix(parsed_data)
                email = get_email(parsed_data)
                institution = get_institution(parsed_data)
                keywords = get_keywords(parsed_data)
                degree = get_degree(parsed_data)
                department = get_department(parsed_data)
                advisor = get_advisor(parsed_data)
                # pub_date = get_pub_date(parsed_data)
                abstract_data = get_abstract(parsed_data)       
            if item.endswith('.xml') and not item.endswith('_DATA.xml'):
                identifier = item.replace('.xml', '')
                if identifier in full_text_urls:
                    full_text_url = full_text_urls.get(identifier)
                else:
                    full_text_url = f"NA"
        csvoutfile.writerow([title, full_text_url, keywords, abstract_data, first_name, middle_name, last_name, suffix, email, institution, advisor, '', '', '', '', degree, department, 'dissertation', pub_date, 'Spring'])

def get_url_chunk(full_text_url_path, diss_fp):
    with open(full_text_url_path, 'r', encoding='utf8') as urls:
        reader = csv.reader(urls)
        next(reader)
        return {row[0].replace(diss_fp, '').replace('.pdf', ''): row[0] for row in reader}

def get_files_on_server(diss_fp, dirpath, full_text_url_path):
    with open(full_text_url_path, 'w', encoding='utf8') as urls:
        writer = csv.writer(urls)
        writer.writerow(['url'])
        files = [[f"{diss_fp}/{item}"] for item in os.listdir(dirpath) if item != '.DS_Store']
        writer.writerows(files)

# def get_google_urls():
#     with open('/Users/aliciadetelich/Desktop/etd_project/scripts/dissertation_download_links.csv', 'r', encoding='utf8') as urls:
#         reader = csv.reader(urls)
#         next(reader)
#         # first column is pub number, second column is download link 
#         return {row[0]: row[1] for row in reader}

def upload_to_server():
    pass

def prep_path_to_server():
    pass


def main():
    diss_fp = input('Please enter path to dissertation directory: ')
    outfile_path = input('Please enter path to outfile: ')
    with open(outfile_path, 'a', encoding='utf8') as csvfile:
        writer = csv.writer(csvfile)
        header_row = ['title', 'fulltext_url', 'keywords', 'abstract', 'author1_fname', 'author1_mname', 'author1_lname', 'author1_suffix', 'author1_email', 'author1_institution', 'advisor1', 'advisor2', 'advisor3', 'disciplines', 'comments', 'degree_name', 'department', 'document_type', 'publication_date', 'season']
        writer.writerow(header_row)
        extract_xml_data(diss_fp, writer)


if __name__ == "__main__":
    main()