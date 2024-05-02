# Paraguay Official Registry Crawler

## Introduction
    This web scraper crawler is designed for extracting data from the Registro Único del Contribuyente (RUC) - the Unique Taxpayer Registry in Paraguay. The script utilizes the Selenium library for dynamic web interactions and the `Request` library for handling HTTP requests.

## Sample Object
    {
        "name": "NAVIERA CONOSUR SA",
        "country_name": "Paraguay",
        "crawler_name": "custom_crawlers.kyb.paraguay.paraguay_official_registry.py",
        "registration_number": "80000001-3"
    }

## Additional Dependencies
    - `time`
    - `sys`
    - `ssl`
    - `traceback`
    - `selenium.webdriver`

## Estimated Processing Time
    The processing time for the crawler depends on the specified range of registration numbers.

## Introduction
    This crawler targets the official registry of Paraguay, specifically the Registro Único del Contribuyente (RUC). It searches for company/organization information using registration numbers within a given range. The script uses Selenium for web automation, interacting with the RUC website to retrieve relevant data.

## How to Run the Crawler
    1. Install the required dependencies: `pip install -r requirements.txt`
    2. Install the custom service dependency in the dist directory: `pip install custom_crawler-1.0.tar.gz`
    3. Set up a virtual environment if necessary.
    4. Set the necessary environment variables in a `.env` file.
    5. Run the script: `python3 path/to/paraguay_crawler.py <start_range> <end_range>` with the desired range of registration numbers.


