
# Crawler: bermuda_company_registry

# Crawler Introduction
This Python script is a web scraper designed to extract information from the Bermuda Registrar of Companies website. The script uses Selenium with undetected_chromedriver to navigate through the web pages, perform searches, and extract company registration details from the official registry. The script is designed to handle CAPTCHAs during the crawling process.

# Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as prepare_data_object, generate_entity_id, and prepare_row_for_db to structure and prepare data for insertion into a database.


### Sample Data Structure

```json
"data":{
    "registration_number": "123456",
    "name": "Sample Company",
    "type": "Type of Entity",
    "registration_date": "2023-01-01"
}
```

# Crawler Type
This is a Selenium-based web scraper crawler that navigates through the web pages, performs searches, and extracts company registration details.

# Additional Dependencies
selenium
requests
beautifulsoup4
undetected-chromedriver

# Estimated Processing Time
The processing time for the crawler is 1 week.

# How to Run the Crawler
1. Install the required dependencies: pip install -r requirements.txt
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a .env file.
4. Navigate to the "custom_crawler/kyb/Bermuda" directory using the command "cd."
5. Run the script: python3 Bermuda.py
