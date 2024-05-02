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
    meta_detail['capital_details'] = record[1]
    meta_detail['listing_date'] = record[2]
    meta_detail['incorporation_date'] = str(pd.to_datetime(record[3]))
    meta_detail['auditor'] = record[5]
    meta_detail['article_of_association'] = record[6]
    meta_detail['description'] = record[7]
    
    people_details = record[8]
    additional_detail = record[9]
    fillings_detail = record[10]

    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name":record[0].replace("'","''"),
        "status": "",
        "registration_number": "",
        "registration_date": "",
        "dissolution_date": "",
        "type": record[4],
        "crawler_name": "crawlers.custom_crawlers.kyb.uae.uae_stock_market_adx_kyb",
        "country_name": "UAE",
        "company_fetched_data_status": "",
        "meta_detail": meta_detail,
        "people_details": people_details,
        "additional_detail": additional_detail,
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
    data_for_db.append(shortuuid.uuid(f'{record[0]}-{record[1]}-{url_}-crawlers.custom_crawlers.kyb.uae_stock_market_adx_kyb')) # entity_id
    data_for_db.append(record[0].replace("'", "")) #name
    data_for_db.append(json.dumps([str(pd.to_datetime(record[3]))])) #dob
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
        ASSETS_API_URL = "https://adxservices.adx.ae/WebServices/DataServices/api/web/assets"
        DETAILS_API_URL = "https://www.adx.ae/en/_vti_bin/adx/svc/Members.svc/ListedCompany?listedcompanyid={}"
        FOREIGNDETAILS_API_URL = "https://adxservices.adx.ae/WebServices/DataServices/api/web/company"
        FINANCIAL_API_URL = "https://www.adx.ae/en/_vti_bin/adx/svc/Members.svc/news?ctn=efid&ctv={}&itms=500"
        NEWS_API_URL = "https://www.adx.ae/en/_vti_bin/adx/svc/Members.svc/news?ctn=eid&ctv={}&itms=500"
        SHAREHOLDERS_API_URL = "https://www.adx.ae/en/_vti_bin/adx/svc/trading.svc/ListedCompanyShareholders?date=01-01-1970&listedcompanyid={}"

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'adxservices.adx.ae',
            'Origin': 'https://www.adx.ae',
            'Referer': 'https://www.adx.ae/',
            'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': "macOS",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }
        company_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': 'ASP.NET_SessionId=lu1lc3p3val1bovpzq23uacs; node=1013017135; dtCookie=v_4_srv_4_sn_2D6B26ECC01A16A9AD9E1C701C2660CC_perc_100000_ol_0_mul_1_app-3A2dffb00433f451c6_0; BIGipServerExt_ADX_WEBSITE_PROD.app~Ext_ADX_WEBSITE_PROD_pool=!E1uWBOmbNPkupSfCi6M5qZ63MDQYiXVwdgiXdVeeZVQBM9j8hdW7IFXLtCOadbMea0hEuDTuw1yPDjc=; _ga=GA1.2.578127861.1684392651; _gid=GA1.2.1246210588.1684392651; WSS_FullScreenMode=false; TS01b242cf=019c04258cbcca3139ab0abf76fe23a4dd10b1bf813750999e37fb686964bb1904d23d1ac90603da7d4706d8914cbc2cd6fbeb18d48efa6afe45783e030a10119889ef9f34bd287c603bcc72ce48f0dd96b4a15f4a349e6e7d3b05182829eeb8e9f8d5a938; TS01aa7d4c=019c04258c72ef154e073891f4469e5804954e7cf688863d1048c858b60125bbb46324d32f4791d0fc242be5de8a4e920c64fc99c586156c6981c79c307a60ccd7ccce83f665c32b02244a300ec96e62a29e9cfe4b; _gat=1; TSd96eb3a0027=08c370503aab20007b2415c1fa769d43cc6cd46924d37c44c91092fe58442ae780911a3e9f547b2008c33ad431113000268f57c7883f1b03e9b21dd167ea9759ab1f484ef7ff426c2f853fbdc569e5de0dfbc60191f522b0350410f24e17d725',
            'Host': 'www.adx.ae',
            'Referer': 'https://www.adx.ae/english/pages/productsandservices/securities/selectcompany/default.aspx?listedcompanyid=ABNIC&ISIN=AEA001701019&pnavTitle=Al%20Buhaira%20National%20Insurance%20Company',
            'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': "macOS",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'X-Dtpc': '4$205622897_420h16vQFFLPTDNVPRTPJKCBTKEHUHFCOQNSIQC-0e0',
            'X-Requested-With': 'XMLHttpRequest'
        }
        financial_headers = copy.deepcopy(company_headers)
        financial_headers['Cookie'] = 'ASP.NET_SessionId=lu1lc3p3val1bovpzq23uacs; node=1013017135; dtCookie=v_4_srv_4_sn_2D6B26ECC01A16A9AD9E1C701C2660CC_perc_100000_ol_0_mul_1_app-3A2dffb00433f451c6_0; BIGipServerExt_ADX_WEBSITE_PROD.app~Ext_ADX_WEBSITE_PROD_pool=!E1uWBOmbNPkupSfCi6M5qZ63MDQYiXVwdgiXdVeeZVQBM9j8hdW7IFXLtCOadbMea0hEuDTuw1yPDjc=; _ga=GA1.2.578127861.1684392651; _gid=GA1.2.1246210588.1684392651; WSS_FullScreenMode=false; TS01b242cf=019c04258c882c249678a8e5a6e1b28d4e45845e90c33a2b198623bea19c924772565efdc78c8269a2740d5c127b2b509a96559d7a40fe5dae4eb3b66bd088b8d2f2ca98c06b2f9e0a85a930ce3b83ecad384a85cde7b60c27c4d8be7ac04eba0cdd28fc6b; TS01aa7d4c=019c04258cd602c9f07fd2d898a6f82d6491d7ee9388863d1048c858b60125bbb46324d32f4791d0fc242be5de8a4e920c64fc99c543c47e5ec846c766f45cda24933cb1d84d37030115c7b5a5877f3a048bdeac67; _gat=1; TSd96eb3a0027=08c370503aab20000fa01b14b5f4c1b6b62535bcd134a3235942a2c3ddf75ffc19cfcd1b66d5865e0815032136113000a6e014faa581a61d6e6eaa10b1c85873e0c2d95b9be95fa6fcec00aa0703d934deb699b98b54715fe5ddf087d15381a7'
        financial_headers['Referer'] = 'https://www.adx.ae/english/pages/productsandservices/securities/selectcompany/financialreports.aspx?listedcompanyid=ABNIC&ISIN=AEA001701019&pnavTitle=Al%20Buhaira%20National%20Insurance%20Company'
        
        news_headers = copy.deepcopy(company_headers)
        news_headers['Cookie'] = 'ASP.NET_SessionId=lu1lc3p3val1bovpzq23uacs; node=1013017135; dtCookie=v_4_srv_4_sn_2D6B26ECC01A16A9AD9E1C701C2660CC_perc_100000_ol_0_mul_1_app-3A2dffb00433f451c6_0; BIGipServerExt_ADX_WEBSITE_PROD.app~Ext_ADX_WEBSITE_PROD_pool=!E1uWBOmbNPkupSfCi6M5qZ63MDQYiXVwdgiXdVeeZVQBM9j8hdW7IFXLtCOadbMea0hEuDTuw1yPDjc=; _ga=GA1.2.578127861.1684392651; _gid=GA1.2.1246210588.1684392651; WSS_FullScreenMode=false; TS01b242cf=019c04258ccdcc18f859ae9e289acf0897e880f3fc16a75fecbfa30d9682a24624acc4c04cfabee13c4ee5c08d7eacc2447d34a327b0df4aa7601dc5a53442ba1924357ba4cc7e746d0f4c2f18adb183c8e73bde6e17a433d18223b258ff5d26f3c9b83e8e; TS01aa7d4c=019c04258cf95f5e574105172f67e2f7bd899912bd88863d1048c858b60125bbb46324d32f4791d0fc242be5de8a4e920c64fc99c52a47d39a0149382e7d24e038af1c12e70f047009e8fa900af2e76f17a4a563ef; _gat=1; TSd96eb3a0027=08c370503aab2000562a4631d503582380ac0ae9d086586e518735fc2e8d80f70525a14b43d6e64c08c72b16a51130006c415c8f73e0edec05a5d24245872d05765a77f73e946fb45d32d2ed76cbe4b8dc1300cfceb79622a04d8bc64118225e'
        news_headers['Referer'] = 'https://www.adx.ae/english/pages/productsandservices/securities/selectcompany/events.aspx?listedcompanyid=ABNIC&ISIN=AEA001701019&pnavTitle=Al%20Buhaira%20National%20Insurance%20Company'

        shareholders_headers = copy.deepcopy(company_headers)
        shareholders_headers['Cookie'] = 'ASP.NET_SessionId=lu1lc3p3val1bovpzq23uacs; node=1013017135; dtCookie=v_4_srv_4_sn_2D6B26ECC01A16A9AD9E1C701C2660CC_perc_100000_ol_0_mul_1_app-3A2dffb00433f451c6_0; BIGipServerExt_ADX_WEBSITE_PROD.app~Ext_ADX_WEBSITE_PROD_pool=!E1uWBOmbNPkupSfCi6M5qZ63MDQYiXVwdgiXdVeeZVQBM9j8hdW7IFXLtCOadbMea0hEuDTuw1yPDjc=; _ga=GA1.2.578127861.1684392651; _gid=GA1.2.1246210588.1684392651; WSS_FullScreenMode=false; TS01b242cf=019c04258c469fb030b41dba8630983e92c0515e41e3f936dc5ed0d23170108d962656af90de15a6fb7b9f6b75326391415247e32c30980767ba79223304137f520158a3e5934f4f761bb232456f086f744bdc54ce58ddda255af94b96a045660a04d45691; TS01aa7d4c=019c04258c0a03b80d9e430ae2ec7b208927b54e3988863d1048c858b60125bbb46324d32f4791d0fc242be5de8a4e920c64fc99c583dd86073d9fe1fd37913b4246c08decdf9c3f59dd16d88e675281fa2a6135af; _gat=1; TSd96eb3a0027=08c370503aab2000523ec78c500c28817f56efaea757bc188a45e6bf7d843bb7bb7469581f15dbc008917b81da1130009989dd4eab163ea04a95e8966b6a83d7a380cf85a788318aed4672c4e65d4ba71625e57bd2b0567cc55ad0cd4d4d6fc9'
        shareholders_headers['Referer'] = 'https://www.adx.ae/english/pages/productsandservices/securities/selectcompany/company-info.aspx?listedcompanyid=ABNIC&ISIN=AEA001701019&pnavTitle=Al%20Buhaira%20National%20Insurance%20Company'

        assets_payload = {'body':'Status=L&Boad=REGULAR&Del=0'}
        foreign_details_payload = {'body':'eqSymbol={}'}
        
        response = requests.post(ASSETS_API_URL, data=assets_payload['body'], headers=headers, timeout=60)
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

        json_response = json.loads(response.content)

        DATA = []
        for profile in json_response['Profiles']:
            company_id = profile['ISIN']
            eq_code = profile['EQCODE']
            print(company_id)

            company_response = requests.get(DETAILS_API_URL.format(company_id), headers=company_headers, timeout=60)
            company_data = json.loads(company_response.content)

            company_name = company_data['Name']
            contact_email = company_data['Email'] if 'Email' in company_data.keys() else ""
            contact_phone_number = company_data['PhoneNumber'] if 'PhoneNumber' in company_data.keys() else ""
            contact_website = company_data['Website'] if 'Website' in company_data.keys() else ""
            contact_details = {'phone_number':contact_phone_number, 'email':contact_email, 'website':contact_website}
            capital_details = company_data['ShareCapital'] if 'ShareCapital' in company_data.keys() else ""
            listing_date = company_data['DateOfListing'] if 'DateOfListing' in company_data.keys() else ""
            incorporation_date = company_data['DateOfIncorporation'] if 'DateOfIncorporation' in company_data.keys() else ""
            company_type = company_data['Type'] if 'Type' in company_data.keys() else ""
            auditor = company_data['Auditor'] if 'Auditor' in company_data.keys() else ""
            article_of_association = company_data['Note'] if 'Note' in company_data.keys() else ""
            company_description = company_data['Description'].replace("'","") if 'Description' in company_data.keys() else ""
            people_details = []
            board_directors = {'type':'board of directors','data':[]}
            for directors in company_data['BoardOfDirectors']:
                board_directors['data'].append({'name':directors['Name'].replace("'",""), 'designation':directors['Title']}) 
            people_details.append(board_directors)
            managers_people = {'type':'general managers','data':[]}
            for managers in company_data['Managers']:
                managers_people['data'].append({'name':managers['Name'].replace("'",""), 'designation':managers['Title']}) 
            people_details.append(managers_people)

        #   Foreign Investments Data Extraction
            foreign_investment_response = requests.post(FOREIGNDETAILS_API_URL, data=foreign_details_payload['body'].format(company_id), headers=headers, timeout=60)
            foreign_investment_data = json.loads(foreign_investment_response.content)
            foreign_investment_details = {'foreign_ownership':'', 'gcc':'',
                                            'uae_national':'', 'arab_nationals':''}
            if len(foreign_investment_data['Fol']) > 0:
                foreign_investment_details = {'foreign_ownership':foreign_investment_data['Fol'][0]['AothPer'], 'gcc':foreign_investment_data['Fol'][0]['AgccPer'],
                                            'uae_national':foreign_investment_data['Fol'][0]['AuaePer'], 'arab_nationals':foreign_investment_data['Fol'][0]['AarbPer']}
            
        #   Filling Details Data Extraction
            filling_details = []
            financial_response = requests.get(FINANCIAL_API_URL.format(company_id), headers=financial_headers, timeout=60)
            financial_data = json.loads(financial_response.content)
            for financial_ in financial_data:
                filling_details.append({'title':financial_['Title'].replace("'",""), 'category':financial_['SubCategoryName'], 'date':financial_['ArticleStartDate'],
                                        'source_url':financial_['Url']})

        #   News Details Data Extraction
            news_details = []
            news_response = requests.get(NEWS_API_URL.format(company_id), headers=news_headers, timeout=60)
            news_data = json.loads(news_response.content)
            for news_ in news_data:
                news_details.append({'title':news_['Title'].replace("'",""), 'category':news_['CategoryName'], 'date':news_['ArticleStartDate'], 'source_url':news_['Url']})
            
        #   Shareholders Data Extraction
            shareholders_details = []
            shareholders_response = requests.get(SHAREHOLDERS_API_URL.format(eq_code), headers=shareholders_headers, timeout=60)
            shareholders_data = json.loads(shareholders_response.content)
            for shareholder_ in shareholders_data:
                shareholders_details.append({'name':shareholder_['Name'].replace("'",""), 'certified':shareholder_['ShareholderType']['Name'], 'shareholder_percentage':shareholder_['Percentage']})

            additional_detail = []
            additional_detail.append({'type':'news/announcements', 'data':news_details})
            additional_detail.append({'type':'shareholder_details', 'data':shareholders_details})
            additional_detail.append({'type':'foreign_investment_details', 'data':[foreign_investment_details]})
            additional_detail.append({'type':'contact_details', 'data':[contact_details]})

            DATA.append([company_name, capital_details, listing_date, incorporation_date, company_type, auditor, article_of_association, company_description, people_details, additional_detail, filling_details])
            
            record = [company_name, capital_details, listing_date, incorporation_date, company_type, auditor, article_of_association, company_description, people_details, additional_detail, filling_details]
            
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
    Description: HTML Crawler for UAE Stock Market ADX
    '''
    countries = "UAE"
    entity_type = "Company/Organization"
    category = "Stock Market"
    name = "Abu Dhabi Securities Exchange (ADX)"
    description = "The website provides an issuers directory, which is a comprehensive listing of all the companies and entities listed on ADX and their information, as well as resources and regulations for issuers and investors, such as disclosure requirements, corporate governance guidelines, and market data and reports."
    source_type = "HTML"
    url = "https://www.adx.ae/english/pages/marketparticipants/issuers/issuers-directory.aspx" 

    number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
