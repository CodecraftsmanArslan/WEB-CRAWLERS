"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid,time
from bs4 import BeautifulSoup
import pandas as pd
import requests, json, os, copy
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from helpers.crawlers_helper_func import CrawlersFunctions

load_dotenv()

'''create an instance of Crawlers Functions'''
crawlers_functions = CrawlersFunctions()
'''GLOBAL VARIABLES'''
environment = os.getenv('ENVIRONMENT')
FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/html/'
FILENAME=''
DATA_SIZE = 0
PAGE_COUNT = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'

def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.
   
    @param record
    @return dict
    '''

    # preparing meta_detail dictionary object
    meta_detail = dict()
    meta_detail['industry_details'] = record[1]
    meta_detail['isin_code'] = record[3]
    meta_detail['incorporation_date'] = record[4]
    meta_detail['address'] = record[7]
    meta_detail['number_of_branches'] = record[10]
    meta_detail['annual_gm_date'] = record[11]

    additional_details = list()
    additional_details.append({"type":"foreign_investments_details", "data":[record[17]]})
    additional_details.append({"type":"financial_reports", "data":[record[15]]})
    additional_details.append({"type":"news_details", "data":[record[16]]})
    additional_details.append({"type":"contact_details", "data":[record[14]]})
    additional_details.append({"type":"capital_details", "data":[record[12]]})
    additional_details.append({"type":"employee_details", "data":[record[9]]})
    additional_details.append({"type":"industry_details", "data":[record[1]]})

    people_details = list()
    people_details.append({"type":"board_details", "data":[record[13]['board_details']]})
    people_details.append({"type":"member_details", "data":[record[13]['member_details']]})
    people_details.append({"type":"administration_details", "data":[record[13]['administration_details']]})

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": record[18],
        "registration_number": record[2],
        "registration_date": record[5],
        "dissolution_date": record[6],
        "type": record[8],
        "crawler_name": "crawlers.custom_crawlers.kyb.oman_stock_market_kyb",
        "country_name": "Oman",
        "company_fetched_data_status": "",
        "meta_detail": meta_detail,
        "additional_details": additional_details,
        "people_details": people_details 
    }
    
    return data_obj

def prepare_data(record, category, country, entity_type, type_, name_, url_, description_):
    '''
    Description: This method is used to prepare the data to be stored into the database
    1) Reads the data from the record
    2) Transforms the data into database writeable format (schema)
    @param record
    @param counter_
    @param schema
    @param category
    @param country
    @param entity_type
    @param type_
    @param name_
    @param url_
    @param description_
    @param dob_field
    @return data_for_db:List<str/json>
    '''
    data_for_db = list()
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{record[1]}-{record[2]}')) # entity_id
    data_for_db.append(record[0].replace("'", "")) #name
    data_for_db.append(json.dumps([str(pd.to_datetime(record[4]))])) #dob
    data_for_db.append(json.dumps([category.title()])) #category
    data_for_db.append(json.dumps([country.title()])) #country
    data_for_db.append(entity_type.title()) #entity_type
    data_for_db.append(json.dumps([])) #img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'","''"), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(record))) # data
    data_for_db.append(json.dumps(source_details)) #source_details
    data_for_db.append(name_ + "-" + type_) # source
    data_for_db.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 
    data_for_db.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        data_for_db.append(detect(data_for_db[1]))
    except:
        data_for_db.append('en')
    data_for_db.append('true')
    return data_for_db


def get_records(source_type, entity_type, country, category, url, name, description):
    '''
    Description: This method is used to Prepare the data to be inserted into the database by parsing the metadata and using parsers mentioned above
    @param source_type:str
    @param category:str
    @param country:str
    @param description:str
    @param url_:str
    @param entity_type:str
    @return data_len:int
    @return status:bool
    '''
    try:
        global DATA_SIZE, STATUS_CODE, CONTENT_TYPE, FILENAME
        SOURCE_URL = url
        API_URL = "https://www.msx.om/companies.aspx/List"
        PROFILE_DATA_URL = "https://www.msx.om/snapshot.aspx?s={}"
        BODMember_DATA_URL = "https://www.msx.om/BODMembersSnap.aspx?s={}"
        Financial_DATA_URL = "https://www.msx.om/snapshot.aspx/FinancialsReports"
        News_DATA_URL = "https://www.msx.om/company-news.aspx?s={}&y={}&f=1&t=12&i="
        ForeignInvestment_DATA_URL = "https://www.msx.om/snapshot.aspx/ForeignInvestments"

        headers = {
                'Authority': 'www.msx.om',
                'Method': 'POST',
                'Path': '/companies.aspx/List',
                'Scheme': 'https',
                'Accept': '*/*',
                'Content-Type': 'application/json',
                'Origin': 'https://www.msx.om',
                'referer': 'https://www.msx.om/companies.aspx',
                'Sec-Ch-Ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': "macOS",
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
            }
        
        response = requests.post(API_URL, headers=headers, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

        json_response = response.json()
        DATA = []
        for item in json_response['d']:
            key = item['Symbol']

            company_name = item['LongNameEn']
            response = requests.get(PROFILE_DATA_URL.format(key), headers=headers, timeout=60)
            soup = BeautifulSoup(response.content, 'html.parser')

        #   Initial Details
            industry_details = {'industry_type':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_ActivityLabel'}).text.replace("'",""),
                                'sector':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_SubSectorLabel'}).text}
            
            reg_number = soup.find('span', {'id':'ctl00_ContentPlaceHolder1_CommercialIDLabel'}).text.replace(' ','')
            registration_number = reg_number.split('#')[-1] if '#' in reg_number else reg_number

            isin_code = soup.find('span', {'id':'ctl00_ContentPlaceHolder1_ISINLabel'}).text
            incorporation_date = soup.find('span', {'id':'ctl00_ContentPlaceHolder1_EstablishedInLabel'}).text.replace("'","")
            registration_date = soup.find('span', {'id':'ctl00_ContentPlaceHolder1_ListedDateLabel'}).text.replace("'","")
            dissolution_date = soup.find('span', {'id':'ctl00_ContentPlaceHolder1_DeListedDateLabel'}).text.replace("'","")
            address = soup.find('span', {'id':'ctl00_ContentPlaceHolder1_HeadOfficeLabel'}).text.replace("'","")
            item_type = soup.find('span', {'id':'ctl00_ContentPlaceHolder1_TypeLabel'}).text
            
            if dissolution_date == "-":
                company_status = "Listed"
            else:
                company_status = "Delisted"

            employee_details = {'omani_employees':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_OmaniLabel'}).text,
                                'non-omani_employees':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_NonOmaniLabel'}).text}
            
            number_of_branches = soup.find('span', {'id':'ctl00_ContentPlaceHolder1_NumberofBranchesLabel'}).text
            annual_gm_date = soup.find('span', {'id':'ctl00_ContentPlaceHolder1_AGMDateLabel'}).text.replace("'","")

        #   Capital Details Extraction
            capital_details = {'authorized_capital':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_AuthorizedCapitalLabel'}).text,
                               'issued_shares':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_IssuedSharesLabel'}).text,
                               'paidup_capital':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_PaidupcapitalLabel'}).text}
            
        #   People Details Extraction
            board_information = {'chairman':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_ChairmanLabel'}).text.replace("'",""),
                                 'deputy':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_DeputyLabel'}).text,
                                 'secretary':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_SecretaryLabel'}).text}
            
            members_name = soup.find('span', {'id':'ctl00_ContentPlaceHolder1_MembersLabel'}).text.split('\r')
            member_details = []
            bod_response = requests.get(BODMember_DATA_URL.format(key), headers=headers, timeout=60)
            if bod_response.json():
                for member in bod_response.json():
                    member_details.append({'name':member['MemberNameEn'].replace("'",""), 'panel_member_detail':{'is_independent':member['IndependentEn'],'is_executive':member['ExecutiveEn'],
                                                                                'is_shareholder':member['ShareholderEn'],'is_representing':member['RepresentingEn']}})
            else:
                for member in members_name:
                    member_details.append({'name':member.replace("'",""), 'panel_member_detail':{'is_independent':'','is_executive':'','is_shareholder':'','is_representing':''}})

            administration_details = {'chief_executive_president':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_ChiefExecutivePresidentLabel'}).text, 'internal_auditor':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_InternalAuditorLabel'}).text, 
                                      'managing_director':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_ManagingDirectorLabel'}).text, 'legal_advisor':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_LegalAdvisorLabel'}).text,
                                      'auditor':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_AuditorLabel'}).text, 'deputy_of_executive_president':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_DeputyofExecutivePresidentLabel'}).text}
            
            people_details = {'board_details':board_information, 'member_details':member_details, 'administration_details':administration_details}

        #   Contact Details Extraction
            contact_details = {'contact_information':'','investor_relations_information':'','company_contact':''}
            contact_information = {'representative':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_RepresentativeLabel'}).text, 'address':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_RepAddressLabel'}).text.replace("'",""), 
                                   'telephone':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_RepTelephoneLabel'}).text, 'mobile':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_RepMobileLabel'}).text, 
                                   'fax':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_RepFaxLabel'}).text, 'email':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_RepEmailIDLabel'}).text}
            investor_relations_information = {'name':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_lblInvRelOff'}).text.replace("'",""), 'address':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_lblInvRelAddress'}).text.replace("'",""), 
                                              'phone_number':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_lblTelephone'}).text, 'email':soup.find('a', {'id':'ctl00_ContentPlaceHolder1_hplInvRelEmailID'}).text}
            company_contact = {'address':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_AddressLabel'}).text.replace("'",""),'telephone':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_TelephoneLabel'}).text,
                               'fax':soup.find('span', {'id':'ctl00_ContentPlaceHolder1_FaxLabel'}).text,'email':soup.find('a', {'id':'ctl00_ContentPlaceHolder1_EmailIDHyperLink'}).text,
                               'website':soup.find('a', {'id':'ctl00_ContentPlaceHolder1_WebsiteHyperLink'}).text}
            contact_details = {'contact_information':contact_information, 'investor_relations_information':investor_relations_information, 'company_contact':company_contact}

        #   Financial Reports Extraction
            financial_reports = []
            headers_financial = copy.deepcopy(headers)
            headers_financial['Path'] = '/snapshot.aspx/FinancialsReports'
            financial_source_url = "https://www.msx.om/MSMDOCS/FinancialReports/{}"
            financial_response = requests.post(Financial_DATA_URL, data=json.dumps({'Symbol':key, 'Year':''}), headers=headers_financial, timeout=60).json()
            for financial_data in financial_response['d']:
                financial_reports.append({'date':financial_data['UploadDate'].replace("'",""), 'title':financial_data['TitleEn'].replace("'",""), 'source_url':financial_source_url.format(financial_data['FileNameEn'])})

        #   News Details Extraction
            news_details = []
            year = 2023
            while year >= 1994:
                news_response = requests.get(News_DATA_URL.format(key,year)).json()
                if news_response:
                    for new in news_response:
                        news_detail_url = "https://www.msx.om/MSMDocs/Images/NewsDocs/{}".format(new['Doc_News']) if new['Doc_News'] != "" else ""
                        news_details.append({'description':new['TitleEn'].replace("'",""), 'source_url':news_detail_url})
                else:
                    break
                year-=1

        #   Foreign Details Extraction
            headers_foreign = copy.deepcopy(headers)
            headers_foreign['Path'] = '/snapshot.aspx/ForeignInvestments'
            fi_response = requests.post(ForeignInvestment_DATA_URL, data=json.dumps({'Symbol':key, 'Owned':'True', 'Year':'', 'Month':''}), headers=headers_foreign, timeout=60)
            foreign_investments_details = fi_response.json()['d']
        
            DATA.append([company_name, industry_details, registration_number, isin_code, incorporation_date, registration_date,
                         dissolution_date, address, item_type, employee_details, number_of_branches, annual_gm_date, capital_details,
                         people_details, contact_details, financial_reports, news_details, foreign_investments_details, company_status])
            
            record = [company_name, industry_details, registration_number, isin_code, incorporation_date, registration_date,
                    dissolution_date, address, item_type, employee_details, number_of_branches, annual_gm_date, capital_details,
                     people_details, contact_details, financial_reports, news_details, foreign_investments_details, company_status]
        
            record_for_db = prepare_data(record, category, country, entity_type, source_type, name, url, description)
                        
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
            
            if record_for_db[1] != "":
                print("Record stored.")
                crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for Oman Stock Market
    '''
    countries = "Oman"
    entity_type = "Company/Organization"
    category = "Stock Market"
    name ="Muscat Securities Market (MSM)"
    description = "This is the website of the Muscat Securities Market (MSM) in Oman. It provides information on the companies listed on the exchange."
    source_type = "HTML"
    url = "https://www.msx.om/companies.aspx" 

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
