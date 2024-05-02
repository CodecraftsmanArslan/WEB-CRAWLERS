# Crawler: Ireland

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Companies Registration Office (CRO)](https://core.cro.ie/). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "BANK OF IRELAND MORTGAGE BANK UNLIMITED COMPANY",
  "type": "PUC - Public Unlimited Company",
  "status": "Normal",
  "meta_detail": {
    "effective_date": "05-21-2004",
    "next_annual_return": "09-30-2023"
  },
  "country_name": "Ireland",
  "crawler_name": "custom_crawlers.kyb.ireland.ireland_kyb.py",
  "addresses_detail": [
    {
      "type": "registered_address",
      "address": "40 MESPIL ROAD, DUBLIN 4, DUBLIN, D04C2N4, Ireland"
    }
  ],
  "registration_date": "05-21-2004",
  "registration_number": "386415",
  "announcements_detail": [
    {
      "date": "02-02-2023",
      "title": "Form B1B73 - Annual Return and Change of ARD",
      "meta_detail": {
        "announcement_status": "Submission Registered"
      }
    },
    {
      "date": "01-31-2023",
      "title": "Form B1B73 - Annual Return and Change of ARD",
      "meta_detail": {
        "announcement_status": "Submission Filed"
      }
    },
    {
      "date": "01-27-2023",
      "title": "Form B10 - Change Director or Secretary Details",
      "meta_detail": {
        "announcement_status": "Submission Registered"
      }
    },
    {
      "date": "01-19-2023",
      "title": "Form B10 - Change Director or Secretary Details",
      "meta_detail": {
        "announcement_status": "Submission Filed"
      }
    },
    {
      "date": "10-23-2022",
      "title": "Form B10 - Change Director or Secretary Details",
      "meta_detail": {
        "announcement_status": "Submission Registered"
      }
    }
  ],
  "previous_names_detail": [
    {
      "name": "BANK OF IRELAND MORTGAGE BANK",
      "meta_detail": {
        "effective_date": "05-21-2004"
      }
    },
    {
      "name": "BANK OF IRELAND MORTGAGE BANK UNLIMITED COMPANY",
      "meta_detail": {
        "effective_date": "04-27-2016"
      }
    },
    {
      "name": "BANK OF IRELAND MORTGAGE BANK",
      "meta_detail": {
        "effective_date": "04-27-2016"
      }
    }
  ]
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
5. Run the script: `python3 crawlers_v2/official_registries/ireland/ireland_kyb.py`