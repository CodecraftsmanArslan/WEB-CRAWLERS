"""Set System Path"""
import sys, traceback,time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from CustomCrawler import CustomCrawler
from bs4 import BeautifulSoup
from dateutil import parser

meta_data = {
    'SOURCE' :'Crossroads Bank for Enterprises',
    'COUNTRY' : 'Belgium',
    'CATEGORY' : 'Official Registry',
    'ENTITY_TYPE' : 'Company/Organization',
    'SOURCE_DETAIL' : {"Source URL": "https://kbopub.economie.fgov.be/kbopub/zoeknummerform.html", 
                        "Source Description": "The Crossroads Bank for Enterprises (CBE) is a database owned by the FPS Economy containing all the basic data concerning companies and their business units. The purpose of the CBE is twofold: increasing the efficiency of public services; and simplifying administrative procedures for companies."},
        'URL' : 'https://kbopub.economie.fgov.be/kbopub/zoeknummerform.html',
        'SOURCE_TYPE' : 'HTML'
    }

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': 'Belgium'
}

STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'HTML'
BASE_URL = 'https://mblsportal.sos.state.mn.us'

belgium_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config,ENV=ENV)
request_helper =  belgium_crawler.get_requests_helper()

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str


def find_next_td(soup, keyword):
    td = soup.find(lambda tag: tag.name == 'td' and keyword in tag.get_text())
    if td is not None:
        return td.find_next_sibling('td')

def find_next_td_text(soup, keyword):
    td = soup.find(lambda tag: tag.name == 'td' and keyword in tag.get_text())
    if td is not None:
        next_td = td.find_next_sibling('td')
        if next_td is not None:
            return next_td.text.strip()
    return ""

def find_next_row(soup, keyword):
    h2_elments = soup.find_all('h2')
    for h2 in h2_elments:
        if keyword in h2.text.strip():
            tr = h2.find_parent('tr')
            if tr is not None:
                return tr.find_next_sibling('tr')
    
def find_td_table_td(soup, keyword):
    try:
        phone_number_td = find_next_td(soup, keyword)
        phone_number_tbl = phone_number_td.find('table')
        phone_number = phone_number_tbl.find('td').text.strip() if phone_number_tbl and phone_number_tbl.find('td') else ''
        return phone_number
    except:
        return ""
    
