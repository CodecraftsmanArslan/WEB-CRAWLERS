# Crawler: Kentucky

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Kentucky Secretary of State](https://web.sos.ky.gov/bussearchnprofile/search). The script utilizes Selenium to retrieve data from pages indexed from 0000001 to 1199997 in the search, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "C. R. BARD, INC.",
  "type": "REG - Name Registration",
  "status": "D - Deleted",
  "meta_detail": {
    "standing": "",
    "managed_by": "",
    "authority_date": "",
    "authorized_shares": "",
    "organization_date": "05-26-1995",
    "last_annual_report": "",
    "profit_or_non_profit": ""
  },
  "country_name": "Kentucky",
  "crawler_name": "custom_crawlers.kyb.kentucky.kentucky_kyb",
  "people_detail": [
    
  ],
  "fillings_detail": [
    {
      "date": "11-16-2001",
      "title": "Renewal",
      "reference": "",
      "effective_date": "11-16-2001"
    },
    {
      "date": "11-30-2000",
      "title": "Renewal",
      "reference": "",
      "effective_date": "11-30-2000"
    },
    {
      "date": "11-19-1999",
      "title": "Renewal",
      "reference": "",
      "effective_date": "11-19-1999"
    },
    {
      "date": "11-24-1998",
      "title": "Renewal",
      "reference": "",
      "effective_date": "11-24-1998"
    },
    {
      "date": "11-24-1997",
      "title": "Renewal",
      "reference": "",
      "effective_date": "11-24-1997"
    },
    {
      "date": "12-6-1996",
      "title": "Renewal",
      "reference": "",
      "effective_date": "12-6-1996"
    },
    {
      "date": "12-11-1995",
      "title": "Renewal",
      "reference": "",
      "effective_date": "12-11-1995"
    }
  ],
  "addresses_detail": [
    
  ],
  "jurisdiction_code": "NJ",
  "registration_date": "05-26-1995",
  "incorporation_date": "",
  "registration_number": "0074678"
}
```


## Crawler Type
This is a web scraper crawler that uses the `Selenium` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Selenium`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler's processing time is estimated to be approximately one month.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 crawlers_v2/official_registries/kentucky/kentucky.py`