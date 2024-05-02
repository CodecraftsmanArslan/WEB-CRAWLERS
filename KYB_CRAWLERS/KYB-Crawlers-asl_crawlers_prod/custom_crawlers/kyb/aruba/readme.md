# Crawler: Aruba

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Chamber of Commerce](https://my.arubachamber.com/register/zoeken?q=%5Bobject%20KeyboardEvent%5D). The script fetches data from the specified API endpoint and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "SUTOGETHER",
  "status": "ACTIEF",
  "industries": "S96020 - HAAR- EN SCHOONHEIDSVERZORGING",
  "meta_detail": {
    "aliases": "SUTOGETHER VBA",
    "status_date": "2023-05-31T18:02:07.3309131Z"
  },
  "country_name": "Aruba",
  "crawler_name": "custom_crawlers.kyb.aruba.aruba.py",
  "jurisdiction": "Aruba",
  "people_detail": [
    {
      "name": "FRANK JUDELL",
      "designation": "DIRECTEUR",
      "meta_detail": {
        "title": "",
        "authority": "BEPERKT",
        "birthplace": ""
      },
      "nationality": "",
      "appointment_date": "2023-05-29"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "53045 PIKININI CASHERO"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "Posted": "1500.0",
          "Social": "0.0",
          "end_date": "",
          "Deposited": "0.0",
          "start_date": ""
        }
      ],
      "type": "capital_information"
    }
  ],
  "incorporation_date": "2023-05-29",
  "registration_number": "55683"
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
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 ASL-Crawlers/custom_crawlers/kyb/aruba/aruba.py`