"""Import required libraries"""
import os
import sys
import json
import copy
import math
import psycopg2
import datetime
from dotenv import load_dotenv
from multiprocessing import Process
load_dotenv()

'''Database configurations '''
conn = psycopg2.connect(host=os.getenv('SEARCH_DB_HOST'), port=os.getenv('SEARCH_DB_PORT'),
                        user=os.getenv('SEARCH_DB_USERNAME'), password=os.getenv('SEARCH_DB_PASSWORD'),
                        dbname=os.getenv('SEARCH_DB_NAME'))

cursor = conn.cursor()

query = """with cte as (
            select inner_name from
            (
                select inner_name, count(*) from
                (
                    select lower(name) inner_name from reports
                ) t1
                group by inner_name
            ) t2
            where count > 1
        )
        select * from reports where lower(name) in
        (
            select * from cte
        ); """


distinct_name_query = """with cte as (
            select inner_name from
            (
                select inner_name, count(*) from
                (
                    select lower(name) inner_name from reports
                ) t1
                group by inner_name
            ) t2
            where count > 1
        )
        select distinct name from reports where lower(name) in
        (
            select * from cte
        ); """
cursor.execute(query)
records = cursor.fetchall()

cursor.execute(distinct_name_query)
distinct_names = cursor.fetchall()

'''Number of Processes'''
NUMBER_OF_PROCESSES = 1


def run_db_query(query):
    """
        Description: This method is used to execute the any queries
        @param: query
    """
    cursor.execute(query)


def union_lists(lst1, lst2):
    """
        Description: This function takes in two lists as input and returns a new list that is the union of the two input lists.
        The union of two sets is a set containing all the elements from both sets, with duplicates removed.
        @param lst1 (list): The first input list
        @param lst2 (list): The second input list
        @return list: The union of the two input lists with duplicates removed.
    """
    final_list = lst1 + lst2
    final_list = [entry.replace("'", '') for entry in final_list]
    # Return the union of the two input lists in the form of list
    return list(set(final_list))


def merge_similar_records(name):
    """
        Description: This function takes in a name as input and merges all the similar records with that name from a list of records.
        The function compares the name of each record with the input name, in a case-insensitive manner.
        It then creates a final record by merging the birth dates, categories, countries, and data fields of all matching records.
        It also returns a list of ids of the records that have been merged.
        @param name (str): The input name to match with the records
        @return tuple: A tuple containing the final merged record and a list of ids of the records that have been merged.
    """
    matching_records = [
        record for record in records if record[2].lower() == name.lower()]
    # take the first record as the base record to merge with others
    final_record = list(matching_records[0])

    for record in matching_records:
        data = record[8]
        # merge birth dates
        birth_dates = record[3]
        for birthdate in birth_dates:
            if birthdate not in final_record[3]:
                final_record[3].append(birthdate)

        # merge categories
        categories = record[4]
        for category in categories:
            if category not in final_record[4]:
                try:
                    final_record[4].append(category)
                except:
                    pass

        # merge countries
        countries = record[5]
        for country in countries:
            if country not in final_record[5]:
                final_record[5].append(country)

        merge_data_ = merge_data_filed(data, final_record[8])
        data = data_replace(data)
        final_record = list(final_record)
        final_record[8] = merge_data_
        final_record = tuple(final_record)
    del_ids = [record_[1] for record_ in matching_records]
    return final_record, del_ids



def merge_data_filed(data, data1):
    """
        Description: This function takes in two data dictionaries and merges them.
        It checks for keys containing the words 'country', 'nationality', 'category', and 'birth' in them,
        and if they match in both data dictionaries, then it merges the values of those keys using the union_lists function.
        The final merged data is returned.
        @param data: the data dictionary
        @param data1: the first data dictionary
        @return final merged data
    """
    final_data = copy.deepcopy(data)
    final_data = data_replace(final_data)
    for section in data:
        for key in data[section]:
            if 'country' in key.lower() or 'nationality' in key.lower():
                try:
                    data_country = data[section][key]
                    data1_country = data1[section][key]
                    if data_country != data1_country:
                        final_data[section][key] = union_lists(
                            data_country, data1_country)
                except:
                    pass

            elif 'category' in key.lower():
                try:
                    data_category = data[section][key]
                    data1_category = data1[section][key]
                    if data_category != data1_category:
                        final_data[section][key] = union_lists(
                            data_category, data1_category)
                except:
                    pass

            elif 'birth' in key.lower():
                try:
                    data_dob = data[section][key]
                    data1_dob = data1[section][key]
                    if data_dob != data1_dob:
                        final_data[section][key] = union_lists(
                            data_dob, data1_dob)
                except:
                    pass
    return final_data