def get_data(soup):
    item = {}
    additional_detail = []
    contacts_detail = []
    people_detail = []
    addresses_detail = []
    enterprise_td = find_next_td(soup, 'Enterprise number')
    item['registration_number'] = enterprise_td.find(string=True, recursive=False).text.strip() if enterprise_td is not None and enterprise_td.find(string=True, recursive=False) else ''
    item['registration_number_status'] = enterprise_td.find('span', class_='upd').get_text(strip=True) if enterprise_td is not None and enterprise_td.find('span', class_='upd') else ''
    item['status'] = find_next_td_text(soup, 'Status')
    legal_status_td = find_next_td(soup, 'Legal situation')
    legal_status = legal_status_td.find('span', class_='pageactief').text.strip() if legal_status_td and legal_status_td.find('span', class_='pageactief') else ''
    date_updated = legal_status_td.find('span', class_='upd').text.strip() if legal_status_td and legal_status_td.find('span', class_='upd') else ''
    if legal_status != '' or date_updated != '':
        additional_detail.append({
            'type': 'legal_status_info',
            'data': [{
                'legal_status': legal_status,
                'date_updated': date_updated
            }]
        })
    item['incorporation_date'] = find_next_td_text(soup, 'Start date')
    name_td = find_next_td(soup, 'Name')
    item['name'] = name_td.find(string=True, recursive=False).strip() if name_td is not None and name_td.find(string=True, recursive=False) else ''
    type_ = name_td.find('span', class_='upd').get_text(strip=True) if name_td is not None and name_td.find('span', class_='upd') is not None else ''
    item['name_type'] = type_.split(',')[0]
    item['name_last_updated'] = ','.join(type_.split(',')[1:])

    abbreviation_td = find_next_td(soup, 'Name')
    abbreviation = abbreviation_td.find(string=True, recursive=False).strip() if abbreviation_td is not None and abbreviation_td.find(string=True, recursive=False) else ''
    abbreviation_type_ = abbreviation_td.find('span', class_='upd').get_text(strip=True) if abbreviation_td is not None and abbreviation_td.find('span', class_='upd') is not None else ''
    abbreviation_type = abbreviation_type_.split(',')[0]
    abbreviation_last_updated = ','.join(type_.split(',')[1:])
    if abbreviation != "":
        additional_detail.append({
            'type': 'abbreviated_name',
            'data': [{
                'abbreviation':abbreviation,
                'type': abbreviation_type,
                'last_updated':abbreviation_last_updated
            }]
        })

    registered_address_td = find_next_td(soup, "Registered seat's address:")
    address_updated = registered_address_td.find('span', class_='upd').get_text(strip=True) if registered_address_td is not None and registered_address_td.find('span', class_='upd') else ''
    registered_address = registered_address_td.get_text(strip=True).replace(address_updated, '').replace('\xa0', ' ') if registered_address_td is not None else ''
    if registered_address != '':
        addresses_detail.append({
            'type': 'registered_address',
            'address': registered_address,
            'meta_detail': {'address_updated': address_updated} if address_updated != '' else {}
        })

    phone_number = find_td_table_td(soup, 'Phone number:')
    if phone_number != '':
        contacts_detail.append({
            'type': 'phone_number',
            'value': phone_number
        })

    fax = find_td_table_td(soup, 'Fax')
    if fax != '':
        contacts_detail.append({
            'type': 'fax',
            'value': fax
        })
    
    email = find_td_table_td(soup, 'Email address:')
    # email = find_td_table_td(soup, 'E-mail:')
    if email != '':
        contacts_detail.append({
            'type': 'email',
            'value': email
        })

    web_address_td = find_next_td(soup, 'Web Address')
    if web_address_td:
        web_address_tbl = web_address_td.find('table')
        if web_address_tbl:
            web_address_tds = web_address_td.find_all('td')
            web_address = web_address_tds[0].text if web_address_tds else ''
            if web_address != "":
                contacts_detail.append({
                    'type': 'website',
                    'value': web_address,
                    'meta_detail': {
                        'last_updated': web_address_tds[1].text
                    }
                })


    item['entity_type'] = find_next_td_text(soup, 'Entity type')
    legal_form_td = find_next_td(soup, 'Legal form')
    item['type'] = legal_form_td.find(string=True, recursive=False).strip() if legal_form_td is not None and legal_form_td.find(string=True, recursive=False) else ''
    item['name_last_updated_2'] = legal_form_td.find('span', class_='upd').get_text(strip=True) if legal_form_td is not None else ''
    establishment_units_td = find_next_td(soup, 'Number of establishment units')
    if establishment_units_td and establishment_units_td.find('strong'):
        additional_detail.append({
            'type': 'establishment_units_info',
            'data': [{
                'number': establishment_units_td.find('strong').text,
                'url': f"https://kbopub.economie.fgov.be/kbopub/{establishment_units_td.find('a').get('href')}" if establishment_units_td is not None and establishment_units_td.find('a') else ''
            }]
        })

    functions_table = soup.find('table', id='toonfctie')
    if functions_table:
        functions_tbody = functions_table.find('tbody')
        if functions_tbody:
            functions_trs = functions_tbody.find_all('tr')
            for functions_tr in functions_trs:
                functions_tds = functions_tr.find_all('td')
                people_detail.append({
                    'designation': functions_tds[0].text.strip(),
                    'name': functions_tds[1].text.strip().replace('\xa0', ''),
                    'appointment_date': functions_tds[2].text.strip()
                })


    entrepreneurial_skill_tr = find_next_row(soup, 'Entrepreneurial skill - Travelling- Fairground operator')
    if entrepreneurial_skill_tr:
        entrepreneurial_skill_tds = entrepreneurial_skill_tr.find_all('td')
        for entrepreneurial_skill_td in entrepreneurial_skill_tds:
            try:
                additional_detail.append({
                    'type': 'entrepreneurial_skills_info',
                    'data': [{
                        'skill': entrepreneurial_skill_td.find(string=True, recursive=False).strip() if entrepreneurial_skill_td is not None else '',
                        'last_updated': entrepreneurial_skill_td.find('span', class_='upd').get_text(strip=True) if entrepreneurial_skill_td is not None else ''
                    }]
                })
            except:
                pass

    characteristics = []
    characteristics_tr = find_next_row(soup, 'Characteristics')
    while True:
        try:
            characteristics_td = characteristics_tr.find('td')
            characteristics.append({
                'description': characteristics_td.find(string=True, recursive=False).strip() if characteristics_td is not None else '',
                'date_updated': characteristics_td.find('span', class_='upd').get_text(strip=True) if characteristics_td is not None else ''
            }) 
            characteristics_tr = characteristics_tr.find_next_sibling('tr')
        except:
            break
    
    if len(characteristics) > 0:
        additional_detail.append({
            'type': 'qualities',
            'data': characteristics
        })

                    
    capital = find_next_td_text(soup, 'Capital')
    annual_assembly = find_next_td_text(soup, 'Annual assembly')
    end_date_financial_year = find_next_td_text(soup, 'End date financial year')

    if capital != '':
        additional_detail.append({
            'type': 'financial_information',
            'data': [{
                'capital': capital.replace('\xa0', ' '),
                'annual_assembly': annual_assembly,
                'end_date_financial_year': end_date_financial_year
            }]
        }) 

    links_between_entities = []
    links_between_entities_tr = find_next_row(soup, 'Links between entities')
    if links_between_entities_tr:
        links_between_entities_tr = links_between_entities_tr.find_next_sibling('tr')
        while True:
            try:
                links_between_entities_href = links_between_entities_tr.find('a')
                links_between_entities.append({
                    'url': f"https://kbopub.economie.fgov.be/kbopub/{links_between_entities_href.get('href')}",
                    'description': links_between_entities_tr.text.replace('\xa0', ' ').replace('\n', '').replace('  ', '').replace('\t', '')
                }) 
                links_between_entities_tr = links_between_entities_tr.find_next_sibling('tr')
            except:
                break

    if len(links_between_entities) > 0:
        additional_detail.append({
            'type': 'entity_links_info',
            'data': links_between_entities
        })

    external_links = []
    external_link_title = ''
    external_link_url = ''
    external_links_tr = find_next_row(soup, 'External links')
    if external_links_tr:
        external_links_td = external_links_tr.find('td')
        for tag_ in external_links_td.find_all(True):
            if tag_.name == 'b':
                external_link_title = tag_.text.strip()
            elif tag_.name == 'a':
                external_link_url += ', ' + tag_.get('href')
            elif external_link_url != '':
                external_links.append({
                    'title': external_link_title,
                    'url': external_link_url
                })
                external_link_title = ''
                external_link_url = ''
    
    if len(external_links) > 0:
        additional_detail.append({
            'type': 'external_links',
            'data': external_links
        })

    vat_activities_info = []
    vat_activities_info_tr = find_next_row(soup, 'Version of the Nacebel codes for the VAT activities 2008')
    while True:
        try:
            vat_activities_info_href = vat_activities_info_tr.find('a')
            vat_activities_title = ''.join(vat_activities_info_tr.find('td').find_all(string=True, recursive=False))
            vat_activities_info.append({
                'title': vat_activities_title.split('-')[0].strip().replace('\xa0', '').replace('\n', ''),
                'code': vat_activities_info_href.text,
                'url': f"https://kbopub.economie.fgov.be/kbopub/{vat_activities_info_href.get('href')}",
                'description': vat_activities_title.split('-')[1].strip().replace('\xa0', '').replace('\n', ''),
                'last_updated': vat_activities_info_tr.find('span').text if vat_activities_info_tr.find('span') else ''
            }) 
            vat_activities_info_tr = vat_activities_info_tr.find_next_sibling('tr')
        except:
            break
    if len(vat_activities_info) > 0:
        additional_detail.append({
            'type': 'vat_activities_info',
            'data': vat_activities_info
        })


    activities_info = []
    activities_info_tr = find_next_row(soup, 'Version of the Nacebel codes for the NSSO activities 2008')
    while True:
        try:
            activities_info_href = activities_info_tr.find('a')
            activities_info_title = ''.join(activities_info_tr.find('td').find_all(string=True, recursive=False))
            activities_info.append({
                'title': activities_info_title.split('-')[0].strip().replace('\xa0', '').replace('\n', ''),
                'code': activities_info_href.text,
                'url': f"https://kbopub.economie.fgov.be/kbopub/{activities_info_href.get('href')}",
                'description': activities_info_title.split('-')[1].strip().replace('\xa0', '').replace('\n', ''),
                'last_updated': activities_info_tr.find('span').text if activities_info_tr.find('span') else ''
            }) 
            activities_info_tr = activities_info_tr.find_next_sibling('tr')
        except:
            break
    if len(activities_info) > 0:
        additional_detail.append({
            'type': 'activities_info',
            'data': activities_info
        })


    admissions_tr = find_next_row(soup, 'Admissions')
    if admissions_tr:
        admissions_description = admissions_tr.find('font').text
        admissions_last_updated = admissions_tr.find('span').text
        if admissions_description != '' or admissions_last_updated != '':
            additional_detail.append({
                'type': 'admissions_info',
                'data': [{
                    'description': admissions_description,
                    'last_updated': admissions_last_updated
                }]
            })

    item['people_detail'] = people_detail
    item['contacts_detail'] = contacts_detail
    item['additional_detail'] = additional_detail
    item['addresses_detail'] = addresses_detail
    return item

