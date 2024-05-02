# Crawler: Brunei

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Ministry of Finance and Economy in Brunei Darussalam](https://ocp.mofe.gov.bn/). The script fetches data from the specified API endpoint, inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "2ND MILLENNIUM CONSTRUCTION COMPANY",
  "type": "Private Company",
  "status": "Registered",
  "country_name": "Brunei",
  "crawler_name": "crawlers.custom_crawlers.kyb.brunei_kyb",
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "NO.4, GROUND FLOOR, BANGUNAN HASBULLAH 3, SIMPANG 137-6, JALAN GADONG, BANDAR SERI BEGAWAN 3180 Brunei Muara Brunei Darussalam",
    }
  ],
  "registration_date": "1900-01-01",
  "registration_number": "P00039537"
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` and `selenium` libraries for scraping data.

## Additional Dependencies
- `Request`
- `selenium`
- `webdriver_manager`

## Estimated Processing Time
The processing time for the crawler is estimated 3 day.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a `.env` file.
4. Run the script: `python3 ASL-Crawlers/custom_crawlers/kyb/brunei/brunei_kyb.py`