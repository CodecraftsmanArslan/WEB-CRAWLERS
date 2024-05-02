# Crawler: Maryland

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Department of Assessments and Taxation](https://egov.maryland.gov/BusinessExpress/EntitySearch). The script use selenium to get the data HTML page, use beautifulsoup to parse, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {"name":"SELIN FINANCE CORP.",
"type":"Corporation",
"status":"Dissolved",
"country_name":"marylandl Islands",
"crawler_name":"crawlers.custom_crawlers.kyb.marylandl_islands.marylandl_islands_kyb",
"people_detail":[],
"annulment_date":"",
"dissolution_date":"",
"registration_date":"",
"incorporation_date":"26-APR-1994",
"registration_number":"624",
"company_fetched_data_status":""}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library to get HTML data from results page and then use `beautifulsoup` to parse and extract required information.

## Additional Dependencies
- `selenium`
- `beautifulsoup4`

## Estimated Processing Time
The processing time for the crawler is estimated > one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/maryland/maryland.py`