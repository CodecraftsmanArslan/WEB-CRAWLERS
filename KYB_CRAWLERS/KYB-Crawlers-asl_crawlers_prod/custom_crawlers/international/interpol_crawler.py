import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import requests
import shortuuid
import json
import time 

# CONSTANTS 
# BASE URL for public api
BASE_URL = 'https://ws-public.interpol.int/notices/v1/red{}'

# Available countries list with short codes and names
COUNTRIES={'AF':'Afghanistan','AL':'Albania','DZ':'Algeria','AS':'American Samoa, United States','AD':'Andorra','AO':'Angola','AI':'Anguilla, United Kingdom','AG':'Antigua and Barbuda','AR':'Argentina','AM':'Armenia','AU':'Australia','AT':'Austria','AZ':'Azerbaijan','BS':'Bahamas','BH':'Bahrain','BD':'Bangladesh','BB':'Barbados','BY':'Belarus','BE':'Belgium','BZ':'Belize','BJ':'Benin','BT':'Bhutan','BO':'Bolivia','BA':'Bosnia and Herzegovina','BW':'Botswana','BR':'Brazil','BN':'Brunei','BG':'Bulgaria','BF':'Burkina Faso','BI':'Burundi','KH':'Cambodia','CM':'Cameroon','CA':'Canada','CV':'Cape Verde','CF':'Central African Republic','TD':'Chad','CL':'Chile','CN':'China','CO':'Colombia','KM':'Comoros','CG':'Congo','CD':'Congo (Democratic Republic of)','CR':'Costa Rica','HR':'Croatia','CU':'Cuba','CY':'Cyprus','CZ':'Czech Republic','CI':"Côte d'Ivoire",'DK':'Denmark','DJ':'Djibouti','DM':'Dominica','DO':'Dominican Republic','EC':'Ecuador','EG':'Egypt','SV':'El Salvador','GQ':'Equatorial Guinea','ER':'Eritrea','EE':'Estonia','SZ':'Eswatini','ET':'Ethiopia','FJ':'Fiji','FI':'Finland','FR':'France','GA':'Gabon','GM':'Gambia','GE':'Georgia','DE':'Germany','GH':'Ghana','GR':'Greece','GD':'Grenada','GT':'Guatemala','GN':'Guinea','GW':'Guinea Bissau','GY':'Guyana','HT':'Haiti','HN':'Honduras','HU':'Hungary','914':'ICC (International Criminal Court)','IS':'Iceland','IN':'India','ID':'Indonesia','IR':'Iran','IQ':'Iraq','IE':'Ireland','IL':'Israel','IT':'Italy','JM':'Jamaica','JP':'Japan','JO':'Jordan','KZ':'Kazakhstan','KE':'Kenya','KI':'Kiribati','KP':"Korea (Democratic People's Republic of)",'KR':'Korea (Republic of)','KW':'Kuwait','KG':'Kyrgyzstan','LA':'Laos','LV':'Latvia','LB':'Lebanon','LS':'Lesotho','LR':'Liberia','LY':'Libya','LI':'Liechtenstein','LT':'Lithuania','LU':'Luxembourg','MO':'Macao, China','MG':'Madagascar','MW':'Malawi','MY':'Malaysia','MV':'Maldives','ML':'Mali','MT':'Malta','MH':'Marshall Islands','MR':'Mauritania','MU':'Mauritius','MX':'Mexico','FM':'Micronesia, Federated States of','MD':'Moldova','MC':'Monaco','MN':'Mongolia','ME':'Montenegro','MA':'Morocco','MZ':'Mozambique','MM':'Myanmar','NA':'Namibia','NR':'Nauru','NP':'Nepal','NL':'Netherlands','NZ':'New Zealand','NI':'Nicaragua','NE':'Niger','NG':'Nigeria','MK':'North Macedonia','NO':'Norway','OM':'Oman','PK':'Pakistan','PW':'Palau','PS':'Palestine, State of','PA':'Panama','PG':'Papua New Guinea','PY':'Paraguay','PE':'Peru','PH':'Philippines','PL':'Poland','PT':'Portugal','QA':'Qatar','RO':'Romania','RU':'Russia','RW':'Rwanda','KN':'Saint Kitts and Nevis','LC':'Saint Lucia','VC':'Saint Vincent and the Grenadines','WS':'Samoa','SM':'San Marino','ST':'Sao Tome and Principe','SA':'Saudi Arabia','SN':'Senegal','RS':'Serbia','SC':'Seychelles','SL':'Sierra Leone','SG':'Singapore','SK':'Slovakia','SI':'Slovenia','SB':'Solomon Islands','SO':'Somalia','ZA':'South Africa','SS':'South Sudan','ES':'Spain','LK':'Sri Lanka','916':'STL (Special Tribunal for Lebanon)','SD':'Sudan','SR':'Suriname','SE':'Sweden','CH':'Switzerland','SY':'Syria','TJ':'Tajikistan','TZ':'Tanzania','TH':'Thailand','TL':'Timor-Leste','TG':'Togo','TO':'Tonga','TT':'Trinidad and Tobago','TN':'Tunisia','TR':'Turkey','TM':'Turkmenistan','TC':'Turks and Caicos (Islands), United Kingdom','TV':'Tuvalu','UG':'Uganda','UA':'Ukraine','922':'UN IRMCT (United Nations International Residual Mechanism for Criminal Tribunals)','UNK':'under UNMIK mandate (Kosovo)','AE':'United Arab Emirates','GB':'United Kingdom','US':'United States','UY':'Uruguay','UZ':'Uzbekistan','VU':'Vanuatu','VA':'Vatican City State','VE':'Venezuela','VN':'Viet Nam','YE':'Yemen','ZM':'Zambia','ZW':'Zimbabwe'}

