"""Import required libraries"""
import os
import psycopg2
import sys
from dotenv import load_dotenv

load_dotenv()


class PostgresConnection:
    _instance = None
    _connections = {}
    _connections_list = ["SEARCH", "SOURCES", "WIKI"]

    def __new__(cls):
        if cls._instance is None:
            # Create a new PostgreSQL connection instance
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_connection(self, db_type):
        if db_type in self._connections_list:
            if db_type in self._connections:
                return self._connections[db_type]

            conn = psycopg2.connect(host=os.getenv(db_type+'_DB_HOST'), port=os.getenv(db_type+'_DB_PORT'), user=os.getenv(
                db_type+'_DB_USERNAME'), password=os.getenv(db_type+'_DB_PASSWORD'), dbname=os.getenv(db_type+'_DB_NAME'))
            self._connections[db_type] = conn
            return conn
        else:
            print('Invalid connection type provided')
            sys.exit()
