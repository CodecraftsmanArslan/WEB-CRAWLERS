# Crawler: Jamaica

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Jamaica Ministry of Industry, Investment and Commerce](https://www.orcjamaica.com/CompanySearch.aspx). The script fetches data from the HTML table by searching years (1980 - 2023) with number(0 - 100000), processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "TWINS CHARLES EBANKS",
  "country_name": "Jamaica",
  "crawler_name": "Jamaica Official Registry",
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "104 McKenzie Drive, Linstead, Jamaica"
    }
  ],
  "registration_date": "07 Jun 2016",
  "registration_number": "4551/2016"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library for search, click and scraping data from the source

## Additional Dependencies
- `selenium`
- `webdriver_manager`
- `datetime`
- `Request`

## Estimated Processing Time
The processing time for the crawler is estimated 2 months.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 ASL-Crawlers/crawlers_v2/official_registries/jamaica/jamaica.py`