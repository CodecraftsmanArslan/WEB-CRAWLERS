"""Import required Library"""
import json
from psycopg2 import pool
from typing import List
from SlackNotifyKYB import SlackNotifier

class DBHelper:
        notify: SlackNotifier = None
        def __init__(self, crawler_name: str, is_translated: bool, ENV: dict, notify:  SlackNotifier) -> None:
                self.total_inserted_count = 0
                self.crawler_name = crawler_name
                self.is_translated = is_translated
                
                self.__HOST = ENV['HOST']
                self.__PORT = ENV['PORT']
                self.__USER = ENV['USER']
                self.__PASSWORD = ENV['PASSWORD']
                self.__DATABASE = ENV['DATABASE']
                self.notify = notify
                self.connection_pool = pool.SimpleConnectionPool(
                        minconn=1,
                        maxconn=10,
                        host=self.__HOST,
                        port=self.__PORT,
                        database=self.__DATABASE,
                        user=self.__USER,
                        password=self.__PASSWORD
                )
                self.conn = self.connection_pool.getconn()
                self.cursor = self.conn.cursor()

        def insert_records(self, records: List[list]) -> bool:
                '''
                Description: This method is used to insert multiple records into the database.
                @param self: The DBHelper object.
                @param records: The list of record lists to be inserted.
                '''
                for record in records:
                        json_data = json.loads(record[7])
                        try:
                                registration_number = json_data['registration_number']
                        except:
                                registration_number = ""
                        record_name = record[1].strip()
                        if self.is_translated:
                                query = """INSERT INTO translate_reports (entity_id, name, birth_incorporation_date, categories, countries, entity_type, image, data,source,source_details, created_at, updated_at, language, is_format_updated)
                                        VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}') ON CONFLICT (entity_id) DO 
                                        UPDATE SET name='{1}', birth_incorporation_date='{2}', categories='{3}', countries='{4}', entity_type='{5}', data='{7}', updated_at='{10}'""".format(*record)
                        else:
                                query = """INSERT INTO reports (entity_id, name, birth_incorporation_date, categories, countries, entity_type, image, data,source, source_details, created_at, updated_at, language, is_format_updated)
                                        VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}') ON CONFLICT (entity_id) DO 
                                        UPDATE SET name='{1}', birth_incorporation_date='{2}', categories='{3}', countries='{4}', entity_type='{5}', data='{7}', updated_at='{10}'""".format(*record)
                        if not (record_name == '' and registration_number.strip() == ''):
                                print("Stored Record.")
                                self.cursor.executemany(query, record)  # Execute the SQL query

                        self.conn.commit()  # Commit the transaction to the database
                        # Increment the total inserted records count
                        self.total_inserted_count += 1
                
                print("Records inserted:", self.total_inserted_count)
                return True

        def get_total_inserted_records(self) -> int:
                return self.total_inserted_count