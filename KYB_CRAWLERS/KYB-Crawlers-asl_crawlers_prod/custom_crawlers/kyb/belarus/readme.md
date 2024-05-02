# Crawler: Belarus

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Unified State Register](https://egr.gov.by/egrn/index.jsp?language=en). The script fetches data from the specified API endpoint inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "Степанов Александр Николаевич",
  "status": "Исключен из ЕГР",
  "industries": "45430 ",
  "meta_detail": {
    "state_body": "Администрация Железнодорожного района г Витебска",
    "last_updated": "2013-10-11",
    "registration_authority": "Администрация Железнодорожного района г Витебска"
  },
  "country_name": "Belarus",
  "crawler_name": "custom_crawlers.kyb.belarus.belarus.py",
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "Республика Беларусь, 210001, Витебская область, г. Витебск, ул. Ильинского, д. 7, кв. 25"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "date": "",
          "decision": "243",
          "exclusion_authority": "Администрация Железнодорожного района г Витебска"
        }
      ],
      "type": "exclusion_information"
    },
    {
      "data": [
        {
          "date": "",
          "decision_number": "243",
          "liquidation_authority": "Администрация Железнодорожного района г Витебска"
        }
      ],
      "type": "liquidation_information"
    }
  ],
  "registration_date": "2012-07-30",
  "registration_number": "391405938"
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` library for scraping.

## Additional Dependencies
- `Request`

## Estimated Processing Time
The processing time for the crawler is estimated 5 days.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 ASL-Crawlers/custom_crawlers/kyb/belarus/belarus.py`