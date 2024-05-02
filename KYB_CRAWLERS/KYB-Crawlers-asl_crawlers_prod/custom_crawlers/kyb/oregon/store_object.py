import psycopg2
import json, os

db_type = "SEARCH"
# Assuming you have the necessary PostgreSQL connection details
db_connection = {
        'host': os.getenv(db_type+'_DB_HOST'),
        'port': os.getenv(db_type+'_DB_PORT'),
        'user': os.getenv(db_type+'_DB_USERNAME'),
        'password': os.getenv(db_type+'_DB_PASSWORD'),
        'dbname': os.getenv(db_type+'_DB_NAME')
    }

def storeRecord(record_for_db):
    conn = psycopg2.connect(**db_connection)
    cursor = conn.cursor()

    entity_id = record_for_db[0]
    new_data = json.loads(record_for_db[7])
    select_query = "SELECT data FROM reports WHERE entity_id = %s"
    cursor.execute(select_query, (entity_id,))
    existing_data = cursor.fetchone()
    if existing_data:
        print(existing_data)
        existing_data = existing_data[0]
        if existing_data != new_data:
            # Extract the existing names from the existing_data
            existing_names = {entry["name"] for entry in existing_data["people_detail"]}

            # Extend the existing_data list with new_data entries that don't already exist
            for entry in new_data["people_detail"]:
                if entry["name"] not in existing_names:
                    existing_data["people_detail"].append(entry)
                    existing_names.add(entry["name"])
            if len(existing_data["addresses_detail"]) == 0 and len(new_data["addresses_detail"]) > 0:
                existing_data["addresses_detail"].append({
                    "address": new_data["addresses_detail"][0]["address"],
                    "type": "general_address"
                })
            update_query = "UPDATE reports SET data = %s WHERE entity_id = %s"
            cursor.execute(update_query, (json.dumps(existing_data), entity_id))
            conn.commit()
            print("Data merged successfully.")
    else: 
        insert_query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
        UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                            WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)

        cursor.execute(insert_query)
        conn.commit()
        print("New record inserted.")

    cursor.close()
    conn.close()
