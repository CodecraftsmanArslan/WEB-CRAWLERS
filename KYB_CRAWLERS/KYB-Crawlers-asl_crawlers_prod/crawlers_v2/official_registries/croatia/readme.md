# Crawler Type

    This is a web scraper crawler designed to extract data from a specific source related to Croatia's official registry. The script employs the `Request` library for making HTTP requests and scraping relevant information from the HTML content of the target website.

## Introduction
    This web scraper is tailored for collecting data from the official registry of Croatia. It navigates through pages, retrieves information about companies/organizations, and compiles a structured dataset. The script uses the `Request` library for handling HTTP requests, allowing seamless interaction with the target website.
    
## Data Structure
    The extracted data is structured into a dictionary containing various key-value pairs. 
    The script defines functions such as `prepare_data` and `prapare_obj` to structure and 
    prepare data for insertion into a database.

## Additional Dependencies
    - `Request`

## Estimated Processing Time
    The processing time for the crawler is estimated to be 10 days.


## Sample Object 
    {
    "name": "AUTOPROMET ČIKO d.o.o.",
    "type": "društvo s ograničenom odgovornošću",
    "industries": "H4941 - Cestovni prijevoz robe",
    "meta_detail": {
        "aliases": "AUTOPROMET ČIKO d.o.o.",
        "hgk_score": "529",
        "hgk_raating": "BBB",
        "block_status": "Not Blocked",
        "ownership_type": "privatno vlasništvo - od osnivanja (GFI 2022)",
        "number_of_employees": "10 (GFI 2022)",
        "personal_identification_number": "54329671474"
    },
    "country_name": "Croatia",
    "crawler_name": "custom_crawlers.kyb.croatia.croatia_kyb.py",
    "people_detail": [
        {
        "name": "Vjekoslav Mataić",
        "designation": "direktor"
        },
        {
        "name": "Vjekoslav Mataić",
        "designation": "jedini član d.o.o."
        }
    ],
    "contacts_detail": [
        {
        "type": "email",
        "value": "cikopromet@gmail.com"
        }
    ],
    "addresses_detail": [
        {
        "type": "general_address",
        "address": "Vranduk 108, Požega, 34000"
        }
    ],
    "incorporation_date": "05-10-2018",
    "registration_number": "030209419"
    }

## How to Run the Crawler
    1. Install the required dependencies: `pip install -r requirements.txt`
    2. Install the custom service dependency in the dist directory: `pip install custom_crawler-1.0.tar.gz`
    3. Set up a virtual environment if necessary.
    4. Set the necessary environment variables in a `.env` file.
    5. Run the script: `python3 ASL-Crawlers/crawlers_v2/official_registries/croatia/croatia.py` with the desired page number as a command line argument (e.g., `python3 croatia.py 1`).

