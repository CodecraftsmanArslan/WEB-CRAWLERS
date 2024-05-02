# Crawler: Hong Kong S.A.R.

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Hong Kong S.A.R. Integrated Companies Registry Information System](https://www.icris.cr.gov.hk/csci/cps_criteria.jsp). The script fetches data from the HTML table by searching CR Number (1 to 3289123 ), processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "BRITISH TRADERS' INSURANCE COMPANY LIMITED -THE-",
  "type": "Public company limited by shares",
  "status": "Dissolved",
  "meta_detail": {
    "remarks": "Dissolved by Members' Voluntary Winding Up",
    "winding_up_mode": "Members' Voluntary Winding Up",
    "register_of_charges": "Unavailable"
  },
  "country_name": "Hong Kong S.A.R.",
  "crawler_name": "Hong Kong S.A.R. Official Registry",
  "dissolution_date": "15-JAN-2003",
  "registration_date": "",
  "incorporation_date": "12-OCT-1865",
  "registration_number": "0000001",
  "previous_names_detail": [
    {
      "name": "BRITISH TRADERS' INSURANCE COMPANY LIMITED -THE-",
      "update_date": "12-OCT-1865"
    }
  ]
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library for loging, the `Request` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `selenium`
- `webdriver_manager`
- `datetime`
- `Request`
- `bs4`
- `nopecha`

## Estimated Processing Time
The processing time for the crawler is estimated 1 month.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Set up Nopecha API KEY in `.env` file.
6. Run the script: `python3 ASL-Crawlers/crawlers_v2/official_registries/hong_kong/hong_kong.py`