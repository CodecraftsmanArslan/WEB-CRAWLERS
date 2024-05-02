# Crawler: Canada

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Canada's Business Registries](https://beta.canadasbusinessregistries.ca/search). The script use API to get Json dictionary using Requests module, scrape the data, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "Kotla-Tarmaki Corp.",
  "type": "Business Corporation",
  "status": "Active",
  "meta_detail": {
    "registry_id": "12362538",
    "status_date": "2020-09-23"
  },
  "country_name": "Canada",
  "crawler_name": "custom_crawlers.kyb.canada.canada.py",
  "addresses_detail": [
    {
      "type": "registered_office",
      "address": "Toronto, Ontario"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "name": "Ontario",
          "aliases": "KOTLA-TARMAKI CORP.",
          "prov_registry_id": "3255517"
        }
      ],
      "type": "provincial_registration_info"
    }
  ],
  "registration_date": "2020-09-23",
  "registration_number": "710752536"
}
```

## Crawler Type
This is a web scraper crawler that uses the `requests` library to fetch API data in json format.

## Additional Dependencies
- `requests`

## Estimated Processing Time
The processing time for the crawler is estimated 30 days.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/canada/canada.py`