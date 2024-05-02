"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
"""Import required libraries"""
from helpers.translate_helper_functions import get_native_language_records, insert_reports_table, update_translation_table, get_countries, update_translation_table_error
from googleapiclient.errors import HttpError
import json
import os
from dotenv import load_dotenv
import html
from googleapiclient.discovery import build
from deep_translator import GoogleTranslator


load_dotenv()


class Translate_Records():

    def __init__(self, API_KEY):
        self.API_KEY = API_KEY

    """Description: This method was implemented to translate data using API key, reason for commenting is the unavailability of API key."""

    # def trans(self, value):
    #     service = build('translate', 'v2', developerKey=self.API_KEY)
    #     translation = service.translations().list(
    #         q=value,
    #         target='en'
    #     ).execute()

    #     translated_record = translation['translations'][0]['translatedText']
    #     translated_record = html.unescape(
    #         translated_record.encode().decode('unicode-escape'))

    #     return translated_record

    def trans(self, record_):
        """Description: This method is used to translate any language to English. It takes the name as input and returns the translated name.
        @param record_:
        @return: translated_record
        """
        try:
            max_chunk_size = 5000  # Maximum chunk size for translation
            translated_chunks = []

            if len(record_) <= max_chunk_size:
                # If the record is within the limit, translate it as a whole
                translated_record = GoogleTranslator(source='auto', target='en').translate(record_)
                translated_chunks.append(translated_record)
            else:
                # Split the record into smaller chunks and translate them in batches
                chunks = [record_[i:i + max_chunk_size] for i in range(0, len(record_), max_chunk_size)]
                batch_size = 10  # Number of chunks to translate in each batch

                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i:i + batch_size]
                    translated_batch = GoogleTranslator(source='auto', target='en').translate(batch)
                    translated_chunks.extend(translated_batch)

            translated_record = ' '.join(translated_chunks)
            return translated_record.replace("'", "''").replace('"', '')

        except Exception as e:
            print(e)
            return None

    def track_path(self, data, text, mappings, key, index):
        for each in data:
            if data[each] == "" or data[each] == " " or each == 'aliases' or data[each] == "N/A" or data[each] == None or each == "crawler_name" or each == "country_name":
                continue
            if isinstance(data[each], str):
                if data[each].strip().replace(" ","") == "" or data[each].isnumeric():
                    continue
            if isinstance(data[each], str):
                current_key = key + each
                text += data[each] + "  &&&  "
                mappings[current_key] = index
                index += 1
            elif isinstance(data[each], dict):
                current_key = key + each + '.'
                text, mappings, index = self.track_path(
                    data[each], text, mappings, current_key, index)
            elif isinstance(data[each], list):
                items = data[each]
                for idx, item in enumerate(items):
                    current_key = key + each + '.' + str(idx) + '.'
                    text, mappings, index = self.track_path(
                        item, text, mappings, current_key, index)

        return text, mappings, index

    def unpack(self, data, text, mappings, tries):
        try:
            splited_text = text.split("&&&")

            for each in mappings:
                instance = data
                sub_key = each.split(".")
                for s_k in sub_key[:-1]:
                    if isinstance(instance, list):
                        instance = instance[int(s_k)]
                    else:
                        instance = instance[s_k]
                instance[sub_key[-1]] = splited_text[mappings[each]
                                                     ].replace("'", '"')
        except Exception as e:
            print(e)
            tries+=1
            return {}, tries

        return data, tries

    def translate_record(self, data, tries):
        text, mappings, index = self.track_path(data, "", {}, "", 0)
        text = self.trans(text)
        data, tries = self.unpack(data, text, mappings, tries)
        if not text:
            return None, tries

        return data, tries


if __name__ == "__main__":

    API_KEYS = [os.getenv("API_KEY_TRANSLATION_1"), os.getenv("API_KEY_TRANSLATION_2"), os.getenv("API_KEY_TRANSLATION_3"),
                os.getenv("API_KEY_TRANSLATION_4"), os.getenv("API_KEY_TRANSLATION_5")]
    index = 0
    api_key = API_KEYS[index]
    countries = get_countries()
    for country in countries:
        records = get_native_language_records(str(country[0]).replace("'",'"'))
        tries = 0
        try:
            for record in records:
                item = [record[1], record[2].replace("'", '"'), json.dumps(record[3]), json.dumps(record[4]), json.dumps(
                    record[5]), record[6], json.dumps(record[7]), record[8], record[9], record[10], record[11], record[12], record[14], record[17]]

                translate = Translate_Records(api_key)
                result, tries = translate.translate_record(record[8], tries)
                if len(result) > 0:
                    if result.get('name'):
                        name = result["name"]
                    item[1] = name
                    item[7] = json.dumps(result)
                    item[12] = 'en'
                    insert_reports_table(item)
                    update_translation_table([True, item[0]])
                    tries = 0
                if not result:
                    update_translation_table_error([True, item[0]])
            if tries > 20:
                break
        except HttpError as e:
            status_code = e.resp.status
            if status_code != 200:
                if index < len(API_KEYS):
                    index += 1
                    api_key = API_KEYS[index]
                    continue
                else:
                    print(e, status_code)
                    break
            print("Exception: ", e)
