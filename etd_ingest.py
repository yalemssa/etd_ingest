#!/usr/bin/python3

from pathlib import Path
import os
import shutil
import zipfile

from lxml import etree
from tqdm import tqdm

from utilities import utilities as utes

'''
Proposed workflow:
1.) Connect to M Drive and get list of files from Dissertations folder - DONE
2.) Compare the file list against another folder (i.e. staging folder) which contains previous extractions - DONE
3.) Move folder to staging area and unzip - make a directory in the staging area with the same name as the zipped file
	and extract each into its own folder; this is really only necessary to keep track of the files which have already been 
	processed. It's possible there's another, better way to do that - DONE
4.) Extract metadata from the .xml file with that ends with _DATA.xml
		-this is not yet done, and the specifics will be determined at the next meeting
		-Most of the mapping from the XML file to the EliScholar metadata is done, with a few questions (see bottom of file)


Need to create metadata for 3 different sources:
	1.) EliScholar - the required metadata is listed in a gsas_dissertations.xslx template on the BePress demo site. As far as I can tell BePress does not have an API through which you can perform bulk uploads. Instead, they have a bulk upload via Excel menu option in their administrative interface. Excel bulk upload spreadsheets can be created and outputed by this script. It seems like the red headings are required fields, though I haven't contacted BePress to get instructions (for some reason the bulk upload page says to do that rather than just giving the instructions). ALSO, the only link to the actual object looks to be the fulltext_url column. It's not clear to me what that value should be.
	2.) Voyager - need input from YUL tech services about metadata fields; will also need info about links here.
	3.) Preservica - need input from KG about metadata fields; also want to manage ingest or no?
'''

DISSERTATION_PATH = 'M:\\Dissertations'
STAGING_PATH = 'M:\\Dissertations_Staging'

def unzip_files(file_list):
	for filename in file_list:
		print(f"Working on {filename}")
		diss_path = f"{DISSERTATION_PATH}/{filename}.zip"
		dest_filepath = f"{STAGING_PATH}/{filename}"
		os.mkdir(dest_filepath)
		with zipfile.ZipFile(diss_path, 'r') as zipped:
			print(f"Unzipping {filename}")
			zipped.extractall(dest_filepath)

def extract_xml_data():
	for filename in file_list:
		data_path = f"{STAGING_PATH}/{filename}"
		for file in os.listdir(data_path):
			if file.endswith('DATA.xml'):
				process_file(f"{data_path}/{file}")

def process_file(filename):
	tree = etree.parse(filename)
	root = tree.getroot()
	#lots of stuff could happen here....need to decide exactly what we want
	#should return a spreadsheet for ingest into EliScholar
	#should also return ingest stuff for Voyager and Preservica
	#not sure if it's possible to manage the actual Preservica ingest here,
	#or if I just want to output some kind of file so that Kevin can ingest.
	#Discuss at next meeting 

def extract_abstract(root):
	#move to a constant?
	abstract = root.find(".//DISS_abstract")
	paragraphs = abstract.getchildren()
	return [paragraph.text for paragraph in paragraphs]


def main():
	new_files = [Path(filename).stem for filename in os.listdir(DISSERTATION_PATH)
					if Path(filename).stem not in os.listdir(STAGING_PATH)
					and filename.endswith('.zip')]
	unzip_files(new_files)
	extract_xml_data(new_files)

if __name__ == "__main__":
	main()



'''
This is the list of tags from the DATA xml file.
The number of paragraph tags in the abstract and the number of advisors may change; this means that I should do some kind of findall?

Don't know what the publication or document type should be...also don't know
the URL

DISS_submission
	DISS_authorship
		DISS_author
			DISS_name
				DISS_surname <--------------------------> author1_lname
				DISS_fname <--------------------------> author1_fname
				DISS_middle <--------------------------> author1_mname
				DISS_suffix <--------------------------> author1_suffix
			DISS_contact
				DISS_contact_effdt
				DISS_address
					DISS_addrline
					DISS_addrline
					DISS_city
					DISS_st
					DISS_pcode
					DISS_country
					DISS_email
					DISS_contact
					DISS_contact_effdt
					DISS_address
					DISS_addrline
					DISS_addrline
					DISS_city
					DISS_st
					DISS_pcode
					DISS_country
				DISS_email <--------------------------> author1_email
			DISS_citizenship
	DISS_description
		DISS_title <--------------------------> title
		DISS_dates
			DISS_comp_date
			DISS_accept_date
		DISS_degree <--------------------------> degree_name
		DISS_institution
			DISS_inst_code
			DISS_inst_name <-----------------------> author1_institution
			DISS_inst_contact <--------------------------> department
			DISS_processing_code
		DISS_advisor <--------------------------> advisor1 (extract; check for multiples); where should committee members go?
			DISS_name
			DISS_surname
			DISS_fname
			DISS_middle
		DISS_cmte_member
			DISS_name
			DISS_surname
			DISS_fname
			DISS_middle
			DISS_suffix
		DISS_cmte_member
			DISS_name
			DISS_surname
			DISS_fname
			DISS_middle
			DISS_suffix
		DISS_categorization
			DISS_category
				DISS_cat_code
				DISS_cat_desc <--------------------------> disciplines
			DISS_keyword <--------------------------> keywords
			DISS_language
	DISS_content
		DISS_abstract <--------------------> abstract (extract children)
			DISS_para
			DISS_para
			DISS_para
			DISS_para
		DISS_binary
	DISS_restriction
	DISS_repository
		DISS_version
		DISS_agreement_decision_date
		DISS_acceptance
		DISS_delayed_release
		DISS_access_option
	DISS_creative_commons_license
		DISS_abbreviation

'''