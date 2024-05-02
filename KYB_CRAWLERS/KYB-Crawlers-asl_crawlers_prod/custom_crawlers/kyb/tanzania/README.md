# Crawler: Tanzania

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Business Registrations and Licensing Agency (BRELA)](https://ors.brela.go.tz/orsreg/searchbusinesspublic). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "OMOYO REAL ESTATE",
  "status": "Registered",
  "country_name": "Tanzania",
  "crawler_name": "custom_crawlers.kyb.tanzania.tanzania_kyb.py",
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "Dar Es Salaam, Kinondoni, Kawe, 14121, MBEZI BEACH OPPOSITE TO MBEZI BEACH HIGH SCHOOL"
    }
  ],
  "registration_number": "523036"
}
```


## Crawler Type
This is a web scraper crawler that uses the `Request` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Request`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler's processing time is estimated to be approximately one week.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/tanzania/tanzania_kyb.py`