"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from bs4 import BeautifulSoup
from CustomCrawler import CustomCrawler

meta_data = {
    'SOURCE' :'Business Register - Ministry of Justice of the Slovak Republic',
    'COUNTRY' : 'Slovakia',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://www.orsr.sk/search_subjekt.asp?lan=en", 
                        "Source Description": "The Business Register, administered by the Ministry of Justice of the Slovak Republic, is a centralized database that maintains official records of legal entities and other entities engaged in business activities within the country. It serves as a comprehensive and reliable source of information on registered businesses, including their legal status, ownership structure, financial statements, and other relevant data."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://www.orsr.sk/search_subjekt.asp?lan=en'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Slovakia Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'

slovakia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = slovakia_crawler.get_requests_helper()


def extract_dates(text):
    date_pattern = r'\b\d{2}/\d{2}/\d{4}\b'
    dates = re.findall(date_pattern, text)
    
    start_date = dates[0].replace("/","-")
    try:
        end_date = dates[1].replace("/","-")
    except:
        end_date = ""
    return start_date, end_date
try:
    URL = 'https://www.orsr.sk/vypis.asp?lan=en&ID=1&SID=2&P=0'
    FILE_URL = 'https://www.orsr.sk/zbl.asp?ID=1&SID=2&lan=en'

    # response = request_helper.make_request(URL)

    # STATUS_CODE = response.status_code
    # DATA_SIZE = len(response.content)
    # CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'

    with open("index.html") as html_data:
        soup = BeautifulSoup(html_data, "html.parser")

    # soup = BeautifulSoup(response.content, 'html.parser')

    for i in range(1,50):
        business_name_check = soup.find_all("table")[i].find("span")
        if not business_name_check:
            continue
        if business_name_check.text.strip() == "Business name:":
            business_name_tables = business_name_check.parent.find_next_sibling().find_all("table")
            business_name = business_name_tables[0].find("td").text.strip().replace("\n", "").replace("  ", "")
            all_previous_names = []
            if len(business_name_tables) >= 1:
                for name_table in business_name_tables[1:]:
                    previous_name_row = name_table.find_all("td")
                    previous_name_dict = {
                        "name": previous_name_row[0].text.strip().replace("\n", "").replace("  ", ""),
                        "from": previous_name_row[1].text.strip().replace("\n", "").replace("  ", "").split("until")[0].replace("(from:", "").replace("/", "-").strip(),
                        "until": previous_name_row[1].text.split("until:")[1].replace("until:", "").replace(")", "").replace("/", "-").strip()
                    }
                    all_previous_names.append(previous_name_dict)
            break

    # Registered address
    for i in range(1,50):
        registered_seat_check = soup.find_all("table")[i].find("span")
        if not registered_seat_check:
            continue
        if registered_seat_check.text.strip() == "Registered seat:":
            registered_seat_tables = registered_seat_check.parent.find_next_sibling().find("table")
            registered_address = registered_seat_tables.find("tr").find_all("td")[0].get_text(separator = " ", strip = True).replace("\n", "").replace("  ", "")
            from_until_date = registered_seat_tables.find("tr").find_all("td")[1].get_text(separator = " ", strip = True)
            from_, until = extract_dates(from_until_date)
            registered_detail = []
            address = {
                "type":"registered_address",
                "address":registered_address,
                "meta_detail":{
                    "from":from_,
                    "until": until
                }
            }
            registered_detail.append(address)
            break

    # Identification number (IČO)
    for i in range(1,50):
        ico_check = soup.find_all("table")[i].find("span")
        if not ico_check:
            continue
        if ico_check.text.strip() == "Identification number (IČO):":
            ico_tables = ico_check.parent.find_next_sibling().find("table")
            ico_number = ico_tables.find("tr").find_all("td")[0].get_text(separator = " ", strip = True)
            break

    # Date of entry
    for i in range(1,50):
        date_of_entry_check = soup.find_all("table")[i].find("span")
        if not date_of_entry_check:
            continue
        if date_of_entry_check.text.strip() == "Date of entry:":
            date_of_entry_tables = date_of_entry_check.parent.find_next_sibling().find("table")
            date_of_entry = date_of_entry_tables.find("tr").find_all("td")[0].get_text(separator = " ", strip = True).replace("/","-")
            break

    # Date of deletion
   
    for i in range(1,50):
        date_of_deletion_check = soup.find_all("table")[i].find("span")
        if not date_of_deletion_check:
            continue
        if date_of_deletion_check.text.strip() == "Date of deletion:":
            date_of_deletion_tables = date_of_deletion_check.parent.find_next_sibling().find("table")
            date_of_deletion = date_of_deletion_tables.find("tr").find_all("td")[0].get_text(separator = " ", strip = True).replace("/","-")
            break
        else:
            date_of_deletion = ""
            break
      
    # Grounds for deleting
    for i in range(1,50):
        Grounds_for_deleting_check = soup.find_all("table")[i].find("span")
        if not Grounds_for_deleting_check:
            continue
        if Grounds_for_deleting_check.text.strip() == "Grounds for deleting:":
            Grounds_for_deleting_tables = Grounds_for_deleting_check.parent.find_next_sibling().find("table")
            Grounds_for_deleting = Grounds_for_deleting_tables.find("tr").find_all("td")[0].get_text(separator = " ", strip = True).replace("/","-")
            break
        else:
            Grounds_for_deleting = ""
            break
    
    # Legal form
    try:
        for i in range(1,50):
            Legal_form_check = soup.find_all("table")[i].find("span")
            if not Legal_form_check:
                continue
            if Legal_form_check.text.strip() == "Legal form:":
                Legal_form_check_tables = Legal_form_check.parent.find_next_sibling().find("table")
                Legal_form = Legal_form_check_tables.find("tr").find_all("td")[0].get_text(separator = " ", strip = True)
                break
    except:
        Legal_form = ""
    
    # Objects of the company
    additional_detail = []
    for i in range(1,50):
        Objects_check = soup.find_all("table")[i].find("span")
        if not Objects_check:
            continue
        if Objects_check.text.strip() == "Objects of the company:":
            Objects_check_tables = Objects_check.parent.find_next_sibling().find_all("table")
            obj_data = []
            for Objects_table in Objects_check_tables:
                Objects_table_all_tds = Objects_table.find_all("td")
                Objects_td_one_data = Objects_table_all_tds[0]
                _td_two_data = Objects_table_all_tds[1]
                object_ = Objects_td_one_data.text.strip().replace("    ", " ")
                date_obj = _td_two_data.text.strip()
                obj_from_, obj_until = extract_dates(date_obj)
                obj_data.append({
                    "object":object_,
                    "from":obj_from_,
                    "until": obj_until
                   
                })
            additional_detail.append({
                "type":"former_industries_information",
                "data":obj_data
            })
            break        


    # Other legal facts
    for i in range(1,50):
        Other_legal_check = soup.find_all("table")[i].find("span")
        if not Other_legal_check:
            continue
        if Other_legal_check.text.strip() == "Other legal facts:":
            Other_legal_check_tables = Other_legal_check.parent.find_next_sibling().find("table")
            Other_legal = Other_legal_check_tables.find("tr").find_all("td")[0].get_text(separator = " ", strip = True)
            Other_legal_from_until_date = Other_legal_check_tables.find("tr").find_all("td")[1].get_text(separator = " ", strip = True)
            obj_from_, obj_until = extract_dates(Other_legal_from_until_date)
            if Other_legal != "":
                Other_legal = {
                    "type":"legal_facts_information",
                    "data":[
                        {
                            "fact":Other_legal,
                            "from":obj_from_,
                            "until": obj_until
                        }
                    ]
                }
                additional_detail.append(Other_legal)
            break
        

    # Capital information
    for i in range(1,50):
        Capital_check = soup.find_all("table")[i].find("span")
        if not Capital_check:
            continue
        if Capital_check.text.strip() == "Capital:" or Capital_check.text.strip() == "Registered capital":
            Capital_check_tables = Capital_check.parent.find_next_sibling().find("table")
            Capital = Capital_check_tables.find("tr").find_all("td")[0].get_text(separator = " ", strip = True)
            Capital_from_until_date = Capital_check_tables.find("tr").find_all("td")[1].get_text(separator = " ", strip = True)
            Capital_from_, Capital_until = extract_dates(Capital_from_until_date)
            if Capital != "":
                Capital_dict = {
                    "type":"capital_information",
                    "data":[
                        {
                            "capital":Capital,
                            "from":Capital_from_,
                            "until": Capital_until
                        }
                    ]
                }
                additional_detail.append(Capital_dict)
            break

    # acts  information
    for i in range(1,50):
        acts_info_check = soup.find_all("table")[i].find("span")
        if not acts_info_check:
            continue
        if acts_info_check.text.strip() == "Acting in the name of the company:":
            acts_info_check_tables = acts_info_check.parent.find_next_sibling().find("table")
            acts_info = acts_info_check_tables.find("tr").find_all("td")[0].get_text(separator = " ", strip = True)
            acts_info_from_until_date = acts_info_check_tables.find("tr").find_all("td")[1].get_text(separator = " ", strip = True)
            acts_info_from_, acts_info_until = extract_dates(acts_info_from_until_date)
            if acts_info != "":
                acts_info = {
                    "type":"acts_information",
                    "data":[
                        {
                            "act":acts_info,
                            "from":acts_info_from_,
                            "until": acts_info_until
                        }
                    ]
                }
                additional_detail.append(acts_info)
            break

    for j in range(1,41):
        Contribution_check = soup.find_all("table")[j].find('span')
        if not Contribution_check:
            continue
        if Contribution_check.text.strip() == "Contribution of each member:" or Contribution_check.text.strip() == "Basic member contribution":
            Contribution_check_tables = Contribution_check.parent.find_next_sibling().find_all("table")
            data_lst = []
            for Contribution_table in Contribution_check_tables:
                Contribution_table_all_tds = Contribution_table.find_all("td")
                td_one_data = Contribution_table_all_tds[0]
                td_two_data = Contribution_table_all_tds[1]
                Contribution = td_one_data.get_text(separator = " ", strip = True)
                date = td_two_data.text.strip()
                Contribution_from_, Contribution_until = extract_dates(date)
                try:
                    # Extracting the name using regular expression
                    name_pattern = r"(.*?)(Amount of investment|Paid up)"
                    name_match = re.search(name_pattern, Contribution)
                    Contribution_name = name_match.group(1).strip()
                    # Extracting the Amount of investment and Paid up using regular expressions
                    amount_pattern = r"Amount of investment: (\d{1,3}(?: \d{3})*(?:,\d{1,2})?) EUR"
                    paid_up_pattern = r"Paid up: (\d{1,3}(?: \d{3})*(?:,\d{1,2})?) EUR"
                    amount_match = re.search(amount_pattern, Contribution)
                    paid_up_match = re.search(paid_up_pattern, Contribution)
                    amount_of_investment = amount_match.group(1)
                    paid_up = paid_up_match.group(1)
                except:
                    amount_of_investment, paid_up, Contribution_name = "", "", ""
                if Contribution or date:
                    Contribution_dict = {
                        "name": Contribution_name,
                        "amount_of_investment": amount_of_investment,
                        "paid_up":paid_up,
                        "from": Contribution_from_,
                        "until":Contribution_until
                    }
                    data_lst.append(Contribution_dict)
            Contribution_d = {
                "type":"member_contributions_information",
                "data":data_lst        
                }
            additional_detail.append(Contribution_d)
    
            break

    #Get all people_detail
    people_detail = []

    for k in range(1,50):
        partner_check = soup.find_all("table")[k].find('span')
        if not partner_check:
            continue
        if partner_check.text.strip() == "Partners:":
            partner_check_tables = partner_check.parent.find_next_sibling().find_all("table")
            for table in partner_check_tables:
                partner_all_tds = table.find_all("td")
                partner_td_one_data = partner_all_tds[0]
                partner_td_two_data = partner_all_tds[1]
                partner_name_address = partner_td_one_data.text.strip()
                partner_date = partner_td_two_data.text.strip()
                partner_from, partner_until = extract_dates(partner_date)
            
                words = partner_name_address.split()
                partner_name = " ".join(words[:2])
                partner_address = " ".join(words[2:])
                
                if partner_name_address or date:
                    partner_dict = {
                        "designation":"partner",
                        "name": partner_name,
                        "address":partner_address,
                        "meta_detail":{
                            "from":partner_from,
                            "until":partner_until
                        }
                    }
                    people_detail.append(partner_dict)
            break

    for m in range(1,50):
        Management_check = soup.find_all("table")[m].find('span')
        if not Management_check:
            continue
        if Management_check.text.strip() == "Management body:":
            Management_check_tables = Management_check.parent.find_next_sibling().find_all("table")
            for table in Management_check_tables:
                Management_all_tds = table.find_all("td")
                Management_td_one_data = Management_all_tds[0]
                Management_td_two_data = Management_all_tds[1]
                Management_name_address = Management_td_one_data.text.strip()
                Management_date = Management_td_two_data.text.strip()
                Management_from, Management_until = extract_dates(Management_date)
            
                words = Management_name_address.split()
                
                Management_name = " ".join(words[:2])
                try:
                    Management_address = " ".join(words[2:]).split("From")[0].strip()
                except: 
                    Management_address= ""
                
                if Management_name_address or date:
                    Management_dict = {
                        "designation":"management",
                        "name": Management_name,
                        "address":Management_address,
                        "meta_detail":{
                            "from":Management_from,
                            "until":Management_until
                        }
                    }
                    people_detail.append(Management_dict)
            break
    
    for super_ in range(1,50):
        Supervisory_check = soup.find_all("table")[super_].find('span')
        if not Supervisory_check:
            continue
        if Supervisory_check.text.strip() == "Supervisory board:":
            Supervisory_check_tables = Supervisory_check.parent.find_next_sibling().find_all("table")
            for table in Supervisory_check_tables:
                Supervisory_all_tds = table.find_all("td")
                Supervisory_td_one_data = Supervisory_all_tds[0]
                Supervisory_td_two_data = Supervisory_all_tds[1]
                Supervisory_name_address = Supervisory_td_one_data.text.strip()
                Supervisory_date = Supervisory_td_two_data.text.strip()
                Supervisory_from, Supervisory_until = extract_dates(Supervisory_date)
            
                words_ = Supervisory_name_address.split()
                Supervisory_name = " ".join(words_[:2])
                Supervisory_address = " ".join(words_[2:]).split("From")[0].strip()
                
                if Supervisory_name_address or Supervisory_date:
                    Supervisory_dict = {
                        "designation":"supervisor",
                        "name": Supervisory_name,
                        "address":Supervisory_address,
                        "meta_detail":{
                            "from":Supervisory_from,
                            "until":Supervisory_until
                        }
                    }
                    people_detail.append(Supervisory_dict)
            break

    try:
        data_updated_on_check = soup.find_all("table")[-1]
        data_updated_on = data_updated_on_check.find_all("tr")[0].find_all("td")[1].get_text(separator = " ", strip = True).replace("/","-")
        data_of_extract = data_updated_on_check.find_all("tr")[1].find_all("td")[1].get_text(separator = " ", strip = True).replace("/","-")
    except:
        data_updated_on, data_of_extract = "", ""

    #Get fillings details
    response2 = request_helper.make_request(FILE_URL)
    soup2 = BeautifulSoup(response2.content, 'html.parser')

    all_filing_data = []
    for i in range(1,40):
        filling_check = soup2.find_all("table")[i].find('span')
        if not filling_check:
            continue
        if filling_check.text.strip() == "Collection of documents:":
            filling_check_tables = filling_check.parent.find_next_sibling().find_all("table")
            for table in filling_check_tables:
                all_tds = table.find_all("td")
                first_td_data = all_tds[0].find_all("span")
                second_td_data = all_tds[1].find("span")
                name_ = first_td_data[0].text
                type_of_document = first_td_data[2].text
                date = second_td_data.text
                the_dict = {
                    "title": name_,
                    "filing_type": type_of_document,
                    "date": date.split("(")[0]
                }
                all_filing_data.append(the_dict)


    OBJ = {
        "name":business_name,
        "previous_names_detail":all_previous_names,
        "addresses_detail":registered_detail,
        "registration_number":ico_number,
        "registration_date":date_of_entry,
        "inactive_date":date_of_deletion,
        "grounds_for_deleting":Grounds_for_deleting,
        "type":Legal_form,
        "source_url":URL,
        "data_updated_on":data_updated_on,
        "data_of_extract":data_of_extract,
        "additional_detail":additional_detail,
        "fillings_detail":all_filing_data,
        "people_detail":people_detail
        }

    OBJ =  slovakia_crawler.prepare_data_object(OBJ)
    ENTITY_ID = slovakia_crawler.generate_entity_id(OBJ['registration_number'], OBJ["name"])
    NAME = OBJ['name'].replace("%","%%")
    BIRTH_INCORPORATION_DATE = OBJ.get("incorporation_date","")
    ROW = slovakia_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
    slovakia_crawler.insert_record(ROW)

    slovakia_crawler.end_crawler()
    log_data = {"status": "success",
                    "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                    "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    slovakia_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    slovakia_crawler.db_log(log_data)
