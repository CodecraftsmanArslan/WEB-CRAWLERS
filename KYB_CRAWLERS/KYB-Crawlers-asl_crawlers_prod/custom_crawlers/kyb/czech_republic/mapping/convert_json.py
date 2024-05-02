import os
import csv
import json
from deep_translator import GoogleTranslator


def googleTranslator(record_):
    """Description: This method is used to translate any language to English. It takes the name as input and returns the translated name.
    @param record_:
    @return: translated_record
    """
    try:
        translated = GoogleTranslator(source='auto', target='en')
        translated_record = translated.translate(record_)
        return translated_record.replace("'", "''").replace('"', '')
    except Exception as e:
        translated_record = ""  # Assign a default value when translation fails
        print("Translation failed:", e)
        return translated_record

def csv_to_json(csv_file):
    json_data = {}
    with open(csv_file, 'r', encoding='UTF-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                chodnota = row['chodnota']
                text =  googleTranslator(row['text'])
            except KeyError:
                chodnota = row['CHODNOTA']
                text = googleTranslator(row['TEXT']) 

            json_data[chodnota] = text
    return json_data

def process_directory(directory):
    for file in os.listdir(directory):
        if file.endswith('.csv'):
            csv_file = os.path.join(directory, file)
            json_data = csv_to_json(csv_file)

            json_file = os.path.splitext(csv_file)[0] + '.json'
            with open(json_file, 'w', encoding='UTF-8') as outfile:
                json.dump(json_data, outfile)

            print(f"Generated JSON file: {json_file}")

# Provide the directory path here
directory_path = '.'
process_directory(directory_path)