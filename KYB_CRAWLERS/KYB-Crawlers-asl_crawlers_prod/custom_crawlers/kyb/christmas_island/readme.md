# Crawler: Christmas Island

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Indian Ocean Territories Regional Development Organisation](https://iot-businesses.com.au/business_directory/?search_keyword=[IOTChristmasIslandSearchKey]&directory_category=5). The script fetches data from the specified API endpoint, processes the retrieved HTML content, inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "Acker Pty Ltd",
  "meta_detail": {
    "description": "Acker Pty Ltd is the largest locally owned company on Christmas Island; specialising in residential and commercial construction, civil works, labour & machinery hire and freight logistics. [IOTChristmasIslandSearchKey]",
  },
  "contact_details":[
    {
      "type":"email",
      "value":"acker@pulau.cx"
    },
    {
      "type":"website",
      "value":"https://www.acker.com.au/"
    },
    {
      "type":"contact_number",
      "value":"08 9164 7916"
    }
  ],
  "country_name": "Christmas Island",
  "crawler_name": "crawlers.custom_crawlers.kyb.christmas_island_kyb",
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
4. Run the scrip for source 1: `python3 ASL-Crawlers/custom_crawlers/kyb/christmas_island/christmas_island_kyb.py`