# Method to read country by short code returns country name
def read_country(idx):
    return COUNTRIES.get(idx,'Unknown')


GENDERS = {
            'M': 'Male',
            'F': 'Female',
            'U': 'Unknown'
        }
def read_gender(idx):
    return GENDERS.get(idx,None)


# Load environment variables
load_dotenv()

# Database configurations
conn = psycopg2.connect(host=os.getenv('SEARCH_DB_HOST'), port=os.getenv('SEARCH_DB_PORT'),
                        user=os.getenv('SEARCH_DB_USERNAME'), password=os.getenv('SEARCH_DB_PASSWORD'),
                        dbname=os.getenv('SEARCH_DB_NAME'))
cursor = conn.cursor()


# Method to write data into db
def insert_data(row):
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


def get_notice_detail(notice_id):
    ENTITY_ID = shortuuid.uuid(notice_id)
    COUNTRY = ['International']
    CATEGORY = ['Warnings and Regulatory Enforcement']
    ENTITY_TYPE = 'Person'
    SOURCE_DETAIL = {"Source URL": "https://www.interpol.int/How-we-work/Notices/View-Red-Notices", "Source Description": "The website contains public Red Notices for wanted persons. The individuals are wanted by the requesting member country, or international tribunal. Member countries apply their own laws in deciding whether to arrest a person. This list is regularly updated by the INTERPOL General Secretariat based on information provided by the countries that request the issuance of the notices and their publication on this website."}
    url = BASE_URL.format(f'/{notice_id}')
    print('Processing', url)
    res = requests.get(url)
    data = res.json()
    bio  =  {
                'forename': data['forename'] if data['forename'] is not None else data['forename'],
                'family_name': data['name'] if data['name'] is not None else data['name'],
                'gender': read_gender(data['sex_id']),
                'date_of_birth': data['date_of_birth'].replace('/','-') if data['date_of_birth'] is not None else '',
                'place_of_birth': data['place_of_birth']+', '+read_country(data['country_of_birth_id']) if data['place_of_birth'] is not None else read_country(data['country_of_birth_id']),
                'nationalities': ','.join([read_country(cidx) for cidx in data['nationalities']]),
                'height': data['height'],
                'weight': data['weight'],
                'color_of_hairs': ','.join(data['hairs_id']) if data['hairs_id'] is not None else None,
                'color_of_eyes': ','.join(data['eyes_colors_id']) if data['eyes_colors_id'] is not None else None,
                'languages_spoken': ','.join([lidx for lidx in data['languages_spoken_ids']]) if data['languages_spoken_ids'] is not None else None,
                'charges': ','.join([read_country(arwarrants['issuing_country_id'])+': '+(arwarrants['charge'] if arwarrants['charge'] is not None else 'N/A') for arwarrants in data['arrest_warrants']])
            }
    imgs_url = BASE_URL.format(f'/{notice_id}/images')
    res = requests.get(imgs_url)
    data = res.json()
    IMAGES = [imgs_url+'/'+img['picture_id'] for img in data['_embedded']['images']]
    BIRTH_INCORPORATION_DATE = [bio['date_of_birth']]
    NAME = f'{bio["forename"]} {bio["family_name"]}'.strip()

    DATA = {
            "name": NAME,
            "status": "",
            "registration_number": notice_id,
            "registration_date": "",
            "dissolution_date": "",
            "type": "Red Notice",
            "crawler_name": "custom_crawlers.international.interpol_crawler",
            "country_name": COUNTRY[0],
            "company_fetched_data_status": "",
            "meta_detail": {
                    "name": f'{bio["forename"]} {bio["family_name"]}'.strip(),
                    "gender": bio['gender'],
                    **({"date_of_birth": bio['date_of_birth']} if bio['date_of_birth'] is not None else {}),
                    "place_of_birth": bio['place_of_birth'],
                    "nationality": bio['nationalities'],
                    **({"height": bio['height']} if bio['height'] != 0 and bio['height'] != None else {}),
                    **({"weight": bio['weight']} if bio['weight'] != 0 and bio['weight'] != None else {}),
                    **({"colour_of_hair": bio['color_of_hairs']} if bio['color_of_hairs'] is not None else {}),
                    **({"colour_of_eyes": bio['color_of_eyes']} if bio['color_of_eyes'] is not None else {}),
                    **({"languages_spoken": bio['languages_spoken']} if bio['languages_spoken'] is not None else {}),
                    "charges": bio['charges']
            },
        }

    ROW = [ENTITY_ID, NAME.replace("'", "''"), json.dumps(BIRTH_INCORPORATION_DATE), 
            json.dumps(CATEGORY), json.dumps(COUNTRY), ENTITY_TYPE, json.dumps(IMAGES), json.dumps(DATA).replace("'", "''"), 
            'INTERPOL',json.dumps(SOURCE_DETAIL).replace("'", "''"),datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'en',True]
    return ROW

for code, country in COUNTRIES.items():
    url = BASE_URL.format(f'?&nationality={code}&resultPerPage=160&page=1')
    print('Processing', url)
    res = requests.get(url)
    data = res.json()
    if not '_embedded' in data:
        print('ERROR: embedd key not found')
        continue
    notices = [notice['entity_id'].replace('/','-') for notice in data['_embedded']['notices']]
    ROWS = []
    for notice in notices:
        row = None
        try:
            row = get_notice_detail(notice)
        except Exception as e:
            print('Exception thrown while data fetch: \n', e)
            print('Retrying in 20 seconds...')
            time.sleep(20)
            row = get_notice_detail(notice)    
        if row is not None: 
            ROWS.append(row)
    
    # Inserting data for a country
    for row in ROWS:
        insert_data(row)
print('FINISHED')