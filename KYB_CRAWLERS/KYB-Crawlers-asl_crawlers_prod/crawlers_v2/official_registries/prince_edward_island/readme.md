
# Prince Edward Island Official Registry Crawler

## Introduction

    Corporate Services is responsible for the registration of corporations and business names in PEI. 
    Businesses of all types can reserve names, register, and manage their registry account information.

## Data Structure
    The extracted data is structured into a dictionary containing various key-value pairs. 
    The script defines functions such as `prepare_data` and `prapare_obj` to structure and 
    prepare data for insertion into a database.

## Sample object {
    "name": "Golden Arrow Hospitality and Food Services Inc.",
    "type": "Incorporated",
    "status": "Active",
    "meta_detail": {
      "nature": "Hospitality and Food Services",
      "aliases": "Aldo Reny's Authentic Italian Gourmet Panini Aldo Reny's",
      "object_typy": "corporate_registry",
      "gazette_date": "September 03, 2022",
      "business_number": "706203809",
      "corporation_type": "Non-distributing"
    },
    "country_name": "Prince Edward Island",
    "crawler_name": "custom_crawlers.kyb.prince_edward_island.prince_edward_island_cr.py",
    "jurisdiction": "",
    "people_detail": [
      {
        "name": "Altug Altinok",
        "designation": "Director, President, Secretary, Treasurer, Shareholder"
      }
    ],
    "addresses_detail": [
      {
        "type": "general_address",
        "address": "286 RICHARD DOUGLAS DR        MERMAID Prince Edward Island C1B 3E4"
      }
    ],
    "registration_date": "August 24, 2022",
    "registration_number": "161899" }

## Range 

    Registration number range starts from 0000 to 999999.

## Crawler Type

    This is a web scraper crawler that uses the `Request` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
    - `Request`
    - `bs4` (BeautifulSoup)

## Estimated Processing Time

    The processing time for the crawler is estimated 4 days.

## How to Run the Crawler
    1. Install the required dependencies: `pip install -r requirements.txt`
    2. Set up a virtual environment if necessary.
    3. Set the necessary environment variables in a `.env` file.
    4. Run the script: `python3 your_script_name.py [optional_arguments]`

      Replace `your_script_name.py` with the actual name of your script.

## Configuration

    ### Metadata
    - **SOURCE:** Corporate Registry of Prince Edward Island, Canada
    - **COUNTRY:** Prince Edward Island
    - **CATEGORY:** Official Registry
    - **ENTITY_TYPE:** Company/Organization
    - **SOURCE_DETAIL:**
    - Source URL: [https://www.princeedwardisland.ca/en/feature/pei-business-corporate-registry#/service/BusinessAPI/BusinessSearch](https://www.princeedwardisland.ca/en/feature/pei-business-corporate-registry#/service/BusinessAPI/BusinessSearch)
    - Source Description: Corporate Services is responsible for the registration of corporations and business names in PEI. Businesses of all types can reserve names, register, and manage their registry account information.
    - **URL:** [https://www.princeedwardisland.ca/en/feature/pei-business-corporate-registry#/service/BusinessAPI/BusinessSearch](https://www.princeedwardisland.ca/en/feature/pei-business-corporate-registry#/service/BusinessAPI/BusinessSearch)
    - **SOURCE_TYPE:** HTML

    ### Crawler Configuration
    - **TRANSLATION_REQUIRED:** False
    - **PROXY_REQUIRED:** False
    - **CAPTCHA_REQUIRED:** False
    - **CRAWLER_NAME:** Prince Edward Island Original Registry

## Usage

    1. Install the required dependencies:

```bash
      pip install -r requirements.txt