import psycopg2
import json
import os
from dotenv import load_dotenv

load_dotenv()

def update_data_column():
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
        select_query = """
        SELECT id, data
        FROM reports
        WHERE countries = '["Myanmar"]'
        AND source ILIKE 'Directorate of Investment Company Administration (DICA) in Myanmar';
        """
        # Execute the query
        cursor.execute(select_query)
        # Fetch all the rows from the 'reports' table
        rows = cursor.fetchall()

        for row in rows:
            id, data = row
            cleaned_data = data

            if 'name' in cleaned_data and 'previous_names_detail' in cleaned_data:
                if cleaned_data['name'] == cleaned_data.get('previous_names_detail', [{}])[0].get('name'):
                    cleaned_data.pop('previous_names_detail')

            # Update the row in the 'reports' table with the modified data
            update_query = "UPDATE reports SET data = %s WHERE id = %s"
            cursor.execute(update_query, (json.dumps(cleaned_data), id))

        # Commit the changes to the database
        connection.commit()
        print("Data has been updated")

    except Exception as error:
        print(error)

    finally:
        # Close the database connection
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed.")

# Call the function to remove 'previous_names_detail' if 'name' matches
update_data_column()
