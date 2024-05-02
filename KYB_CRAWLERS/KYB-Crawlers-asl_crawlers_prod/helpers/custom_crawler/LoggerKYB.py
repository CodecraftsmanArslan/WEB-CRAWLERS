"""Import required libraries"""
import psycopg2
from datetime import datetime
import traceback

class Logger:
    """Logger class"""
    __HOST = None
    __PORT = None
    __USER = None
    __PASSWORD = None
    __DATABASE = None
    SERVER_IP = None

    def __init__(self, crawler_name: str, ENV: dict) -> None:
        print(f'Logger intitalized for {crawler_name}')
        """Constructor"""
        self.start_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.crawler_name = crawler_name
        self.__HOST = ENV['HOST']
        self.__PORT = ENV['PORT']
        self.__USER = ENV['USER']
        self.__PASSWORD = ENV['PASSWORD']
        self.__DATABASE = ENV['DATABASE']
        self.SERVER_IP = ENV['SERVER_IP']
        
        self.establish_connection()
        self.insert_query = """INSERT INTO crawler_stats(starts_at, ends_at, crawler_name, process_time, server_ip, total_sources, created_at, updated_at) 
                    VALUES('{0}', DEFAULT, '{1}', DEFAULT, '{2}', '{3}', '{4}', '{5}');""".format(self.start_at,self.crawler_name,  self.SERVER_IP, 0,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
        
        self.cursor.execute(self.insert_query)
        self.conn.commit()
        
        self.close_connection()

    def establish_connection(self):
        """
        Establishes a connection to the PostgreSQL database using the provided credentials.
        Initializes the database connection and cursor objects for executing queries.
        """
        self.conn = psycopg2.connect(host=self.__HOST, port=self.__PORT, user=self.__USER, password=self.__PASSWORD, dbname=self.__DATABASE)
        self.cursor = self.conn.cursor()

    def close_connection(self):
        """
        Closes the database connection and cursor objects, freeing up resources.
        """
        self.cursor.close()
        self.conn.close()

    def log(self, data: dict):
        """Logs the query"""
        try:
            self.establish_connection()
            if data is not None:
                print("****************************************************************")
                print("*****************************START******************************")
                self.data = data
                self.error_message = self.get_error_message(type(data['error']).__name__) if data['status'] == 'fail' else 'No Error'
                self.query = """INSERT INTO logs_kyb(url, source_type, number_of_records, created_at, status, error_message, 
                error_type, data_size, server_ip, content_type, status_code, trace_back, crawler) VALUES('{0}','{1}','{2}','{3}','{4}','{5}', '{6}','{7}' ,'{8}','{9}','{10}', '{11}','{12}');""".format(data['url'].replace("'", "''"), 
                data['source_type'].upper(), 
                data['number_of_records'], 
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                data['status'], self.error_message.replace("'", "''"),
                type(data['error']).__name__.replace("'", "''") if data['status'] == 'fail' else 'N/A', 
                data['data_size'], 
                self.SERVER_IP,
                data['content_type'] if 'content_type' in list(data.keys()) else 'Optional',
                data['status_code'] if 'status_code' in list(data.keys()) else '00',
                data['trace_back'] if 'trace_back' in list(data.keys()) else '',
                data['crawler'] if 'crawler' in list(data.keys()) else '',
                )
                print('\n\n\n', self.query, '\n\n\n')
                self.is_crawled_query = """UPDATE sources set is_crawled = true where url = '{0}'""".format(data['url'].replace("'", "''"))
                print(f'*******************| UPDATE QUERY: {self.is_crawled_query} |****************************')
                print(f'*******************| SOURCE URL: {data["url"]} |****************************')
                
                self.cursor.execute(self.query)
                self.conn.commit()

                self.crawler_stats_log(data)
                
                print("======================SOURCE UPDATED================================")
                print("*****************************END******************************")

                self.close_connection()
                return self.cursor.rowcount
        except Exception as e:
            tb = traceback.format_exc()
            print(e,tb)
            
    def crawler_stats_log(self, data):
        """
        Description: Logs crawler statistics data into a PostgreSQL database.
        This function establishes a connection to the specified PostgreSQL database and logs
        the provided crawler statistics data. It first inserts a new record into the 'crawler_stats' 
        table if the input data is not None. If a record with the same 'ends_at' timestamp already 
        exists, it updates the existing record with the new data.
        @param: data (dict)
        @return None
        """
        try:
            self.establish_connection()
            if data is not None:
                self.data = data
                ends_at_str = data['ends_at'] if 'ends_at' in data else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                start_at_str = self.start_at
                ends_at_date = datetime.strptime(ends_at_str, "%Y-%m-%d %H:%M:%S")
                start_at_date = datetime.strptime(start_at_str, "%Y-%m-%d %H:%M:%S")
                process_time = ends_at_date - start_at_date
                
                self.update_query = """UPDATE crawler_stats SET ends_at = '{0}', updated_at = '{1}', process_time = '{2}', total_sources = '{4}'
                       WHERE id = (SELECT id FROM crawler_stats WHERE crawler_name = '{3}' ORDER BY created_at DESC LIMIT 1);
                    """.format(ends_at_str, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), process_time, self.crawler_name, data.get('data_size',0))
                
                print('\n\n\n', self.update_query, '\n\n\n')
                self.cursor.execute(self.update_query)
                self.conn.commit()

                self.close_connection()
                return self.cursor.rowcount
        except Exception as e:
            tb = traceback.format_exc()
            print(e,tb)

    
    def get_error_message(self, message):
            """
            Get get error message from log_messages table
            @:param message
            @:return error_message
            """
            self.establish_connection()
            query = """SELECT error_message FROM log_messages WHERE error_type = '{0}'""".format(message)
            self.cursor.execute(query)
            data = self.cursor.fetchone()
            return data[0] if data is not None else message