"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from proxies_lst import get_a_random_proxy

meta_data = {
    'SOURCE' :'Registry Agency Bulgaria',
    'COUNTRY' : 'Bulgaria',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://portal.registryagency.bg/CR/en/Reports/ActiveCondition", 
                        "Source Description": "The Registry Agency of the Republic of Bulgaria operates under the Ministry of Justice to maintain important national databases and public records, including the Commercial Register, Property Register, and Civil Number Register. The agency provides registry information to government institutions and issues documents to the public based on this data."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://portal.registryagency.bg/CR/en/Reports/ActiveCondition'
}

crawler_config = {
    'TRANSLATION_REQUIRED': True,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Bulgaria Source Two"
}

bulgaria_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = bulgaria_crawler.get_requests_helper()
s =  bulgaria_crawler.get_requests_session()

response = request_helper.make_request("https://portal.registryagency.bg/CR/en/Reports/ActiveCondition")
SATAUS_CODE = response.status_code
DATA_SIZE = len(response.content)
CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
cookie = response.cookies.get_dict()

HEADERS =  {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Cookie": f"currentLang=en; EPZEUSessionID={cookie['EPZEUSessionID']}; cookiePrivacyAccept=1; usr_active_timestamp=1693472604164",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}


"""Global Variables"""
SATAUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'


def extract_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()

def crawl():
    
    arguments = sys.argv
    start_number = int(arguments[1]) if len(arguments)>1 else 0
    end_number = 840000000
    for number in range(start_number,end_number):
        num = str(number).zfill(9)
        proxy = get_a_random_proxy()
        API_URL = f'https://portal.registryagency.bg/CR/api/Deeds/{num}?loadFieldsFromAllLegalForms=false'
        while True:
            response_api = request_helper.make_request(API_URL, proxy=proxy, max_retries=4)
            if not response_api:
                proxy = get_a_random_proxy()
                continue
            if response_api.status_code == 200:
                response_api = response_api
                break
            else:
                time.sleep(5)
        if len(response_api.content) == 0:
            print("skip number = ", num)
            continue
        data = response_api.json()
        try:
            NAME = data['fullName'].split('<span')[0]
        except:
            NAME = data['fullName']
        registration_number = data['uic']
        # 1st_fields
        fields = data['sections'][0]['subDeeds'][0]['groups'][0]['fields']
        arr = []
        # Function to extract data from htmlData using BeautifulSoup
        extracted_data_dict = {}
        code_html_dict = {}
        # Extract and print data from each object
        for item in fields:
            name_code = item['nameCode']
            html_data = item['htmlData']
            extracted_data = extract_data(html_data)
            code_html_dict[name_code] = html_data
            extracted_data_dict[name_code] = extracted_data
        try:
            capital_fields = data['sections'][0]['subDeeds'][0]['groups'][1]['fields']
            for capital_field in capital_fields:
                name_code_ = capital_field['nameCode']
                html_data_ = capital_field['htmlData']
                extracted_data_ = extract_data(html_data_)
                code_html_dict[name_code_] = html_data_
                extracted_data_dict[name_code_] = extracted_data_
        except IndexError:
            print('index not found')

        type_ = extracted_data_dict.get('CR_F_3_L',"")
        desription = extracted_data_dict.get('CR_F_6_L','')
        try:
            incorporation_date = data['sections'][0]['subDeeds'][0]['groups'][0]['fields'][0]['fieldEntryDate'].split("T")[0]
        except:
            incorporation_date = ""
        try:
            dissolution_date = data['sections'][0]['subDeeds'][0]['groups'][0]['fields'][10]['fieldEntryDate'].split("T")[0]
        except:    
            dissolution_date = ""
        try:
            industries = extracted_data_dict['CR_F_6a_L'].split(":")[-1].strip()
        except:
            industries = ""
        try:    
            industry_code = extracted_data_dict['CR_F_6a_L'].split(":")[1].split("class")[0].strip()
        except:
            industry_code = ""

        transfer_of_a_share =  extracted_data_dict.get('CR_F_24_L','')

        country_pattern = r"Country: (.+?)Region:"
        region_pattern = r"Region: (.+?), Municipality:"
        municipality_pattern = r"Municipality: (.+?)City/Village:"
        city_pattern = r"City/Village: (.+?)Phone:"
        city_pattern2 = r"City/Village: (.+?)p.c."
        phone_pattern = r"Phone: (.+?)Email address:"
        email_pattern = r"Email address: (.+)"
        website_pattern = r"Web page: (.+)"

        address = extracted_data_dict['CR_F_5_L']
        try:
            country = re.search(country_pattern, address).group(1)
            region = re.search(region_pattern, address).group(1)
            municipality = re.search(municipality_pattern, address).group(1)
        except:
            country, region, municipality = "","",""
        try:
            city = re.search(city_pattern, address).group(1)
        except:
            try:
                city = re.search(city_pattern2, address).group(1)
            except:
                city = ""
        try:
            phone = re.search(phone_pattern, address).group(1)
        except: 
            phone = "" 
        try:
            email = re.search(email_pattern, address).group(1)
        except:
            email = ""
        try:
            website=re.search(website_pattern,address).group(1)
        except:
            website = ""  
        address_ = extracted_data_dict.get('CR_F_5a_L','')
        try:
            country_ = re.search(country_pattern, address_).group(1)
            region_ = re.search(region_pattern, address_).group(1)
            municipality_ = re.search(municipality_pattern, address_).group(1)
        except:
            country_, region_, municipality_ = "","",""
        try:
            city_ = re.search(city_pattern, address_).group(1)
        except:
            try:
                city_ = re.search(city_pattern2, address_).group(1)
            except:
                city_ = ""
        
        try:
            person_name = extracted_data_dict['CR_F_23_L'].split(":")[0].replace(', Country','')
            person_country = extracted_data_dict['CR_F_23_L'].split(":")[-1]
        except:
            person_name, person_country = "",""
        try:
            Manner_of_representation = extracted_data_dict.get('CR_F_11_L','').split(':')[-1]
        except:
            Manner_of_representation  = ""
        
        aliases = extracted_data_dict.get('CR_F_4_L','')
        

        # second_fields
        second_fields = data['sections'][1]['subDeeds'][0]['groups'][0]['fields']
        filling_details = []
        base_url = 'https://portal.registryagency.bg/CR/'
        try:
            for item_ in second_fields:
                html_data = item_['htmlData']
                soup2 = BeautifulSoup(html_data,'html.parser')
                records = soup2.find_all('div', class_='record-container--preview')
                for record in records:
                    title_elem = record.find('p', class_='field-text')
                    title_text = title_elem.get_text(strip=True)
                    title_match = re.match(r'^(.*?)Date of announcement: (.*?)$', title_text)
                    if title_match:
                        title = title_match.group(1).strip()
                        date_announcement = title_match.group(2).strip()
                    else:
                        title = title_text
                        date_announcement = ""
                    year_match = re.search(r'Year: (\d+)y', title)
                    if year_match:
                        year = year_match.group(1)
                    else:
                        year = ""
                        
                    href = record.find('a', href=True)['href']
                    file_url = base_url+href

                    filling_details.append({
                        'title': title,
                        'file_url': file_url,
                        'date': date_announcement,
                        "meta_detail":{
                            'year': year
                        }
                    })
        except:
            filling_details = []
        # third_fields
        announcement_detail = []
        try:
            third_fields = data['sections'][2]['subDeeds'][0]['groups'][0]['fields']
            for third_item in third_fields:
                third_itemhtml_data = third_item['htmlData']
                soup3 = BeautifulSoup(third_itemhtml_data,'html.parser')
                third_records = soup3.find_all('div', class_='record-container--preview')
                for elem in third_records:
                    title_elem_ = elem.find('p', class_='field-text')
                    announcement_title = title_elem_.contents[0].strip()
                    announcement_file_url = base_url+elem.find('a', href=True)['href']
                    date_elem = title_elem_.find(string=lambda string: 'Date of announcement' in string)
                    announcement_date = date_elem.split(': ')[1].strip()
                    announcement_detail.append({
                        'title': announcement_title,
                        'date': announcement_date,
                        "meta_detail":{
                            'file_url': announcement_file_url
                        }
                    })
        except:
            announcement_detail = []
        
        additional_detail = []
        # fourth_fields
        incomingNumberWithCtx = data['uicWithCtx']
        SECOND_API = f'https://portal.registryagency.bg/CR/api/Deeds/{incomingNumberWithCtx}/Applications?page=1&pageSize=25&count=0'
        while True:
            api_response = request_helper.make_request(SECOND_API,proxy=proxy, max_retries=4)
            if not api_response:
                proxy = get_a_random_proxy()
                continue
            if api_response.status_code == 200:
                api_datas = api_response.json()
                break
            else:
                time.sleep(7)
        case_information = []
        for api_data in api_datas:
            Documents_submitted = api_data.get('applicationTypeName','')
            entry_number = api_data.get('incomingNumber',"")
            submitted_via = api_data.get('officeName',"")
            result = api_data.get('resultHTML','')
            result_test = extract_data(result)
            case_info = {
                        "documents_submitted":Documents_submitted,
                        "entry_number":entry_number,
                        "submitted_via":submitted_via,
                        "result":result_test.split(' ')[0]
                    }
            case_information.append(case_info)
        
        additional_detail.append({
            "type":"case_information",
            "data":case_information
        })
        
        if extracted_data_dict.get('CR_F_7_L','') != "":
            additional_detail.append({
                "type":'beneficial_owner',
                "data":[
                    {
                        "name":extracted_data_dict.get('CR_F_7_L','').split(' Country:')[0].replace(",",'').strip(),
                        "nationality":extracted_data_dict.get('CR_F_7_L','').split(' Country:')[-1].strip()
                    }
                ]
            })
        
        if extracted_data_dict.get('CR_F_31_L','') != "":
            additional_detail.append({
                "type":"capital_information",
                "data":[
                    {
                    "capital":extracted_data_dict.get('CR_F_31_L',''),
                    "pain_in_capital":extracted_data_dict.get('CR_F_32_L',''),
                    "Non_cash_contribution":extracted_data_dict.get('CR_F_33_L','')
                    }
                ]
            })
        
        try:
            CompanyCases_API = f'https://portal.registryagency.bg/CR/api/Companies/CompanyCases/{registration_number}'
            for i in range(1,6):
                CompanyCases_response = request_helper.make_request(CompanyCases_API, proxy=True, max_retries=4)
                if not CompanyCases_response:
                    continue
                if CompanyCases_response.status_code == 200:
                    CompanyCases = CompanyCases_response.json()
                    break
                else:
                    time.sleep(7)
            cases_dist = []
            for cases in CompanyCases['items'][0]['children'][0]['children']:
                for case in cases['children']:
                    soup7 = BeautifulSoup(case['text'],'html.parser')
                    case_url = soup7.find('a')['href']
                    soup7_text = soup7.get_text(separator = ",")
                    case_title=  soup7_text.split(",")[1]
                    cases_dist.append({
                        "title":case_title,
                        "file_url":base_url+case_url
                    })
            copmany_case_dict = {
                "type":"company_case_information",
                "data": cases_dist
            }
            additional_detail.append(copmany_case_dict)
        except:
            copmany_case_dict = {}
            if copmany_case_dict != {}:
                additional_detail.append(copmany_case_dict)

        INTRUCTION_API = f'https://portal.registryagency.bg/CR/api/Instructions?page=1&pageSize=25&count=0&uic={registration_number}&incomingNumber=&isActiveWithoutDeed=false&loadIncomingLinkedDeeds=false&mode=1&applicationDateFrom=&applicationDateTo='
        for i in range(1,6):
            intruction_response = request_helper.make_request(INTRUCTION_API, proxy=True, max_retries=4)
            print('intruction_response',intruction_response)
            if not intruction_response:
                continue
            if intruction_response.status_code == 200:
                intruction_data = intruction_response.json()
                break
            else:
                time.sleep(7)
        in_lst = []
        try:
            for in_data in intruction_data:
                soup8 = BeautifulSoup(in_data.get('link',''),'html.parser')
                instruction_url = soup8.find('a')['href']
                instruction_url_ = 'https://portal.registryagency.bg'+instruction_url
                in_dict = {
                    "application_form_number":in_data.get('incomingNumber',''),
                    "instruction_issue":in_data.get('fromDate','').split("T")[0],
                    "instruction_removed":in_data.get('endDate','').split("T")[0],
                    "instruction_url":instruction_url_,
                }
                in_lst.append(in_dict)
            
            additional_detail.append({
                "type":"instructions_details",
                "data":in_lst
            })
        except:
            pass
        
        # all people details 
        people_detail = []
        procuter_api = f'https://portal.registryagency.bg/CR/api/Deeds/{registration_number}/SubDeeds/2/0011/Fields/00410/History' 
        for i in range(1,6):
            procuter_response = request_helper.make_request(procuter_api, proxy=True, max_retries=4)
            if not procuter_response:
                continue
            if procuter_response.status_code == 200:
                procuter_data = procuter_response.json()
                break
            else:
                time.sleep(7)
        
        try:
            designation = 'procurators'
            for procuter in procuter_data:
                soup9 = BeautifulSoup(procuter.get('htmlData',''),'html.parser')
                names = soup9.find('p', class_='field-text').get_text(strip=True)
                try:
                    status = soup9.find('div', class_='erasure-text-inline').get_text(strip=True)
                except:
                    status = ""
                aws = {
                    "designation":designation,
                    "name":names,
                    "meta_detail":{
                        "status":status,
                        "date":procuter.get('fieldEntryDate','').split('T')[0]
                        }  
                }
                people_detail.append(aws)
        except:
            aws = {}
            people_detail.append(aws)
        
        
        # manager detail
        try:
            soup5 = BeautifulSoup(code_html_dict['CR_F_7_L'], 'html.parser')
            for div_ in soup5.find_all('div', class_='record-container--preview'):
                text_ = div_.find('p', class_='field-text').get_text()
                matchs = re.search(r'^(.*?),\sCountry:\s(.*?)$', text_)
                if matchs:
                    name_ = matchs.group(1)
                    nationality_ = matchs.group(2)
                else:
                    name_ ,nationality_= "", ""
                
                if person_name !="":
                    maneger_dict = {
                                "designation":"manager",
                                "name":person_name,
                                "nationality":person_country
                                }
                    people_detail.append(maneger_dict)
                else:
                    if name_ !="":
                        maneger_dict = {
                                    "designation":"manager",
                                    "name":name_,
                                    "nationality":nationality_
                                    }
                        people_detail.append(maneger_dict)
        except KeyError:
            maneger_dict = {}
            people_detail.append(maneger_dict)
        
        # partner detail
        try:
            soup4 = BeautifulSoup(code_html_dict['CR_F_19_L'],'html.parser')
            for div in soup4.find_all('div', class_='record-container--preview'):
                text = div.find('p', class_='field-text').get_text()
                _match = re.search(r'^(.*?),\sCountry:\s(.*?),\sPortion\sof\sshareholding:\s(\d+\sBGN)', text)
                if _match:
                    name = _match.group(1)
                    nationality = _match.group(2)
                    shareholding = _match.group(3)
                else:
                    name, nationality, shareholding = "", "", ""
                
                if name !="":
                    partner_dict = {
                        "designation": "partner",
                        "name": name.strip(),
                        "nationality": nationality.strip(),
                        "meta_detail":{
                            "portion_of_shareholding":shareholding
                        }
                    }
                    people_detail.append(partner_dict) 
        except:
            partner_dict = {}
            people_detail.append(partner_dict)
        pattern_ = r'^(.*?)\s*,\s*Country:\s*(.*?)$'
        try:
            match_ = re.search(pattern_, extracted_data_dict['CR_F_18_L'])
            if match_:
                trader_name = match_.group(1)
                trader_nationality = match_.group(2)
            else:
                trader_name, trader_nationality = "", ""
            if trader_name !="":
                trader = {
                    "designation":"trader",
                    "name":trader_name,
                    "nationality":trader_nationality
                }
                people_detail.append(trader)
        except:
            trader= {}
            people_detail.append(trader)
        
        try:
            match2 = re.search(pattern_, extracted_data_dict['CR_F_9_L'])
            if match2:
                chairman_name = match2.group(1)
                chairman_nationality = match2.group(2)
            else:
                chairman_name, chairman_nationality = "", ""
            if chairman_name !="":
                chairman = {
                    "designation":"chairman",
                    "name":chairman_name,
                    "nationality":chairman_nationality
                }
                
                people_detail.append(chairman)
        except:
            chairman= {}
            people_detail.append(chairman)
        try:
            soup6 = BeautifulSoup(code_html_dict['CR_F_12d_L'],'html.parser')
            manner_match = re.search(r'manner of determination of the mandate:\s(.*?)<br/>Name of the management body:\s(.*?)<br/>', code_html_dict['CR_F_12d_L'])
            manner_of_determination = manner_match.group(1) if manner_match else ""
            management_body = manner_match.group(2) if manner_match else ""

            for div in soup6.find_all('div', class_='record-container--preview'):
                text = div.find('p', class_='field-text').get_text()
                match__ = re.search(r'^(.*?),\sCountry:\s(.*?)$', text)
                if match__:
                    detail_name = match__.group(1)
                    detail_nationality = match__.group(2)
                else:
                    detail_name, detail_nationality= "", ""
                
                if detail_name !="":
                    detail = {
                        "designation": management_body.strip(),
                        "name": detail_name.strip(),
                        "nationality": detail_nationality.strip(),
                        "meta_detail":{
                            "mandate": manner_of_determination.strip()
                        }
                    }
                    people_detail.append(detail)
        except:
            detail = {}
            people_detail.append(detail)
        
        try:
            soup7 = BeautifulSoup(code_html_dict.get('CR_F_13_L',''), 'html.parser')
            
            for _div in soup7.find_all('div', class_='record-container'):
            
                _text = _div.find('p', class_='field-text').get_text(strip=True)
                if 'Date of expiration of the mandate:' in _text:
                    date_of_mandate = _text.replace('Date of expiration of the mandate:', '').strip()
                else:
                    _name, _country = _text.split(', Country:')
                    if _name !="":
                        management_dict = {
                            "designation": "management_board",
                            "name": _name.strip(),
                            "nationality": _country.strip(),
                            "meta_detail":{
                            "termination_date":date_of_mandate.replace(" y.","").replace(".","-")
                            }
                        }

                    people_detail.append(management_dict)
        except Exception as e:
            management_dict = {}
            people_detail.append(management_dict)
        
        try:
            soup8 = BeautifulSoup(code_html_dict.get('CR_F_13a_L'), 'html.parser')
            for aw_div in soup8.find_all('div', class_='record-container'):
                aw_text = aw_div.find('p', class_='field-text').get_text(strip=True)
                if 'Date of expiration of the mandate:' in aw_text:
                    _date_of_mandate = aw_text.replace('Date of expiration of the mandate:', '').strip()
                else:
                    aw_name, zw_country = aw_text.split(', Country:')
                    if aw_name != "":
                        monitoring_dict = {
                                "name": aw_name.strip(),
                                "nationality": zw_country.strip(),
                                "designation": 'monitoring_board',
                                "meta_detail":{
                                    "termination_date":_date_of_mandate.replace(" y.","").replace(".","-")
                                }
                            }
                    
                        people_detail.append(monitoring_dict)
        except:
            monitoring_dict = {}
            people_detail.append(monitoring_dict)

        OBJ = {
                "name":NAME.replace("\"",""),
                "registration_number":registration_number,
                "type":type_,
                "description":desription,
                "industry_code":industry_code,
                "industries":industries,
                "erasure_of_the_trader/NPLE":extracted_data_dict.get('CR_F_27_L',''),
                "transfer_of_a_share":transfer_of_a_share,
                "manner_of_representation":Manner_of_representation,
                "incorporation_date":incorporation_date,
                'dissolution_date':dissolution_date,
                "aliases":aliases.replace("\"",""),
                "source_url":API_URL.replace("%","%%"),
                "addresses_detail":[
                    {
                        "type":"office_address",
                        "address":country+' '+region+' '+ city+' '+municipality
                    },
                    {
                        "type":"correspondence_address",
                        "address":country_+' '+region_+' '+ city_+' '+municipality_
                    }
                ],
                "contacts_detail":[
                    {
                        "type":"phone_number",
                        "value":phone.replace('-, Fax: -','')
                    },
                    {
                        "type":"email",
                        "value":email.replace('-, Web page: -','')
                    },
                    {
                        "type":"website_link",
                        "value":website
                    }
                ],
                "people_detail":people_detail,
                "fillings_detail":filling_details,
                "announcements_detail":announcement_detail,
                "additional_detail":additional_detail
            }   

        OBJ = bulgaria_crawler.prepare_data_object(OBJ)
        ENTITY_ID = bulgaria_crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
        NAME = OBJ['name'].replace("%","%%")
        BIRTH_INCORPORATION_DATE = OBJ['incorporation_date']
        ROW = bulgaria_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
        bulgaria_crawler.insert_record(ROW)

    return SATAUS_CODE,DATA_SIZE, CONTENT_TYPE

try:
    
    SATAUS_CODE,DATA_SIZE, CONTENT_TYPE = crawl()
    
    bulgaria_crawler.end_crawler()
    log_data = {"status": "success",
                 "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back":"",  "crawler":"HTML"}
    bulgaria_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": SATAUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    bulgaria_crawler.db_log(log_data)