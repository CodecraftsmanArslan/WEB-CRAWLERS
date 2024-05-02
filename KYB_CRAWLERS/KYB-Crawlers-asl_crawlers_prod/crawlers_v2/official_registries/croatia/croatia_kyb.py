"""Import required library"""
import json , os
import traceback,sys, time
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from CustomCrawler import CustomCrawler
from load_env.load_env import ENV

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
arguments = sys.argv
PAGE = int(arguments[1]) if len(arguments)>1 else 1

meta_data = {
    'SOURCE' :'Digitalna komora',
    'COUNTRY' : 'Croatia',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://digitalnakomora.hr/e-gospodarske-informacije/poslovne-informacije/vodici", 
                        "Source Description": "The Digital Chamber, a communication platform for business entities, public administration and citizens, is a project of the Croatian Chamber of Commerce, co-financed by the European Fund for Regional Development from the Operational Program Competitiveness and Cohesion"},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://digitalnakomora.hr/e-gospodarske-informacije/poslovne-informacije/vodici'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Croatia Official Registry"
}

croatia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
requests_helper = croatia_crawler.get_requests_helper()

#  Loged in usig these credentials 
body = {"email":"lahrasab@letresearch.com","password":"mKe4UPAD!3ZwaX6"}
json_data = json.dumps(body)
data_headers = {
    "Content-Type": "application/json"
}
response = requests_helper.make_request("https://cms.digitalnakomora.hr/hgk/user/login","POST", data=json_data, headers=data_headers, verify=True, timeout=60*60, max_retries=10)
cookies = response.cookies
cookie_set = ""
# Iterate over the cookies
for cookie in cookies:
    cookie_set += cookie.name+"="+cookie.value+";"

headers = {
        "accept": "application/json",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie":cookie_set,
        "Referer": "https://digitalnakomora.hr/pretraga/poslovni-subjekti",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Type": "application/json"
    }

def get_blocked_status(value):
    """
    Determine the blocked status based on the provided value.

    Args:
        value (int): An integer representing the blocked status, where:
                     - 0 indicates "Not Blocked"
                     - 1 indicates "Blocked"
    
    Returns:
        str or int: The corresponding status as a string ("Not Blocked" or "Blocked"),
                    or the original value if it does not match the expected values.

    Note:
        This function is designed to interpret numeric values (0 or 1) as blocked status.
        If the provided value is not 0 or 1, the function returns the original value.
    """
    if value == 0:
        return "Not Blocked"
    elif value == 1:
        return "Blocked"
    
    # If the provided value is neither 0 nor 1, return the original value
    return value



