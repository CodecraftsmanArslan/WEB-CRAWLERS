# Crawler: kosovo_business_registry

# Crawler Introduction
This Python script is a web scraper designed to extract information from the Agjencia e Regjistrimit të Bizneseve Kosovo (ARBK) website. The script iterates through specific ranges of business IDs, collects data from corresponding URLs, and processes the extracted information. The data is then inserted into a database, and relevant details are logged.

# Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as generate_urls, prepare_data_object, and prepare_row_for_db to structure and prepare data for insertion into a database.

# Sample Data Structure
```json
"data":{
    "name": "Sample Business",
    "aliases": "Alias1, Alias2",
    "type": "Type of Business",
    "registration_number": "123456",
    "business_number": "789012",
    "fiscal_number": "345678",
    "tax_number": "901234",
    "number_of_employees": "50",
    "registration_date": "2023-01-01",
    "jurisdiction": "Municipality",
    "addresses_detail": [
        {
            "type": "general_address",
            "address": "123 Main St, City, Country"
        }
    ],
    "contacts_detail": [
        {
            "type": "telephone_number",
            "value": "+123456789"
        },
        {
            "type": "email",
            "value": "info@example.com"
        }
    ],
    "status": "Active",
    "capital": "50000 €",
    "tax_authority_status": "Tax Compliant",
    "additional_detail": [
        {
            "type": "activity_information",
            "data": [
                {
                    "activity_code": "123",
                    "name": "Activity 1",
                    "activity_type": "Type 1"
                },
                {
                    "activity_code": "456",
                    "name": "Activity 2",
                    "activity_type": "Type 2"
                }
            ]
        }
    ],
    "people_detail": [
        {
            "name": "John Doe",
            "designation": "Director",
            "meta_detail": {
                "power": "50%"
            }
        },
        {
            "name": "Jane Doe",
            "designation": "owner/shareholder",
            "meta_detail": {
                "capital_€": "25000 €",
                "capital_%": "50%"
            }
        }
    ]
}

```

# Crawler Type
This is a BeautifulSoup-based web scraper crawler that iterates through specific business ID ranges to extract data.

# Additional Dependencies
requests
beautifulsoup4

# Estimated Processing Time
The processing time for the crawler is 1 month.

# How to Run the Crawler
1. Install the required dependencies: pip install -r requirements.txt
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a .env file.
4. Navigate to the "custom_crawler/kyb/kosovo" directory using the command "cd."
5. Run the script: python3 kosovo.py