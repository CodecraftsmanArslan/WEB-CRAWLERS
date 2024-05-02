# Crawler: Faroe Islands

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Skráseting Føroya](https://www.skraseting.fo/en/companies/search-companies?&name=_&page=1).The script fetches data from PDF and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "Sp/F Intra",
  "meta_detail": {
    "purpose": "Endamál felagsins er at veita internettænastu, ráðgeving og annað virksemi í hesum sambandi.",
    "municipality": "Runavíkar",
    "accounting_date_1": "22-01-2021",
    "accounting_date_2": "16-06-2022",
    "accounting_date_3": "22-06-2023",
    "participation_fee": "DKK: 186.667",
    "recruitment_rules": "Felagið verður teknað av høvuðsleiðsluni saman"
  },
  "country_name": "Faroe Islands",
  "crawler_name": "custom_crawlers.kyb.faroe_islands.faroe_islands_pdf.py",
  "people_detail": [
    {
      "name": "Jaspur Langgaard",
      "address": "Nesvegur 103 655 Nes, Eysturoy",
      "designation": "Stjóri"
    },
    {
      "name": "Ulf Bech Christensen",
      "address": "Bækkelunds Have 19DK-5210 Odense NV, Danmark",
      "designation": "Nevndarformaður"
    },
    {
      "name": "Ben Arabo",
      "address": "á Oyrareingjum 110415 Oyrareingir",
      "designation": "Nevndarlimur"
    },
    {
      "name": "Jaspur Langgaard",
      "address": "Nesvegur 103655 Nes, Eysturoy",
      "designation": "Nevndarlimur"
    },
    {
      "name": "Reimund Langgaard",
      "address": "við Myllutjørn 59188 Hoyvík",
      "designation": "Nevndarlimur"
    }
  ],
  "addresses_detail": [
    {
      "type": "registered_address",
      "address": "Heiðavegur 53 600 Saltangará",
      "meta_detail": {
        "address_url": "https://www.skraseting.fo/api/Skraseting/LysingPdf?id=35599&s=NLJJpO_FUpjtsz-tYoeUJEWtpTw"
      }
    }
  ],
  "registration_date": "09-10-2023",
  "registration_number": "3493"
}
```

## Crawler Type
This is a web scraper crawler that uses the `PyPDF2` and `requests` libraries for scraping.

## Additional Dependencies
- `PyPDF2` 
- `requests`


## Estimated Processing Time
The processing time for the crawler is estimated 30 minniutes.


## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the scrip for source 1: `python3 custom_crawlers/kyb/faroe_islands/faroe_islands_pdf.py`
