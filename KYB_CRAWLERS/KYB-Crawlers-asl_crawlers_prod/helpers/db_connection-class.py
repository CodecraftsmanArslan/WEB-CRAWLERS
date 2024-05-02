import os
import psycopg2
import sys
from dotenv import load_dotenv

load_dotenv()


class PostgresConnection:
    def __init__(self, db_type):
        self.db_type = db_type
        self.connection = None

    def get_connection(self):
        if self.connection is not None:
            return self.connection

        if self.db_type in ["SEARCH", "SOURCES", "WIKI"]:
            self.connection = psycopg2.connect(
                host=os.getenv(self.db_type+'_DB_HOST'),
                port=os.getenv(self.db_type+'_DB_PORT'),
                user=os.getenv(self.db_type+'_DB_USERNAME'),
                password=os.getenv(self.db_type+'_DB_PASSWORD'),
                dbname=os.getenv(self.db_type+'_DB_NAME')
            )
            return self.connection
        else:
            print('Invalid connection type provided')
            sys.exit()
