"""Set System Path"""
import sys, traceback, json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from CustomCrawler import CustomCrawler
from datetime import datetime
from bs4 import BeautifulSoup
from load_env.load_env import ENV


meta_data = {
    'SOURCE' :'West Virginia Secretary of State',
    'COUNTRY' : 'West Virginia',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://apps.sos.wv.gov/business/corporations/", 
                        "Source Description": "The West Virginia Secretary of State's online data services serves as a central hub for accessing vital business and election information. It aims to provide users with efficient and convenient access to the services and data they need to interact with the Secretary of State's office in West Virginia."},
    'URL' : 'https://apps.sos.wv.gov/business/corporations/',
    'SOURCE_TYPE' : 'HTML'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'West Virginia Official Registry'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'

west_virginia_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  west_virginia_crawler.get_requests_helper()

# Check if a command-line argument is provided
start_number = int(sys.argv[1]) if len(sys.argv) > 1 else 1
end_number = int(sys.argv[2]) if len(sys.argv) > 2 else 145702

def main_function():
    """
    Description: This function performs the main crawling process for data from a West Virginia Secretary of State website.
    @return:
    - Tuple: The status code, data size, and content type of the crawled data.
    """
    for i in range(start_number, end_number):

        additional_detail = []
        addresses_detail = []
        people_detail = []
         # Convert the number to a string and pad with leading zeros
        org = str(i).zfill(6)
        url = f"https://apps.sos.wv.gov/business/corporations/organization.aspx?org={org}"
        print("org_number",org)

        response = request_helper.make_request(url, method="GET")
        STATUS_CODE = response.status_code
        DATA_SIZE = len(response.content)
        html_content = response.text

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the element with id "lblOrg"
        name_element = soup.find(id="lblOrg")
        NAME = name_element.get_text() if name_element is not None else ""
        
        tables = soup.find_all('table')
        if len(tables) == 0:
            print("Data table not Found")
            continue

        rows = tables[0].find_all("tr")
        headers = [header.get_text(strip=True) for header in rows[1].find_all("td")]
        data_row = [cell.get_text(strip=True) for cell in rows[2].find_all("td")]

        data = dict(zip(headers, data_row))

        org_type = data.get('Org Type')
        effective_date = data.get('Effective Date').replace('/', '-') if data.get('Effective Date') is not None else ""
        established_date = data.get('Established Date').replace('/', '-') if data.get('Established Date') is not None else ""
        filing_date = data.get('Filing Date').replace('/', '-') if data.get('Filing Date') is not None else ""
        charter = data.get('Charter')
        class_ = data.get('Class')
        sec_type = data.get('Sec Type')
        termination_date = data.get('Termination Date').replace('/', '-') if data.get('Termination Date') is not None else ""
        termination_reason = data.get('Termination Reason')
        rows = soup.find_all('tr')

        data = {}

        # Iterate over the rows and extract the th and td values
        for row in rows:
            # Find all th elements within the current row
            th_elements = row.find_all('th')
            
            # Only process rows that contain th elements
            if th_elements:
                td_elements = row.find_all('td')
                
                for th, td in zip(th_elements, td_elements):
                    data[th.get_text(strip=True)] = td.get_text(strip=True)

        industries = data.get('Business Purpose')

        if data.get('Capital Stock') != "" or data.get('Authorized Shares') != "" or data.get('Par Value') != "":
            additional_detail.append({
                "type": "shares_information",
                "data": [{
                    "capital_stock": data.get('Capital Stock') if data.get('Capital Stock') is not None else "",
                    "authorized_share": data.get('Authorized Shares') if data.get('Authorized Shares') is not None else "",
                    "share_par_value": data.get('Par Value') if data.get('Par Value') is not None else ""
                }]
            })
        STATE_NAME = json.load(open('state_names.json'))
        charter_state = ""
        charter_state_value = data.get('Charter State')
        if charter_state_value in STATE_NAME:
            charter_state = STATE_NAME[charter_state_value]
        elif charter_state_value is not None:
            charter_state = charter_state_value
        charter_county = data.get('Charter County') if data.get('Charter County') is not None else ""
        control_number = data.get('Control Number') if data.get('Control Number') is not None else ""
        excess_acres = data.get('Excess Acres') if data.get('Excess Acres') is not None else ""
        at_will_term = data.get('At Will Term') if data.get('At Will Term') is not None else ""
        at_will_term_years = data.get('At Will Term Years') if data.get('At Will Term Years') is not None else ""
        member_managed = data.get('Member Managed') if data.get('Member Managed') is not None else ""

        if data.get('Designated Office Address') is not None:
            addresses_detail.append({
                "type": "office_address",
                "address": data.get('Designated Office Address').replace("'", "''").replace('NONE LISTED','').replace('NONE','').replace("AND OTHERS","").replace("N/A","").replace('NO OTHERS LISTED','').replace("NONE ADDRESSES LISTED","") if data.get('Designated Office Address') is not None else ""
            })

        if data.get('Mailing Address') is not None:
            addresses_detail.append({
                "type": "postal_address",
                "address": data.get('Mailing Address').replace("'", "''").replace('NONE LISTED','').replace('NONE','').replace("AND OTHERS","").replace("N/A","").replace('NO OTHERS LISTED','').replace("NONE ADDRESSES LISTED","") if data.get('Mailing Address') is not None else ""
            })

        if data.get('Notice of Process Address') is not None:
            addresses_detail.append({
                "type": "notice_address",
                "address": data.get('Notice of Process Address').replace("'", "''").replace('NONE LISTED','').replace('NONE','').replace("AND OTHERS","").replace("N/A","").replace('NO OTHERS LISTED','').replace("NONE ADDRESSES LISTED","") if data.get('Notice of Process Address') is not None else ""
            })

        if data.get('Principal Office Address') is not None:
            addresses_detail.append({
                "type": "principal_office_address",
                "address": data.get('Principal Office Address').replace("'", "''").replace('NONE LISTED','').replace('NONE','').replace("AND OTHERS","").replace("N/A","").replace('NO OTHERS LISTED','').replace("NONE ADDRESSES LISTED","") if data.get('Principal Office Address') is not None else ""
            })

        data = {}
        # Find the desired <h2> element
        h2_element = soup.find('h2', string="DBA")

        # Find the parent table of the <h2> element
        table = h2_element.find_parent('table') if h2_element else None
        if table is not None:
            rows = table.find_all("tr")

            headers = [header.get_text(strip=True) for header in rows[1].find_all("td")]
            data_row = [cell.get_text(strip=True) for cell in rows[2].find_all("td")]

            data = dict(zip(headers, data_row))

            additional_detail.append({
                "type": "dba_information",
                "data": [{
                    "name": data.get('DBA Name').replace("'", "") if data.get('DBA Name') is not None else "",
                    "description": data.get('Description').replace("'", "") if data.get('Description') is not None else "",
                    "effective_date": data.get('Effective Date').replace('/', '-') if data.get('Effective Date') is not None else "",
                    "termination_date": data.get('Termination Date').replace('/', '-') if data.get('Termination Date') is not None else ""
                }]
            })

        # Find the desired <h2> element
        h2_element = soup.find('h2', string="Officers")

        # Find the parent table of the <h2> element
        table = h2_element.find_parent('table') if h2_element else None

        if table is not None:
            rows = table.find_all("tr")

            # Iterate over the rows and extract the th and td values
            for row in rows:
                # Find all th elements within the current row
                th_elements = row.find_all('th')
                
                # Only process rows that contain th elements
                if th_elements:
                    td_elements = row.find_all('td')
                    for th, td in zip(th_elements, td_elements):
                        # Remove <br> tags from address
                        for br in td.find_all('br'):
                            br.replace_with(' ')
                        address_value = ''.join(str(item) for item in td.contents[1:]).strip(),
                       # Check if address_value is a tuple
                        if isinstance(address_value, tuple):
                            address_value = address_value[0]  # Access the string element within the tuple
                        # Apply the replace method if address_value is not None
                        if address_value is not None:
                            address_value = address_value.replace('NONE LISTED','').replace('NONE','').replace("AND OTHERS","").replace("N/A","").replace('NO OTHERS LISTED','').replace("NONE ADDRESSES LISTED","")
                        people_name = td.contents[0].strip().replace('NONE LISTED 97-99','').replace('NONE','').replace("AND OTHERS","").replace("N/A","").replace('NO OTHERS LISTED','').replace("SAME AS ABOVE","").replace("SAME AS SEC","").replace("99-00NL","").replace("N/L 97-8","").replace("AND OTHER","").replace("*** NO 88-89 OFFICERS","").replace("NL 01-02","").replace("NL 00-01","").replace(".","") if isinstance(td.contents[0], str) and td.contents[0] is not None else ""
                        people_desig = th.text.strip() if th.text is not None else ""
                        if people_name != "" and address_value != "":
                            people_detail.append({
                                'name': people_name,
                                "address": address_value,
                                'designation': people_desig
                            })

        registration_number = org

        DATA = {
            "name": NAME,
            "type": org_type,
            "incorporation_date": established_date,
            "registration_date": filing_date,
            "dissolution_date": termination_date,
            "industries": industries,
            "jurisdiction": charter_state,
            "addresses_detail": addresses_detail,
            "additional_detail": additional_detail,
            "people_detail": people_detail,
            "registration_number": registration_number,
            "effective_date": effective_date,
            "charter": charter,
            "class": class_,
            "sec_type": sec_type,
            "dissolution_reason": termination_reason,
            "charter_county": charter_county,
            "control_number": control_number,
            "excess_acres": excess_acres,
            "at_will_term": at_will_term,
            "at_will_term_years": at_will_term_years,
            "member_managed": member_managed
        }

        ENTITY_ID = west_virginia_crawler.generate_entity_id(company_name=NAME, reg_number=registration_number)
        BIRTH_INCORPORATION_DATE = ''
        DATA = west_virginia_crawler.prepare_data_object(DATA)
        ROW = west_virginia_crawler.prepare_row_for_db(ENTITY_ID, NAME.replace("%", "%%"), BIRTH_INCORPORATION_DATE, DATA)

        west_virginia_crawler.insert_record(ROW)
    
    return STATUS_CODE, DATA_SIZE, CONTENT_TYPE
    
try:
    STATUS_CODE, DATA_SIZE, CONTENT_TYPE =  main_function()    
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML", "ends_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    west_virginia_crawler.db_log(log_data)
    west_virginia_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    west_virginia_crawler.db_log(log_data)