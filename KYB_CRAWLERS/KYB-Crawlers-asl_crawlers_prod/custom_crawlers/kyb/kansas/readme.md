# Crawler: kansas_secretary_of_state

# Crawler Introduction
This Python script is a web scraper designed to extract information from the Kansas Secretary of State Business Services website. The script navigates through the specified HTML elements using Selenium, fetches data, and processes it. The extracted information is then inserted into a database, and relevant details are logged.

# Data Structure

The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as get_paras, prepare_data_object, and prepare_row_for_db to structure and prepare data for insertion into a database.

# Sample Data Structure
```json
"data":{
    "name": "Sample Company",
    "registration_number": "123456",
    "addresses_detail": [
        {
            "type": "mailing_address",
            "address": "123 Main St, City, State, 12345"
        }
    ],
    "type": "Corporation",
    "registration_date": "2023-01-01",
    "jurisdiction": "Kansas",
    "status": "Active",
    "people_detail": [
        {
            "designation": "registered_agent",
            "name": "John Doe",
            "address": "456 Agent St, City, State, 56789"
        }
    ],
    "additional_detail": [
        {
            "type": "type_annual_reports_info",
            "data": [
                {
                    "note": "Annual reports information",
                    "tax_closing_month": "December",
                    "last_annual_report_on_file": "2022-12-31",
                    "next_annual_report_due": "2023-12-31",
                    "forfeiture_date": "2024-01-01"
                }
            ]
        }
    ],
    "fillings_detail": [
        {
            "date": "2023-01-15",
            "filing_type": "Annual Report",
            "title": "Annual Report"
        }
    ],
    "previous_name_detail": [
        {
            "name": "Previous Company Name"
        }
    ]
}
```

# Crawler Type
This is a Selenium-based web scraper crawler that navigates through HTML elements to extract data.

# Additional Dependencies
selenium
beautifulsoup4

# Estimated Processing Time
The processing time for the crawler is 2 week.

# How to Run the Crawler
1. Install the required dependencies: pip install -r requirements.txt
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a .env file.
4. Navigate to the "custom_crawler/kyb/kansas" directory using the command "cd."
5. Run the script: python3 kansas.py
