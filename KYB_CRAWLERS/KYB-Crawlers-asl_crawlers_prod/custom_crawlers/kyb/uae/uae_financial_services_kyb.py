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
import requests, json, os, re
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
    meta_detail['capital_details'] = record[2]
    meta_detail['country_of_origin'] = record[3]
    meta_detail['fiscal_year'] = record[4]
    meta_detail['incorporation_date'] = str(pd.to_datetime(record[5]))
    meta_detail['industry_details'] = record[6]
    meta_detail['isin_code'] = record[7]
    meta_detail['listing_date'] = record[8]
    meta_detail['registrar'] = record[10]

    people_details = record[9]
    additional_detail = record[12]
    addresses_detail = record[1]
    fillings_detail = record[11]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": "",
        "crawler_name": "crawlers.custom_crawlers.kyb.uae.uae_financial_services_kyb",
        "country_name": "UAE",
        "company_fetched_data_status": "",
        "meta_detail": meta_detail,
        "people_details": people_details,
        "additional_detail": additional_detail,
        "addresses_detail": addresses_detail,
        "fillings_detail": fillings_detail
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{record[-1]}-{url_}-uae_financial_services_kyb')) # entity_id
    data_for_db.append(record[0].replace("'", "")) #name
    data_for_db.append(json.dumps([str(pd.to_datetime(record[5]))])) #dob
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
        API_URL = "https://api2.dfm.ae/web/widgets/v1/data"

        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'api2.dfm.ae',
            'Origin': 'https://www.dfm.ae',
            'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': "macOS",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }

        payload = {'body': 'Command=LiteSecuritiesLists&Language=en'}
        details_payload = {'body': 'Command=companyprofile&lang=en&symbol={}'}
        reports_payload = {'body': 'Command=GetFreshCorporateGovernanceReports&Company={}&Language=en'}
        general_meetings_payload = {'body': 'Command=GetFreshGeneralMeetings&Company={}&Language=en'}
        shareholders_payload = {'body': 'Command=GetFreshTopShareholders&Company={}&Language=en'}
        foreign_investment_payload = {'body': 'Command=GetFreshForeignInvestment&Company={}&Language=en'}
        news_payload = {'body': 'Command=GetDisclosures&Company={}&Language=en'}

        response = requests.post(API_URL, data=payload['body'], headers=headers, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

        json_response = json.loads(response.content)
        equities = json_response['Equities']

        DATA = []
        for entity in equities:
            symbol = entity['SecuritySymbol']
            print(entity['SecuritySymbol'])

            details_response = requests.post(API_URL, data=details_payload['body'].format(symbol), headers=headers, timeout=60)
            details_data = json.loads(details_response.content)

            entity_name = details_data.get('FullName')
            address = details_data.get('ContactDetails').get('OfficeAddress').replace("'","")
            capital_details = details_data.get('AuthorizedCapital')
            contact_details = {'phone_number':details_data.get('ContactDetails').get('Phone'), 'fax_number':details_data.get('ContactDetails').get('Fax'), 
                               'website':details_data.get('ContactDetails').get('Website'), 'email':details_data.get('ContactDetails').get('Email')}
            origin = re.search(r'<strong>(.*?)</strong>', details_data.get('CompanyBrief')) if details_data.get('CompanyBrief') else ""
            country_of_origin = origin.group(1).split(':')[-1] if origin else "" if origin != "" else ""
            fiscal_year = details_data.get('FiscalYearEnd')
            incorporation_date = details_data.get('EstablishedDate')
            industry_details = details_data.get('Sector')
            isin_code = details_data.get('ISIN')
            listing_date = details_data.get('DateOfListing')

            people_details = []
            board_members = {'type':'board_members', 'data':[]}
            for bds in details_data.get('Board'):
                board_members['data'].append({'name':bds.get('Name').replace("'",""), 'designation':bds.get('Title').replace("'","")})
            people_details.append(board_members)
            top_management = {'type':'top_management', 'data':[]}
            for managers in details_data.get('TopManagement'):
                top_management['data'].append({'name':managers.get('Name').replace("'",""), 'designation':managers.get('Title').replace("'","")})
            people_details.append(top_management)

            share_details = {'issued_shares':details_data.get('IssuedShares'), 'par_value_shares':details_data.get('PerShareValue')}
            registrar = details_data.get('Registrar')

        #   News Details
            news_details = []
            news_response = requests.post(API_URL, data=news_payload['body'].format(symbol), headers=headers, timeout=60)
            news_data = json.loads(news_response.content)
            for news in news_data:
                news_details.append({'description':news.get('Title').replace("'",""), 'date':news.get('Date'), 'source_url':news.get('FileContent').split('>')[0].split('href=')[-1].replace("'","")})

        #   Filling Details
            filling_details = []
            reports_response = requests.post(API_URL, data=reports_payload['body'].format(symbol), headers=headers, timeout=60)
            reports_data = json.loads(reports_response.content)
            for report in reports_data:
                filling_details.append({'description':report.get('Title').replace("'",""), 'date':report.get('Date'), 'source_url':report.get('EnglishFileContent').split('>')[0].split('href=')[-1].replace("'","")})
            
        #   General Meeting Details
            general_meeting_details = []
            general_meeting_response = requests.post(API_URL, data=general_meetings_payload['body'].format(symbol), headers=headers, timeout=60)
            general_meetings_data = json.loads(general_meeting_response.content)
            for gm in general_meetings_data:
                object_gm = {'date':gm.get('publication_date'), 'source_url':[]}
                for resource in gm['resources']:
                    object_gm['source_url'].append(resource['r_path'].replace("'",""))
                general_meeting_details.append(object_gm)

        #   Shareholders Details
            shareholders_details = {'individual_investors':[], 'associated_groups':[]}
            shareholders_response = requests.post(API_URL, data=shareholders_payload['body'].format(symbol), headers=headers, timeout=60)
            shareholders_data = json.loads(shareholders_response.content)
            if shareholders_data.get('Item2'):
                for shareholder in shareholders_data.get('Item2'):
                    if shareholder.get('IsAssociated') == False:
                        shareholders_details['individual_investors'].append({'name': shareholder.get('Name').strip(), 'share_percentage': shareholder.get('Percentage')})
                    if shareholder.get('IsAssociated') == True:
                        associates = shareholder.get('Shareholders')
                        group_name = shareholder.get('Name')
                        for associate in associates:
                            shareholders_details['associated_groups'].append({'group':group_name, 'name':associate.get('Name').strip(), 'share_percentage':associate.get('Percentage')})

        #   Foreign Investment Details
            foreign_investment_response = requests.post(API_URL, data=foreign_investment_payload['body'].format(symbol), headers=headers, timeout=60)
            foreign_investment_data = json.loads(foreign_investment_response.content)
            foreign_investment_details = {'national':{'actual':foreign_investment_data.get('NationalActual'), 'permitted':foreign_investment_data.get('NationalPermitted'), 'available':foreign_investment_data.get('NationalAvailable')},
                                          'gcc':{'actual':foreign_investment_data.get('GCCActual'), 'permitted':foreign_investment_data.get('GCCPermitted'), 'available':foreign_investment_data.get('GCCAvailable')},
                                          'foreign':{'actual':foreign_investment_data.get('ForeignActual'), 'permitted':foreign_investment_data.get('ForeignPermitted'), 'available':foreign_investment_data.get('ForeignAvailable')}
                                        }
            
            additional_details = []
            additional_details.append({'type':'contact_details', 'data':[contact_details]})
            additional_details.append({'type':'news/announcements', 'data':news_details})
            additional_details.append({'type':'share_details', 'data':[share_details]})
            additional_details.append({'type':'general_meeting_details', 'data':general_meeting_details})   
            additional_details.append({'type':'shareholders_details', 'data':[shareholders_details]}) 
            additional_details.append({'type':'foreign_investment_details', 'data':[foreign_investment_details]})    

            address_detail = [{'type':'address', 'address':address}]    

            DATA.append([entity_name, address_detail, capital_details, country_of_origin, fiscal_year, incorporation_date, industry_details, isin_code, listing_date, people_details, registrar, filling_details, additional_details, address])
            
            record = [entity_name, address_detail, capital_details, country_of_origin, fiscal_year, incorporation_date, industry_details, isin_code, listing_date, people_details, registrar, filling_details, additional_details, address]
        
            record_for_db = prepare_data(record, category, country, entity_type, source_type, name, url, description)
                        
            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)
            
            print("Stored record.")
            if record_for_db[1] != "":
                crawlers_functions.db_connection(query)

        return len(DATA), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")


if __name__ == '__main__':
    '''
    Description: HTML Crawler for UAE Financial market
    '''
    countries = "UAE"
    entity_type = "Company/Organization"
    category = "Financial Services"
    name ="Dubai Financial Market. (DFM)"
    description = "The website provides information and resources on listed securities, including equities, bonds, funds, and derivatives, as well as market data, news, and insights on the UAE and regional markets. In summary, DFM is the publisher of the website, which is dedicated to providing a premier stock exchange platform for investors and companies in the UAE and the region."
    source_type = "HTML"
    url = "https://www.dfm.ae/en/the-exchange/market-information/listed-securities/equities" 

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
