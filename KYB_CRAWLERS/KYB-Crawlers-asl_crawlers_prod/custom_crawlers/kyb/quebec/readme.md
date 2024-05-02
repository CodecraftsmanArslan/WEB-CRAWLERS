# Crawler: Quebec

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [International Registries, Inc](https://www.registreentreprises.gouv.qc.ca/RQAnonymeGR/GR/GR03/GR03A2_19A_PIU_RechEnt_PC/PageRechSimple.aspx?T1.CodeService=S00436&Clng=F&WT.co_f=22fd9cf9e710717554b1680487218676). The script use selenium to crawl and to get HTML data, use beautifulsoup4 to parse, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "DTN, LLC",
  "type": "Société par actions ou compagnie",
  "status": "Immatriculée",
  "meta_detail": {
    "status_updated": "2010-01-25",
    "name_index_updated": "2021-10-15"
  },
  "country_name": "Quebec",
  "crawler_name": "custom_crawlers.kyb.quebec.quebec.py",
  "people_detail": [
    {
      "name": "CRAC",
      "address": "4284 rue De La Roche Montréal (Québec) H2J3H9 Canada",
      "designation": "representative"
    },
    {
      "name": "DTN US Holdings, LLC",
      "address": "100-18205 Capitol Ave Omaha Nebraska 68022 USA",
      "designation": "shareholder"
    },
    {
      "name": "Christoph Grolman",
      "address": "11400 Rupp Drive Bursville Minnesota 55337 USA",
      "designation": "Administrateur",
      "appointment_date": "2017-05-31"
    },
    {
      "name": "Jeremy Abson",
      "address": "11400 Rupp Drive Bursville Minnesota 55337 USA",
      "designation": "Administrateur",
      "appointment_date": "2017-05-31"
    },
    {
      "name": "Marc Chesover",
      "address": "11400 Rupp Drive Bursville Minnesota 55337 USA",
      "designation": "Administrateur",
      "appointment_date": "2021-12-01"
    },
    {
      "name": "Jesse Carlisle",
      "address": "11400 Rupp Drive Bursville Minnesota 55337 USA",
      "designation": "Secrétaire"
    },
    {
      "name": "Thomas Dilworth",
      "address": "11400 Rupp Drive Bursville Minnesota 55337 USA",
      "designation": "Principal dirigeant:  CFO"
    }
  ],
  "fillings_detail": [
    {
      "date": "2022-11-03",
      "filing_type": "DÉCLARATION DE MISE À JOUR ANNUELLE 2022"
    },
    {
      "date": "2021-10-15",
      "filing_type": "DÉCLARATION DE MISE À JOUR ANNUELLE 2021"
    },
    {
      "date": "2021-10-15",
      "filing_type": "DÉCLARATION DE MISE À JOUR ANNUELLE 2020"
    },
    {
      "date": "2020-07-04",
      "filing_type": "Déclaration de mise à jour courante"
    },
    {
      "date": "2019-12-31",
      "filing_type": "Déclaration de mise à jour courante"
    },
    {
      "date": "2019-12-02",
      "filing_type": "DÉCLARATION DE MISE À JOUR ANNUELLE 2019"
    },
    {
      "date": "2018-11-29",
      "filing_type": "DÉCLARATION DE MISE À JOUR ANNUELLE 2018"
    },
    {
      "date": "2017-08-15",
      "filing_type": "DÉCLARATION DE MISE À JOUR ANNUELLE 2017"
    },
    {
      "date": "2016-06-25",
      "filing_type": "Déclaration de mise à jour courante"
    },
    {
      "date": "2016-06-10",
      "filing_type": "DÉCLARATION DE MISE À JOUR ANNUELLE 2016"
    },
    {
      "date": "2016-04-21",
      "filing_type": "DÉCLARATION DE MISE À JOUR ANNUELLE 2015"
    },
    {
      "date": "2016-04-08",
      "filing_type": "DÉCLARATION DE MISE À JOUR ANNUELLE 2014"
    },
    {
      "date": "2016-04-08",
      "filing_type": "DÉCLARATION DE MISE À JOUR ANNUELLE 2013"
    },
    {
      "date": "2015-04-27",
      "filing_type": "Déclaration de mise à jour courante"
    },
    {
      "date": "2014-09-15",
      "filing_type": "Déclaration de mise à jour courante"
    },
    {
      "date": "2013-10-11",
      "filing_type": "Déclaration de mise à jour courante"
    },
    {
      "date": "2013-09-19",
      "filing_type": "DÉCLARATION DE MISE À JOUR ANNUELLE 2012"
    },
    {
      "date": "2013-09-19",
      "filing_type": "DÉCLARATION DE MISE À JOUR ANNUELLE 2011"
    },
    {
      "date": "2011-12-19",
      "filing_type": "Déclaration de mise à jour courante"
    },
    {
      "date": "2010-01-25",
      "filing_type": "Déclaration d'immatriculation"
    }
  ],
  "addresses_detail": [
    {
      "type": "home_address",
      "address": "100-18205 Capitol Ave Omaha Nebraska 68022 USA"
    },
    {
      "type": "legal_address",
      "address": "Aucune adresse"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "legal_diet": "DELAWARE : Autre loi étrangère",
          "current_diet": "DELAWARE : Autre loi étrangère"
        }
      ],
      "type": "legal_framework"
    },
    {
      "data": [
        {
          "info_status_update": "2022-11-03",
          "last_annual_update": "2022-11-03 2022",
          "2022_filing_declaration": "2022-11-15",
          "2023_filing_declaration": "2023-11-17"
        }
      ],
      "type": "update_dates"
    },
    {
      "data": [
        {
          "activity": "Autres industries du matériel électronique et de communication",
          "description": "ÉLECTRONIQUES",
          "activity_code": "3359"
        }
      ],
      "type": "activities_info"
    },
    {
      "data": [
        {
          "employee_count": "Aucun",
          "propotion_of_non_spoken_french_employees": "Non tenue de déclarer cette information"
        }
      ],
      "type": "employees_info"
    },
    {
      "data": [
        {
          "name": "DTN US Holdings, LLC",
          "address": "100-18205 Capitol Ave Omaha Nebraska 68022 USA"
        }
      ],
      "type": "shareholders_info"
    },
    {
      "data": [
        {
          "name": "Groupe DTN",
          "update_date": "2017-08-15",
          "previous_name_status": "En vigueur"
        },
        {
          "name": "ENTREPRISES TELVENT DTN",
          "update_date": "2010-01-25",
          "previous_name_status": "Antérieur",
          "declaration_withdrawn": "2021-10-15"
        }
      ],
      "type": "aliases_info"
    }
  ],
  "registration_date": "2010-01-25",
  "incorporation_date": "2006-03-31 Constitution",
  "registration_number": "1166347915",
  "previous_names_detail": [
    {
      "name": "DTN, LLC",
      "meta_detail": {
        "name_status": "En vigueur",
        "declaration_withdrawn": "",
        "name_in_foreign_language": ""
      },
      "update_date": "2017-08-15"
    },
    {
      "name": "Telvent DTN LLC",
      "meta_detail": {
        "name_status": "Antérieur",
        "declaration_withdrawn": "2017-08-15",
        "name_in_foreign_language": ""
      },
      "update_date": "2013-10-11"
    },
    {
      "name": "TELVENT DTN, INC.",
      "meta_detail": {
        "name_status": "Antérieur",
        "declaration_withdrawn": "2013-10-11",
        "name_in_foreign_language": ""
      },
      "update_date": "2006-03-31"
    }
  ]
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library to get HTML data and `beautifulsoup4` to extract required information.

## Additional Dependencies
- `selenium`
- `beautifulsoup4`

## Estimated Processing Time
The processing time for the crawler is estimated > one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/quebec/quebec.py`