from datetime import datetime, timedelta
import pandas as pd
import psycopg2, re
import json, os
from dotenv import load_dotenv
load_dotenv()
# Connect to the PostgreSQL database
connection = psycopg2.connect(
    host=os.getenv('SEARCH_DB_HOST'),
    database=os.getenv('SEARCH_DB_NAME'),
    user=os.getenv('SEARCH_DB_USERNAME'),
    password=os.getenv('SEARCH_DB_PASSWORD'),
    port=os.getenv('SEARCH_DB_PORT')
)
# Create a cursor to perform database operations
cursor = connection.cursor()
# SQL query to fetch the data from the 'reports' table
select_query = "SELECT entity_id, birth_incorporation_date, data FROM translate_reports where countries='[\"Saudi Arabia\"]' and categories = '[\"Official Registry\"]';"
# Execute the query
cursor.execute(select_query)
# Fetch all the rows from the 'reports' table
rows = cursor.fetchall()
for row in rows:
    entity_id = row[0]
    birth_incorporation_date = row[1][0]
    data = row[2]
    # Assuming the numeric value represents the number of days since January 1, 1900
    epoch = datetime(1900, 1, 1)
    try:
        result_date = epoch + timedelta(days=float(birth_incorporation_date))
        date_incorporation = json.dumps([str(result_date).split(" ")[0]])
    except:
        continue
    try:
        registration_date = float(data['registration_date'])
        registration_date = str(epoch + timedelta(days=registration_date)).split(" ")[0]
        data['registration_date'] = registration_date
    except:
        continue
    update_query = "UPDATE translate_reports SET birth_incorporation_date = %s , data = %s WHERE entity_id = %s"
    cursor.execute(update_query, (date_incorporation, json.dumps(data), entity_id))
        # Commit the changes to the database
    connection.commit()
    print("Data has been update", entity_id)
    
if connection:
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed.")