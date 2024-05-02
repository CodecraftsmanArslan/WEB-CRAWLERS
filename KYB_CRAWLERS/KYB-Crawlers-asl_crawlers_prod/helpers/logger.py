"""Import required libraries"""
import json
from datetime import datetime
from helpers.slack_notify import SlackNotifier
from dotenv import load_dotenv
from helpers.db_connection import PostgresConnection
import os
import traceback
load_dotenv()


class Logger:
    """Logger class"""
    notifier = SlackNotifier()
    db = PostgresConnection()
    conn = db.get_connection('SEARCH')
    cursor = conn.cursor()
    sources_db = PostgresConnection()
    sources_conn = db.get_connection('SOURCES')
    sources_cursor = sources_conn.cursor()

    def __init__(self, data=None) -> None:
        """Constructor"""
        if data is not None:
            print("****************************************************************")
            print("*****************************START******************************")
            self.data = data
            self.error_message = self.get_error_message(type(data['error']).__name__) if data['status'] == 'fail' else 'No Error'
            self.query = """INSERT INTO logs(url, source_type, number_of_records, created_at, status, error_message, 
            missing_keys, error_type, data_size, server_ip, content_type, status_code, file_path, trace_back, crawler) VALUES('{0}','{1}','{2}','{3}','{4}','{5}', '{6}','{7}' ,'{8}','{9}','{10}', '{11}','{12}', '{13}', '{14}');""".format(data['url'].replace("'", "''"), 
            data['source_type'].upper(), 
            data['number_of_records'], 
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            data['status'], self.error_message.replace("'", "''"), 
            json.dumps(data['missing_keys']), 
            type(data['error']).__name__.replace("'", "''") if data['status'] == 'fail' else 'N/A', 
            data['data_size'], 
            os.getenv('SERVER_IP'),
            data['content_type'] if 'content_type' in list(data.keys()) else 'Optional',
            data['status_code'] if 'status_code' in list(data.keys()) else '00',
            data['file_path'] if 'file_path' in list(data.keys()) else '',
            data['trace_back'] if 'trace_back' in list(data.keys()) else '',
            data['crawler'] if 'crawler' in list(data.keys()) else '',
            )
            print('\n\n\n', self.query, '\n\n\n')
            self.is_crawled_query = """UPDATE sources set is_crawled = true where url = '{0}'""".format(data['url'].replace("'", "''"))
            print(f'*******************| UPDATE QUERY: {self.is_crawled_query} |****************************')
            print(f'*******************| SOURCE URL: {data["url"]} |****************************')
            

    def log(self):
        """Logs the query"""
        try:
            self.cursor.execute(self.query)
            self.sources_cursor.execute(self.is_crawled_query)
            self.conn.commit()
            self.sources_conn.commit()
            print("======================SOURCE UPDATED================================")
            print("*****************************END******************************")
            if self.data['status'] in ('fail','faulty'):
                self.notifier.notify({
                    "event": self.data['status'],
                    "message": {
                        "source_type": self.data['source_type'],
                        "source_url": self.data['url'],
                        **({"error_message": (self.error_message)} if self.data['status'] == 'fail' else {}),
                        **({"missing_keys": self.data['missing_keys']} if self.data['status'] == 'faulty' else {}),
                        "num_records": str(self.data['number_of_records']),
                        "status": self.data['status']
                    }
                })
            return self.cursor.rowcount
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            

    def get_crawling_calculation(self, start_date):
        """
        Get records from logs table based on given timestamps
        @:param start_date
        @:return all records
        """
        query = f"SELECT source_type, COUNT(*), SUM(number_of_records) FROM logs WHERE  created_at BETWEEN " \
                f"'{start_date}'::timestamp AND now()::timestamp GROUP BY source_type;"
        self.cursor.execute(query)
        self.conn.commit()
        records = self.cursor.fetchall()
        return records
    
    def get_error_message(self, message):
        """
        Get get error message from log_messages table
        @:param message
        @:return error_message
        """
        query = """SELECT error_message FROM log_messages WHERE error_type = '{0}'""".format(message)
        self.cursor.execute(query)
        data = self.cursor.fetchone()
        return data[0] if data is not None else message