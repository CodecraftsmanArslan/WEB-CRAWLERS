import psycopg2
import json, os
from dotenv import load_dotenv
load_dotenv()
def remove_na_and_empty_addresses():
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host=os.getenv('SEARCH_DB_HOST'),
            database=os.getenv('SEARCH_DB_NAME'),
            user=os.getenv('SEARCH_DB_USERNAME'),
            password=os.getenv('SEARCH_DB_PASSWORD'),
            port=os.getenv('SEARCH_DB_PORT')
        )
        # Create a cursor to perform database operations
        cursor = connection.cursor()
        # SQL query to fetch the data from the 'reports' table
        select_query = "SELECT id, data FROM reports where countries='[\"Belarus\"]' and categories = '[\"Official Registry\"]';"
        # Execute the query
        cursor.execute(select_query)
        # Fetch all the rows from the 'reports' table
        rows = cursor.fetchall()
        for row in rows:
            id = row[0]
            data = row[1]
            # Remove and return the specified dictionary
            removed_dict = None
            updated_additional_detail = []

            for item in data["additional_detail"]:
                if item['data'][0] == {}:
                    removed_dict = item
                else:
                    updated_additional_detail.append(item)

            # Update the data_dict
            data["additional_detail"] = updated_additional_detail

    # Update the row in the 'reports' table with the modified data
            update_query = "UPDATE reports SET data = %s WHERE id = %s"
            cursor.execute(update_query, (json.dumps(data), id))
        # Commit the changes to the database
        connection.commit()
        print("Data has been update")
    except Exception as error:
        print(error)
    finally:
        # Close the database connection
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed.")
# Call the function to remove 'N/A' and empty addresses from 'addresses_detail'
remove_na_and_empty_addresses()