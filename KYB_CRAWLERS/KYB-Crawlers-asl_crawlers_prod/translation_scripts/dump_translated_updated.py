"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import os,json 
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from googleapiclient.errors import HttpError
from helpers.translate_helper_functions import get_native_language_records, insert_reports_table, update_translation_table, get_countries, update_translation_table_error
load_dotenv()

def trans(record_):
    """Description: This method is used to translate any language to English. It takes the name as input and returns the translated name.
    @param record_:
    @return: translated_record
    """
    try:
        max_chunk_size = 5000
        translated_chunks = []

        if len(record_) <= max_chunk_size:
            translated_record = GoogleTranslator(source='auto', target='en').translate(record_)
            translated_chunks.append(translated_record)
        else:
            chunks = [record_[i:i + max_chunk_size] for i in range(0, len(record_), max_chunk_size)]
            batch_size = 10 

            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                translated_batch = GoogleTranslator(source='auto', target='en').translate(batch)
                translated_chunks.extend(translated_batch)

        translated_record = ' '.join(translated_chunks)
        return translated_record.replace("'", "''").replace('"', '')
    except Exception as e:
        print(e)
        return None

def track_path(data):
    for each in data:
        if data[each] == "" or data[each] == " " or each == 'aliases' or each == 'aliases(state_language)' or each == 'aliases(official_language)' or data[each] == "N/A" or data[each] == None or each == "crawler_name" or each == "country_name":
            continue
        if isinstance(data[each], str):
            if data[each].strip().replace(" ","") == "" or data[each].isnumeric():
                continue
        if isinstance(data[each], str):
            data[each] = trans(data[each])
        elif isinstance(data[each], dict):
            data[each] = track_path(data[each])
        elif isinstance(data[each], list):
            items = data[each]
            results = []
            for idx, item in enumerate(items):
                item_ = track_path(item)
                results.append(item_)
            data[each] = results

    return data


if __name__ == "__main__":
    countries = get_countries()
    for country in countries:
        records = get_native_language_records(str(country[0]).replace("'",'"'))
        try:
            for record in records:
                item = [record[1], record[2].replace("'", '"'), json.dumps(record[3]), json.dumps(record[4]), json.dumps(
                    record[5]), record[6], json.dumps(record[7]),  json.dumps(record[8]).replace("'", "''"), record[9], record[10], record[11], record[12].replace("'","''"), record[14], record[17]]
                
                result = track_path(record[8])
                
                if len(result) > 0:
                    if result.get('name'):
                        name = result["name"]
                    try:
                        item[1] = name
                    except:
                        item[1] = ''
                    item[7] = json.dumps(result)
                    item[12] = 'en'
                    insert_reports_table(item)
                    update_translation_table([True, item[0]])

                if not result:
                    update_translation_table_error([True, item[0]])

        except HttpError as e:
            status_code = e.resp.status
            print("Exception: ", e)