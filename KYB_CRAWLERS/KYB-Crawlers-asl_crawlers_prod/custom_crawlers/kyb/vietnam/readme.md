# Crawler: Vietnam Official Registry

# Crawler Introduction
This Python script is a web scraper designed to extract information from the Companies House Vietnam official registry. The script fetches data from the specified HTML endpoint, processes the retrieved content, and inserts relevant company information into a database.

# Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as extract_company_info to parse HTML content and prepare data for insertion into the database.

``` json 
"data": {
    "name": "Sample Company",
    "registration_date": "01/01/2022",
    "registration_number": "123456",
    "type": "Private Limited Company",
    "status": "Active",
    "addresses_detail": [
        {
            "type": "head_office_address",
            "address": "123 Main Street, City, Country"
        }
    ],
    "people_detail": [
        {
            "designation": "authorized_representative",
            "name": "John Doe"
        }
    ],
    "fillings_detail": [],
    "additional_detail": []
}
```

# Crawler Type
This is a web scraper crawler that uses the requests library for making HTTP requests and BeautifulSoup for HTML parsing.

# Additional Dependencies
requests
bs4 (BeautifulSoup)
selenium (if required)

# Estimated Processing Time
The processing time for the crawler is 1 month.

# How to Run the Crawler
1. Install the required dependencies: pip install -r requirements.txt
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a .env file.
4. Navigate to the "custom_crawler/kyb/vietnam" directory using the command "cd."
5. Run the script: python3 vietnam.py