import os
import psycopg2

from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(host=os.getenv('SEARCH_DB_HOST'), port=os.getenv('SEARCH_DB_PORT'),
                        user=os.getenv('SEARCH_DB_USERNAME'), password=os.getenv('SEARCH_DB_PASSWORD'), dbname=os.getenv('SEARCH_DB_NAME'))

cursor = conn.cursor()

def get_countries():
    try:
        sql = '''select distinct countries from translate_reports where is_translated = False order by countries;'''
        cursor.execute(sql)
        data = cursor.fetchall()
        conn.commit()
        print('Records Retrieved!')
        return data
    except Exception as e:
        conn.rollback()
        print('Error retrieving records')
        print(e)
    
    return

def get_countries_desc():
    try:
        sql = '''select distinct countries from translate_reports where is_translated = False order by countries desc;'''
        cursor.execute(sql)
        data = cursor.fetchall()
        conn.commit()
        print('Records Retrieved!')
        return data
    except Exception as e:
        conn.rollback()
        print('Error retrieving records')
        print(e)
    
    return

def get_native_language_records(country):
    try:
        sql = '''select * from translate_reports where countries = '{}' and is_translated = False;'''.format(country)
        cursor.execute(sql)
        data = cursor.fetchall()
        conn.commit()
        print('Records Retrieved!')
        return data
    except Exception as e:
        conn.rollback()
        print('Error retrieving records')
        print(e)
    
    return

def update_translation_table(data_array):
    try:
        sql = "update translate_reports set is_translated = %s where entity_id = %s"
        cursor.execute(sql, data_array)
        conn.commit()
        print('Updated translation status')
    except Exception as e:
        conn.rollback()
        print('Error Updating translation flag')
        print(e)

def update_translation_table_error(data_array):
    try:
        sql = "update translate_reports set is_error = %s where entity_id = %s"
        cursor.execute(sql, data_array)
        conn.commit()
        print('Updated translation Error status')
    except Exception as e:
        conn.rollback()
        print('Error Updating translation flag')
        print(e)

def insert_reports_table(data_array):
    try:
        sql = """INSERT INTO reports (entity_id, name, birth_incorporation_date, categories, countries, entity_type, image, data, source, created_at, updated_at, source_details, language, is_format_updated)
                                        VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}') ON CONFLICT (entity_id) DO 
                                        UPDATE SET name='{1}', birth_incorporation_date='{2}', categories='{3}', countries='{4}', entity_type='{5}', data='{7}', updated_at='{10}'"""
        cursor.execute(sql.format(*data_array))
        conn.commit()
        print('Translated record inserted')
    except Exception as e:
        conn.rollback()
        print('Error inserting translated record')
        print(e)