def data_replace(data):
    """
        Description: This function takes in a dictionary 'data' and performs a string replacement operation on the values.
        For each section in the dictionary, it iterates over the values in that section.
        It then performs a deep copy of the values, to avoid modifying the original values, into a new list 'val_'.
        @param data: Dictionary
        @return: data
    """
    keys_to_update = []
    sections_to_update = []
    section_key_updates = []
    for section in data:
        if "'" in section:
            section_key_updates.append(section)
        for values in data[section]:
            val_ = copy.deepcopy([])
            try:
                for val in data[section][values]:
                    val = val.replace("'", "").replace("\\", "")
                    val_.append(val)
                data[section][values] = val_
                if "'" in values:
                    keys_to_update.append(values)
                    sections_to_update.append(section)
            except:
                pass
    for i in range(len(keys_to_update)):
        data[sections_to_update[i]][keys_to_update[i].replace("'", '')] = data[sections_to_update[i]].pop(keys_to_update[i])
    for i in range(len(section_key_updates)):
        data[section_key_updates[i].replace("'", '')] = data.pop(section_key_updates[i])
    return data


def prepare_data(merge_record):
    """
        Description: This function takes in the final merged record as input and prepares it in a format that can be stored in a database.
        It creates a new list 'arr' and appends various elements of the 'merge_record' in a specific order.
        The elements are converted to string format using json.dumps() for elements that are in JSON format.
        The current date and time is also appended to the list.
        It returns the final prepared list 'arr'.
        @param merge_record
        @return arr:list
    """
    if 'mg-' not in str(merge_record[1]):
        arr = []
        arr.append('mg-'+merge_record[1])
        arr.append(merge_record[2].replace("'", ""))
        arr.append(json.dumps(merge_record[3]))
        arr.append(json.dumps(merge_record[4]))
        arr.append(json.dumps(merge_record[5]))
        arr.append(merge_record[6].replace("'", ""))
        arr.append(json.dumps(merge_record[7]))
        arr.append(json.dumps(merge_record[8]))
        arr.append(json.dumps(merge_record[9]))
        arr.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        arr.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        try:
            arr.append("'"+merge_record[12].replace("'", "")+"'")
        except:
            arr.append('NULL')
        try:
            arr.append("'"+merge_record[-2]+"'")
        except:
            arr.append('NULL')
        return arr
    else:
        return None



def prepare_megre_log(merge_record, del_ids):
    """
    Description: This function takes in the final merged record as input and prepares it in a format that can be stored in a database.
    It creates a new list 'arr' and appends various elements of the 'merge_record' in a specific order.
    The elements are converted to string format using json.dumps() for elements that are in JSON format.
    The current date and time is also appended to the list.
    It returns the final prepared list 'arr'.
    @param merge_record
    @param del_ids
    @return arr:list
    """
    arr = []
    arr.append('mg-'+merge_record[1])
    arr.append(json.dumps(del_ids))
    arr.append(merge_record[2].replace("'", ""))
    arr.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    arr.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return arr


def trigger_process(distinct_names):
    """
        Description: This function processes the records and performs the following operations:
        Calls 'merge_similar_records' function for each distinct name to get the merged record and list of records to be deleted.
        Prepares the data to be inserted into the 'reports' table.
        Prepares the data to be inserted into the 'merge_logs' table.
        Inserts the data into the respective tables.
        Deletes the duplicate records.
        @param distinct_names (list): List of distinct names of records.
    """
    for name in distinct_names:
        merge_record, del_ids_ = merge_similar_records(name[0])

        insertion_data = prepare_data(merge_record)
        if insertion_data:
            insert_data = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source, created_at,updated_at, source_details,language) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}',{11},{12}) ON CONFLICT (entity_id) DO
                        UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                            WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*insertion_data)

            merge_log = prepare_megre_log(merge_record, del_ids_)
            insert_mg_log = """INSERT INTO merge_logs (merge_id, duplicate_id, name, created_at, updated_at) VALUES ('{0}', '{1}', '{2}', '{3}','{4}') ON CONFLICT (merge_id) DO UPDATE SET updated_at = '{4}' """.format(
                *merge_log)
            run_db_query(insert_data)
            run_db_query(insert_mg_log)

            for id_ in del_ids_:
                insert_merge_query = "INSERT INTO reports_merged SELECT id, entity_id, name, birth_incorporation_date, categories, countries, entity_type, image, data, source, created_at, updated_at, source_details, adverse_media, language, parent_id FROM reports where entity_id = '{}'".format(id_)
                run_db_query(insert_merge_query)
                
                delete_query = "DELETE FROM reports WHERE entity_id = '{}'".format(id_)
                run_db_query(delete_query)
            
            conn.commit()
            print('\ninsert_data query', insertion_data)


if __name__ == '__main__':
    trigger_process(distinct_names)
