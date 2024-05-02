# Crawler: Cayman Island

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Chamber of Commerce Cayman Islands](https://web.caymanchamber.ky/allcategories). The script use Selenium to crawl to data page, then use beautifulsoup to parse and scrape the data, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "BDO",
  "industries": "We specialise in the auditing of offshore mutual funds and captive insurance companies. Our clientele also includes banks, hotels, and many other local enterprises. We also provide accounting services and financial advice to growing businesses.",
  "meta_detail": {
    "map_url": "https://web.caymanchamber.ky/directory/results/map.aspx?listingid=1812",
    "territory": "Grand Cayman",
    "category_name": "Accounting",
    "starting_year": "2008"
  },
  "country_name": "Cayman Island",
  "crawler_name": "custom_crawlers.kyb.cayman_island.cayman.py",
  "jurisdiction": "CAYMAN ISLANDS",
  "contacts_detail": [
    {
      "type": "phone_number",
      "value": "(345) 943-8800"
    },
    {
      "type:": "fax_number",
      "value": "(345) 943-8801"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "BDO , P.O. Box 31118, CAYMAN ISLANDS"
    }
  ],
  "registration_number": "KY1-1205"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library to crawl and `beautifulsoup` to parse and scrape data.

## Additional Dependencies
- `bs4 (BeautifulSoup 4)`
- `selenium`

## Estimated Processing Time
The processing time for the crawler is estimated 3 days.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/cayman_island/cayman.py`