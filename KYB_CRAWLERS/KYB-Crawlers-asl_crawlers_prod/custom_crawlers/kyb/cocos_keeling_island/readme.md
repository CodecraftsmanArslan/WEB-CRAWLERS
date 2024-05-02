# Crawler: Cocos (Keeling) Islands

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Indian Ocean Territories Regional Development Organisation](https://iot-businesses.com.au/business_directory/?search_keyword=[IOTCocosKeelingIslandSearchKey]&directory_category=). The script fetches data from the specified API endpoint, processes the retrieved HTML content, inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "Cocos Boats Bikes & Bits",
  "meta_detail": {
    "description": "For all your boat and small motor services and repairs, Cocos Boats, Bikes & Bits is the local agent for Victory Parks Australia Outboard Parts and sells Delkor marine batteries and Valvoline lubricants. You can also speak to Jeff about testing, tagging and re-plug services. [IOTCocosKeelingIslandSearchKey]"
  },
  "country_name": "Cocos (Keeling) Islands",
  "crawler_name": "crawlers.custom_crawlers.kyb.cocos_keeling_islands.Cocos_(Keeling)_Islands_kyb",
  "contact_details":[
    {
      "type":"email",
      "value":"jeffandjillwelch@gmail.com"
    },
    {
      "type":"contact_number",
      "value":"9162 7509"
    }
  ],
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Request`
- `bs4` (BeautifulSoup)


## Estimated Processing Time
The processing time for the crawler is estimated 20 minniutes.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt` 
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a `.env` file.
4. Run the scrip for source 1: `python3 ASL-Crawlers/custom_crawlers/kyb/cocos_keeling_island/cocos_keeling_island_kyb.py`
