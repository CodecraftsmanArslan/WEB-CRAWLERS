# Crawler: Austria

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Austrian Business Register](https://firmenbuch.at/Sitemap/). The script fetches data from CSV and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "000fff.studio OG",
  "meta_detail": {
    "incorporated_in": "Austria"
  },
  "country_name": "Austria",
  "crawler_name": "custom_crawlers.kyb.austria_br_crawler",
  "registration_number": "506315g",
  "addresses_detail":[
    {
        "type":"general_address",
        "address": "Urbangasse 8/Souterrain, 1170 Wien",
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
The processing time for the crawler is estimated 1 day.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a `.env` file.
4. Run the script: `python3 ASL-Crawlers/custom_crawlers/kyb/austria_br/austria_br_crawler.py`