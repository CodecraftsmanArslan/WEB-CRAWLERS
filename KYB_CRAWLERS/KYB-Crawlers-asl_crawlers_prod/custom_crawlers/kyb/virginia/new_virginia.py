"""Set System Path"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from proxies_lst import get_a_random_proxy

meta_data = {
    'SOURCE' :'Clerks Information System (CIS) of the Virginia State Corporation Commission',
    'COUNTRY' : 'Virginia',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://cis.scc.virginia.gov/EntitySearch/Index", 
                        "Source Description": "Clerk's Information System (CIS) of the Virginia State Corporation Commission. It provides information about entities registered in Virginia such as corporations, limited liability companies (LLCs), and limited partnerships."},
    'URL' : 'https://cis.scc.virginia.gov/EntitySearch/Index',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Virginia Official Registry'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

virginia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  virginia_crawler.get_requests_helper()


def get_additional_information(business_id):
    additional_detail = []
    url = f"https://cis.scc.virginia.gov/EntitySearch/BusinessPreviousQualification"
    page_no = 1
    proxy = get_a_random_proxy()
    while True:
        payload = {
            "businessid": business_id,
            "source": "FromEntityResult",
            "pidx": page_no
        }
        while True:
            response = request_helper.make_request(method="POST", url=url, data=payload, proxy=proxy)
            if not response:
                proxy = get_a_random_proxy()
            else:
                break
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find('table')
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        if len(trs) == 1:
            break
        for tr in trs:
            tds = tr.find_all('td')
            additional_detail.append({
                "type": "",
                "data": [{
                    "name": tds[0].text.strip(),
                    "registration_number": tds[1].text.strip,
                    "status": tds[2].text.strip,
                    "document_type": tds[3].text.strip,
                    "date_added": tds[4].text.strip
                }]
            })
        page_no += 1
    return additional_detail


def get_previous_names_detail(business_id):
    previous_names_detail = []
    url = f"https://cis.scc.virginia.gov/EntitySearch/BusinessNameHistory"
    page_no = 1
    proxy = get_a_random_proxy()
    while True:
        payload = {
            "businessid": business_id,
            "source": "FromEntityResult",
            "pidx": page_no
        }
        while True:
            response = request_helper.make_request(method="POST", url=url, data=payload, proxy=proxy)
            if not response:
                proxy = get_a_random_proxy()
            else:
                break
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find('table')
        if table:
            tbody = table.find('tbody')
            trs = tbody.find_all('tr')
            if len(trs) == 1:
                break
            for tr in trs:
                tds = tr.find_all('td')
                previous_names_detail.append({
                    "name": tds[2].text,
                    "update_date": tds[1].text.replace("N/A", "").replace("/", "-") if tds[1].text is not None else "",
                    "meta_detail":{
                        "name_type": tds[3].text,
                        "start_date":tds[0].text.replace("/", "-") if tds[0].text is not None else "",
                    }
                })
            page_no += 1
        for previous_names in previous_names_detail:
            previous_names["meta_detail"] = {key: value for key, value in previous_names["meta_detail"].items() if value != ''}
    return previous_names_detail


def get_fillings_detail(business_id):
    fillings_detail = []
    base_url = "https://cis.scc.virginia.gov"
    url = f"https://cis.scc.virginia.gov/EntitySearch/BusinessFilings"
    page_no = 1
    proxy = get_a_random_proxy()
    while True:
        payload = {
            "businessid": business_id,
            "source": "FromEntityResult",
            "pidx": page_no
        }
        while True:
            response = request_helper.make_request(method="POST", url=url, data=payload, proxy=proxy)
            if not response:
                proxy = get_a_random_proxy()
            else:
                break
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find('table')
        if table:
            tbody = table.find('tbody')
            trs = tbody.find_all('tr')
            if len(trs) == 1:
                break
            for tr in trs:
                tds = tr.find_all('td')
                fillings_detail.append({
                    "date": tds[0].text.strip().replace("/", "-") if tds[0].text is not None else "",
                    "filing_code": tds[2].text.strip(),
                    "title": tds[4].text.strip(),
                    "file_url": f"{base_url}{tds[9].find('a')['href']}" if tds[9].find('a') is not None else "",
                    "meta_detail": {
                        "effective_date": tds[1].text.strip().replace("/", "-") if tds[1].text is not None else "",
                        "microfilm_number": tds[3].text.strip(),
                        "amendment_type": tds[6].text.strip().replace('N/A', '') if tds[6].text is not None else "",
                        "status": tds[5].text.strip(),
                        "page_count": tds[8].text.strip().replace("N/A", "") if tds[8].text is not None else "",
                        "source": tds[7].text.strip(),
                    }
                })
            page_no += 1
        for filling in fillings_detail:
            filling["meta_detail"] = {key: value for key, value in filling["meta_detail"].items() if value != ''}
    return fillings_detail


def get_information(soup):
    data = {}
    key = None
    for element in soup.find_all(class_=['col-xs-6', 'text-right']):
        if 'text-right' in element['class']:
            key = element.get_text(strip=True)
        elif key:
            data[key] = element.get_text(strip=True)
            key = None
    return data    


def get_prinical_information(soup):
    table = soup.find('table', {'id': 'grid_principalList'})
    people_detail = []
    if table is not None:
        principal_information = table.find_all('tr')

        for info in principal_information:
            cells = info.find_all('td')
            if len(cells) >= 5:
                people_detail.append({
                    "name": cells[2].get_text(strip=True),
                    "address": cells[3].get_text(strip=True),
                    "designation": cells[0].get_text(strip=True),
                    "meta_detail":{
                        "director": cells[1].get_text(strip=True),
                        "last_updated": cells[4].get_text(strip=True).replace("/", "-") if cells[4].get_text(strip=True) is not None else "",
                    }
                })
    return people_detail


def get_data(soup, business_id):
    data = {}
    addresses_detail = []
    people_detail = []
    fillings_detail = []
    previous_names_detail = []
    additional_detail = []
    res = get_information(soup)
    data["registration_number"] = res.get("Entity ID:")
    data["series_llc"] = res.get("Series LLC:").replace("N/A", "") if res.get("Series LLC:") is not None else ""
    data["status"] = res.get("Entity Status:")
    data["name"] = res.get("Entity Name:")
    data["type"] = res.get("Entity Type:")
    addresses_detail.append({
        "type": "office_address",
        "address": res.get("Address:")
    })
    data["reason_for_status"] = res.get("Reason for Status:")
    data["incorporation_date"] = res.get("Formation Date:").replace("/", "-") if res.get("Formation Date:") is not None else ""
    data["current_status_date"] = res.get("Status Date:").replace("/", "-") if res.get("Status Date:") is not None else ""
    data["duration_period"] = res.get("Period of Duration:")
    data["industries"] = res.get("Industry Code:")
    data["jurisdiction_code"] = res.get("Jurisdiction:")
    data["jurisdiction"] = "Virginia"
    data["annual_report_due_date"] = res.get("Annual Report Due Date:").replace("N/A", "").replace("/", "-") if res.get("Annual Report Due Date:") is not None else ""
    data["charter_fee"] = res.get("Charter Fee:")
    data["registration_fee_due_date"] = res.get("Registration Fee Due Date").replace("None", "").replace("/", "-") if res.get("Registration Fee Due Date") is not None else ""
    data["total_shares"] = res.get("Total Shares:")
    meta_detail = {
        "entity_type": res.get("RA Type:"),
        "locality": res.get("Locality:"),
        "qualification": res.get("​​RA Qualification:") if res.get("​​RA Qualification:") is not None else "",
    }
    meta_detail = {key: value for key, value in meta_detail.items() if value != None and value != "null"}
    people_detail.append({
        "name": res.get("Name:"),
        "address": res.get("Registered Office Address:"),
        "appointment_date": res.get("Appointed Date:") if res.get("Appointed Date:") is not None else "",
        "meta_detail": meta_detail
    })
    fillings_detail.extend(get_fillings_detail(business_id))
    previous_names_detail.extend(get_previous_names_detail(business_id))
    people_detail.extend(get_prinical_information(soup))
    additional_detail.extend(get_additional_information(business_id))
    data["addresses_detail"] = addresses_detail
    data["people_detail"] = people_detail
    data["fillings_detail"] = fillings_detail
    data["previous_names_detail"] = previous_names_detail
    data["additional_detail"] = additional_detail
    return data


# Check if a command-line argument is provided
if len(sys.argv) > 1:
    business_id = int(sys.argv[1])
else:
    business_id = 14772


try:
    proxy = get_a_random_proxy()
    for i in range(business_id, 11586825):
        print('Page No. ', business_id)
        url = f"https://cis.scc.virginia.gov/EntitySearch/BusinessInformation?businessId={business_id}&source=FromEntityResult&isSeries%20=%20false"
        while True:
            response = request_helper.make_request(url, proxy=proxy)
            print(response)
            if not response:
                proxy = get_a_random_proxy()
                continue
            else:
                break
        
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        DATA = get_data(soup, business_id)
        print(DATA)
        DATA["incorporation_date"] = DATA["incorporation_date"].replace("N-A", "") if DATA["incorporation_date"] is not None else ""
        registration_number  = DATA.get('registration_number')
        NAME = DATA.get('name')
        ENTITY_ID = virginia_crawler.generate_entity_id(company_name=NAME, reg_number=registration_number)
        BIRTH_INCORPORATION_DATE = ''
        DATA = virginia_crawler.prepare_data_object(DATA)
        ROW = virginia_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, DATA)
        virginia_crawler.insert_record(ROW)
        business_id += 1
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    virginia_crawler.db_log(log_data)
    virginia_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    virginia_crawler.db_log(log_data)

