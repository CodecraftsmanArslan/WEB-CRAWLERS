import requests
from bs4 import BeautifulSoup
import shortuuid
from dotenv import load_dotenv
from datetime import datetime
import os
import psycopg2
import json
import pandas as pd
import gzip
from deep_translator import GoogleTranslator

def googleTranslator(record_):
    """Description: This method is used to translate any language to English. It takes the name as input and returns the translated name.
    @param record_:
    @return: translated_record
    """
    try:
        translated = GoogleTranslator(source='auto', target='en')
        translated_record = translated.translate(record_)
        return translated_record.replace("'", "''").replace('"', '')
    except Exception as e:
        translated_record = ""  # Assign a default value when translation fails
        print("Translation failed:", e)
        return translated_record

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

# Load environment variables
load_dotenv()

# Database configurations
conn = psycopg2.connect(host=os.getenv('SEARCH_DB_HOST'), port=os.getenv('SEARCH_DB_PORT'),
                        user=os.getenv('SEARCH_DB_USERNAME'), password=os.getenv('SEARCH_DB_PASSWORD'),
                        dbname=os.getenv('SEARCH_DB_NAME'))
cursor = conn.cursor()
def insert_data(data):
    for row in data:
        query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,
                image,data,source,source_details,created_at,updated_at,language,is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}',
                '{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) 
                    DO UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', 
                    image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb WHEN NOT '{6}'::jsonb <@ reports.image 
                    THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}',is_format_updated='{13}'
                """.format(*row)
        cursor.execute(query)
        conn.commit()
        print('INSERTED RECORD')

# Constants
SOURCE = 'Norwegian Ministry of Trade and Industry - The Brønnøysund Register Centre'
COUNTRY = ['Norway']
CATEGORY = ['Official Registry']
ENTITY_TYPE = 'Company/Organization'
SOURCE_DETAIL = {"Source URL": "https://data.brreg.no/enhetsregisteret/oppslag/enheter",
                 "Source Description": "This website is maintained by the Norwegian government's Brønnøysund Register Centre that provides access to the Enhanced Business Registry or the \"Enhetsregisteret\" in Norway. The registry is a publicly available database that contains information on all registered businesses in Norway."}
IMAGES = []
# METHOD TO PARSE CSV


CHILD_PARENT_ARRAY = {}

# method fo get organization roles
ROLLER_API = "https://data.brreg.no/enhetsregisteret/api/enheter/{}/roller"
def get_org_people(cid):
    try:
        print('Fetching Roller Api for ', cid)
        res = requests.get(ROLLER_API.format(cid))
        if res.status_code != 200:
            return None
        data = res.json()
        ROLES = []
        for roller in data['rollegrupper']:
            # print(roller.keys())
            role_type = roller['type']['beskrivelse']
            roles = [{'designation': role['type']['beskrivelse'], 
                        **({"meta_detail":{'date_of_birth': role['person']['fodselsdato']}, 'name': ' '.join(role['person']['navn'].values())} 
                        if 'person' in role
                            else {'meta_detail':{'registration_number': role['enhet']['organisasjonsnummer']}, 'name': ' '.join(role['enhet']['navn'])})                
                    } for role in roller['roller'] if "Regnskapsfører" != role['type']['beskrivelse'] and "Revisor" != role['type']['beskrivelse']]
            ROLES.extend(roles)
        return ROLES
    except:
        return []

def get_data(id):
    data = {}
    people_detail = []
    try:
        response = requests.get(f"https://data.brreg.no/enhetsregisteret/oppslag/enheter/{id}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            all_classes = soup.find_all('div', class_='row')
            for element in all_classes:
                if "Kunngjøringer" in element.text:
                    a_tag = element.find_next('a')
                    if a_tag:
                        href = a_tag.get('href')
                        if href:
                            data["announcements_detail"] = [{
                                "meta_detail": {
                                    "source_url": href
                                }
                            }]
                elif "Regnskapsfører" in element.text or "Revisor" in element.text:
                    rolleinnehaver_elements = element.find_all('app-rolleinnehaver')
                    keywords = ["Org.nr.", "Forretningsadresse:"]
                    for rolleinnehaver_element in rolleinnehaver_elements:
                        text = rolleinnehaver_element.text
                        info = {}
                        for i in range(len(keywords)-1):
                            start = text.index(keywords[i]) + len(keywords[i])
                            end = text.index(keywords[i+1])
                            info[keywords[i]] = text[start:end].strip()
                            name_start = 0
                            name_end = text.index("Org.nr.")
                            info["name"] = text[name_start:name_end].strip()
                            info[keywords[-1]] = text.split(keywords[-1], 1)[1].strip()
                            meta_detail = {"organization_number": info["Org.nr."]} if info["Org.nr."] != "" and info["Org.nr."] is not None else {}
                            people_detail.append({ 
                                "designation": "Regnskapsfører" if "Regnskapsfører" in element.text else "Revisor",
                                "name": info["name"],
                                "address": info["Forretningsadresse:"],
                                "meta_detail": meta_detail
                            })
                elif "Stiftelsesdato" in element.text:
                    incor_date = element.find_next('dd')
                    if incor_date:
                        data["incorporation_date"] = incor_date.text.replace(".", "-")
        if len(people_detail) > 0:
            data["people_detail"] = people_detail
    except Exception as e:
        print("Error", e)
    return data

def parse_json(fpath):
    print("Parsing ", fpath)
    with gzip.open(f'norway/input/{fpath}', 'r') as f:
        data = json.load(f)

    ROWS = []
    i = -1
    for co in data:
        i += 1
        # break
        NAME = co['navn'] if 'navn' in co else ''
        REG_NUMBER = co['organisasjonsnummer'] if 'organisasjonsnummer' in co else ''
        ORG_FORM = co['organisasjonsform']['beskrivelse'] if 'organisasjonsform' in co else ''
        NO_EMPLOYEES = co['antallAnsatte'] if 'antallAnsatte' in co else ""
        TARGET_FORM = co['maalform'] if 'maalform' in co else ''
        Institutional_Sector_Code = f"{co['institusjonellSektorkode']['kode']} {co['institusjonellSektorkode']['beskrivelse']}" if "institusjonellSektorkode" in co else ''
        TRADE_CODE = f"{co['naeringskode1']['kode']} {co['naeringskode1']['beskrivelse']}" if "naeringskode1" in co else ""
        REG_DATE = co['registreringsdatoEnhetsregisteret'] if 'registreringsdatoEnhetsregisteret' in co else ''
        START_DATE = co['oppstartsdato'] if 'oppstartsdato' in co else ''
        PARENT_COMPANY = co['overordnetEnhet'] if (
            'overordnetEnhet' in co and fpath == 'sub_unit.json.gz') else ''
        WEBSITE = co['hjemmeside'] if 'hjemmeside' in co else ''
        LAST_SUBMITTED_ANNUAL_ACCOUNT = co['sisteInnsendteAarsregnskap'] if 'sisteInnsendteAarsregnskap' in co else ''
        ENTITY_ID = shortuuid.uuid(f'{REG_NUMBER}-{REG_DATE}-norway_kyb_crawler')
        BIRTH_INCORPORATION_DATE = [REG_DATE] if REG_DATE is not None else []
        if fpath == 'sub_unit.json.gz':
            if PARENT_COMPANY in CHILD_PARENT_ARRAY:
                CHILD_PARENT_ARRAY[PARENT_COMPANY].append(REG_NUMBER)
            else:
                CHILD_PARENT_ARRAY[PARENT_COMPANY] = [REG_NUMBER]
            parent_data = [{
                'business_number': PARENT_COMPANY,
                'reference_link': f'https://data.brreg.no/enhetsregisteret/oppslag/enheter/{PARENT_COMPANY}'
            }]
        else:
            parent_data = [{
                'business_number': sub_unit,
                'reference_link': f'https://data.brreg.no/enhetsregisteret/oppslag/enheter/{sub_unit}'
            } for sub_unit in CHILD_PARENT_ARRAY[REG_NUMBER]] if REG_NUMBER in CHILD_PARENT_ARRAY else []
        PEOPLE = []
        try:
            PEOPLE = get_org_people(REG_NUMBER)
        except Exception as e:
            print('Error while fetching roles...')
            print(e)
        if PEOPLE is None:
            PEOPLE = []
        page_res = get_data(REG_NUMBER)
        if "people_detail" in page_res and len(page_res["people_detail"]) > 0:
            PEOPLE.extend(page_res["people_detail"])
        DATA = {
            "name": NAME,
            "status": "",
            "registration_number": REG_NUMBER,
            "registration_date": REG_DATE,
            "dissolution_date": "",
            "incorporation_date": page_res["incorporation_date"] if "incorporation_date" in page_res else "",
            "type": ORG_FORM,
            "crawler_name": "custom_crawlers.kyb.norway.norway_kyb_crawler",
            "country_name": COUNTRY[0],
            "company_fetched_data_status": "",
            "industries": TRADE_CODE if TRADE_CODE else "",
            **({"additional_detail": [
                {
                    "type": "linked_main_unit" if fpath == 'sub_unit.json.gz' else "linked_sub_unit",
                            "data": parent_data
                }
            ]} if parent_data and len(parent_data)>0 else {}),
            "people_detail": PEOPLE if PEOPLE != None else [],
            "addresses_detail": [],
            "meta_detail": {
                **({"number_of_employees": str(NO_EMPLOYEES)} if NO_EMPLOYEES else {}),
                **({ "last_submitted_annual_account": LAST_SUBMITTED_ANNUAL_ACCOUNT} if LAST_SUBMITTED_ANNUAL_ACCOUNT else {}),
                **({"internet_address": WEBSITE} if WEBSITE else {}),
                **({"target_form": TARGET_FORM} if TARGET_FORM else {}),
                **({"institutional_sector_code": Institutional_Sector_Code} if Institutional_Sector_Code else {}),
                'unit_type':fpath.split('.')[0],
            },
            "announcements_detail": page_res["announcements_detail"] if "announcements_detail" in page_res and len(page_res["announcements_detail"]) > 0 else [],
        }
  
        if 'beliggenhetsadresse' in co:
            LOCATION_ADDRESS = {
                "type": "location_address",
                "address": f"{', '.join(co['beliggenhetsadresse']['adresse'])} {co['beliggenhetsadresse']['postnummer'] if 'postnummer' in co['beliggenhetsadresse'] else ''}, {co['beliggenhetsadresse']['kommunenummer'] if 'kommunenummer' in co['beliggenhetsadresse'] else ''} {co['beliggenhetsadresse']['kommune'] if 'kommune' in co['beliggenhetsadresse'] else ''} {co['beliggenhetsadresse']['land'] if 'land' in co['beliggenhetsadresse'] else ''}",
                "description": "",
            }
            DATA["addresses_detail"].append(LOCATION_ADDRESS)
        if 'postadresse' in co:
            POST_ADDRESS = {
                "type": "postal_address",
                "address": f"{', '.join(co['postadresse']['adresse'])} {co['postadresse']['postnummer'] if 'postnummer' in co['postadresse'] else ''}, {co['postadresse']['kommunenummer'] if 'kommunenummer' in co['postadresse'] else ''} {co['postadresse']['kommune'] if 'kommune' in co['postadresse'] else ''} {co['postadresse']['land'] if 'land' in co['postadresse'] else ''}",
                "description": "",
            }
            DATA["addresses_detail"].append(POST_ADDRESS)
        if 'forretningsadresse' in co:
            BUSINESS_ADDRESS = {
                "type": "business_address",
                "address": f"{', '.join(co['forretningsadresse']['adresse'])} {co['forretningsadresse']['postnummer'] if 'postnummer' in co['forretningsadresse'] else ''}, {co['forretningsadresse']['kommunenummer'] if 'kommunenummer' in co['forretningsadresse'] else ''} {co['forretningsadresse']['kommune'] if 'kommune' in co['forretningsadresse'] else ''} {co['forretningsadresse']['land'] if 'land' in co['forretningsadresse'] else ''}",
                "description": "",
            }
            DATA["addresses_detail"].append(BUSINESS_ADDRESS)

        ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE),
               json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(
                   IMAGES), json.dumps(DATA).replace("'", "''"),
               SOURCE, json.dumps(SOURCE_DETAIL).replace(
                   "'", "''"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'en', True]
        ROWS.append(ROW)
        
        # inset per 20 records in db
        if i%20 == 0:
            insert_data(ROWS)
            ROWS = []
        
    return ROWS


def download_and_extract(fname, url):
    print('Downloading file')
    res = requests.get(url, headers=headers)
    print(res.status_code)
    if res.status_code == 200:
        f = open(f'norway/input/{fname}.json.gz', 'wb+')
        f.write(res.content)
        f.close()
        return f.name
    else:
        print('Invalid response from server: ', res.status_code)
    return None


URLS = {
    'main_unit': 'https://data.brreg.no/enhetsregisteret/oppslag/enheter/lastned',
    'sub_unit': 'https://data.brreg.no/enhetsregisteret/oppslag/underenheter/lastned'
}

# Main execution entry
for name, url in sorted(URLS.items())[::-1]:
    print('processing ',name, url)
    download_and_extract(name,URLS[name])
    data = parse_json(f'{name}.json.gz')
    insert_data(data)