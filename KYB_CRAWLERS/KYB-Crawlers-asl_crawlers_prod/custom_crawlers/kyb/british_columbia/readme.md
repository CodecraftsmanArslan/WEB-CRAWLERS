# Crawler: British Columbia

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [OrgBook British Columbia](ttps://www.orgbook.gov.bc.ca/search?q=%2a&category%3Aentity_type=&credential_type_id=&inactive=&page=1). The script fetches data from the specified API endpoint, inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
    "name": "NORTH PEACE EAGLES LADIES HOCKEY ASSOCIATION",
    "type": "Society",
    "status": "Active",
    "meta_detail": {
        "legal_form": "Society",
        "business_number": "767815012",
        "incorporated_in": "British Columbia",
        "incorporation_number": "S0077860"
    },
    "country_name": "British Columbia",
    "crawler_name": "custom_crawlers.kyb.british_columbia_crawler",
    "registration_date": "2023-03-06",
    "registration_number": "767815012",
    "company_fetched_data_status": ""
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` library for scraping.

## Additional Dependencies
- `Request`

## Estimated Processing Time
The processing time for the crawler is estimated 1 day.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a `.env` file.
4. Run the script: `python3 ASL-Crawlers/custom_crawlers/kyb/british_columbia/british_columbia_crawler.py`