"""Set System Path"""
import re
import string
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import traceback
import datetime
import shortuuid
import pandas as pd
import requests, json,os
from bs4 import BeautifulSoup
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from deep_translator import GoogleTranslator
from helpers.crawlers_helper_func import CrawlersFunctions
import time
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
    meta_detail['aliases'] = record["اسم الشركة"].replace("'","''")
    meta_detail['establishment_id_no'] = record["الرقم الوطني للمنشأه"].replace("'","''")
    meta_detail['comments'] = str(record['ملاحظات'].replace("'","''")) if 'ملاحظات' in record else ""
    meta_detail['last_updated'] = record['تاريخ آخر تعديل للشركة'].replace("'","''").replace("/","-") if 'تاريخ آخر تعديل للشركة' in record else ""
   
    po_box = record['صندوق بريد'].replace("'","''") if 'صندوق بريد' in record else ""
    city = record['المحافظة'].replace("'","''") if 'المحافظة' in record else ""
    postal_code = record['الرمز البريدي'].replace("'","''") if 'الرمز البريدي' in record else ""
    address = record['مركز الشركة'].replace("'","''").replace("-","") if 'مركز الشركة' in record else ""
    address_details = dict()
    address_details['type'] = "general_address"    
    address_details['address'] = str(address +' '+city+' '+postal_code+' '+ po_box).strip()
    
    # create data object dictionary containing all above dictionaries
    data_obj = {
        "name": record["اسم الشركة"].replace("'","''"),
        "status": record['حالة الشركة'].replace("'","''"),
        "registration_number": record['رقم الشركة'] ,
        "registration_date": record['تاريخ تسجيل الشركة'].replace("/","-"),
        "type": record["نوع الشركة"].replace("'","''"),
        "crawler_name": "crawlers.custom_crawlers.kyb.jordan.jordan_official_registry_kyb",
        "country_name": "Jordan",
        "jurisdiction": record['المحافظة'].replace("'","''") if 'المحافظة' in record else "",
        "meta_detail": meta_detail,
        'addresses_detail': [address_details],
        'people_detail': record['people_detail'],
        'additional_detail': record['additional_detail'],
        'fillings_detail': record['fillings_detail'],

        'contacts_detail':[ 
            {
                "type": 'phone_number',
                "value": record['الهاتف'].replace("'","''") if 'الهاتف' in record else "",
            } if  record['الهاتف'] != '' else None,
            {
                'type': 'email',
                "value": record['البريد الإلكتروني'].replace("'","''") if 'البريد الإلكتروني' in record else "",
            } if record['البريد الإلكتروني'] != '' else None,
            {
                'type' : 'fax_number',
                "value": record['الفاكس'].replace("'","''") if 'الفاكس' in record else "",
            } if record['الفاكس'] != '' else None,
            {
                'type': 'telephone',
                "value": record['الخلوي'].replace("'","''") if 'الخلوي' in record else "",
            } if  record['الخلوي'] != '' else None,
        ]
    }

    data_obj['contacts_detail'] = [p for p in data_obj['contacts_detail'] if p]
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
    data_for_db.append(shortuuid.uuid(record['رقم الشركة']+record["اسم الشركة"]+"jordan_kyb")) # entity_id
    data_for_db.append(record["اسم الشركة"].replace("'","''")) #name
    data_for_db.append(json.dumps([])) #dob
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
        print(url)
        response = requests.get(SOURCE_URL, verify=False ,headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        # Parse the page content using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        # Find the table element containing the data
        body_data = soup.find('div', class_='search-form')
        data = {}

        location_ID_number_element = body_data.find("td", string="الرقم الوطني للمنشأه")
        data['الرقم الوطني للمنشأه'] = location_ID_number_element.findNextSibling('td').text.strip()

        type_element = body_data.find("td", string="نوع الشركة")
        data['نوع الشركة'] = type_element.findNextSibling('td').text.strip()

        name_element = body_data.find("td", string="اسم الشركة")
        data['اسم الشركة'] = name_element.findNextSibling('td').text.strip()

        registration_element = body_data.find("td", string="رقم الشركة")
        data['رقم الشركة'] = registration_element.findNextSibling('td').text.strip()

        status_element = body_data.find("td", string="حالة الشركة")
        data['حالة الشركة'] = status_element.findNextSibling('td').text.strip()

        registration_date_element = body_data.find("td", string="تاريخ تسجيل الشركة")
        data['تاريخ تسجيل الشركة'] = registration_date_element.findNextSibling('td').text.strip()

        last_update_element = body_data.find("td", string="تاريخ آخر تعديل للشركة")
        data['تاريخ آخر تعديل للشركة'] = last_update_element.findNextSibling('td').text.strip()

        comment_element = body_data.find("td", string="ملاحظات")
        data['ملاحظات'] = comment_element.findNextSibling('td').text.strip()

        address_element = body_data.find("td", string="مركز الشركة")
        data['مركز الشركة'] = address_element.findNextSibling('td').text.strip()

        jurisdiction_element = body_data.find("td", string="المحافظة")
        data['المحافظة'] = jurisdiction_element.findNextSibling('td').text.strip()

        phone_element = body_data.find("td", string="الهاتف")
        data['الهاتف'] = phone_element.findNextSibling('td').text.strip()

        pobox_element = body_data.find("td", string="صندوق بريد")
        data['صندوق بريد'] = pobox_element.findNextSibling('td').text.strip()

        email_element = body_data.find("td", string="البريد الإلكتروني")
        data['البريد الإلكتروني'] = email_element.findNextSibling('td').text.strip()

        city_element = body_data.find("td", string="المدينة")
        data['المدينة'] = city_element.findNextSibling('td').text.strip()

        fax_element = body_data.find("td", string="الفاكس")
        data['الفاكس'] = fax_element.findNextSibling('td').text.strip()

        postcode_element = body_data.find("td", string="الرمز البريدي")
        data['الرمز البريدي'] = postcode_element.findNextSibling('td').text.strip()

        telefone_element = body_data.find("td", string="الخلوي")
        data['الخلوي'] = telefone_element.findNextSibling('td').text.strip()

        filing_details = body_data.find("td", string="اعلانات الجريدة الرسمية")
        filing_table = filing_details.find_next('table')

        filing_detail = list()
        if filing_table is not None:

            filing_rows = filing_table.find_all('tr')

            for row in filing_rows[1:]:
                columns = row.find_all('td')
                if len(columns) > 1:
                    file_obj = dict()
                    file_obj['title']  = str(columns[1].text.strip().replace("'","''"))
                    file_obj['date']  =columns[2].text.strip().replace("/","-")
                    file_obj['meta_detail'] = {
                       'issue_number': columns[0].text.strip(),
                    }
                    filing_detail.append(file_obj)

        data['fillings_detail'] = filing_detail

        additional_detail = list()

        pattern = re.compile("معلومات عن الشركة في مركزها الأم")
        parent_company_details = body_data.find("td", string=pattern)

        if parent_company_details is not None:

            parent_company_obj = dict()
            headquarter_element = body_data.find("td", string="رقم الشركة في مركزها الام")
            parent_company_obj['company_headquarters'] = headquarter_element.findNextSibling('td').text.strip().replace("'","''").replace("-------------","").replace("----------","").replace("---------","").replace("--","").replace("-","")

            representative_element = body_data.find("td", string="اسم مدير الشركة - الممثل")
            parent_company_obj['representative'] = representative_element.findNextSibling('td').text.strip().replace("'","''")

            parent_headquarter_element = body_data.find("td", string="مركز الشركة الأم")
            parent_company_obj['parent_company_headquarter'] = parent_headquarter_element.findNextSibling('td').text.strip().replace("'","''")

            parent_capital_element = body_data.find("td", string="رأس المال بالشركةالأم")
            parent_company_obj['parent_company_capital'] = parent_capital_element.findNextSibling('td').text.strip().replace("'","''")
            
            parent_registration_element = body_data.find_all("td", string="تاريخ تسجيل الشركة") if len(body_data.find_all("td", string="تاريخ تسجيل الشركة")) > 1 else None
            parent_company_obj['company_registration'] = parent_registration_element[1].findNextSibling('td').text.strip().replace("'","''").replace("/","-") if parent_registration_element is not None else '' 

            objective_element = body_data.find("td", string="غايات الشركة بالمركز الأم")
            parent_company_obj['company_objective'] = objective_element.findNextSibling('td').text.strip().replace("'","''") 

            contracting_party_element = body_data.find("td", string="الجهة المتعاقد معها")
            parent_company_obj['contracting_party'] = contracting_party_element.findNextSibling('td').text.strip().replace("'","''") 

            first_phone_element = body_data.find("td", string="هاتف اول")
            parent_company_obj['first_phone'] = first_phone_element.findNextSibling('td').text.strip().replace("'","''")

            second_phone_element = body_data.find("td", string="هاتف ثاني")
            parent_company_obj['second_phone'] = second_phone_element.findNextSibling('td').text.strip().replace("'","''")


            parent_fax_element = body_data.find_all("td", string="الفاكس") if len(body_data.find_all("td", string="الفاكس")) > 1 else None
            parent_company_obj['fax'] = parent_fax_element[1].findNextSibling('td').text.strip().replace("'","''") if parent_fax_element is not None else '' 

            parent_email_element = body_data.find_all("td", string="البريد الإلكتروني") if len(body_data.find_all("td", string="البريد الإلكتروني")) > 1 else None
            parent_company_obj['email'] = parent_email_element[1].findNextSibling('td').text.strip().replace("'","''") if parent_email_element is not None else '' 

            parent_postal_code_element = body_data.find_all("td", string="الرمز البريدي") if len(body_data.find_all("td", string="الرمز البريدي")) > 1 else None
            parent_company_obj['postal_code'] = parent_postal_code_element[1].findNextSibling('td').text.strip().replace("'","''") if parent_postal_code_element is not None else '' 

            parent_company_full = dict()
            parent_company_full['type'] = 'parent_company_information'
            parent_company_full['data'] = [parent_company_obj]

            additional_detail.append(parent_company_full)
          

        pattern = re.compile("معلومات رأس المال")
        capital_information = body_data.find("td", string=pattern)

        if capital_information is not None:

            capital_obj = dict()

            registered_capital_element = body_data.find("td", string="رأس المال عند التسجيل")
            capital_obj['registered_capital'] = registered_capital_element.findNextSibling('td').text.strip().replace("'","''")

            current_capital_element = body_data.find("td", string="رأس المال الحالي")
            capital_obj['current_capital'] = current_capital_element.findNextSibling('td').text.strip().replace("'","''")

            paidup_capital_element = body_data.find("span", string="رأس المال المدفوع")
            capital_obj['paid_up_capital'] = paidup_capital_element.find_next('td').text.strip().replace("'","''")  if paidup_capital_element is not None else ''

            cash_sahre_element = body_data.find("td", string="الحصة النقدية")
            capital_obj['cash_share'] = cash_sahre_element.findNextSibling('td').text.strip().replace("'","''")

            in_kind_share_element = body_data.find("td", string="الحصة العينية")
            capital_obj['in_kind_share'] = in_kind_share_element.findNextSibling('td').text.strip().replace("'","''")

            capita_information = dict()
            capita_information['type'] = 'capital_information'
            capita_information['data'] = [capital_obj]


            additional_detail.append(capita_information)
        
        activity_information = body_data.find("td", string="غــايــات الـشـركـة")

        if activity_information is not None:

            activity_table = activity_information.find_next('table')

            if activity_table is not None:

                activity_rows = activity_table.find_all('tr')

                activity_data_obj = list()

                for row in activity_rows[1:]:
                    columns = row.find_all('td')
                    
                    if len(columns) >= 1:
                        activity_obj = dict()
                        activity_obj['activity_code']  =columns[0].text.strip()
                        activity_obj['activity']  = str(columns[1].text.strip().replace("'","''"))
                        activity_data_obj.append(activity_obj)

                if len(activity_data_obj) > 0:
                        activity_final_obj = dict()
                        activity_final_obj['type'] = 'activity_information'
                        activity_final_obj['data'] =  activity_data_obj

                        additional_detail.append(activity_final_obj)

        
        authorizations = body_data.find('td', string='الـمفـوضـون بالـتوقيع')

        if authorizations is not None:

            authorrization_table = authorizations.find_next('table')

            if authorrization_table is not None:

                autorize_rows = authorrization_table.find_all('tr')

                authorize_data_obj = list()

                for row in autorize_rows[1:]:
                    authorize_columns = row.find_all('td')

        
                    if len(authorize_columns) >=2:
                        authorize_obj = dict()
                        authorize_obj['authorization_date']  =authorize_columns[0].text.strip()
                        authorize_obj['authorization']  = str(authorize_columns[1].text.strip().replace("'","''"))
                        authorize_data_obj.append(authorize_obj)

                if len(authorize_data_obj) > 0:
                        authorization_final_obj = dict()
                        authorization_final_obj['type'] = 'authorization_information'
                        authorization_final_obj['data'] =  authorize_data_obj

                        additional_detail.append(authorization_final_obj)

        
        
        data['additional_detail'] = additional_detail   

        people_details = body_data.find("td", string="الـــشـركـــاء")
        people_detail_list = list()
        if people_details is not None:

            people_table = people_details.find_next('table')

            if people_table is not None:

                people_rows = people_table.find_all('tr')

                for row in people_rows[1:]:
                    columns = row.find_all('td')
                    
                    if len(columns) > 3:
                        people_obj = dict()
                        people_obj['name'] = str(columns[1].text.strip().replace("'","''"))
                        people_obj['designation']  = str(columns[2].text.strip().replace("'","''"))+"/"+"Partner"
                        people_obj['nationality']  =str(columns[4].text.strip().replace("'","''"))
                        people_obj['meta_detail']= {
                            'national_id' : columns[0].text.strip() if columns[0].text.strip() != '0' else '',
                            'ownership_stake': columns[3].text.strip().replace("'","''"),
             
                        }
                        people_detail_list.append(people_obj)


        data['people_detail'] = people_detail_list

        record_for_db = prepare_data(data, category,country, entity_type, source_type, name, url, description)
        query = """INSERT INTO translate_reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
                            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}',data='{7}',updated_at='{10}'""".format(*record_for_db)
              
        print("stored in database\n")
        crawlers_functions.db_connection(query)

        return len(data), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e,tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'","''")

if __name__ == '__main__':
    '''
    Description: HTML Crawler for Jordan
    '''
    name = 'Companies Control Department'
    description = "The Companies Control Department is a financially and administratively independent national institution. It reports to the Minister of Industry and Trade "
    entity_type = 'Company/Organisation'
    source_type = 'HTML'
    countries = 'Jordan'
    category = 'Official Registry'
    arguments = sys.argv
    COMPNY_ID = int(arguments[1]) if len(arguments)>1 else 1
    # df = pd.read_csv(".//insolvency/input/jordan_urls.csv")
    for i in range(COMPNY_ID,94859):
        url = f'https://portal.ccd.gov.jo/search/bycompanynameframe21.aspx?CompanyID={i}'
        # url = urls[1][0]
        number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                    category, url,name, description)
    logger = Logger({"number_of_records": number_of_records, "status": status,
                    "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path":file_path,"trace_back":trace_back,  "crawler":"HTML"})
    logger.log()
