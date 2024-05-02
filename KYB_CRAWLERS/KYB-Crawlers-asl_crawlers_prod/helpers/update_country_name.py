"""Import Required Library"""
import json
import os
import psycopg2
import pandas as pd
import datetime
import pycountry
from dotenv import load_dotenv
load_dotenv()

# Connecting to PostgreSQL using psycopg2
conn = psycopg2.connect(host=os.getenv('SEARCH_DB_HOST'), port=os.getenv('SEARCH_DB_PORT'),
                        user=os.getenv('SEARCH_DB_USERNAME'), password=os.getenv('SEARCH_DB_PASSWORD'),
                        dbname=os.getenv('SEARCH_DB_NAME'))

cursor = conn.cursor()

get_record = """SELECT id, countries FROM reports where cast(countries as varchar) != '[]';"""
cursor.execute(get_record)
records = cursor.fetchall()

def clean_country(countries):
    '''
    Description: This method is used to clean name of countries and convert short code to full country names
    @param countries: list of str
    @return list of country names
    '''
    country_names = []
    for country_code in countries:
        try:
            country_name = pycountry.countries.lookup(country_code).name
            country_names.append(country_name.replace("'", "''"))
        except LookupError:
            # If the country code is not recognized, append the original name or code of the country
            country_names.append(country_code)

    # If all country codes were not recognized, return the original list
    if country_names == countries:
        return countries
    
    return country_names

for record in records:
    id_ = record[0]
    countries = record[1]
    full_name_country = clean_country(countries)
    update_record = """UPDATE reports SET  countries = '{0}' WHERE id = '{1}' """.format(json.dumps(full_name_country), id_)
    
    cursor.execute(update_record)
    conn.commit() 

    print('\nUpdated record', update_record)
