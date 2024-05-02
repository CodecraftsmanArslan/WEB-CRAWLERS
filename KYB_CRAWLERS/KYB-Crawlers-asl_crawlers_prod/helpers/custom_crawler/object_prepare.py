import re
def truncate_value(value, replace_values):
    """
    Description: Recursively removes leading and trailing spaces from a string, and replaces specific values with an empty string.
    @param:
    - value (str, list, dict, or any): The input value to be truncated or processed.
    - replace_values (list): A list of values to be replaced with an empty string.
    @return:
    - str, list, dict, or any: Processed value with leading/trailing spaces removed and specific values replaced with an empty string.
    """
    if isinstance(value, str):
        value = value.strip()  # Remove leading and trailing spaces
        if value in replace_values:
            return ""
        return value
    elif isinstance(value, list):
        return [truncate_value(item, replace_values) for item in value]
    elif isinstance(value, dict):
        return {key: truncate_value(val, replace_values) for key, val in value.items()}
    else:
        return value

def create_data_object(field_values,crawler_name):
    """
    Description: Creates a data object for processing and insertion into the database, handling specific replacements and filtering empty fields.
    @param:
    - field_values (dict): Dictionary containing field values to be processed.
    - crawler_name (str): Name of the crawler generating the data.
    @return:
    - dict: Processed data object ready for database insertion.
    """
    replace_values = ["--None--","#NONE","NONE","#NULL","NULL","None","None,","#Null","Null","null","null,","none","none,","#none","-","/","N/A","None","-/","[Not Provided]","UnClassified",]  
    field_values = truncate_value(field_values, replace_values)
    data_obj = {
        "name": field_values.get("name", ""),
        "country_name": field_values.get("country_name", ""),
        "crawler_name": crawler_name,
        "countries": field_values.get("countries", ""),
        "registration_number": field_values.get("registration_number", ""),
        "registration_date": field_values.get("registration_date", ""),
        "status": field_values.get("status", ""),
        "type": field_values.get("type", ""),
        "incorporation_date": field_values.get("incorporation_date", ""),
        "jurisdiction": field_values.get("jurisdiction", ""),
        "jurisdiction_code": field_values.get("jurisdiction_code", ""),
        "industries": field_values.get("industries", ""),
        "tax_number": field_values.get("tax_number", ""),
        "dissolution_date": field_values.get("dissolution_date", ""),
        "inactive_date": field_values.get("inactive_date", ""),
        "meta_detail": {},
        "contacts_detail": field_values.get("contacts_detail", []),
        "previous_names_detail": field_values.get("previous_names_detail", []),
        "fillings_detail": field_values.get("fillings_detail", []),
        "addresses_detail": field_values.get("addresses_detail", []),
        "announcements_detail": field_values.get("announcements_detail", []),
        "people_detail": field_values.get("people_detail", []),
        "additional_detail": field_values.get("additional_detail", [])
    }
    
    for key in field_values.keys():
        if key not in data_obj: # If the key is not present in data_obj, insert it with its value in the meta_detail dictionary
            data_obj["meta_detail"][key] = field_values[key] 
    fields_to_process = ["people_detail", "announcements_detail", "addresses_detail", "fillings_detail", "previous_names_detail"]
    for field in fields_to_process:
        if field in data_obj:
            details = data_obj[field]
            updated_details = []
            for detail in details:
                if not detail or all(value == "" for value in detail.values()):
                    continue
                keys_to_remove = [key for key, value in detail.items() if key != "type" and value == ""]
                if "meta_detail" in detail:
                    meta_detail = detail["meta_detail"]
                    keys_to_remove.extend(key for key, value in meta_detail.items() if value == "")
                    if not meta_detail or all(value == "" for value in meta_detail.values()):
                        del detail["meta_detail"]
                updated_detail = {key: detail[key] for key in detail if key not in keys_to_remove}
                updated_details.append(updated_detail)
            data_obj[field] = [detail for detail in updated_details if detail]
            if not data_obj[field]:
                del data_obj[field]
    if "addresses_detail" in data_obj:
        addresses_detail = data_obj["addresses_detail"]
        updated_addresses_detail = []
        for detail in addresses_detail:
            if len(detail) == 1 and "type" in detail:
                continue
            updated_detail = truncate_value(detail, replace_values)
            updated_addresses_detail.append(updated_detail)
        data_obj["addresses_detail"] = updated_addresses_detail
    if "previous_names_detail" in data_obj:
        previous_names_detail = data_obj["previous_names_detail"]
        if all(not detail or all(value == "" for value in detail.values()) for detail in previous_names_detail):
            del data_obj["previous_names_detail"]
    if "additional_detail" in data_obj:
        additional_details = data_obj["additional_detail"]
        updated_additional_details = []
        for detail in additional_details:
            activities = detail.get("data", [])
            updated_activities = []
            for activity in activities:
                updated_activity = {key: value for key, value in activity.items() if value != ""}
                updated_activities.append(updated_activity)
            if updated_activities:
                detail["data"] = updated_activities
                updated_additional_details.append(detail)
        data_obj["additional_detail"] = updated_additional_details
    if "contacts_detail" in data_obj:
        contacts = data_obj["contacts_detail"]
        data_obj["contacts_detail"] = [contact for contact in contacts if contact.get("value")]
    data_obj = {key: value for key, value in data_obj.items() if value} # Remove empty fields from data_obj and meta_detail
    if "meta_detail" in data_obj:
        data_obj["meta_detail"] = {key: value for key, value in data_obj["meta_detail"].items() if value} # Filter the items to remove any key-value pairs with empty values
    if "meta_detail" in data_obj and not data_obj["meta_detail"]: # Check if "meta_detail" is empty, and if so, remove it from "data_obj"
        del data_obj["meta_detail"]
    fields_to_check = [
    "tax_number", "inactive_date", "dissolution_date",
    "industries", "jurisdiction_code", "jurisdiction", "incorporation_date",
    "type", "status", "registration_date", "registration_number", "countries", "country_name", "name"]
    for field in fields_to_check:
        if field in field_values:
            data_obj[field] = field_values[field]
        else:
            data_obj.pop(field, None)
    return data_obj
