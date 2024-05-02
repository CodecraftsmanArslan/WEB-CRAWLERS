# Crawler: Colorado

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Colorado Secretary of State, Business Division](https://data.colorado.gov/Business/Business-Entities-in-Colorado/4ykn-tg5h). The script fetches data from the specified API endpoint, processes the retrieved HTML content, inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "PMI MORTGAGE INSURANCE CO.",
  "type": "Foreign Corporation",
  "status": "Good Standing",
  "meta_detail": {
    "jurisdiction": "AZ"
  },
  "country_name": "Colorado",
  "crawler_name": "crawlers.custom_crawlers.kyb.colorado.colorado_kyb",
  "addresses_detail": [
    {
      "type": "principal_office_address",
      "address": "3003 Oak Rd Ste 300 US Walnut Creek CA 94597",
    },
    {
      "type": "registered_agent_address",
      "address": "7700 E Arapahoe Rd Ste 220 Centennial US CO 80112"
    },
  ],
  "additional_detail": [
    {
      "data": [
        {
          "registered_agent_organization": "C T Corporation System"
        }
      ],
      "type": "registered_agent"
    }
  ],
  "registration_date": "1974-08-16T00:00:00.000",
  "registration_number": "19871056634"
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` and `pandas` libraries for scraping.

## Additional Dependencies
- `Request`
- `pandas` 



## Estimated Processing Time
The processing time for the crawler is estimated 30 minniutes.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt` 
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a `.env` file.
4. Run the scrip for source 1: `python3 ASL-Crawlers/custom_crawlers/kyb/colorado/colorado_kyb.py`
