# Crawler: Alaska

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Alaska Corporations, Business & Professional Licensing](https://www.commerce.alaska.gov/cbp/main/). The script fetches data from the CSV and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "ALASKA AIRLINES, INC.",
  "type": "Business Corporation",
  "status": "Good Standing",
  "meta_detail": {
    "aliases": "",
    "end_date": "Perpetual"
  },
  "country_name": "Alaska",
  "crawler_name": "custom_crawlers.kyb.alaska.alaska_corporation_kyb",
  "people_detail": [
    {
      "name": "Corporation Service Company",
      "designation": "registered_agent"
    }
  ],
  "fillings_detail": [
    {
      "filling_date": "1-2-2025"
    }
  ],
  "addresses_detail": [
    {
      "type": "postal_address",
      "address": "PO BOX 68900 SEATTLE UNITED STATES WA 98168",
    }
  ],
  "registration_date": "12-9-1937",
  "incorporation_date": "12-9-1937",
  "registration_number": "1127D",
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` and `pandas` libraries for scraping

## Additional Dependencies
- `Request`
- `pandas`

## Estimated Processing Time
The processing time for the crawler is estimated 3 days.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a `.env` file.
4. Run the script: `python3 ASL-Crawlers/custom_crawlers/kyb/alaska/alaska_corporation.py`