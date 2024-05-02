import pandas as pd
import os
import psycopg2
import json
from dotenv import load_dotenv
import wget
import shortuuid
import datetime
import sys
import zipfile
import shutil

# Load environment variables
load_dotenv()

# Database configurations
conn = psycopg2.connect(host=os.getenv('SEARCH_DB_HOST'), port=os.getenv('SEARCH_DB_PORT'),
                        user=os.getenv('SEARCH_DB_USERNAME'), password=os.getenv('SEARCH_DB_PASSWORD'),
                        dbname=os.getenv('SEARCH_DB_NAME'))
cursor = conn.cursor()

# Read data from CSV file
FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/custom_scripts'
    
if os.path.exists(f'{FILE_PATH}/france_ky3'):
    shutil.rmtree(f'{FILE_PATH}/france_ky3')

os.mkdir(f'{FILE_PATH}/france_ky3')

wget.download('https://www.data.gouv.fr/fr/datasets/r/0835cd60-2c2a-497b-bc64-404de704ce89',f'{FILE_PATH}/france_ky3/france_ky3.zip')

with zipfile.ZipFile(f'{FILE_PATH}/france_ky3/france_ky3.zip', 'r') as zip_ref:
    zip_ref.extractall(f'{FILE_PATH}/france_ky3')

filenames = os.listdir(f'{FILE_PATH}/france_ky3')
csv_files = [ filename for filename in filenames if filename.endswith( '.csv' ) ]

df = pd.read_csv(f'{FILE_PATH}/france_kyb3/{csv_files[0]}'.format(FILE_PATH), low_memory=False)

# Fill null values with "N/A"
df = df.fillna("N/A")

# Replace spaces in column names with nothing
df.columns = df.columns.str.replace(' ', '')


def prepare_data_object(row):
    """
    Prepare data object by extracting relevant information from a row of the dataframe.
    :param row: A row of the dataframe
    :return: A dictionary containing the relevant information
    """
    section_details = {
        "Summary": {
            "Main Activity": "activitePrincipaleUniteLegale",
            "Employer Nature": "caractereEmployeurUniteLegale",
            "Legal Category": "categorieJuridiqueUniteLegale",
            "Change indicator in Main Activity": "changementActivitePrincipaleUniteLegale",
            "Indicator of change in the employer nature ": "changementCaractereEmployeurUniteLegale",
            "Indicator of Change in the Legal Category": "changementCategorieJuridiqueUniteLegale",
            "Legal Unit Denomination Change Indicator": "changementDenominationUniteLegale",
            "Change indicator for the Name": "changementDenominationUsuelleUniteLegale",
            "Indicator of Change in Social and Solidarity": "changementEconomieSocialeSolidaireUniteLegale",
            "Economy": "changementEtatAdministratifUniteLegale",
            "Indicator of Change in the Administrative Status ": "changementNicSiegeUniteLegale",
            "Legal Unit NIC Change Indicator": "changementNomUniteLegale",
            "Individual Name Change Indicator": "changementNomUsageUniteLegale",
            "Indicator of Change of the Name of the Natural": "changementSocieteMissionUniteLegale",
            "Person": "dateDebut",
            "Indicator of Change  to the Field of Companies ": "dateFin",
            "Start Date of History Period": "denominationUniteLegale",
            "End date of History Period": "denominationUsuelle1UniteLegale",
            "Name": "denominationUniteLegale",
            "Usual Denomination": "denominationUsuelle3UniteLegale",
            "Usual Denomination-Second Field": "economieSocialeSolidaireUniteLegale",
            "Usual Denomination-Third Field": "etatAdministratifUniteLegale",
            "Belonging to the Field of Social and Solidarity": "nicSiegeUniteLegale",
            "Administrative State of the Legal Unit": "nomenclatureActivitePrincipaleUniteLegale",
            "Internal classification number (NIC)": "nomUniteLegale",
            "Activity Nomenclature": "nomUsageUniteLegale",
            "Natural Person's Name": "siren",
            "User Name": "societeMissionUniteLegale",
            "Siren Number": "siren",
            "Belonging to the Field of Companies": "societeMissionUniteLegale"
        },
        "Report Details": {
            "Name": "denominationUniteLegale",
            "Entity Type": "Company/Organization"
        }
    }
    obj = {}
    try:
        for key in section_details:
            obj[key] = {}
            for sub_key in section_details[key]:
                if sub_key == "Entity Type":
                    obj[key][sub_key] = "Company/Organization"
                elif sub_key == "Category":
                    obj[key][sub_key] ="COMPANY/SIE"
                elif sub_key == "Country":
                    obj[key][sub_key] = "FRANCE"
                
                obj[key][sub_key] = str(row[section_details[key][sub_key]]).lower()
    except:
        pass
    return obj


def prepare_db_rec(row):
    """
    Prepare a record that can be inserted into the database.
    :param row: A row of the dataframe
    :return: A list of values to be inserted into the database
    """
    arr = []
    url_ = "https://www.data.gouv.fr/fr/datasets/r/0835cd60-2c2a-497b-bc64-404de704ce89"
    arr.append(shortuuid.uuid(f'{str(row["denominationUniteLegale"])}{url_}'))
    arr.append(str(row['denominationUniteLegale']).replace("'", "''").lower())
    arr.append(json.dumps([]))
    arr.append(json.dumps(['COMPANY/SIE']))
    arr.append(json.dumps(['FRANCE']))
    arr.append('Company/Organization')
    arr.append(json.dumps([]))
    arr.append(json.dumps(prepare_data_object(row)).replace("'", "''"))
    description = "The public database containing information concerning French companies and business establishments, as well as their geographic locations. The database, known as SIRENE, is managed by the French national statistics bureau INSEE and contains data such as registered company names, addresses and identification numbers (SIREN and SIRET), as well as other related information."
    arr.append(json.dumps({'Source URL': url_, 'Source Description': description.replace("'","''"), 'Name': "French National Statistics Bureau INSEE"}))
    arr.append('French National Statistics Bureau INSEE - HTML')
    arr.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    arr.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    arr.append('en')
    return arr


for row in df.iterrows():
    rec = prepare_db_rec(row[1])
    query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type, image,data,source_details,source,created_at,updated_at,language) 
                VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}', '{7}', '{8}','{9}','{10}','{11}','{12}') ON CONFLICT (entity_id) 
                DO UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', 
                image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb WHEN NOT '{6}'::jsonb <@ reports.image 
                THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'
                """.format(*rec)
    cursor.execute(query)
    conn.commit()
    print('\nadded ', row[1]['denominationUniteLegale'])



