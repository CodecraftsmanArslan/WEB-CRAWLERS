# Crawler: Belize

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Belize Companies & Corporate Affairs Registry](https://obrs.bccar.bz/bereg/searchbusinesspublic). The script fetches data from the specified API endpoint inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "PICTURE SIGNS",
  "type": "Individual",
  "status": "Active",
  "category": "Business Name",
  "country_name": "Belize",
  "crawler_name": "custom_crawlers.kyb.belize.belize_kyb_crawler",
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "Belize, Belize, city, 5764 meighan ave."
    }
  ],
  "registration_date": "2023-05-24",
  "registration_number": "000022349"
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` library for scraping.

## Additional Dependencies
- `Request`
- `pandas`

## Estimated Processing Time
The processing time for the crawler is estimated 1 day.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a `.env` file.
4. Run the script: `python3 ASL-Crawlers/custom_crawlers/kyb/balize/belize_kyb_crawler.py`