"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
import calendar
from CustomCrawler import CustomCrawler
from dateutil import parser
from bs4 import BeautifulSoup

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

meta_data = {
    'SOURCE' :'New Zealand Companies Office',
    'COUNTRY' : 'New Zealand',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/search?q=&entityTypes=ALL&entityStatusGroups=ALL&incorpFrom=&incorpTo=&addressTypes=ALL&addressKeyword=&start=0&limit=15&sf=&sd=&advancedPanel=true&mode=advanced#results", 
                        "Source Description": "The Companies Office in New Zealand is the government agency responsible for the administration and regulation of companies, business entities, and intellectual property rights in the country. It provides various services related to company registration, maintenance, and disclosure."},
    'SOURCE_TYPE': 'HTML',
    'URL' : 'https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/search?q=&entityTypes=ALL&entityStatusGroups=ALL&incorpFrom=&incorpTo=&addressTypes=ALL&addressKeyword=&start=0&limit=15&sf=&sd=&advancedPanel=true&mode=advanced#results'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "New Zealand",
}

new_zealand_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper = new_zealand_crawler.get_requests_helper()

def format_url(js_string, company_number):
    js_pattern = r'^javascript:showDocumentDetails\(\d+\);$'
    js_pattern2 = r'^javascript:goTo\(\'/companies/app/ui/pages/companies/\d+/documents\'\);$'
    if re.match(js_pattern, js_string):
        pattern = r'\b\d+\b'
        matches = re.findall(pattern, js_string)
        if matches:
            return f"https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/{company_number}/{int(matches[0])}/entityFilingRequirement"
        else:
            return ""
    elif re.match(js_pattern2, js_string):
        url = re.search(r"/companies/app/ui/pages/companies/\d+/documents", js_string)
        if url:
            return f"https://app.companiesoffice.govt.nz{url.group()}"
        else:
            return ""

    return js_string

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%m-%d-%Y")
    except Exception as e:
        pass
    return date_str

def get_shareholdings(soup):
    shareholdings = []
    div_elements = soup.find_all('div', {'class': 'allocationDetail'})

    for div_element in div_elements:
        share_element_1 = soup.find('input', {'name': 'shares'})
        share_1 = share_element_1['value']
        share_element_2 = div_element.find('span', {'class': 'shareLabel'})
        share_2 = share_element_2.text.strip()
        share = f"{share_1} shares {share_2}"
        name_element = div_element.find('div', {'class': 'labelValue col2'})
        name = name_element.text.strip()
        address_elements = div_element.find_all('div', {'class': 'labelValue col2'})
        address = address_elements[1].text.strip()
        shareholdings.append({
            "name": name if name is not None else "",
            "address": address.replace("\r\n", "").replace("\x00", ""),
            "designation": "shareholder",
            "meta_detail":{"share_allocation": share}
        })

    return shareholdings



def get_previous_names_detail(soup):
    previous_names_detail = []
    label_div = soup.find('div', {'class': 'previousNames'})
    if label_div is not None:
        previous_names = label_div.find_all('label')
        for name_label in previous_names:
            company_name = name_label.text.strip().split(' (')[0]
            inactivation_date = re.search(r'from (\d{1,2} \w{3} \d{4})', name_label.text).group(1)
            update_date = re.search(r'to (\d{1,2} \w{3} \d{4})', name_label.text).group(1)
            if company_name != "" and company_name is not None:
                previous_names_detail.append({
                    "name": company_name,
                    "update_date": format_date(update_date),
                    "meta_detail":{"inact_date": format_date(inactivation_date)}
                })

    return previous_names_detail

def contact_info(soup):
    # Create a dictionary to store the label-text to value mappings
    result_dict = {}

    # Define the labels to search for
    labels_to_search = [
        "Trading Name(s):",
        "Phone Number(s):",
        "Email Address(es):",
        "Website(s):",
        "Industry Classification(s):"
    ]

    # Find the <label> elements with the specified texts and get their next sibling <td> values
    for label_text in labels_to_search:
        label_element = soup.find('label', string=label_text)
        if label_element:
            td_value = label_element.find_next('td').text.strip()
            result_dict[label_text] = td_value

    return result_dict

def get_shares_information(soup):
    shares_info = []
    total_share_value = soup.find('label', string='Total Number of Shares:').find_next('span').text.strip() if soup.find('label', string='Total Number of Shares:') is not None else ""
    extensive_shareholding_value = soup.find('label', string='Extensive Shareholding:')
    if extensive_shareholding_value is not None:    
        extensive_shareholding_value = "No" if (soup.find('label', string='Extensive Shareholding:').find_next_sibling().get('class') == ['noLabel']) else ""
    if total_share_value is not None and total_share_value != "":
        shares_info.append({
            "type": "shares_information",
            "data": [{
                "total_share": total_share_value,
                "extensive_shareholding": extensive_shareholding_value
            }]
        })

    return shares_info


