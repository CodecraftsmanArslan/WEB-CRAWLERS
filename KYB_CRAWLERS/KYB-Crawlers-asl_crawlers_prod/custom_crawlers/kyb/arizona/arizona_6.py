"""Import required library"""
import sys, traceback, time, re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import warnings
from CustomCrawler import CustomCrawler
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
warnings.filterwarnings('ignore')
from proxies_lst import get_a_random_proxy

meta_data = {
    'SOURCE' :'Arizona Corporation Commission (ACC)',
    'COUNTRY' : 'Arizona',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://corp.sec.state.ma.us/corpweb/corpsearch/CorpSearch.aspx", 
                        "Source Description": "The Arizona Corporation Commission (ACC) is a regulatory agency responsible for overseeing and regulating various businesses and industries within the state of Arizona, USA. The commission is composed of five elected commissioners who serve as the central authority for matters related to corporations, utilities, securities, and railroad safety."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://corp.sec.state.ma.us/corpweb/corpsearch/CorpSearch.aspx'
}
crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Arizona_6 Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

arizona_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = arizona_crawler.get_requests_helper()

s =  arizona_crawler.get_requests_session()

start_llp = 90569601
end_llp = 99999999

arguments = sys.argv
ENTITY_NUM = int(arguments[1]) if len(arguments)>1 else start_llp

