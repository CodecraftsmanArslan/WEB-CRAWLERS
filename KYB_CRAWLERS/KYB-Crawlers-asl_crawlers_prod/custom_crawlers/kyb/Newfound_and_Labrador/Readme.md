
# Crawler: newfoundland_and_labrador_official_registry

# Crawler Introduction
This Python script is a web scraper designed to extract information from the Government website for the province of Newfoundland and Labrador in Canada. The script utilizes the Selenium library for browser automation, navigates through the official registry portal, and retrieves relevant information about companies and organizations in Newfoundland and Labrador. The extracted data is then processed and stored in a MongoDB collection named "reports."

# Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as prepare_data_object and prepare_row_for_db to structure and prepare data for insertion into a database.
```json
"data": {
    "name": "Sample Company Name",
    "registration_number": "123456789",
    "status": "Active",
    "dissolution_date": "",
    "registration_type": "Corporation",
    "status_info": "In Good Standing",
    "last_annual_return_filed": "2022-01-01",
    "business_type": "Sample Business Type",
    "jurisdiction_code": "NL",
    "filing_type": "Sample Filing Type",
    "min/max_directors": "Min: 1, Max: 10",
    "additional_info": "Additional information about the company.",
    "incorporation_date": "2020-01-01",
    "registration_date": "2020-01-01",
    "addresses_detail": [
        {
            "type": "mailing_address",
            "address": "123 Main St, City, Province, Country, Postal Code"
        },
        {
            "type": "registered_address",
            "address": "456 Business Blvd, City, Province, Country, Postal Code",
            "meta_detail": {
                "address_status": "Active"
            }
        },
        {
            "type": "outside_address",
            "address": "789 International St, City, Country",
            "meta_detail": {
                "address_status": "Inactive"
            }
        }
    ],
    "additional_detail": [
        {
            "type": "historical_remarks",
            "data": [
                {
                    "description": "Historical remarks about the company."
                }
            ]
        },
        {
            "type": "amalgamated_information",
            "data": [
                {
                    "amalgamated_from": "ABC Corporation",
                    "amalgamation_id": "78901234"
                },
                {
                    "amalgamated_into": "XYZ Inc.",
                    "amalgamation_id": "56789012"
                }
            ]
        }
    ],
    "people_detail": [
        {
            "designation": "director",
            "name": "John Doe"
        },
        {
            "designation": "registered_agent",
            "name": "Jane Smith",
            "address": "456 Business Blvd, City, Province, Country, Postal Code"
        }
    ],
    "previous_names_detail": [
        {
            "name": "Previous Company Name 1",
            "meta_detail": {
                "date_changed": "2021-01-01"
            }
        },
        {
            "name": "Previous Company Name 2",
            "meta_detail": {
                "date_changed": "2020-01-01"
            }
        }
    ]
}
```

# Crawler Type
This is a web scraper crawler that uses the Selenium library for browser automation.

Additional Dependencies
Selenium
BeautifulSoup
Requests

# Estimated Processing Time
The processing time for the crawler is estimated to be around 2 week.


# How to Run the Crawler
1. Install the required dependencies: pip install -r requirements.txt
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a .env file.
4. Run the script: python3 path/to/newfoundland_and_labrador_official_registry.py
5. Navigate to the "custom_crawler/kyb/Newfound_and_Labrador" directory using the command "cd."
6. Run the script: python3 newfound.py