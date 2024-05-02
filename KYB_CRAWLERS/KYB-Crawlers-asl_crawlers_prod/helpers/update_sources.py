"""Import Required Library"""
import os
import json
import psycopg2
import datetime
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connecting to PostgreSQL using psycopg2
conn = psycopg2.connect(host=os.getenv('SOURCES_DB_HOST'), port=os.getenv('SOURCES_DB_PORT'),
                        user=os.getenv('SOURCES_DB_USERNAME'), password=os.getenv('SOURCES_DB_PASSWORD'),
                        dbname=os.getenv('SOURCES_DB_NAME'))

cursor = conn.cursor()

sheet_id = '1shBln2Dz9RK1ogB_UtyU6DHKhs2B2rU_gjBpzRGPXFw'
sheet_name = 'Sheet1'
url_ = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'

# Read data from Google Sheets
df = pd.read_csv(url_)

# Get maximum ID from sources table
get_max_id = """SELECT max(id) FROM sources;"""
cursor.execute(get_max_id)
max_id = cursor.fetchall()[0][0]

# Rename columns
df.rename({"name": "name", "countries": "countries", "category": "category", "url": "url", "description": "description",
           "entity_typee": "entity_type", "source_type": "source_type", "domain": "domain"}, axis=1, inplace=True)


def prepare_data(df, index):
    """Prepares data for inserting/updating records in sources table.
    @param df: Data
    @param index: integer
    @return: array of data
    """
    arr = []
    arr.append(df['name'].replace("'", ""))
    if str(df['description']) == 'nan':
        arr.append("NULL")
    else:
        arr.append("'"+str(df['description']).replace("'", "''") + "'")
    arr.append(df['source_type'])

    if str(df['countries']) == 'nan':
        arr.append(json.dumps([]))
    else:
        arr.append(json.dumps([df['countries']]))

    if str(df['category']) == 'nan':
        arr.append('[]')
    else:
        arr.append(df['category'])
    arr.append(df['url'].replace("'", "''"))

    arr.append(json.dumps({}))

    if str(df['entity_type']) == 'nan':
        arr.append('NULL')
    else:
        arr.append("'" + str(df['entity_type']) + "'")
    arr.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    arr.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    arr.append(max_id+index+1)
    arr.append(2)
    arr.append(df['domain'])
    return arr

# Iterate over each row in the dataframe
for index, row in df.iterrows():
    # Prepare data for updating/inserting record in sources table
    data = prepare_data(row, index)

    # Define update sources with their domain
    update_record = """UPDATE sources SET name = '{0}', description = {1}, source_type = '{2}', countries = '{3}', category = '{4}', entity_type = {7} ,updated_at = '{9}'
                            WHERE url ILIKE %s""".format(*data)
        
    cursor.execute(update_record, (f'%{data[-1]}%',))
    conn.commit() 

    print('\nUpdated record', data)
