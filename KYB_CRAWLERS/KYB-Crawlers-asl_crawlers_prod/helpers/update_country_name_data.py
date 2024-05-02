"""Import Required Library"""
import copy
import json
import os
import psycopg2
import pandas as pd
import datetime
import pycountry
from dotenv import load_dotenv
load_dotenv()


'''Database configurations '''
conn = psycopg2.connect(host=os.getenv('SEARCH_DB_HOST'), port=os.getenv('SEARCH_DB_PORT'),
                        user=os.getenv('SEARCH_DB_USERNAME'), password=os.getenv('SEARCH_DB_PASSWORD'),
                        dbname=os.getenv('SEARCH_DB_NAME'))

cursor = conn.cursor()


get_record = """SELECT id, data  FROM reports;"""
cursor.execute(get_record)

records = cursor.fetchall()

country_code_obj = {"eu": "European Union", "lv":"Latvia"}

def get_country_and_nationality(data):
    """
    Returns a deep copy of the input data with country and nationality codes replaced with their respective names.
    @param data (dict): 
    @returns metadata (dict):

    """
    metadata = copy.deepcopy(data)
    for section in metadata:
        for key in metadata[section]:
            if key.lower() == 'country' or key.lower() =='countries':
                countries_code = metadata[section][key]
                if isinstance(countries_code, list) and len(countries_code) == 1 and isinstance(countries_code[0], list):
                        countries_code = countries_code[0]
                elif isinstance(countries_code, list) and all(isinstance(item, str) for item in countries_code):
                    pass  # country_code is already a list of strings
                
                country_names = []
                for country_code in countries_code:
                    try:
                        country_name = pycountry.countries.lookup(country_code).name
                        country_names.append(country_name)
                    except LookupError:
                        if country_code in country_code_obj:
                            country_names.append(country_code_obj[country_code])
                        else:
                            country_names.append("European Union")
                metadata[section][key] = country_names
            
            elif key.lower() == 'nationality' or key.lower() == 'nationalities':
                nationalities_code = metadata[section][key]
                nationality_names = []
                for Nationality_code in nationalities_code:
                    try:
                        nationality_name = pycountry.countries.lookup(Nationality_code).name
                        nationality_names.append(nationality_name)
                    except LookupError:
                        if Nationality_code in country_code_obj:
                            nationality_names.append(country_code_obj[Nationality_code])
                        else:
                            nationality_names.append("European Union")
                
                metadata[section][key] = nationality_names
                                           

    return metadata


for record in records:
    id_ = record[0]
    data = record[1]
    data_country_code = get_country_and_nationality(data)
    updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    update_record = """UPDATE reports SET  data = '{0}', updated_at = '{1}' WHERE id = '{2}' """.format(
        json.dumps(data_country_code).replace("'","''"), updated_at, id_)
    
    cursor.execute(update_record)
    conn.commit()
    
    print('\nUpdated record', update_record)
