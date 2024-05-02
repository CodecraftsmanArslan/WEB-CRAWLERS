# Crawler: Falkland Islands

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Falkland Islands Government](https://www.falklands.gov.fk/registry/companies/incorporated-companies).The script fetches data from using selenium for processes the retrieved HTML content, inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "Arch Henderson Atlantic Ltd",
  "country_name": "Falkland Islands",
  "crawler_name": "crawlers.custom_crawlers.kyb.falkland_islands.falkland_islands_kyb",
  "fillings_detail": [
    {
      "title": "certificate_of_incorporation",
      "file_url": "https://www.falklands.gov.fk/registry/component/jdownloads/?task=download.send&id=145&catid=16&m=0&Itemid=101"
    }
  ],
  "incorporation_date": "06-09-2013",
  "registration_number": "15015"
}
```

## Crawler Type
This is a web scraper crawler that uses the ``Selenium` library for scraping.

## Additional Dependencies
- `selenium` 
- `webdriver_manager`


## Estimated Processing Time
The processing time for the source one is estimated 50 minniutes and source two is estimated 3 days.


## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a `.env` file.
4. Run the scrip for source 1: `python3 custom_crawlers/kyb/falkland_islands/falkland_islands_kyb.py`
