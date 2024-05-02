# Crawler: Singapore

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Open Data Portal of the Singapore Government](https://beta.data.gov.sg/datasets). The script downloads a zip file, loads a CSV file, and retrieves data from the CSV file and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "101 PETS",
  "type": "BN",
  "status": "D",
  "meta_detail": {
    "issuance_agency_id": "ACRA"
  },
  "country_name": "Singapore",
  "crawler_name": "custom_crawlers.kyb.singapore.singapore_kyb_crawler",
  "addresses_detail": [
    {
      "type": "registration_address",
      "address": "SUNGEI TENGAH ROAD, 699008",
      "description": "",
      "meta_detail": {
        "reg_postal_code": "699008",
        "reg_street_name": "SUNGEI TENGAH ROAD"
      }
    }
  ],
  "dissolution_date": "",
  "registration_date": "2016-05-03",
  "registration_number": "",
  "company_fetched_data_status": "resolved"
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` library for download zip and `Panda` for CSV read.

## Additional Dependencies
- `Request`
- `Panda`

## Estimated Processing Time
The crawler's processing time is estimated to be approximately one week.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/singapore/singapore_kyb_crawler.py`