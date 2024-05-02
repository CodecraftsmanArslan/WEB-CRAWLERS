# Crawler: Italy

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Italian Business Register](https://italianbusinessregister.it/en/home). The script use selenium to crawl to data page, get HTML, beautifulsoup to parse, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "A & A - S.R.L.",
  "type": "Shareholding or Joint-stock Company",
  "country_name": "Italy",
  "crawler_name": "custom_crawlers.kyb.Italy.italy.py",
  "contacts_detail": [
    {
      "type": "email",
      "value": "aeasrl1@pec.it"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "Legnano (MI) - Via Carlo Cattaneo 96"
    }
  ]
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library crawl to data page, get HTML data and then use `beautifulsoup` to parse and extract required information.

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
5. Run the script: `python3 custom_crawlers/kyb/italy/italy.py`