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
    
if os.path.exists(f'{FILE_PATH}/france_kyb2'):
    shutil.rmtree(f'{FILE_PATH}/france_kyb2')

os.mkdir(f'{FILE_PATH}/france_kyb2')

wget.download('https://www.data.gouv.fr/fr/datasets/r/0651fb76-bcf3-4f6a-a38d-bc04fa708576',f'{FILE_PATH}/france_kyb2/france_kyb2.zip')

with zipfile.ZipFile(f'{FILE_PATH}/france_kyb2/france_kyb2.zip', 'r') as zip_ref:
    zip_ref.extractall(f'{FILE_PATH}/france_kyb2')

filenames = os.listdir(f'{FILE_PATH}/france_kyb2')
csv_files = [ filename for filename in filenames if filename.endswith( '.csv' ) ]

df = pd.read_csv(f'{FILE_PATH}/france_kyb2/{csv_files[0]}'.format(FILE_PATH), low_memory=False)

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
        "Main Activity ofEstablishment": "activitePrincipaleEtablissement",
        "Main Activity of the Registered Professional": "activitePrincipaleRegistreMetiersEtablissement",
        "Validity of the Establishment's Employees": "anneeEffectifsEtablissement",
        "Employer Nature of the Establishment": "caractereEmployeurEtablissement",
        "Secondary Address CEDEX Code": "codeCedex2Etablissement",
        "CEDEX Code": "codeCedexEtablissement",
        "Secondary Address Common Code": "codeCommune2Etablissement",
        "Commune code": "codeCommuneEtablissement",
        "Country Code of the Secondary Address": "codePaysEtranger2Etablissement",
        "Country Code for an Establishment ": "codePaysEtrangerEtablissement",
        "Postal Code of the Secondary Address": "codePostal2Etablissement",
        "Postal Code": "codePostalEtablissement",
        "Secondary Address Complement": "complementAdresse2Etablissement",
        "Additional Address": "complementAdresseEtablissement",
        "Establishment Creation Date": "dateCreationEtablissement",
        "Start Date of an Institution's History Period": "dateDebut",
        "Date of Last Processing": "dateDernierTraitementEtablissement",
        "Name": "denominationUsuelleEtablissement",
        "Special Distribution of the Establishment's": "distributionSpeciale2Etablissement",
        "Secondary Address": "distributionSpecialeEtablissement",
        "Establishment Special Distribution": "enseigne1Etablissement",
        "First line of the Establishment's Sign": "enseigne2Etablissement",
        "Second line of Establishment Sign": "enseigne3Etablissement",
        "Third Line of Establishment Sign": "etablissementSiege",
        "Seat quality": "etatAdministratifEtablissement",
        "Administrative State ": "indiceRepetition2Etablissement",
        "Repetition index in the channel": "indiceRepetitionEtablissement",
        "Lane Repetition Index": "libelleCedex2Etablissement",
        "CEDEX Code of the Secondary Address": "libelleCommune2Etablissement",
        "Cedex Code": "libelleCedexEtablissement",
        "Label of the Municipality of the Secondary Address": "libelleCommuneEtablissement",
        "Name of the municipality": "libelleCommuneEtranger2Etablissement",
        "Municipality of the Secondary Address": "libelleCommuneEtrangerEtablissement",
        "Name of the Municipality ": "libellePaysEtranger2Etablissement",
        "Description of the Secondary Address": "libellePaysEtrangerEtablissement",
        "Name of the Country for an Establishment Located Abroad": "libelleVoie2Etablissement",
        "Label of Secondary address": "libelleVoieEtablissement",
        "Label of Address": "libelleVoieEtablissement",
        "Internal Classification Number": "nic",
        "Number of Periods of Establishment": "nombrePeriodesEtablissement",
        "Activity Classification ": "nomenclatureActivitePrincipaleEtablissement",
        "Secondary Address Channel Number": "numeroVoie2Etablissement",
        "Channel Number": "numeroVoieEtablissement",
        "Siren Number": "siren",
        "Siret Number": "siret",
        "Establishment Broadcast Status": "statutDiffusionEtablissement",
        "Section of Employees ": "trancheEffectifsEtablissement",
        "Secondary Address Channel Type": "typeVoie2Etablissement",
        "Channel Type": "typeVoieEtablissement"
    },
    "Report Details": {
        "Name": "denominationUsuelleEtablissement",
        "Entity Type": "",
        "Category": "",
        "Country": ""
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
    url_ = "https://www.data.gouv.fr/fr/datasets/r/0651fb76-bcf3-4f6a-a38d-bc04fa708576"
    arr.append(shortuuid.uuid(f'{str(row["libelleCommuneEtablissement"])}{url_}'))
    arr.append(str(row['libelleCommuneEtablissement']).replace("'", "''").lower())
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
    print('\nadded ', row[1]['libelleCommuneEtablissement'])



