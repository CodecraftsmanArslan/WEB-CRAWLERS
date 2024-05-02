
# Crawler: Afghanistan Official Registry

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Afghanistan Official Registry](https://afghanistan.revenuedev.org/owner). The script fetches data from the specified API endpoint, processes the retrieved JSON content, and inserts relevant information into a MongoDB collection. The extracted data includes details about companies, licenses, and beneficial owners.

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data_object` and `prepare_row_for_db` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {

  "name": "ساحه گزک(محدوده 18)",
  "status": "REGISTERED",
  "meta_detail": {
    "aliases": "ساحه گزک(محدوده 18)",
    "description": "نوت : موقعیت ساحه فوق الذکر در گزارش ساحوی ولسوالی ده سبز بوده و اما در سیستم در ولسوالی بگرامی قرار دارد",
    "company_code": "BLK-313"
  },
  "country_name": "Afghanistan",\
  "crawler_name": "custom_crawlers.kyb.Afghanistan.block.py",
  "inactive_date": "",\
  "additional_detail": [
    {
      "data": [
        {
          "coordinate": "34.530994444444445 69.42822222222222, 34.52865277777778 69.42672222222222, 34.53073055555556 69.4235361111111, 34.5335416667 69.42504722222222, 34.52855 69.42661944444444, 34.52843611111111 69.42110833333334, 34.53015277777778 69.42142222222222, 34.530633333333334 69.42348333333334"
        }
      ],
      "type": "coordinates_information"
    }

  ],

  "registration_date": "2023-09-10"

}
```

# Crawler Type
This is a web scraper crawler that uses the requests library for scraping and BeautifulSoup for HTML parsing.

# Additional Dependencies
requests
beautifulsoup4


# Estimated Processing Time
The processing time for the crawler is estimated to be around 1 day.

How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5.  Navigate to the "custom_crawler/kyb/afghanistan" directory using the command "cd."
6. Run the script: python3 afghanistan.py