def get_fillings_detail(soup, company_number):
    # Initialize a list to store the extracted data
    data_list = []
    table_div = soup.find('div', class_='dataList')
    table = table_div.find('table')
    rows = table.select('tbody tr')
    # Loop through each row and extract the data
    for row in rows:
        # Extract date and document type from the row
        date = row.select_one('td:nth-child(1)').text.strip()
        document_type = row.select_one('td:nth-child(2) a').text.strip() if row.select_one('td:nth-child(2) a') is not None else ""
        if document_type == "": continue
        # Optional: Extract the link if it exists
        link = row.select_one('td:nth-child(2) a')['href'] if row.select_one('td:nth-child(2) a') else ''
        
        # Create a dictionary to store the extracted data for each row
        row_data = {
            "date": format_date(date),
            "title": document_type,
            "file_url": format_url(link, company_number),
        }
        
        # Append the row data to the data_list
        data_list.append(row_data)
    return data_list

def get_directors(soup, company_number):
    data = []
    # Find the <td> element with class="director"
    director_tds = soup.find_all('td', class_='director')
    for director_td in director_tds:
        if director_td.find('label', {'for': 'consent'}) is not None:
            consent_link = format_url(director_td.find('label', {'for': 'consent'}).find_next('a')['href'], company_number)
        else:
            consent_link = None
        data.append({
            "name": director_td.find('label', {'for': 'fullName'}).next_sibling.strip().replace("\r\n", "") if director_td.find('label', {'for': 'fullName'}) else "",
            "address": director_td.find('label', {'for': 'residentialAddress'}).next_sibling.strip().replace("\r\n", "").replace("\x00", "") if director_td.find('label', {'for': 'residentialAddress'}) else "",
            "appointment_date": format_date(director_td.find('label', {'for': 'appointmentDate'}).next_sibling.strip()) if director_td.find('label', {'for': 'appointmentDate'}) else "",
            "shareholder": director_td.find('label', {'for': 'shareholder'}).next_sibling.strip() if director_td.find('label', {'for': 'shareholder'}) is not None else "",
            "meta_detail": {"consent_link": consent_link} if consent_link is not None and consent_link != "" else {},
            "designation": "director"
        })

    return data

def get_key_value_pairs(soup):
    key_value_pairs = {}
    rows = soup.find_all('div', class_='row')
    for row in rows:
        label_element = row.find('label')
        if label_element:
            key = label_element.text.strip()
            # Iterate through the contents and find the value
            value = ''
            for content in row.contents:
                if isinstance(content, str):
                    value += content.strip()
            key_value_pairs[key] = value
    return key_value_pairs

