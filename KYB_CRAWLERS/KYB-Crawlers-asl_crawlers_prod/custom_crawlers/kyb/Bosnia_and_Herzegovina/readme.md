#  Crawler: bosnia_and_herzegovina_company_registry
# Crawler Introduction
This Python script is a web scraper designed to extract information from the Federal Ministry of Justice and Judicial Commission - Register of Business Entities website in Bosnia and Herzegovina. The script utilizes Selenium to navigate through the web pages, perform searches, and extract company registration details from the official registry.

# Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as prepare_data_object, generate_entity_id, and prepare_row_for_db to structure and prepare data for insertion into a database.


### Sample Data Structure

``` json
"data":{
    "registration_number": "123456",
    "name": "Sample Company",
    "type": "Type of Entity",
    "abbreviation": "ABC",
    "status": "Active",
    "unique_id": "789",
    "cutoms_number": "987",
    "addresses_detail": [
        {
            "type": "general_address",
            "address": "Sample Address"
        }
    ],
    "additional_detail": [
        {
            "type": "foreign_trade_info",
            "data": [
                {
                    "authorized_for_foreign_trade": "Yes"
                }
            ]
        },
        {
            "type": "Notes",
            "data": [
                {
                    "date": "2023-01-01",
                    "description": "Sample Description"
                }
            ]
        },
        {
            "type": "business_activity_info",
            "data": [
                {
                    "activity": "Sample Activity",
                    "activity code": "123"
                }
            ]
        },
        {
            "type": "founder_participation_in_capital",
            "data": [
                {
                    "name": "Founder Name",
                    "capital": "1000",
                    "capital_in_money": "800",
                    "capital_in_rights": "100",
                    "capital_in_assets": "100"
                }
            ]
        }
    ],
    "people_detail": [
        {
            "designation": "founder",
            "name": "Founder Name",
            "meta_detail": {
                "capital_contracted": "2000",
                "capital_paid_in": "1500"
            },
            "shares": "50"
        }
    ]
}
```
# Crawler Type
This is a Selenium-based web scraper crawler that navigates through the web pages, performs searches, and extracts company registration details.

# Additional Dependencies
selenium
beautifulsoup4


# Estimated Processing Time
The processing time for the crawler is 1 week.

# How to Run the Crawler
1. Install the required dependencies: pip install -r requirements.txt
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a .env file.
4. Navigate to the "custom_crawler/kyb/Bosnia_and_Herzegovina" directory using the command "cd."
5. Run the script: python3 bosnia.py
