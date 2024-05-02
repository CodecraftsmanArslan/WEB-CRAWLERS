import psycopg2, os, json
from dotenv import load_dotenv

def remove_na_and_empty_addresses():
    try:
        # Load environment variables
        load_dotenv()

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
        select_query = "SELECT id, data FROM reports WHERE countries='[\"Armenia\"]' AND data::text ILIKE '%none%';"

        # Execute the query
        cursor.execute(select_query)

        # Fetch all the rows from the 'reports' table
        rows = cursor.fetchall()

        for row in rows:
            id = row[0]
            data = row[1]
            cleaned_data = {}

            for key, value in data.items():
                if key == 'addresses_detail':
                    cleaned_value = []

                    for entry in value:
                        cleaned_entry = {}

                        # Use a dictionary comprehension to replace "none" with ""
                        cleaned_entry = {inner_key: inner_value.replace("none,", "").replace("none", "").replace("  ", "") if inner_key == 'address' and isinstance(inner_value, str) else inner_value
                                        for inner_key, inner_value in entry.items()}

                        cleaned_value.append(cleaned_entry)

                    if cleaned_value:
                        cleaned_data[key] = cleaned_value
                else:
                    cleaned_data[key] = value

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

# Call the function to replace "none" with "" in the 'address' field
remove_na_and_empty_addresses()

