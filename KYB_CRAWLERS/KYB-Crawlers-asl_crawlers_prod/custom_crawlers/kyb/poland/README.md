# Crawler: Poland

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Portal Rejestrów Sądowych](https://wyszukiwarka-krs.ms.gov.pl/). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "AIE SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ",
  "type": "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ",
  "tax_number": "",
  "meta_detail": {
    "register_name": "Rejestr Przedsiębiorców",
    "business_number": "93105492000000"
  },
  "country_name": "Poland",
  "crawler_name": "custom_crawlers.kyb.poland.poland_kyb.py",
  "people_detail": [
    {
      "name": "WŁODARSKA, KATARZYNA, DANUTA",
      "designation": "PREZES ZARZĄDU"
    }
  ],
  "addresses_detail": [
    {
      "type": "office_address",
      "address": "DOLNOŚLĄSKIE, M. WROCŁAW, M. WROCŁAW, WROCŁAW, KAZIMIERZA WIELKIEGO 9, 50-320"
    }
  ],
  "dissolution_date": "",
  "additional_detail": [
    {
      "data": [
        {
          "issue_date": "02-19-2001",
          "authority_name": "SĄD REJONOWY DLA WROCŁAWIA FABRYCZNEJ VIII WYDZIAŁ GOSPODARCZY DS. UPADŁOŚCIOWO-UKŁADOWYCH",
          "completion_date": "06-22-2001",
          "completion_manner": "POSTANOWIENIE SĄDU REJONOWEGO DLA WROCŁAWIA-FABRYCZNEJ  (SYGN. AKT VIII U 245/00) STWIERDZAJĄCE UKOŃCZENIE POSTĘPOWANIA UPADŁOŚCIOWEGO",
          "conducting_manner": "",
          "legal_act_signature": "VIII U 245/00"
        }
      ],
      "type": "Bankruptcy_proceeding_information"
    },
    {
      "data": [
        {
          "name": "ZARZĄD",
          "way_of_representation": "DO SKŁADANIA OŚWIADCZEŃ I PODPISYWANIA W IMIENIU SPÓŁKI UPOWAŻNIONY JEST PREZES ZARZĄDU."
        }
      ],
      "type": "representation_body_information"
    }
  ],
  "registration_date": "01-02-2002",
  "registration_number": "0000076360"
}
```


## Crawler Type
This is a web scraper crawler that uses the `Request` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Request`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler's processing time is estimated to be approximately one week.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/poland/poland_kyb.py`