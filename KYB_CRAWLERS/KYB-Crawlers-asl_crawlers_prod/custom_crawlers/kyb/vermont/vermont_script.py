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
        select_query = "SELECT id, data FROM reports where countries='[\"Vermont\"]' and data::text ilike '%none%';"
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
                        has_empty_value = False
                        for inner_key, inner_value in entry.items():
                            cleaned_inner_value = inner_value.replace("null", " ").replace("  ", "").replace("None", " ").replace("none", " ").replace('NONE', ' ').replace('noneO', "").strip() if isinstance(inner_value, str) else inner_value
                            if cleaned_inner_value == "":
                                has_empty_value = True
                            cleaned_entry[inner_key] = cleaned_inner_value
                        if not has_empty_value:
                            cleaned_value.append(cleaned_entry)
                    if cleaned_value:  # Only add non-empty lists
                        cleaned_data[key] = cleaned_value
                elif key == 'people_detail':
                    cleaned_value = []
                    for entry in value:
                        cleaned_entry = {}
                        has_empty_value = False
                        for inner_key, inner_value in entry.items():
                            cleaned_inner_value = inner_value.replace("null", " ").replace("  ", "").replace("None", " ").replace("none", " ").replace('NONE', ' ').replace('noneO', "").strip() if isinstance(inner_value, str) else inner_value
                            if cleaned_inner_value == "":
                                has_empty_value = True
                            cleaned_entry[inner_key] = cleaned_inner_value
                        if not has_empty_value:
                            cleaned_value.append(cleaned_entry)
                    if cleaned_value:  # Only add non-empty lists
                        cleaned_data[key] = cleaned_value
                elif key == 'meta_detail':
                    cleaned_value = {}
                    for inner_key, inner_value in value.items():
                        cleaned_inner_value = inner_value.replace("null", " ").replace("  ", "").replace("None", " ").replace("none", " ").replace('NONE', ' ').replace('noneO', "").strip() if isinstance(inner_value, str) else inner_value
                        cleaned_value[inner_key] = cleaned_inner_value
                    if cleaned_value:  # Only add non-empty dictionaries
                        cleaned_data[key] = cleaned_value
                else:
                    if isinstance(value, str):
                        cleaned_value = value.replace("null", " ").replace("  ", "").replace("None", " ").replace("none", " ").replace('NONE', ' ').replace('noneO', "").strip()
                        if cleaned_value:  # Only add non-empty strings
                            cleaned_data[key] = cleaned_value
                    else:
                        cleaned_data[key] = value

    # Update the row in the 'reports' table with the modified data
            update_query = "UPDATE reports SET data = %s WHERE id = %s"
            cursor.execute(update_query, (json.dumps(cleaned_data), id))
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