def extract_company_data(company_number):
    data = {}
    addresses_detail = []
    additional_detail = []
    people_detail = []

    url = f"https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/{company_number}/detail"
    response = request_helper.make_request(url)
    soup = BeautifulSoup(response.content, "html.parser")
    data["name"] = soup.find('h1').contents[0].text.strip().replace("%", "") if soup.find('h1') is not None else ""
    res = get_key_value_pairs(soup)
    data["registration_number"] = res.get('Company number:')
    data["business_number"] = res.get("NZBN:")
    data["incorporation_date"] = format_date(res.get("Incorporation Date:"))
    data["status"] = res.get("Company Status:")
    data["type"] = res.get("Entity type:")
    data["company_record_link"] = soup.find("label", string="Company record link:").find_next('a')['href']
    if res.get("Registered office address:") != "" and res.get("Registered office address:") is not None:
        addresses_detail.append({
            "type": "office_address",
            "address": res.get("Registered office address:").replace("\r\n", "").replace("O\x00", "").replace("\\u0000s", "").replace("\x00s", "").replace("\x00"," ")
        })
    if res.get("Address for service:") != "" and res.get("Address for service:") is not None:
        addresses_detail.append({
            "type": "service_address",
            "address": res.get("Address for service:").replace("\r\n", "")
        })
    holding_company_info = soup.find('div', {'class': 'ultimateHoldingCompany'})
    if holding_company_info is not None:
        holding_comp_name = holding_company_info.find('a').text if holding_company_info.find('a') is not None else ""
        holding_comp_source_url = holding_company_info.find('a')['href'] if holding_company_info.find('a') is not None else ""
    
    business_number = ""
    for span_element in soup.find_all('span'):
        if "NZBN:" in span_element.text:
            business_number = span_element.text.replace("NZBN:", "").strip()
            break

    ultimate_holding_company_label = soup.find(id='ultimateHoldingCompany')
    if ultimate_holding_company_label:
        link_element = ultimate_holding_company_label.find_next('a')
        company_name, source_url = (link_element.get_text(strip=True), link_element['href']) if ultimate_holding_company_label else ("", "")
        if company_name != "" and company_name is not None and soup.find('strong', string='Registration number / ID').find_next('span').text.strip() != "[Not specified]":
            additional_detail.append({
                "type": "holding_company_information",
                "data": [{
                    "name": company_name,
                    "source_url": f"https://app.companiesoffice.govt.nz{source_url}" if source_url is not None else "",
                    "entity_type": soup.find('strong', string='Type of entity').find_next('span').text.strip(),
                    "registration_number": soup.find('strong', string='Registration number / ID').find_next('span').text.strip(),
                    "business_number": business_number,
                    "jurisdiction": soup.find('strong', string='Country of registration').find_next('span').text.strip(),
                    "address": soup.find('strong', string='Registered office address').find_next('span', {'id': 'regAddress'}).text.strip()
                }]
            })

    contact_detail = contact_info(soup)
    data["constitution_filed"] = soup.find('label', string='Constitution filed:').find_next('a').text.strip().replace("Edit", "")
    data["ar_filing_month"] = label_element.next_sibling.strip().replace('\xa0', ' ').split()[0].capitalize() if (label_element := soup.find('label', string="AR filing month:")) and (label_element.next_sibling is not None) and (label_element.next_sibling.strip().replace('\xa0', ' ').split()[0].capitalize() in calendar.month_name[1:]) else ""
    data["fra_reporting_month"] = soup.find('label', string='FRA Reporting Month:').next_sibling.strip() if soup.find('label', string='FRA Reporting Month:') else ""
    data["industries"] = contact_detail.get("Industry Classification(s):") if contact_detail.get("Industry Classification(s):") is not None else ""

    data["contacts_detail"] = [
        {"type": "telephone_number", "value": contact_detail.get("Phone Number(s):")} if contact_detail.get("Phone Number(s):") != "" and contact_detail.get("Phone Number(s):") is not None else None,
        {"type": "email", "value": contact_detail.get("Email Address(es):").replace('(Sales)\nView more','')} if contact_detail.get("Email Address(es):") != "" and contact_detail.get("Email Address(es):") is not None else None,
        {"type": "website_link", "value": contact_detail.get("Website(s):")} if contact_detail.get("Website(s):") != "" and contact_detail.get("Website(s):") is not None else None
    ]

    # Filter out the None values before printing (optional, for cleaner output)
    data["contacts_detail"] = [contact for contact in data["contacts_detail"] if contact is not None]

    additional_detail.extend(get_shares_information(soup))
    people_detail.extend(get_shareholdings(soup))
    data["aliases"] = contact_detail.get("Trading Name(s):").replace('%',"%%") if contact_detail.get("Trading Name(s):") is not None else ""
    people_detail.extend(get_directors(soup, res.get('Company number:')))
    data["people_detail"] = people_detail 
    data["additional_detail"] = additional_detail
    data["addresses_detail"] = addresses_detail
    data["fillings_detail"] = get_fillings_detail(soup, res.get('Company number:'))
    data["previous_names_detail"] = get_previous_names_detail(soup)

    return data

def get_companies(record_num):
    company_numbers = []
    url = f"https://app.companiesoffice.govt.nz/companies/app/ui/pages/companies/search?q={record_num}&start=0&limit=1000&entitySearch=&addressKeyword=&postalCode=&incorpFrom=&incorpTo=&country=&addressType=&advancedPanel=true&mode=advanced&sf=&sd=&entityTypes=ALL&entityStatusGroups=ALL&addressTypes=ALL"
    response = request_helper.make_request(url)
    soup = BeautifulSoup(response.content, "html.parser")
    entity_info_spans = soup.find_all('span', class_='entityInfo')
    for span in entity_info_spans:
        text = span.get_text()
        if text is not None and '(' and ')' in text:
            value = text.split('(')[1].split(')')[0].strip()
        else: continue
        company_numbers.append(value)
    return company_numbers

try:
    base_url = "https://app.companiesoffice.govt.nz/"
    start_interval = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    for record_num in range(start_interval, 99999):
        # record_num = str(record_num).zfill(5)
        company_numbers = get_companies(record_num)
        if company_numbers is None: continue
        for company_number in company_numbers:
            print(f"Record No: {record_num}")
            company_data = extract_company_data(company_number)  
            print(company_data)
            ENTITY_ID = new_zealand_crawler.generate_entity_id(company_name=company_data.get("name"), reg_number=company_data.get("registration_number"))
            BIRTH_INCORPORATION_DATE = ''
            DATA = new_zealand_crawler.prepare_data_object(company_data)
            ROW = new_zealand_crawler.prepare_row_for_db(ENTITY_ID, company_data.get("name").replace("%","%%"), BIRTH_INCORPORATION_DATE, DATA)
            new_zealand_crawler.insert_record(ROW)

    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    new_zealand_crawler.db_log(log_data)
    new_zealand_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    new_zealand_crawler.db_log(log_data)
