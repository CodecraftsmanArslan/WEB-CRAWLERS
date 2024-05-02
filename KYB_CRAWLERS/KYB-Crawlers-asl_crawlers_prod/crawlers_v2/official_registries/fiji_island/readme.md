# Crawler: Fiji Islands

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Fiji Islands Ministry of Communications](https://roc.digital.gov.fj/BuyInformation/Search). The script fetches data from the HTML table by searching Alphabets(r) and digit (0 to 9), processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "MELROSE APARTMENT",
  "type": "BUSINESS NAME",
  "status": "CEASED",
  "country_name": "Fiji Island",
  "crawler_name": "Fiji Island Official Registry",
  "registration_number": "RCBS2017F0048"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library for scraping and `multiprocessing` for multiple processors.

## Additional Dependencies
- `selenium`
- `webdriver_manager`
- `datetime`

## Estimated Processing Time
The processing time for the crawler is estimated 4 days.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 ASL-Crawlers/crawlers_v2/official_registries/fiji_island/fiji.py`