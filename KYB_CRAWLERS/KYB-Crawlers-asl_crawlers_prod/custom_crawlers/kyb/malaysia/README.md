# Crawler: Malaysia

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Companies Commission of Malaysia](https://www.ssm.com.my/Pages/Quick_Link_backup/e-Search.aspx). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "SK PROPERTIES (M) PLT",
  "status": "DISSOLVED",
  "tax_number": "",
  "country_name": "Malaysia",
  "crawler_name": "custom_crawlers.kyb.malaysia.malaysia_kyb.py",
  "registration_number": "LLP0000092-LGN"
}
```


## Crawler Type
This is a web scraper crawler that uses the `Request` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Request`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler's processing time is estimated to be approximately one month.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/malaysia/malaysia_kyb.py`