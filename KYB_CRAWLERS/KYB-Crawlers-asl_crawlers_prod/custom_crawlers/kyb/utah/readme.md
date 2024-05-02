# Crawler: Utah

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Utah.gov](https://secure.utah.gov/bes/index.html). The script use selenium to get HTML and beautifulsoup to parse and extract data, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "ALTA RE PARTNERS LLC",
  "type": "LLC - Domestic",
  "status": "Active",
  "meta_detail": {
    "next_renewal": "08-31-2023",
    "address_detail": [
      {
        "type": "general_address",
        "address": "3206 s Sunset Hollow Drive, Bountiful, UT 84010"
      }
    ]
  },
  "country_name": "Utah",
  "crawler_name": "custom_crawlers.kyb.utah.utah.py",
  "jurisdiction": "",
  "people_detail": [
    {
      "name": "Jacob Murray",
      "address": "3206 s Sunset Hollow Drive",
      "designation": "registered_agent"
    }
  ],
  "fillings_detail": [
    {
      "date": "2022-08-04",
      "filing_code": "12942999-0160",
      "filing_type": "Public_Applications"
    }
  ],
  "registration_date": "08-04-2022",
  "registration_number": "12942999-0160"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` to crawl and `beautifulsoup` to extract required information.

## Additional Dependencies
- `selenium`
- `beautifulsoup`

## Estimated Processing Time
The processing time for the crawler is estimated > one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/utah/utah.py`