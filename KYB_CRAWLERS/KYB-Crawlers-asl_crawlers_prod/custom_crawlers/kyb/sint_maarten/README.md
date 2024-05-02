# Crawler: Sint Maarten (Dutch)

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [St. Maarten Chamber of Commerce & Industry (COCI)](https://www.chamberofcommerce.sx/services/business-registry/).The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "VINOLA N.V.",
  "type": "Limited Liability Company",
  "meta_detail": {
    "aliases": "VINOLA N.V."
  },
  "inactive_date": "2014-01-01",
  "people_detail": [
    {
      "name": "PEDRO RENE IGLESIAS",
      "designation": "Liquidator"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "Mullet Bay",
      "description": "",
      "meta_detail": {}
    }
  ],
  "dissolution_date": "2014-01-01",
  "incorporation_date": "1997-05-23",
  "registration_number": "10015"
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
5. Run the script: `python3 custom_crawlers/kyb/sint_maarten/sint_maarten.py`