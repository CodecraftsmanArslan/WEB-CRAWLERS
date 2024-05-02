# Crawler: New Jersey

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [New Jersey Portal](https://www.njportal.com/DOR/BusinessNameSearch/Search/EntityId). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "SCHWENDT & KEEPHART-CERTIFIED PUBLIC ACCOUNTANTS-A PROFESSIONAL ASSOC",
  "type": "PA",
  "status": "",
  "meta_detail": {
    "city": "LAWRENCEVILLE"
  },
  "country_name": "New Jersey",
  "crawler_name": "custom_crawlers.kyb.new_jersey.new_jersey_kyb",
  "incorporation_date": "7-1-1975",
  "registration_number": "0100000002"
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
5. Run the script: `python3 custom_crawlers/kyb/new_jersey/new_jersey_kyb.py`