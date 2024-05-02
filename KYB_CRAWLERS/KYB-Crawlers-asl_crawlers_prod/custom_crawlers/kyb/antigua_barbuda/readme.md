# Crawler: Antigua And Barbuda

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Ministry of Legal Affairs](https://abipco.gov.ag/). The script fetches data from the specified API endpoint by adding alphabets(a - z) and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "H2 Limited",
  "type": "Private Ordinary Company",
  "status": "Active",
  "industries": "Intellectual Property & Commerce Office",
  "country_name": "Antigua And Barbuda",
  "crawler_name": "custom_crawlers.kyb.antigua_barbuda.antigua_barbuda.py",
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "11 Old Parham Road, St. John's, ANTIGUA AND BARBUDA"
    }
  ],
  "registration_date": "2004-01-06",
  "registration_number": "C4765"
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
5. Run the script: `python3 ASL-Crawlers/custom_crawlers/kyb/antigua_barbuda/antigua_barbuda.py`