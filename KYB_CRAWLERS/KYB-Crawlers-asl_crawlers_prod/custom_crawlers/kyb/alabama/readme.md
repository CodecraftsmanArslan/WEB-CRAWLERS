# Crawler: Alabama

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Alabama Secretary of State](https://arc-sos.state.al.us/cgi/corpdetail.mbr/detail?corp=000000001). The script fetches data from the specified API endpoint by adding page number (000000001 - 002900267), processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "A Bonding, Inc.",
  "type": "Domestic Corporation",
  "status": "Exists",
  "industries": "BAIL BONDS, ETC",
  "meta_detail": {
    "place_of_formation": "Jefferson County"
  },
  "country_name": "Alabama",
  "crawler_name": "Alabama Official Registry",
  "people_detail": [
    {
      "name": "JOHNSTON, J REESE JR",
      "designation": "incorporator",
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "BIRMINGHAM, AL"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "capital_paid_in": "$1,000",
          "authorized_share_capital": "$1,000"
        }
      ],
      "type": "capital_information"
    }
  ],
  "incorporation_date": "01-04-1966",
  "registration_number": "000 - 000 - 001",
  "previous_names_detail": [
    {
      "name": "H & M Bonding Company, Inc.",
      "update_date": "09/14/1970"
    }
  ]
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Request`
- `bs4`

## Estimated Processing Time
The processing time for the crawler is estimated 1 month.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a `.env` file.
4. Run the script: `python3 ASL-Crawlers/custom_crawlers/kyb/alabama/alabama.py`