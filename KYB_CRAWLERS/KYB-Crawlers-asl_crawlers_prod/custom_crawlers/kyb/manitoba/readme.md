# Crawler: Manitoba

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [International Registries, Inc](https://companiesonline.gov.mb.ca/EntitySearch). The script use selenium to login to website and get the data HTML page, use beautifulsoup to parse, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "FlexITy Systems Inc.",
  "type": "FD SHARE CORP",
  "status": "Active (New Name)",
  "meta_detail": {
    "current_name": "FlexITy Solutions Inc.",
    "compliance_status": "DEFAULT"
  },
  "country_name": "Manitoba",
  "crawler_name": "custom_crawlers.kyb.manitoba.manitoba.py",
  "jurisdiction": "",
  "registration_number": "6608575",
  "previous_names_detail": [
    {
      "name": "FlexITy Systems Inc."
    }
  ]
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library to login and get HTML data from results page and then use `beautifulsoup` to parse and extract required information.

## Additional Dependencies
- `selenium`
- `beautifulsoup4`

## Estimated Processing Time
The processing time for the crawler is estimated < one hour.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/manitoba/manitoba.py`