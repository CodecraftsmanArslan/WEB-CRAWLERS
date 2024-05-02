# Crawler: Virgin Island (US)

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Virgin Islands Department of Licensing and Consumer Affairs (DLCA)](https://secure.dlca.vi.gov/license/Asps/Search/License_search.aspx). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "PAIN MEDICINE VI, PLLC",
  "industries": "Office of Health Practitioners",
  "meta_detail": {
    "aliases": "PAIN MEDICINE VI",
    "license_number": "2-49797-1L",
    "expiration_date": "01-31-2024"
  },
  "country_name": "Virgin Island (US)",
  "crawler_name": "custom_crawlers.kyb.virgin_island.virgin_island_kyb.py",
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "BEESTON HILL MEDICAL CENTER 1AA BEESTON HILL  SUITE 4  St. Croix"
    }
  ],
  "registration_number": ""
}
```


## Crawler Type
This is a web scraper crawler that uses the `Request` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Request`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler is expected to complete processing in around two days.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/virgin_island/virgin_island_kyb.py`