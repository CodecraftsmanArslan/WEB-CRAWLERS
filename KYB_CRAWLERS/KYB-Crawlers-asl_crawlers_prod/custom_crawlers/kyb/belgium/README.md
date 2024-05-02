# Crawler: Belgium

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Crossroads Bank for Enterprises](https://kbopub.economie.fgov.be/kbopub/zoeknummerform.html). The script fetches data from the specified API endpoint, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "Bank- en verzekeringsagent Regio Kempen Oost",
  "type": "Limited partnership",
  "status": "Active",
  "meta_detail": {
    "name_type": "Name in Dutch",
    "entity_type": "Legal person",
    "name_last_updated": "since January 1, 2021",
    "name_last_updated_2": "Since January 1, 2020"
  },
  "country_name": "Belgium",
  "crawler_name": "custom_crawlers.kyb.belgium.belgium_kyb.py",
  "contacts_detail": [
    {
      "type": "phone_number",
      "value": "011548040"
    },
    {
      "type": "fax",
      "value": "011548049"
    },
    {
      "type": "email",
      "value": "dennis.plessers@mandat.belfius.be"
    }
  ],
  "addresses_detail": [
    {
      "type": "registered_address",
      "address": "Hertog Janplein 453920 Lommel",
      "meta_detail": {
        "address_updated": "Since September 1, 2011"
      }
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "date_updated": "Since December 21, 2000",
          "legal_status": "Normal situation"
        }
      ],
      "type": "legal_status_info"
    },
    {
      "data": [
        {
          "type": "Name in Dutch",
          "abbreviation": "Bank- en verzekeringsagent Regio Kempen Oost",
          "last_updated": "since January 1, 2021"
        }
      ],
      "type": "abbreviated_name"
    },
    {
      "data": [
        {
          "url": "https://kbopub.economie.fgov.be/kbopub/vestiginglijst.html?ondernemingsnummer=473590424",
          "number": "5"
        }
      ],
      "type": "establishment_units_info"
    },
    {
      "data": [
        {
          "skill": "Knowledge of basic management",
          "last_updated": "Since February 20, 2018"
        }
      ],
      "type": "entrepreneurial_skills_info"
    },
    {
      "data": [
        {
          "description": "Employer National Social Security Office",
          "date_updated": "Since January 1, 2001"
        },
        {
          "description": "Enterprise subject to registration",
          "date_updated": "Since November 1, 2018"
        }
      ],
      "type": "qualities"
    },
    {
      "data": [
        {
          "url": "https://kbopub.economie.fgov.be/kbopub/toonondernemingps.html?ondernemingsnummer=466424597",
          "description": "0466.424.597 (Bank- en verzekeringsagent KEMPEN OOST) thas been absorbed by this entity since January 1, 2021"
        }
      ],
      "type": "entity_links_info"
    },
    {
      "data": [
        {
          "url": ", http://www.ejustice.just.fgov.be/cgi_tsv/tsv_rech.pl?language=fr&btw=0473590424&liste=Liste"
        },
        {
          "url": ", https://consult.cbso.nbb.be/consult-enterprise/0473590424"
        },
        {
          "url": ", https://statuts.notaire.be/stapor_v1/enterprise/0473590424/statutes"
        },
        {
          "url": ", https://employer-identification-consult.prd.pub.socialsecurity.be/employer/enterprise/0473590424"
        }
      ],
      "type": "external_links"
    },
    {
      "data": [
        {
          "url": "https://kbopub.economie.fgov.be/kbopub/naceToelichting.html?nace.code=66191",
          "code": "66.191",
          "title": "NSSO2008",
          "description": "Activities of banking agents and brokers",
          "last_updated": "Since January 1, 2008"
        }
      ],
      "type": "activities_info"
    }
  ],
  "incorporation_date": "December 21, 2000",
  "registration_number": "0473.590.424"
}
```


## Crawler Type
This is a web scraper crawler that uses the `Requests` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Requests`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler's processing time is estimated to be approximately one week.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/belgium/belgium_kyb.py`