all_range_num = [f"{str(i).zfill(7)}" for i in range(ENTITY_NUM, end_llp + 1)]
try:
    for number in all_range_num:
        print('entityNumber =', number)
        URL = f'https://ecorp.azcc.gov/BusinessSearch/BusinessInfo?entityNumber={number}'
        hearders = {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        proxy = get_a_random_proxy()
        while True:
            response = request_helper.make_request(URL,headers=hearders,proxy=proxy)
            if not response:
                proxy = get_a_random_proxy()
            else:
                break

        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        content = response.content
        
        content_string = content.decode('utf-8')
        
        if "eCorp is a web-based application used to create and manage the life cycle of your business registration" in content_string:
            print("Skipping URL:", URL)
            continue

        soup = BeautifulSoup(content,'html.parser')

        BusinessName = soup.find('label',{'for':'Business_BusinessName'}).find_next('div').get_text(strip=True)
        BusinessNumber = soup.find('label',{'for':'Business_BusinessNumber'}).find_next('div').get_text(strip=True)
        EntityType = soup.find('label', {'for': 'Business_EntityType'}).find_next('div').get_text(strip=True)
        Business_Status = soup.find('label', {'for': 'Business_Status'}).find_next('div').get_text(strip=True)
        FormationDate = soup.find('label', {'for': 'Business_FormationDate'}).find_next('div').get_text(strip=True).replace("/","-")
        try:
            StatusReasons = soup.find('a', class_='statusTooltip').get_text(strip=True)
        except:
            StatusReasons = ""
        ApprovalDate = soup.find('label', {'for': 'Business_ApprovalDate'}).find_next('div').get_text(strip=True).replace("/","-")
        InActiveDate = soup.find('label', {'for': 'Business_InActiveDate'}).find_next('div').get_text(strip=True).replace("/","-")
        DateOfIncorporation = soup.find('label', {'for': 'Business_DateOfIncorporation'}).find_next('div').get_text(strip=True).replace("/","-")
        BusinessType = soup.find('label', {'for': 'Business_BusinessType'}).find_next('div').get_text(strip=True)
        LastARFiledDate = soup.find('label', {'for': 'Business_LastARFiledDate'}).find_next('div').get_text(strip=True)
        PlaceofFormationName = soup.find('label', {'for': 'Business_PlaceofFormationName'}).find_next('div').get_text(strip=True)
        ARDurationInYears = soup.find('label', {'for': 'Business_ARDurationInYears'}).find_next('div').get_text(strip=True)
        YearsDue = soup.find('label', {'for': 'Business_YearsDue'}).find_next('div').get_text(strip=True)
        OriginalPublishDates = soup.find('label', {'for': 'Business_OriginalPublishDates'}).find_next('div').get_text(strip=True)
        AgentName = soup.find('label', {'for': 'Agent_AgentName'}).find_next('div').get_text(strip=True)
        AgentStatus = soup.find('label', {'for': 'Agent_AgentStatus'}).find_next('div').get_text(strip=True).replace("/","-")
        PrincipalAddress_Attention = soup.find('label', {'for': 'Agent_PrincipalAddress_Attention'}).find_next('div').get_text(strip=True)
        Agent_PrincipalAddress = soup.find('label', {'for': 'Agent_PrincipalAddress'}).find_next('div').get_text(strip=True)
        AgentStatusEffect = soup.find('label', {'for': 'Agent_AgentStatusEffect'}).find_next('div').get_text(strip=True).replace("/","-")
        Agent_EmailAddress = soup.find('label', {'for': 'Agent_EmailAddress'}).find_next('div').get_text(strip=True)
        Agent_MailingAddress_Attention = soup.find('label', {'for': 'Agent_MailingAddress_Attention'}).find_next('div').get_text(strip=True)
        Agent_MailingAddress_FullAddress = soup.find('label', {'for': 'Agent_MailingAddress_FullAddress'}).find_next('div').get_text(strip=True)
        Agent_MailingAddress_County = soup.find('label', {'for': 'Agent_MailingAddress_County'}).find_next('div').get_text(strip=True)
        KnownPlaceofBusiness_address = soup.find('label',{'for': 'Business_KnownPlaceofBusiness'}).find_next_sibling(string=True).strip()
        KnownPlaceofBusiness_County = soup.find('label', {'for': 'Business_KnownPlaceofBusiness_County'}).find_next_sibling(string=True).strip()
        KnownPlaceofBusiness_ModifiedDate = soup.find('label', {'for': 'Business_KnownPlaceofBusiness_ModifiedDate'}).find_next_sibling(string=True).strip().replace("/","-")
        PrincipalOfficeAddress_FullAddress1 = soup.find('label', {'for': 'Business_PrincipalOfficeAddress_FullAddress1'}).find_next_sibling(string=True).strip()
        PrincipalOfficeAddress_County = soup.find('label', {'for': 'Business_PrincipalOfficeAddress_County'}).find_next_sibling(string=True).strip()
        PrincipalOfficeAddress_ModifiedDate = soup.find('label', {'for': 'Business_PrincipalOfficeAddress_ModifiedDate'}).find_next_sibling(string=True).strip().replace("/","-")

        # get all people details
        people_detail = []
        table = soup.find('table', id='grid_principalList')
        for row in table.find_all('tr', class_=['bgwhite', 'bgrowalt']):
            columns = row.find_all('td')
            title = columns[0].get_text(strip=True)
            name = columns[1].get_text(strip=True)
            address = columns[3].get_text(strip=True)
            date = columns[4].get_text(strip=True).replace("/","-")
            last_updated = columns[5].get_text(strip=True).replace("/","-")
            pdetail={
                "designation":title,
                "name":name.replace("%","%%"),
                "address":address.replace("%","%%"),
                "appointment_date":date,
                "meta_detail":{
                    "last_updated":last_updated
                }  
            }
            people_detail.append(pdetail)

        pdetail2={
                "designation":"registered_agent",
                "name":AgentName.replace("%","%%"),
                "address":PrincipalAddress_Attention.replace("%","%%"),
                "email":Agent_EmailAddress,
                "postal_address":Agent_MailingAddress_FullAddress.replace("%","%%"),
                "meta_detail":{
                    "status":AgentStatus,
                    "last_updated":AgentStatusEffect
                }
            }

        people_detail.append(pdetail2)
        
        buttons = soup.find_all('input', {'id': 'btnClear'})

        for button in buttons[:1]:
            onclick_value = button['onclick']
            businessId = onclick_value.split("(")[-1].replace(")","").strip()
            # get Filling data
            fillings_url = 'https://ecorp.azcc.gov/BusinessSearch/BusinessFilings'
            payload = {
                    "businessId":businessId,
                    "source":"online"
                    }
            while True:
                filling_response = request_helper.make_request(fillings_url,method = 'POST',headers= hearders,data= payload, proxy=proxy)
                print('filling_response = ',filling_response.status_code)
                if not filling_response:
                    proxy = get_a_random_proxy()
                else:
                    break
                
            filling_content = filling_response.content
            soup2 = BeautifulSoup(filling_content, 'html.parser')
            try:
                table2 = soup2.find('table', class_='gridstyle')
                fillings_detail = []
                for row_ in table2.find_all('tr', class_='bgwhite'):
                    columns_ = row_.find_all('td')
                    document_type = columns_[0].find('span').get_text(strip=True)
                    file_url = 'https://ecorp.azcc.gov'+columns_[0].find('a').get('href')
                    barcode_id = columns_[1].get_text(strip=True)
                    date = columns_[2].get_text(strip=True).replace("/","-")
                    status = columns_[3].get_text(strip=True)
                    
                    fillings_dict = {
                        "filing_type":document_type,
                        "filing_code":barcode_id,
                        "date":date,
                        "meta_detail":{
                            "status":status
                        },
                        "file_url":file_url
                    }
                    fillings_detail.append(fillings_dict)
            except AttributeError:
                fillings_detail = []

        # data object
        OBJ = {
                "name":BusinessName.replace("%","%%"),
                "registration_number":BusinessNumber,
                "type":EntityType,
                "status":Business_Status,
                "formation_date":FormationDate,
                "reason_for_status":StatusReasons,
                "registration_date":ApprovalDate,
                "status_date":InActiveDate,
                "incorporation_date":DateOfIncorporation,
                "industries":BusinessType.replace("%","%%"),
                "last_annual_report_filed":LastARFiledDate,
                "jurisdiction":PlaceofFormationName,
                "annual_report_due_date":ARDurationInYears,
                "years_due":YearsDue,
                "publish_date":OriginalPublishDates,
                "addresses_detail":[
                    {
                        "type":"general_address",
                        "address":KnownPlaceofBusiness_address.replace("%","%%"),
                        "meta_detail":{
                            "county":KnownPlaceofBusiness_County,
                            "last_updated":KnownPlaceofBusiness_ModifiedDate
                        }
                    },
                    {
                        "type":"office_address",
                        "address":PrincipalOfficeAddress_FullAddress1.replace("%","%%"),
                        "meta_detail":{
                            "county":PrincipalOfficeAddress_County,
                            "last_updated":PrincipalOfficeAddress_ModifiedDate
                        }
                    }
                ],
                "people_detail":people_detail,
                "fillings_detail":fillings_detail
        }
    
        OBJ =  arizona_crawler.prepare_data_object(OBJ)
        ENTITY_ID = arizona_crawler.generate_entity_id(OBJ['registration_number'], company_name=OBJ['name'])
        NAME = OBJ['name']
        BIRTH_INCORPORATION_DATE = OBJ['incorporation_date']
        ROW = arizona_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE,OBJ)
        arizona_crawler.insert_record(ROW)

    arizona_crawler.end_crawler()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    arizona_crawler.db_log(log_data)

except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    arizona_crawler.db_log(log_data)  