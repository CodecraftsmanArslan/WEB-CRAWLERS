# Crawler: Bulgaria

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Bulgarian Chamber of Commerce and Industry](https://newregister.bcci.bg/edipub/CombinedReports). The script fetches data from the two sources both source have specified API endpoint, inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data":{
  "name": "АКВАВЕО БЪЛГАРИЯ SLLC",
  "type": "Еднолично дружество с ограничена отговорност",
  "industries": "",
  "meta_detail": {
    "description": "Консултантска дейност, инженерингова дейност, проектиране, хидрогеоложки проучвания и изследвания, ландшафтно проектиране и изграждане, вътрешна и външна търговия, комисионерска, спедиторска, превозна, складова, лизингови дейности и дейност на търговско представителство и търговско посредничество; рекламни, информационни, програмни и други услуги, както и всякакъв вид други дейности и услуги, незабранени от закона. Дейностите, за които съгласно българското законодателство се изисква предварително разрешение, лицензия или друг разрешителен акт, ще се осъществяват след получаването му.",
    "announcement_detail": [
      {
        "date": "25.08.2011 11. 09:42:22",
        "title": "Актуален дружествен договор/учредителен акт/устав",
        "file_url": "https://portal.registryagency.bg/CR/DocumentAccess/MjAxNjgxMzIyJmUmYzA0YWFiNGE2NWFmNDMzNThiZjgwOTMzZTI5NDFmZWOOndAknq8vtrIft05AO69ONfedveShM8lWp4ahgfNjiw"
      }
    ]
  },
  "country_name": "Bulgaria",
  "crawler_name": "custom_crawlers.kyb.bulgaria.bulgaria_kyb2.py",
  "people_detail": [
    {
      "name": "Велислава Николаева Петрова",
      "designation": "manager",
      "nationality": "БЪЛГАРИЯ"
    }
  ],
  "fillings_detail": [
    {
      "date": "15.01.2013 13. 08:48:54",
      "year": "2011",
      "title": "Годишен финансов отчетYear: 2011y.Годишен финансов отчет",
      "file_url": "https://portal.registryagency.bg/CR/DocumentAccess/MjAxNjgxMzIyJmUmM2ExOTY1Zjc1ZmI3NGY3NGIyMDRlYjQ1NTAwYmRlMjhiR0XnabvFiCnoKYIPuu9E2UgPYVxrfwt-MaLCWweMBg"
    },
    {
      "date": "17.10.2013 13. 15:41:35",
      "year": "2012",
      "title": "Годишен финансов отчетYear: 2012y.Годишен финансов отчет",
      "file_url": "https://portal.registryagency.bg/CR/DocumentAccess/MjAxNjgxMzIyJmUmMzlkYTJkYjliYjZhNGFiZDkxOTEyZGEyZTVhNDFmY2INv7YcZYySI-N-mPrEeR4rkDZs6JwSUPJqx4e4uDKWQw"
    },
    {
      "date": "12.03.2015 15. 08:42:06",
      "year": "2013",
      "title": "Годишен финансов отчетYear: 2013y.Годишен финансов отчет",
      "file_url": "https://portal.registryagency.bg/CR/DocumentAccess/MjAxNjgxMzIyJmUmNWMzNDU1OGY1MmQ4NGE3M2JiNmZlYTIwNTVmMzE2NGIdMEeP9oiYrk2Ukc97PhhAZF7i63L5BPJFooi8djRnJA"
    },
    {
      "date": "22.03.2016 16. 14:13:41",
      "year": "2014",
      "title": "Годишен финансов отчетYear: 2014y.Годишен финансов отчет",
      "file_url": "https://portal.registryagency.bg/CR/DocumentAccess/MjAxNjgxMzIyJmUmZTlhZjg0Njc4OTlhNGRiMTljZGY0MTE5NGI3ZDU0NDWMGoTDDW6Vw3FKSStgPu_utrKxdnDPdzxn-Pp07sgPrQ"
    },
    {
      "date": "17.08.2017 17. 10:16:11",
      "year": "2015",
      "title": "Годишен финансов отчетYear: 2015y.Годишен финансов отчет",
      "file_url": "https://portal.registryagency.bg/CR/DocumentAccess/MjAxNjgxMzIyJmUmMzE1MzA3MDY5YWE2NDVhMmI0MzEzYzIyMTZlMmMzMGITgRPYIZFNPfX3SY4ZvSabViF19n_IgCjyAfQINbxFBw"
    },
    {
      "date": "12.06.2020 20. 09:47:00",
      "year": "2016",
      "title": "Годишен финансов отчетYear: 2016y.Годишен финансов отчет",
      "file_url": "https://portal.registryagency.bg/CR/DocumentAccess/MjAxNjgxMzIyJmUmZGIxNDY0NTUzMDQ3NDU1NGJjNjYwZDkzZDYwNDdkM2PzM8i1vBgaHW3m6mKdkFr09ya7Ua1mCqGgu3jKppQGag"
    },
    {
      "date": "06.02.2021 21. 11:20:03",
      "year": "2017",
      "title": "Годишен финансов отчетYear: 2017y.Годишен финансов отчет",
      "file_url": "https://portal.registryagency.bg/CR/DocumentAccess/MjAxNjgxMzIyJmUmYmY1ZmFmNTcyOWRhNDAwYWEyYzI1NzRiMDY0N2RjZDaQTIqVrMxaA9mfmCDH-HL2TClubF1MhvxAorcNFBfArA"
    },
    {
      "date": "10.02.2022 22. 14:46:19",
      "year": "2018",
      "title": "Годишен финансов отчетYear: 2018y.Годишен финансов отчет",
      "file_url": "https://portal.registryagency.bg/CR/DocumentAccess/MjAxNjgxMzIyJmUmNTkwNDcwZjU3OTBhNGJiMmE5ZWMxZDk1MmViYTZlYWJ6Q87LJjJJwY1KGmHkd0kGW4zi6NtVxEcvaf47GgsyHw"
    },
    {
      "date": "17.06.2023 23. 15:48:34",
      "year": "2019",
      "title": "Годишен финансов отчетYear: 2019y.Годишен финансов отчет",
      "file_url": "https://portal.registryagency.bg/CR/DocumentAccess/MjAxNjgxMzIyJmUmOGI4NjU2MjgwZDA5NDRlM2E1MjFmNjI5MzI1YWI1NjSZKK5uK1h914-gj3vgMNjam9CaD3TynUzgYPHxamFiXQ"
    }
  ],
  "addresses_detail": [
    {
      "type": "office_address",
      "address": "БЪЛГАРИЯ София (столица) гр. София, p.c. 1505р-н Оборищеr. -, str. бул. \"Мадрид\" № 58, bl. -, ent. -, fl. 2, ap. 30  Столична"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "result": "Processing",
          "documents_submitted": "Заявление Г2"
        }
      ],
      "type": "case_information"
    },
    {
      "data": [
        {
          "result": "Processing",
          "documents_submitted": "Заявление Г2"
        }
      ],
      "type": "case_information"
    },
    {
      "data": [
        {
          "result": "Registration 20230617154834",
          "entry_number": "20230617154834",
          "documents_submitted": "Заявление Г2"
        }
      ],
      "type": "case_information"
    },
    {
      "data": [
        {
          "result": "Registration 20220210144619",
          "entry_number": "20220210144619",
          "documents_submitted": "Заявление Г2"
        }
      ],
      "type": "case_information"
    },
    {
      "data": [
        {
          "result": "Registration 20210206112003",
          "entry_number": "20210206112003",
          "documents_submitted": "Заявление Г2"
        }
      ],
      "type": "case_information"
    },
    {
      "data": [
        {
          "result": "Registration 20200612094700",
          "entry_number": "20200612094700",
          "documents_submitted": "Заявление Г2"
        }
      ],
      "type": "case_information"
    },
    {
      "data": [
        {
          "result": "Registration 20170817101611",
          "entry_number": "20170817101611",
          "documents_submitted": "Заявление Г2"
        }
      ],
      "type": "case_information"
    },
    {
      "data": [
        {
          "result": "Registration 20160322141341",
          "entry_number": "20160322141341",
          "documents_submitted": "Заявление Г2"
        }
      ],
      "type": "case_information"
    },
    {
      "data": [
        {
          "result": "Registration 20150312084206",
          "entry_number": "20150312084206",
          "submitted_via": "ТС АВ София",
          "documents_submitted": "Заявление Г2"
        }
      ],
      "type": "case_information"
    },
    {
      "data": [
        {
          "result": "Registration 20131017154135",
          "entry_number": "20131017154135",
          "submitted_via": "ТС АВ София",
          "documents_submitted": "Заявление Г2"
        }
      ],
      "type": "case_information"
    },
    {
      "data": [
        {
          "result": "Registration 20130115084854",
          "entry_number": "20130115084854",
          "submitted_via": "ТС АВ София",
          "documents_submitted": "Заявление Г2"
        }
      ],
      "type": "case_information"
    },
    {
      "data": [
        {
          "result": "Registration 20110825094222",
          "entry_number": "20110825094222",
          "documents_submitted": "Заявление А4"
        }
      ],
      "type": "case_information"
    },
    {
      "data": [
        {
          "name": "Велислава Николаева Петрова",
          "nationality": "БЪЛГАРИЯ"
        }
      ],
      "type": "beneficial_owner"
    }
  ],
  "registration_number": "201681322"
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request`library for scraping data.

## Additional Dependencies
- `Request`


## Estimated Processing Time
The processing time for the crawler is estimated 3 day.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the scrip for source 1: `python3 custom_crawlers/kyb/bulgaria/bulgaria_kyb.py`
6. Run the script for source 2: `python3 custom_crawlers/kyb/bulgaria/bulgaria_kyb2.py`