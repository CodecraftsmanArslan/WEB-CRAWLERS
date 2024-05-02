# Crawler: Australia

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Australian Securities and Investments Commission (ASIC)](https://data.gov.au/data/dataset/7b8656f9-606d-4337-af29-66b89b2eeefb/resource/5c3914e6-413e-4a2c-b890-bf8efe3eabf2/download/company_202303.csv). The script fetches data from CSV and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
    "name": "ROWAN KIMPTON & ASSOCIATES PTY. LTD.",
    "type": "APTY",
    "status": "REGD",
    "meta_detail": {
        "aliases": "",
        "category": "LMSH",
        "sub_category": "PROP",
        "tax_id_number": "76007239492",
        "previous_state": "VIC",
        "current_name_indicator": "Y",
        "state_registration_number": "C0325451G"
    },
    "country_name": "Australia",
    "crawler_name": "custom_crawlers.kyb.australia_kyb_crawler",
    "registration_date": "06/06/1989",
    "registration_number": "007239492"
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` and `pandas`libraries for scraping.

## Additional Dependencies
- `Request`
- `pandas`

## Estimated Processing Time
The processing time for the crawler is estimated 1 day.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt` 
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a `.env` file.
4. Run the script: `python3 ASL-Crawlers/custom_crawlers/kyb/australia/australia_kyb_crawler.py`