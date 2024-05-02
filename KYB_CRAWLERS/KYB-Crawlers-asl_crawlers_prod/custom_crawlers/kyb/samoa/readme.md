# Crawler: Samoa

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Ministry of Commerce, Industry, and Labour](https://www.businessregistries.gov.ws/samoa-br-companies/viewInstance/view.html?id=3729e4694cee83de20eb808637ff90e208ab93f1bc175da231482ef817b5b1bd&_timestamp=1569489803389829). The script use selenium to crawl, extract, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "KRAMER AUSENCO  LTD",
  "type": "Private Company",
  "status": "Registered",
  "industries": "Construction- Civil engineering",
  "meta_detail": {
    "company_rule": "Rules differ from model rules",
    "filing_month": "March",
    "last_filed_date": "15-Mar-2023",
    "re_registration_date": "03-Mar-2009"
  },
  "country_name": "Samoa",
  "crawler_name": "custom_crawlers.kyb.samoa.samoa.py",
  "people_detail": [
    {
      "name": "Toleafoa Mara COFFIN HUNTER AKA COFFIN KRAMER",
      "address": "Apia Park, Vaiala, Vaimauga Sisifo, Samoa",
      "designation": "director",
      "meta_detail": {
        "consent": "https://www.businessregistries.gov.ws/samoa-br-companies/viewInstance/resource.html?node=W1265&drmKey=a9c947c9a4d2503a&drr=ss918289c17b8434df4a610c8ac082d48e7b4e65cba54b3416877ca73aced2cdcc66b8949b6fff5f68b545a5705fc80262ux&id=3729e4694cee83de20eb808637ff90e239596fce9111bbb44aa28868578c03b3"
      },
      "postal_address": "Po Box 3641, Apia, Samoa",
      "appointment_date": "06-Aug-2018"
    },
    {
      "name": "Arthur BUDVIETAS",
      "address": "Saleufi, Vaimauga Sisifo, Samoa",
      "designation": "former_director",
      "meta_detail": {
        "consent": "https://www.businessregistries.gov.ws/samoa-br-companies/viewInstance/resource.html?node=W1147&drmKey=74ae0853fb72c63f&drr=ss918289c17b8434df4a610c8ac082d48e7b4e65cba54b3416877ca73aced2cdcc66b8949b6fff5f68b545a5705fc80262ux&id=3729e4694cee83de20eb808637ff90e239596fce9111bbb44aa28868578c03b3"
      },
      "postal_address": "P.O Box 593, Apia, Samoa",
      "appointment_date": "28-Nov-2001"
    },
    {
      "name": "Konrad LOBER",
      "address": "Talimatau, Faleata Sasae, Samoa",
      "designation": "former_director",
      "meta_detail": {
        "consent": "https://www.businessregistries.gov.ws/samoa-br-companies/viewInstance/resource.html?node=W1717&drmKey=f8ccfbebd5f99f1c&drr=ss918289c17b8434df4a610c8ac082d48e7b4e65cba54b3416877ca73aced2cdcc66b8949b6fff5f68b545a5705fc80262ux&id=3729e4694cee83de20eb808637ff90e239596fce9111bbb44aa28868578c03b3"
      },
      "postal_address": "Postal Address is the same as the Residential Address",
      "appointment_date": "01-Aug-2014"
    },
    {
      "name": "Bruce NICHOLSON",
      "address": "Not Provided, Australia",
      "designation": "former_director",
      "meta_detail": {
        "consent": "https://www.businessregistries.gov.ws/samoa-br-companies/viewInstance/resource.html?node=W1835&drmKey=deecf0b5fd7999d3&drr=ss918289c17b8434df4a610c8ac082d48e7b4e65cba54b3416877ca73aced2cdcc66b8949b6fff5f68b545a5705fc80262ux&id=3729e4694cee83de20eb808637ff90e239596fce9111bbb44aa28868578c03b3"
      },
      "postal_address": "P.O Box 593, Apia, Samoa",
      "appointment_date": "28-Nov-2001"
    },
    {
      "name": "Frank KRAMER",
      "address": "Not Provided, Australia",
      "designation": "director",
      "meta_detail": {
        "consent": "https://www.businessregistries.gov.ws/samoa-br-companies/viewInstance/resource.html?node=W1383&drmKey=deecf0b5fd7999d3&drr=ss918289c17b8434df4a610c8ac082d48e7b4e65cba54b3416877ca73aced2cdcc66b8949b6fff5f68b545a5705fc80262ux&id=3729e4694cee83de20eb808637ff90e239596fce9111bbb44aa28868578c03b3"
      },
      "postal_address": "P.O Box 593, Apia, Samoa",
      "appointment_date": "28-Nov-2001"
    },
    {
      "name": "Adam Anthony KRAMER",
      "address": "321 Swann Road, St Lucia, Qld 4067, Australia",
      "designation": "director",
      "meta_detail": {
        "consent": "https://www.businessregistries.gov.ws/samoa-br-companies/viewInstance/resource.html?node=W1501&drmKey=7e82e98d6665ad96&drr=ss918289c17b8434df4a610c8ac082d48e7b4e65cba54b3416877ca73aced2cdcc66b8949b6fff5f68b545a5705fc80262ux&id=3729e4694cee83de20eb808637ff90e239596fce9111bbb44aa28868578c03b3"
      },
      "postal_address": "Po Box 593, Apia, Samoa",
      "appointment_date": "24-Sep-2021"
    },
    {
      "name": "Michael Thomas KRAMER",
      "address": "8301/43 Forbes Street, West End, Brisnane, Qld 4101, Australia",
      "designation": "director",
      "meta_detail": {
        "consent": "https://www.businessregistries.gov.ws/samoa-br-companies/viewInstance/resource.html?node=W1609&drmKey=7528dc77e8ba2199&drr=ss918289c17b8434df4a610c8ac082d48e7b4e65cba54b3416877ca73aced2cdcc66b8949b6fff5f68b545a5705fc80262ux&id=3729e4694cee83de20eb808637ff90e239596fce9111bbb44aa28868578c03b3"
      },
      "postal_address": "Postal Address is the same as the Residential Address",
      "appointment_date": "22-May-2017"
    },
    {
      "name": "KRAMER AUSENCO PACIFIC PTY LIMITED",
      "address": "Not Provided, Australia",
      "designation": "shareholder",
      "appointment_date": "28-Nov-2001"
    },
    {
      "name": "Frank KRAMER",
      "address": "Not Provided, Australia",
      "designation": "shareholder",
      "appointment_date": "28-Nov-2001"
    },
    {
      "name": "KRAMER AUSENCO PACIFIC PTY LIMITED",
      "designation": "shareholder",
      "meta_detail": {
        "number_of_share": "999"
      }
    },
    {
      "name": "Frank KRAMER",
      "designation": "shareholder",
      "meta_detail": {
        "number_of_share": "1"
      }
    }
  ],
  "contacts_detail": [
    {
      "type": "email",
      "value": "arpenn@lesamapenn.ws"
    },
    {
      "type": "phone_number",
      "value": "(685) 20321"
    },
    {
      "type": "fax",
      "value": "(685) 21335"
    }
  ],
  "fillings_detail": [
    {
      "date": "15-Mar-2023",
      "title": "FORM 12 ANNUAL RETURN",
      "meta-detail": {
        "submission_date": "15-Mar-2023"
      }
    },
    {
      "date": "26-Mar-2022",
      "title": "FORM 12 ANNUAL RETURN",
      "meta-detail": {
        "submission_date": "24-Mar-2022"
      }
    },
    {
      "date": "07-Oct-2021",
      "title": "FORM 10 NOTICE OF CHANGE OF DIRECTORS OR DIRECTOR DETAILS",
      "meta-detail": {
        "submission_date": "07-Oct-2021"
      }
    },
    {
      "date": "29-Sep-2021",
      "title": "FORM 10 NOTICE OF CHANGE OF DIRECTORS OR DIRECTOR DETAILS",
      "meta-detail": {
        "submission_date": "29-Sep-2021"
      }
    },
    {
      "date": "22-Mar-2021",
      "title": "FORM 12 ANNUAL RETURN",
      "meta-detail": {
        "submission_date": "22-Mar-2021"
      }
    },
    {
      "date": "06-Mar-2020",
      "title": "FORM 12 ANNUAL RETURN",
      "meta-detail": {
        "submission_date": "06-Mar-2020"
      }
    },
    {
      "date": "08-Mar-2019",
      "title": "FORM 12 ANNUAL RETURN",
      "meta-detail": {
        "submission_date": "08-Mar-2019"
      }
    },
    {
      "date": "11-Jan-2019",
      "title": "FORM 10 NOTICE OF CHANGE OF DIRECTORS OR DIRECTOR DETAILS",
      "meta-detail": {
        "submission_date": "09-Jan-2019"
      }
    },
    {
      "date": "07-Dec-2018",
      "title": "FORM 6 NOTICE OF CHANGE OF REGISTERED OFFICE OR POSTAL ADDRESS",
      "meta-detail": {
        "submission_date": "06-Dec-2018"
      }
    },
    {
      "date": "15-Aug-2018",
      "title": "FORM 10 NOTICE OF CHANGE OF DIRECTORS OR DIRECTOR DETAILS",
      "meta-detail": {
        "submission_date": "10-Aug-2018"
      }
    },
    {
      "date": "05-Mar-2018",
      "title": "FORM 12 ANNUAL RETURN",
      "meta-detail": {
        "submission_date": "05-Mar-2018"
      }
    },
    {
      "date": "09-Aug-2017",
      "title": "FORM 10 NOTICE OF CHANGE OF DIRECTORS OR DIRECTOR DETAILS",
      "meta-detail": {
        "submission_date": "08-Aug-2017"
      }
    },
    {
      "date": "17-Mar-2017",
      "title": "FORM 12 ANNUAL RETURN",
      "meta-detail": {
        "submission_date": "15-Mar-2017"
      }
    },
    {
      "date": "09-Mar-2015",
      "title": "FORM 12 ANNUAL RETURN",
      "meta-detail": {
        "submission_date": "05-Mar-2015"
      }
    },
    {
      "date": "08-Aug-2014",
      "title": "FORM 10 NOTICE OF CHANGE OF DIRECTORS OR DIRECTOR DETAILS",
      "meta-detail": {
        "submission_date": "08-Aug-2014"
      }
    },
    {
      "date": "07-Aug-2014",
      "title": "FORM 10 NOTICE OF CHANGE OF DIRECTORS OR DIRECTOR DETAILS",
      "meta-detail": {
        "submission_date": "07-Aug-2014"
      }
    },
    {
      "date": "10-Apr-2014",
      "title": "FORM 10 NOTICE OF CHANGE OF DIRECTORS OR DIRECTOR DETAILS",
      "meta-detail": {
        "submission_date": "10-Apr-2014"
      }
    },
    {
      "date": "20-Mar-2014",
      "title": "FORM 12 ANNUAL RETURN",
      "meta-detail": {
        "submission_date": "20-Mar-2014"
      }
    },
    {
      "date": "06-Mar-2013",
      "title": "FORM 12 ANNUAL RETURN",
      "meta-detail": {
        "submission_date": "06-Mar-2013"
      }
    },
    {
      "date": "28-Nov-2001",
      "title": "FORM 1 APPLICATION FOR INCORPORATION OF COMPANY",
      "meta-detail": {
        "submission_date": "15-Feb-2013"
      }
    }
  ],
  "addresses_detail": [
    {
      "type": "office_address",
      "address": "First Floor, Le Alaimoana Hotel Complex, Apia Park, East Coast Rd, Vaimauga Sisifo, Samoa",
      "meta_detail": {
        "start_date": "13-Dec-2018"
      }
    },
    {
      "type": "postal_address",
      "address": "P. O. Box 593, Apia, Samoa",
      "meta_detail": {
        "start_date": "28-Nov-2001"
      }
    },
    {
      "type": "service_address",
      "address": "Same as Registered Office Address",
      "meta_detail": {
        "start_date": "28-Nov-2001"
      }
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "total_shares": "1000",
          "more_than_one_class": "No",
          "extensive_shareholding": "No"
        }
      ],
      "type": "share_information"
    }
  ],
  "incorporation_date": "28-Nov-2001",
  "registration_number": "0164"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library to crawl and extract required information.

## Additional Dependencies
- `selenium`

## Estimated Processing Time
The processing time for the crawler is estimated < one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/samoa/samoa.py`