# Crawler: alberta_business_registry

# Crawler Introduction
This Python script is a web scraper designed to extract information from the Government of Alberta website. The script uses Selenium and BeautifulSoup to navigate through the web pages, extract relevant information, and store it in a database. The crawler focuses on obtaining business licensing data from the official registry.

# Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as prepare_data_object, generate_entity_id, and prepare_row_for_db to structure and prepare data for insertion into a database.

### Sample Data Structure

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
        },
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
This is a Selenium-based web scraper crawler that navigates through the web pages to extract business licensing data.

# Additional Dependencies
selenium
requests
beautifulsoup4


# Estimated Processing Time
The processing time for the crawler is 2 week.

# How to Run the Crawler
1. Install the required dependencies: pip install -r requirements.txt
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a .env file.
4.  Navigate to the "custom_crawler/kyb/alberta" directory using the command "cd."
5. Run the script: python3 alberta.py