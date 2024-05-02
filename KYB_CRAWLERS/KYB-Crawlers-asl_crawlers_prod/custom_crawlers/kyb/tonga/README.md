# Crawler: Tonga

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Business Registries Office](https://www.businessregistries.gov.to/tonga-master/viewInstance/view.html?id=68611da4d66d5171951e99d252c458288ad0d0183ce5bee4&_timestamp=8720001250345005). The script utilizes Selenium to extract data from web pages indexed between a to z and 0 to 9, as part of the search process, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "'AMANAKI LELEI COMPANY LIMITED",
  "status": "Registered",
  "tax_number": "465889",
  "meta_detail": {
    "filing_month": "November",
    "have_own_rules": "No",
    "last_filed_date": "11-22-2022"
  },
  "country_name": "Tonga",
  "crawler_name": "custom_crawlers.kyb.tonga.tonga_kyb.py",
  "people_detail": [
    {
      "name": "Ofa Ki La'Ie LISALA",
      "address": "Veitongo, Tongatapu, Tonga",
      "designation": "director",
      "meta_detail": {
        "consent": "This person has consented to act as a director for this company",
        "appointment_date": "03-06-2012"
      }
    },
    {
      "name": "Ofa Ki La'Ie LISALA",
      "address": "Veitongo, Tongatapu, Tonga",
      "designation": "shareholder",
      "meta_detail": {
        "also_a_director": "No",
        "appointment_date": "03-06-2012"
      }
    },
    {
      "name": "Ding Zhao LI",
      "address": "Veitongo, Tongatapu, Tonga",
      "designation": "shareholder",
      "meta_detail": {
        "also_a_director": "No",
        "appointment_date": "03-06-2012"
      }
    }
  ],
  "fillings_detail": [
    {
      "date": "11-22-2022",
      "title": "ANNUAL RETURN (FORM 4)",
      "file_url": "https://www.businessregistries.gov.to/tonga-companies/viewInstance/view.html?id=96f72855028835040a4b6049f18a01ad6747b46ef505cd95&_timestamp=1212429264203886#",
      "meta_detail": {
        "submission_date": "11-22-2022"
      }
    },
    {
      "date": "11-15-2021",
      "title": "ANNUAL RETURN (FORM 4)",
      "file_url": "https://www.businessregistries.gov.to/tonga-companies/viewInstance/view.html?id=96f72855028835040a4b6049f18a01ad6747b46ef505cd95&_timestamp=1212429264203886#",
      "meta_detail": {
        "submission_date": "11-15-2021"
      }
    },
    {
      "date": "11-24-2020",
      "title": "ANNUAL RETURN (FORM 4)",
      "file_url": "https://www.businessregistries.gov.to/tonga-companies/viewInstance/view.html?id=96f72855028835040a4b6049f18a01ad6747b46ef505cd95&_timestamp=1212429264203886#",
      "meta_detail": {
        "submission_date": "11-24-2020"
      }
    },
    {
      "date": "06-16-2020",
      "title": "REGISTRAR NOTICE OF CHANGE OF STATUS",
      "file_url": "https://www.businessregistries.gov.to/tonga-companies/viewInstance/view.html?id=96f72855028835040a4b6049f18a01ad6747b46ef505cd95&_timestamp=1212429264203886#",
      "meta_detail": {
        "submission_date": "06-16-2020"
      }
    },
    {
      "date": "06-01-2020",
      "title": "REGISTRAR'S NOTICE OF REMOVAL",
      "file_url": "https://www.businessregistries.gov.to/tonga-companies/viewInstance/view.html?id=96f72855028835040a4b6049f18a01ad6747b46ef505cd95&_timestamp=1212429264203886#",
      "meta_detail": {
        "submission_date": "06-01-2020"
      }
    },
    {
      "date": "07-08-2019",
      "title": "REGISTRAR NOTICE OF CHANGE OF STATUS",
      "file_url": "https://www.businessregistries.gov.to/tonga-companies/viewInstance/view.html?id=96f72855028835040a4b6049f18a01ad6747b46ef505cd95&_timestamp=1212429264203886#",
      "meta_detail": {
        "submission_date": "07-08-2019"
      }
    },
    {
      "date": "06-01-2019",
      "title": "REGISTRAR'S NOTICE OF REMOVAL",
      "file_url": "https://www.businessregistries.gov.to/tonga-companies/viewInstance/view.html?id=96f72855028835040a4b6049f18a01ad6747b46ef505cd95&_timestamp=1212429264203886#",
      "meta_detail": {
        "submission_date": "06-01-2019"
      }
    },
    {
      "date": "05-24-2018",
      "title": "ANNUAL RETURN (FORM 4)",
      "file_url": "https://www.businessregistries.gov.to/tonga-companies/viewInstance/view.html?id=96f72855028835040a4b6049f18a01ad6747b46ef505cd95&_timestamp=1212429264203886#",
      "meta_detail": {
        "submission_date": "05-24-2018"
      }
    },
    {
      "date": "06-15-2017",
      "title": "REGISTRAR NOTICE OF CHANGE OF STATUS",
      "file_url": "https://www.businessregistries.gov.to/tonga-companies/viewInstance/view.html?id=96f72855028835040a4b6049f18a01ad6747b46ef505cd95&_timestamp=1212429264203886#",
      "meta_detail": {
        "submission_date": "06-15-2017"
      }
    },
    {
      "date": "06-01-2017",
      "title": "REGISTRAR'S NOTICE OF REMOVAL",
      "file_url": "https://www.businessregistries.gov.to/tonga-companies/viewInstance/view.html?id=96f72855028835040a4b6049f18a01ad6747b46ef505cd95&_timestamp=1212429264203886#",
      "meta_detail": {
        "submission_date": "06-01-2017"
      }
    },
    {
      "date": "05-17-2016",
      "title": "ANNUAL RETURN (FORM 4)",
      "file_url": "https://www.businessregistries.gov.to/tonga-companies/viewInstance/view.html?id=96f72855028835040a4b6049f18a01ad6747b46ef505cd95&_timestamp=1212429264203886#",
      "meta_detail": {
        "submission_date": "05-17-2016"
      }
    },
    {
      "date": "06-10-2014",
      "title": "2013 ANNUAL RETURN",
      "file_url": "https://www.businessregistries.gov.to/tonga-companies/viewInstance/view.html?id=96f72855028835040a4b6049f18a01ad6747b46ef505cd95&_timestamp=1212429264203886#",
      "meta_detail": {
        "submission_date": "06-10-2014"
      }
    },
    {
      "date": "03-06-2012",
      "title": "NEW COMPANY REGISTRATION",
      "file_url": "https://www.businessregistries.gov.to/tonga-companies/viewInstance/view.html?id=96f72855028835040a4b6049f18a01ad6747b46ef505cd95&_timestamp=1212429264203886#",
      "meta_detail": {
        "submission_date": "03-06-2012"
      }
    }
  ],
  "addresses_detail": [
    {
      "type": "office_address",
      "address": "Veitongo, Tongatapu, Tonga",
      "meta_detail": {
        "effective_date": "03-06-2012"
      }
    },
    {
      "type": "service_address",
      "address": "Veitongo, Tongatapu, Tonga",
      "meta_detail": {
        "effective_date": "03-06-2012"
      }
    },
    {
      "type": "communication_address",
      "address": "Veitongo, Tongatapu, Tonga",
      "meta_detail": {
        "effective_date": "03-06-2012"
      }
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "total_shares": "100",
          "more_than_one_class": "No"
        }
      ],
      "type": "share_information"
    }
  ],
  "registration_date": "03-06-2012",
  "incorporation_date": "03-06-2012",
  "registration_number": "9005361"
}
```


## Crawler Type
This is a web scraper crawler that uses the `Selenium` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Selenium`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler's processing time is estimated to be approximately one week.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/tonga/tonga_kyb.py`