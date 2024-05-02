
# Crawler: kyrgyzstan_official_registry

## Crawler Introduction
This Python script serves as a web scraper designed to extract information from the [Ministry of Justice of Kyrgyzstan Official Registry](https://register.minjust.gov.kg/register/SearchAction.seam?firstResult=163275&logic=and&cid=3028892). The script utilizes the `BeautifulSoup` library for HTML parsing and `requests` for making HTTP requests. Extracted data is structured into a dictionary and prepared for insertion into a database.

## Data Structure
The extracted data is organized into a dictionary with various key-value pairs. Functions such as `contains_text` and `get_value` are defined to facilitate data extraction. The structured data is then processed using the `prepare_data_object` function for database insertion.

### Sample Data Structure
```json
"data": {
    "name(state_language)": "Sample Company (на государственном языке)",
    "name": "Sample Company (на официальном языке)",
    "abbreviated_name(state_language)": "Sample Abbreviated Name (на государственном языке)",
    "abbreviated_name(official_language)": "Sample Abbreviated Name (на официальном языке)",
    "type": "Sample Organization Type",
    "foreign_enterprise": "Yes",
    "registration_number": "Sample Registration Number",
    "okpo_code": "Sample OKPO Code",
    "tax_number": "Sample Tax Number",
    "addresses_detail": [
        {
            "type": "general_address",
            "address": "Sample Address",
            "meta_detail": {
                "house_number": "Sample House Number",
                "apartment_number": "Sample Apartment Number"
            }
        }
    ],
    "additional_detail": [
        {
            "type": "state_regsitration_information",
            "data": [
                {
                    "state_registration_status": "Sample Registration Status",
                    "date": "Sample Date",
                    "initial_registration_date": "Sample Initial Registration Date"
                }
            ]
        },
        {
            "type": "founders_information",
            "data": [
                {
                    "industries": "Sample Industries",
                    "industry_code": "Sample Industry Code",
                    "founders(individual)": "Sample Individual Founders",
                    "founder(legal_entity)": "Sample Legal Entity Founders",
                    "total_founders": "Sample Total Founders"
                }
            ]
        }
    ],
    "contacts_detail": [
        {
            "type": "telephone",
            "value": "Sample Telephone Number"
        },
        {
            "type": "fax",
            "value": "Sample Fax Number"
        },
        {
            "type": "email",
            "value": "sample@example.com"
        }
    ],
    "method_of_creation": "Sample Method of Creation",
    "ownership_form": "Sample Ownership Form",
    "people_detail": [
        {
            "designation": "head_of_organization",
            "name": "Sample Head of Organization Name"
        },
        {
            "designation": "founder",
            "name": "Sample Founder Name"
        }
    ]
}
```

# Crawler Type
This is a web scraper crawler utilizing the BeautifulSoup library for HTML parsing and requests for making HTTP requests.

# Additional Dependencies
BeautifulSoup
requests

# Estimated Processing Time
The estimated processing time for the crawler is 1 week.

# How to Run the Crawler
1. Install the required dependencies: pip install -r requirements.txt
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a .env file.
4.  Navigate to the "custom_crawler/kyb/kyrgyzstan" directory using the command "cd."
5. Run the script: python3 kyrgyzstan_kyb.py