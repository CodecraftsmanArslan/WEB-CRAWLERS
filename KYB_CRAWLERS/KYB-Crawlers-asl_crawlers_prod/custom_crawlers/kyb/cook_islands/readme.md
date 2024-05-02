# Crawler: Cook Islands

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Cook Islands Registry Services, Ministry of Justice of the Cook Islands](https://registry.justice.gov.ck/corp/search.aspx). The script fetches data from the specified API endpoint, processes the retrieved HTML content, inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "159 WEST LIMITED",
  "type": "Cook Islands Company",
  "status": "Registered",
  "meta_detail": {
    "principal_activity": "AccommodationAgriculture services",
    "is_foreign_enterprise": false,
    "annual_return_due_date": "07-05-2024"
  },
  "country_name": "Cook Islands",
  "crawler_name": "crawlers.custom_crawlers.kyb.cook_islands_kyb",
  "fillings_detail": [
    {
      "title": "AR1  Annual return",
      "filing_code": "112530010",
      "filing_date": "27-06-2023",
      "meta_detail": {
        "effective_date": "27-06-2023"
      }
    },
    {
      "title": "C7  Notice of transfer of shares",
      "filing_code": "112510010",
      "filing_date": "23-06-2023",
      "meta_detail": {
        "effective_date": "23-06-2023"
      }
    },
    {
      "title": "AR1  Annual return",
      "filing_code": "64610015",
      "filing_date": "26-04-2022",
      "meta_detail": {
        "effective_date": "26-04-2022"
      }
    },
    {
      "title": "B1  Application for reregistration by existing Cook Islands company",
      "filing_code": "18730014",
      "filing_date": "01-10-2020",
      "meta_detail": {
        "effective_date": "01-10-2020"
      }
    }
  ],
  "addresses_detail": [
    {
      "type": "office_address",
      "address": " TAPUTAPUATEA ROAD TAPUTAPUATEA AVARUA, RAROTONGA, COOK ISLANDS "
    },
    {
      "type": "postal_address",
      "address": " PO BOX 167 TAPUTAPUATEA AVARUA, RAROTONGA, COOK ISLANDS "
    }
  ],
  "registration_date": "11-04-2018",
  "registration_number": "C3750"
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` and `pandas` libraries for scraping.

## Additional Dependencies
- `Request`
- `pandas` 



## Estimated Processing Time
The processing time for the crawler is estimated 40 minniutes.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt` 
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a `.env` file.
4. Run the scrip for source 1: `python3 ASL-Crawlers/custom_crawlers/kyb/cook_islands/cook_islands_kyb.py`