def fill_null_fields(data):
    """
    Recursively traverse a nested dictionary or list and replace any None values with an empty string.

    Args:
        data (dict or list): The input data structure to be processed, which can be a dictionary or a list.

    Returns:
        dict or list: The modified data structure with None values replaced by empty strings.

    Note:
        This function iterates through the keys and values of a dictionary or the elements of a list.
        If a value is None, it is replaced with an empty string.
        If a value is itself a nested dictionary or list, the function is called recursively to handle nested structures.

    Example:
        Input:
        {'name': 'John', 'age': None, 'details': {'city': 'New York', 'zipcode': None}}

        Output:
        {'name': 'John', 'age': '', 'details': {'city': 'New York', 'zipcode': ''}}
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if value is None:
                data[key] = ""
            elif isinstance(value, (dict, list)):
                fill_null_fields(value)
    elif isinstance(data, list):
        for item in data:
            fill_null_fields(item)

    return data


def convert_date(date_string):
    """
    Convert a date string from the format "%d.%m.%Y" to "%d-%m-%Y".

    Args:
        date_string (str): The input date string in the format "%d.%m.%Y".

    Returns:
        str: The formatted date string in the format "%d-%m-%Y", or an empty string if the input is None or empty.

    Note:
        This function parses the input date string using the "%d.%m.%Y" format.
        If the input is a valid date string, it converts it to the "%d-%m-%Y" format.
        If the input is None or an empty string, the function returns an empty string.

    Example:
        Input:
        "15.12.2022"

        Output:
        "15-12-2022"
    """
    if date_string:
        date_string = date_string.rstrip('.')  # Remove trailing '.' if present
        date = datetime.strptime(date_string, "%d.%m.%Y")
        formatted_date = date.strftime("%d-%m-%Y")
        return formatted_date
    return ""

def get_details_response(data_id):
    """
    Get details response for a specific data ID.

    Parameters:
    - data_id (str): The ID of the data to retrieve details for.

    Returns:
    dict: Details response with null fields filled.
    """
    detail_api = f"https://digitalnakomora.hr/HGKClaniceAPI/api/PoslovniSubjekt/PoslovniSubjektInfo/{data_id}"
    detail_res = requests_helper.make_request(detail_api, "GET", headers=headers, verify=True, timeout=60*60, max_retries=10)
    return fill_null_fields(detail_res.json())

def prepare_people_detail(people):
    """
    Prepare a list of people details.

    Parameters:
    - people (list): List of people information.

    Returns:
    list: List of dictionaries containing name and designation details for each person.
    """
    return [{
        "name": director["imePrezime"].strip().replace('"', '').replace("'", "''"),
        "designation": director["funckijaOsobe"].strip().replace("'", "''")
    } for item in people for director in item['osobe']] if len(people) > 0 else []

def prepare_address_detail(address):
    """
    Prepare a list of address details.

    Parameters:
    - address (str): The address information.

    Returns:
    list: List containing a dictionary with the address and type details.
    """
    return [{
        "address": address.strip().replace("'", "''"),
        "type": "general_address"
    }] if address else []

def prepare_contacts_detail(email):
    """
    Prepare a list of contact details.

    Parameters:
    - email (str): The email address.

    Returns:
    list: List containing a dictionary with the email type and value details.
    """
    return [{
        'type': "email",
        'value': email.strip().replace("'", "''")
    }] if email else []

#Main function to fetch data
def main():
    i = PAGE
    consecutive_empty_data_count = 0
    while True:
        print("page_number :", i)
        BODY={"searchInput":"_","sortByColumn":"PuniNaziv","sortOrder":1,"pageSize":100,"pageNumber":i}
        json_data = json.dumps(BODY)
        res = requests_helper.make_request("https://digitalnakomora.hr/HGKGospodarskaMrezaAPI/api/PoslovniSubjekt/GetFiltered","POST",data=json_data, headers=headers, verify=True, timeout=60*60, max_retries=10)
        STATUS_CODE = res.status_code
        DATA_SIZE = len(res.content)
        CONTENT_TYPE = res.headers['Content-Type'] if 'Content-Type' in res.headers else 'N/A'
        response = res.json()
        if response is None:
            continue


        if response is not None and 'data' in response and 'items' in response['data'] and len(response['data']['items']) == 0:
            consecutive_empty_data_count +=1
            i += 1
            time.sleep(60)
            if consecutive_empty_data_count >= 20:
                break
            continue
        consecutive_empty_data_count = 0
        i += 1

        data_items = response['data']['items']
        

        if len(data_items) > 0:

            for data in data_items:
                details_response = get_details_response(data['id']);
                if ('data' in details_response and 'info' in details_response['data'] and 'kratkiNaziv' in details_response['data']['info']) or ('data' in details_response and 'info' in details_response['data'] and 'mbs' in details_response['data']['info']):
                    OBJ = {
                        "name": details_response['data']['info']["kratkiNaziv"].strip(),
                        "registration_number": str(details_response['data']['info']['mbs']),
                        "registration_date":"",
                        "type": details_response['data']['pravniStatus']["pravniOblik"].strip().replace("'", "''"),
                        "personal_identification_number": details_response['data']['info']['oib'],
                        "industries": details_response['data']['info']['djelatnost'].strip().replace("'", "''"),
                        "number_of_employees": details_response['data']['info']['brojZaposlenih'],
                        "incorporation_date": convert_date(details_response['data']['pravniStatus']['datumIMjestoOsnivanja']) ,
                        "block_status": get_blocked_status(details_response['data']['pravniStatus']['statusBlokade']).strip().replace("'", "''"),
                        "ownership_type": details_response['data']['pravniStatus']['oblikVlasnistva'].strip().replace("'", "''").replace("%", " percent"),
                        "hgk_raating": details_response['data']['pravniStatus']['HGKRejting'].strip().replace("'", "''"),
                        "hgk_score":details_response['data']['pravniStatus']["HGKScore"].strip().replace("'", "''"),
                        "addresses_detail": prepare_address_detail( details_response['data']['info']["adresaSjedista"].strip().replace("'", "''")),
                        "people_detail" : prepare_people_detail(details_response['data']['info']['ljudi']),
                        "contacts_detail": prepare_contacts_detail(details_response['data']['kontakt']['emailSudreg'].strip().replace("'", "''"))
                    }
                else:
                    continue
                OBJ = croatia_crawler.prepare_data_object(OBJ) 
                ENTITY_ID = croatia_crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
                NAME = OBJ['name'].replace("%","%%")
                BIRTH_INCORPORATION_DATE = OBJ.get('incorporation_date') if OBJ.get('incorporation_date') else ''
                ROW = croatia_crawler.prepare_row_for_db(ENTITY_ID,NAME,BIRTH_INCORPORATION_DATE,OBJ)
                croatia_crawler.insert_record(ROW)

               

    return STATUS_CODE,DATA_SIZE, CONTENT_TYPE

try:
    STATUS_CODE,DATA_SIZE, CONTENT_TYPE = main()
    croatia_crawler.end_crawler()
    log_data = {"status": "success",
                 "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML","ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    croatia_crawler.db_log(log_data)
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": "fail",
                 "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE, 
                 "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}

    croatia_crawler.db_log(log_data)