try:
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 400000000 #473590424
    for reg_num in range(start, 999900000):
        record_num = str(reg_num).zfill(10)
        print(f"Record No: {record_num}")
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'kbopub.economie.fgov.be',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }
        response = request_helper.make_request(f"https://kbopub.economie.fgov.be/kbopub/zoeknummerform.html?lang=en&nummer={record_num}&actionLu=Zoek", headers=headers, data={})
        if response is not None:
            soup = BeautifulSoup(response.text, 'html.parser')
            data = get_data(soup)
            if data['registration_number'] == '' and data['name'] == '':
                print(f"Record not found against the {record_num}")
                continue
            ENTITY_ID = belgium_crawler.generate_entity_id(company_name=data.get('name'), reg_number=data.get('registration_number'))
            BIRTH_INCORPORATION_DATE = ''
            DATA = belgium_crawler.prepare_data_object(data)
            ROW = belgium_crawler.prepare_row_for_db(ENTITY_ID, data.get('name'), BIRTH_INCORPORATION_DATE, DATA)
            belgium_crawler.insert_record(ROW)
    log_data = {"status": 'success',
                    "error": "", "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":"",  "crawler":"HTML"}
    
    belgium_crawler.db_log(log_data)
    belgium_crawler.end_crawler()
except Exception as e:
    tb = traceback.format_exc()
    print(e,tb)
    log_data = {"status": 'fail',
                    "error": e, "url": meta_data['URL'], "source_type": meta_data['SOURCE_TYPE'], "data_size": DATA_SIZE, "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back":tb.replace("'","''"),  "crawler":"HTML"}
    
    belgium_crawler.db_log(log_data)
