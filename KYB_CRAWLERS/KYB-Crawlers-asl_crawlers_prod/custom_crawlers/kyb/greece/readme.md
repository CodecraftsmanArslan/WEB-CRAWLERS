# Crawler: Greece

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Chamber of Commerce greeces](https://web.caymanchamber.ky/allcategories). The script use API endpoints to fetch data in JSON format, extract data, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "TASTY BANK Ιδιωτική Κεφαλαιουχική Εταιρία",
  "type": "PC",
  "status": "Active",
  "tax_number": "800880861",
  "meta_detail": {
    "eu_id": "ELGEMI.143837804000",
    "name_in_latin": "TASTY BANK Idiotiki Kefalaiouchiki Etairia"
  },
  "country_name": "Greece",
  "crawler_name": "custom_crawlers.kyb.greece.greece.py",
  "people_detail": [
    {
      "name": "IOANNIS TSATSANIDIS",
      "designation": "member",
      "meta_detail": {
        "status": "Active",
        "authority": "Member & Administrator",
        "ownership": 95,
        "appointment_period": "10-04-2017 -"
      }
    },
    {
      "name": "SOFIA TSATSANIDOU",
      "designation": "member",
      "meta_detail": {
        "status": "Active",
        "authority": "Partner - Member",
        "ownership": 5,
        "appointment_period": "10-04-2017 -"
      }
    }
  ],
  "contacts_detail": [
    {
      "type": "website",
      "value": "www.tastybank.gr"
    },
    {
      "type": "email",
      "value": "info@tastybank.gr"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "GIANNITSON 31, THESSALONIKIS / THESSALONIKIS, 54627"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "name": "TASTY BANK I.K.E. (rendered in Latin characters)"
        },
        {
          "name": "TASTY BANK Ι.Κ.Ε."
        }
      ],
      "type": "aliases_info"
    },
    {
      "data": [
        {
          "name": "TASTY BANK Ι.Κ.Ε.",
          "status": "Active"
        },
        {
          "name": "TASTY BANK I.K.E. (rendered in Latin characters)",
          "status": "Active"
        }
      ],
      "type": "distinctive_titles_detail"
    },
    {
      "data": [
        {
          "capital": 15000,
          "currency": "EUR",
          "share_type": "Capital",
          "share_value": 1,
          "number_of_shares": "15000"
        }
      ],
      "type": "capital_info"
    },
    {
      "data": [
        {
          "KAD_Type": "Κύρια",
          "KAD_code": "46.37.1",
          "KAD_description": "WHOLESALE OF COFFEE, TEA, COCOA AND SPICES"
        },
        {
          "KAD_Type": "Κύρια",
          "KAD_code": "46.37.10",
          "KAD_description": "WHOLESALE OF COFFEE, TEA, COCOA AND SPICES"
        },
        {
          "KAD_Type": "Δευτερεύουσα",
          "KAD_code": "46.32.11.16",
          "KAD_description": "WHOLESALE OF FRESH AND FROZEN MEAT"
        },
        {
          "KAD_Type": "Δευτερεύουσα",
          "KAD_code": "66.19.91",
          "KAD_description": "FINANCIAL ADVISORY SERVICES"
        },
        {
          "KAD_Type": "Δευτερεύουσα",
          "KAD_code": "46.33.13",
          "KAD_description": "WHOLESALE OF EDIBLE OILS AND FATS"
        },
        {
          "KAD_Type": "Δευτερεύουσα",
          "KAD_code": "46.17.11.24",
          "KAD_description": "COMMERCIAL AGENTS ACTING AS INTERMEDIARIES IN THE SALE OF TEA AND COFFEE"
        },
        {
          "KAD_Type": "Δευτερεύουσα",
          "KAD_code": "47.29.22",
          "KAD_description": "RETAIL SALE OF EDIBLE OILS AND FATS"
        },
        {
          "KAD_Type": "Δευτερεύουσα",
          "KAD_code": "47.22.13",
          "KAD_description": "RETAIL TRADE IN MEAT"
        },
        {
          "KAD_Type": "Δευτερεύουσα",
          "KAD_code": "01.24",
          "description": "Το χονδρικό εμπόριο καφέ, τσαγιού, Κακάου και μπαχαρικών ( ΚΑΔ 46.37.10.00 ), το χονδρικό εμπόριο Νωπών και κατεψυγμένων κρεάτων ( ΚΑΔ 46.32.11.16 ), η εμπορική αντιπροσώπευση στην πώληση Τσαγιού και καφέ ( ΚΑΔ 46.17.11.24 ), το χονδρικό εμπόριο βρώσιμων ελαίων και λιπών ( ΚΑΔ 46.33.13.24 ), το Λιανικό εμπόριο βρώσιμων ελαίων και λιπών ( ΚΑΔ 47.29.22.00 ), το Λιανικό εμπόριο κρέατος ( ΚΑΔ 47.22.13.00 ), η καλλιέργεια μηλοειδών και πυρηνόκαρπων ( ΚΑΔ 01.24.00.00 ) και Υπηρεσίες παροχής Χρηματοοικονομικών Συμβουλών ( ΚΑΔ 66.19.91.00 ) , καθώς και άλλες συναφείς με τις παραπάνω δραστηριότητες.",
          "KAD_description": "CULTIVATION OF APPLE AND STONE FRUIT"
        }
      ],
      "type": "activity_info"
    },
    {
      "data": [
        {
          "url": "https://publicity.businessportal.gr/api/download/financial/1293932",
          "title": "ΕΚΘΕΣΗ ΔΙΑΧΕΙΡΗΣΗΣ ΧΡΗΣΗΣ 2021 TASTY BANK IKE.pdf",
          "submission_date": "30-11-2022",
          "reporting_period": "01-01-2021 - 31-12-2021"
        },
        {
          "url": "https://publicity.businessportal.gr/api/download/financial/1293933",
          "title": "ΠΡΟΣΑΡΤΗΜΑ ΧΡΗΣΗΣ ΚΑΙ ΙΣΟΛΟΓΙΣΜΟΣ ΧΡΗΣΗ 2021 TASTY BANK IKE.pdf",
          "submission_date": "30-11-2022",
          "reporting_period": "01-01-2021 - 31-12-2021"
        },
        {
          "url": "https://publicity.businessportal.gr/api/download/financial/1293930",
          "title": "ΕΚΘΕΣΗ ΔΙΑΧΕΙΡΗΣΗΣ ΧΡΗΣΗΣ 2020 TASTY BANK IKE.pdf",
          "submission_date": "30-11-2022",
          "reporting_period": "01-01-2020 - 31-12-2020"
        },
        {
          "url": "https://publicity.businessportal.gr/api/download/financial/1293931",
          "title": "ΠΡΟΣΑΡΤΗΜΑ ΧΡΗΣΗΣ ΚΑΙ ΙΣΟΛΟΓΙΣΜΟΣ ΧΡΗΣΗ 2020 TASTY BANK IKE.pdf",
          "submission_date": "30-11-2022",
          "reporting_period": "01-01-2020 - 31-12-2020"
        },
        {
          "url": "https://publicity.businessportal.gr/api/download/financial/723027",
          "title": "ΕΚΘΕΣΗ ΔΙΑΧΕΙΡΗΣΗΣ ΧΡΗΣΗΣ 2019 TASTY BANK IKE.pdf",
          "submission_date": "19-11-2020",
          "reporting_period": "01-01-2019 - 31-12-2019"
        },
        {
          "url": "https://publicity.businessportal.gr/api/download/financial/723028",
          "title": "ΠΡΟΣΑΡΤΗΜΑ ΧΡΗΣΗΣ ΚΑΙ ΙΣΟΛΟΓΙΣΜΟΣ ΧΡΗΣΗ 2019 TASTY BANK IKE.pdf",
          "submission_date": "19-11-2020",
          "reporting_period": "01-01-2019 - 31-12-2019"
        },
        {
          "url": "https://publicity.businessportal.gr/api/download/financial/534366",
          "title": "ΕΚΘΕΣΗ ΔΙΑΧΕΙΡΗΣΗΣ ΧΡΗΣΗΣ 2018 TASTY BANK IKE.pdf",
          "submission_date": "08-11-2019",
          "reporting_period": "01-01-2018 - 31-12-2018"
        },
        {
          "url": "https://publicity.businessportal.gr/api/download/financial/534367",
          "title": "ΠΡΟΣΑΡΤΗΜΑ ΧΡΗΣΗΣ ΚΑΙ ΙΣΟΛΟΓΙΣΜΟΣ ΧΡΗΣΗ 2018 TASTY BANK IKE.pdf",
          "submission_date": "08-11-2019",
          "reporting_period": "01-01-2018 - 31-12-2018"
        }
      ],
      "type": "financial_statements"
    },
    {
      "data": [
        {
          "chamber_phone": "2310370100",
          "chamber_webiste": "http://www.ebeth.gr/",
          "shipping_service": "CHAMBER OF COMMERCE & INDUSTRY OF THESSALONIKI",
          "chamber_department": "Commercial",
          "chamber_registry_number": "61454",
          "chamber_registration_date": "10-04-2017"
        }
      ],
      "type": "competent_local_service_info"
    }
  ],
  "registration_date": "10-04-2017",
  "registration_number": "143837804000",
  "announcements_detail": [
    {
      "date": "30-11-2022",
      "description": "Announcement of the entry of the Minutes of the General Meeting of Shareholders for the approval and publication of the Financial Statements",
      "meta_detail": {
        "url": "https://publicity.businessportal.gr/api/download/Modifications/3341922"
      }
    },
    {
      "date": "30-11-2022",
      "description": "Announcement of the entry of the Minutes of the General Meeting of Shareholders for the approval and publication of the Financial Statements",
      "meta_detail": {
        "url": "https://publicity.businessportal.gr/api/download/Modifications/3341923"
      }
    },
    {
      "date": "19-11-2020",
      "description": "Announcement of the entry of the Minutes of the General Meeting of Shareholders for the approval and publication of the Financial Statements",
      "meta_detail": {
        "url": "https://publicity.businessportal.gr/api/download/Modifications/2376087"
      }
    },
    {
      "date": "11-08-2019",
      "description": "Announcement of the entry of the Minutes of the General Meeting of Shareholders for the approval and publication of the Financial Statements",
      "meta_detail": {
        "url": "https://publicity.businessportal.gr/api/download/Modifications/1964693"
      }
    },
    {
      "date": "20-09-2018",
      "description": "Announcement of the entry of the Minutes of the General Meeting of Shareholders for the approval and publication of the Financial Statements",
      "meta_detail": {
        "url": "https://publicity.businessportal.gr/api/download/Modifications/1482742"
      }
    },
    {
      "date": "12-11-2017",
      "description": "Website registration",
      "meta_detail": {
        "url": "https://publicity.businessportal.gr/api/download/Modifications/1271637"
      }
    },
    {
      "date": "12-11-2017",
      "description": "Announcement of certification of payment of share capital",
      "meta_detail": {
        "url": "https://publicity.businessportal.gr/api/download/Modifications/1271677"
      }
    }
  ]
}
```

## Crawler Type
This is a web scraper crawler that uses the `requests` library to fetch JSON data and extract required information.

## Additional Dependencies
- `requests`

## Estimated Processing Time
The processing time for the crawler is estimated > one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/greece/greece.py`