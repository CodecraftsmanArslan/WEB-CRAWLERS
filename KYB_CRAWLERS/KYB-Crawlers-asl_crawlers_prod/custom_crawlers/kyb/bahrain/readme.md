# Crawler: Bahrain

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Ministry of Industry and Commerce - Commercial Registration Portal - SIJILAT](https://www.sijilat.bh/)(https://s2.sijilat.bh/?cultLangS3=EN&menucd=A0101108). There are two crawlers, one for agencies and one for companies. The script of companies use requests module to API data in JSON format, and inserts relevant information into a PosgreSQL data table named "reports.". The script of agencies use selenium module to fetch html data, use BeautifulSoup for parsing, and inserts relevant information into a PosgreSQL data table named "reports." 

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"company_data": {
  "name": "FAKHRO SHIPPING AGENCY W.L.L",
  "type": "With Limited Liability Company",
  "status": "ACTIVE",
  "meta_detail": {
    "alias": "وكالة فخرو للملاحة المحدودة ذ.م.م",
    "expiry_date": "28-03-2024",
    "nationality": "BAHRAINI",
    "financial_year_end": "31/12"
  },
  "country_name": "Bahrain",
  "crawler_name": "custom_crawlers.kyb.bahrain.bahrain.py",
  "people_detail": [
    {
      "name": "ABDULLA YOUSIF FAKHRO & SONS B.S.C.(C)",
      "designation": "partner",
      "meta_detail": {
        "id": "1256-1",
        "name_in_arabic": "شركة عبدالله يوسف فخرو واولاده ش.م.ب مقفلة"
      },
      "nationality": "BAHRAINI"
    },
    {
      "name": "ABDULLA ESAM ABDULLA   FAKHRO",
      "designation": "authorized_person",
      "meta_detail": {
        "name_in_arabic": "عبدالله عصام عبدالله   فخرو",
        "authority_level": "Solely"
      },
      "nationality": "BAHRAINI"
    },
    {
      "name": "ADEL ABDULLA YOUSIF FAKHRO",
      "designation": "authorized_person",
      "meta_detail": {
        "name_in_arabic": "عادل عبدالله يوسف فخرو",
        "authority_level": "Solely"
      },
      "nationality": "BAHRAINI"
    },
    {
      "name": "JOHAN OLOF    FULKE",
      "designation": "authorized_person",
      "meta_detail": {
        "name_in_arabic": "",
        "authority_level": "Solely"
      },
      "nationality": "SWEDISH"
    },
    {
      "name": "MOHAMED ADEL ABDULLA FAKHRO",
      "designation": "authorized_person",
      "meta_detail": {
        "name_in_arabic": "محمد عادل عبدالله فخرو",
        "authority_level": "Solely"
      },
      "nationality": "BAHRAINI"
    },
    {
      "name": "YOUSIF ABDULLA YOUSIF FAKHRO",
      "designation": "authorized_person",
      "meta_detail": {
        "name_in_arabic": "يوسف عبدالله يوسف فخرو",
        "authority_level": "Solely"
      },
      "nationality": "BAHRAINI"
    },
    {
      "name": "ABDULLA YOUSIF FAKHRO & SONS B.S.C.(C)",
      "designation": "partner/shareholder",
      "meta_detail": {
        "share": "199",
        "name_in_arabic": "شركة عبدالله يوسف فخرو واولاده ش.م.ب مقفلة",
        "mortgagor_status": "",
        "sequester_status": "",
        "ownership_percentage": "99.50"
      },
      "nationality": "BAHRAINI"
    },
    {
      "name": "ADEL ABDULLA YOUSIF FAKHRO",
      "designation": "partner/shareholder",
      "meta_detail": {
        "share": "1",
        "name_in_arabic": "عادل عبدالله يوسف فخرو",
        "mortgagor_status": "",
        "sequester_status": "",
        "ownership_percentage": "0.50"
      },
      "nationality": "BAHRAINI"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "2, 1995, 1527, , 115, HIDD"
    },
    {
      "type": "postal_address",
      "address": "2, 1995, 1527, , 115, HIDD 5826"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "code": "522901",
          "status": "Not Restricted",
          "activites": "Cargo Clearance",
          "description": "This activity includes the activities of cargo clearance"
        },
        {
          "code": "5224-1",
          "status": "Not Restricted",
          "activites": "Cargo handling",
          "description": "Loading and unloading of goods and providing the necessary arrangements for receiving the goods or assembling them from the owner or the shipper, using vehicles that are appropriate to the nature of this activity; for example using forklifts (these vehicles are not allowed to be driven on the streets and public roads). This activity does not permit transportation of goods in any way. ,,The activities that allow transportation of goods by road are as follows:,• Road transport of goods - Internal transport of goods: International code 4923-1 ,• Road transport of goods - International transport of goods: International code 4923-2 ,,On the other hand, the below activity allows for cargo handling and freight unloading within the seaports: ,• Cargo handling - Freight and unloading services in seaports 5224-2 ,,The below activity allows for carrying out cargo handling at the airport:,The activities of air transport agencies and international freight: International code 522903"
        },
        {
          "code": "8292-1",
          "status": "Not Restricted",
          "activites": "Packaging activities",
          "description": "Includes establishments primarily engaged in providing packaging services to others such as goods packaging and preparing for shipment, and transporting them to the loading dock, sites, or final destination. It also includes the provision of packaging services for household and personal luggage or goods."
        },
        {
          "code": "71209-1",
          "status": "Not Restricted",
          "activites": "Other Testing and analysis activities",
          "description": "This activity includes testing and analysis activities not specified elsewhere"
        },
        {
          "code": "5229022",
          "status": "Not Restricted",
          "activites": "Shipping Agent",
          "description": "This activity includes international navigation lines agents who organize the marine transportation for passengers and related services. It also includes international marine agents operating in organizing carriage of goods by sea, and are authorized to book places for goods imported from abroad or export or re-exported to abroad. This includes the operations of ship chartering, leasing and operating on specific marine lines."
        },
        {
          "code": "5229021",
          "status": "Not Restricted",
          "activites": "Sea Freight Agent",
          "description": "This activity includes providing the necessary arrangement to receive or gather the goods from the owner or shipper and arrange for their carriage and facilitate the task of completing the sea transport contract between the shipper and the ocean carrier, ship owner, or the agent."
        },
        {
          "code": "8299-2",
          "status": "Not Restricted",
          "activites": "Other business support service activities - Clearance of Government Transactions",
          "description": "Offices that work in the preparation and completion of documents, personal and business transactions document to submit those documents to the governmental and non-governmental bodies and follow-up"
        },
        {
          "code": "521-1",
          "status": "Not Restricted",
          "activites": "Warehousing and storage",
          "description": "This includes: ,- operation of storage and warehouse facilities for all kind of goods: ,· operation of grain silos, general merchandise warehouses, refrigerated warehouses, storage tanks etc. ,- storage of goods in foreign trade zones ,- blast freezing"
        }
      ],
      "type": "business_activities"
    },
    {
      "data": [
        {
          "code": "7911-1",
          "name": "Travel Agencies Office",
          "local_code": "0521340",
          "description": "Travel office activities - Travel Agencies Office",
          "international_code": "630401"
        }
      ],
      "type": "old_activities_info"
    },
    {
      "data": [
        {
          "issued": "20000",
          "currency": "Bahrain Dinar",
          "authorized": "20000",
          "total_shares": "200",
          "local_investment": "20000",
          "share_nominal_value": "100",
          "paid_capital_in_cash": "20000"
        }
      ],
      "type": "capital_info"
    },
    {
      "data": [
        {
          "name": "FAKHRO SHIPPING AGENCY W.L.L",
          "status": "ACTIVE",
          "registration_date": "28-03-1964",
          "registration_number": "9-1",
          "registry_expiry_date": "28-03-2024"
        },
        {
          "name": "AHMED & ABDULLA FAKHROO",
          "status": "SOLD OR LEGAL STATUS CHANGED",
          "registration_date": "16-10-1961",
          "registration_number": "9-3",
          "registry_expiry_date": "16-10-2004"
        }
      ],
      "type": "additional_branches_info"
    }
  ],
  "registration_date": "28-03-1964",
  "registration_number": "9-1"
}
```
```json
"agency_data": {
  "name": "ABDULAZIZ ALTAMIMI & SONS",
  "type": "Partnership Company",
  "status": "ACTIVE",
  "meta_detail": {
    "alias": "عبدالعزيز التميمي واولاده",
    "period": "Limited",
    "expiry_date": "16-04-2024",
    "nationality": "BAHRAINI",
    "financial_year_end": "31/12"
  },
  "country_name": "Bahrain",
  "crawler_name": "custom_crawlers.kyb.bahrain.bahrain_ag.py",
  "people_detail": [
    {
      "name": "123123",
      "email": "12313@sdf.com",
      "address": "123123",
      "designation": "agency_agent",
      "nationality": "AFGHAN"
    },
    {
      "name": "KHALID ABDULAZIZ EBRAHIM ALTAMIMI",
      "designation": "authorized_person",
      "meta_detail": {
        "name_in_arabic": "خالد عبدالعزيز ابراهيم التميمي",
        "authority_level": "Solely"
      },
      "nationality": "BAHRAINI"
    },
    {
      "name": "JAMAL ABDULAZIZ EBRAHIM ALTIMIMI",
      "designation": "partner/shareholder",
      "meta_detail": {
        "share": "140",
        "name_in_arabic": "جمال عبدالعزيز ابراهيم التميمي",
        "mortgagor_status": "",
        "sequester_status": "",
        "ownership_percentage": "28"
      },
      "nationality": "BAHRAINI"
    },
    {
      "name": "KHALID ABDULAZIZ EBRAHIM ALTAMIMI",
      "designation": "partner/shareholder",
      "meta_detail": {
        "share": "140",
        "name_in_arabic": "خالد عبدالعزيز ابراهيم التميمي",
        "mortgagor_status": "",
        "sequester_status": "",
        "ownership_percentage": "28"
      },
      "nationality": "BAHRAINI"
    },
    {
      "name": "MUNEERA EBRAHIM FAHAD ALBASSAM",
      "designation": "partner/shareholder",
      "meta_detail": {
        "share": "80",
        "name_in_arabic": "منيره ابراهيم فهد البسام",
        "mortgagor_status": "",
        "sequester_status": "",
        "ownership_percentage": "16"
      },
      "nationality": "BAHRAINI"
    },
    {
      "name": "OSAMA ABDULAZIZ EBRAHIM ALTAMIMI",
      "designation": "partner/shareholder",
      "meta_detail": {
        "share": "140",
        "name_in_arabic": "اسامه عبدالعزيز ابراهيم التميمي",
        "mortgagor_status": "",
        "sequester_status": "",
        "ownership_percentage": "28"
      },
      "nationality": "BAHRAINI"
    }
  ],
  "contacts_detail": [
    {
      "type": "agency_mobile_number",
      "value": "(+973) 33322101"
    },
    {
      "type": "agency_email",
      "value": "khalid4good@gmail.com"
    },
    {
      "type": "agency_phone_number",
      "value": "(+973) 33322101"
    },
    {
      "type": "agency_fax_number",
      "value": "(+973) 17210757"
    }
  ],
  "addresses_detail": [
    {
      "type": "agency_general_address",
      "address": "1325, 525, 305, MANAMA CENTER / وسط المنامة"
    },
    {
      "type": "agency_postal_address",
      "address": "1325, 525, 305, MANAMA CENTER / وسط المنامة,"
    },
    {
      "type": "general_address",
      "address": "0, 1325, 525, ROAD 525, 305, MANAMA CENTER"
    },
    {
      "type": "postal_address",
      "address": "0, 1325, 525, ROAD 525, 305, MANAMA CENTER"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "code": "4659-1",
          "status": "Not Restricted",
          "activites": "Sale/Trade in other machinery and equipment and parts",
          "description": "This activity includes the wholesale and/or retail of all kind of machinery and equipment not specified elsewhere, such as:,- Office machinery and equipment, except computers and computer peripheral equipment,- Office furniture,- Renewable Energy equipment, tools, and parts, such as solar panels.,- Transport equipment except motor vehicles, motorcycles and bicycles,- Production-line robots,- Wires and switches and other installation equipment for industrial use,- Electrical material such as electrical motors, transformers,- Machine tools of any type and for any material,- other machinery for use in industry, trade and navigation and other services,- computer-controlled machine tools,- computer-controlled machinery for the textile industry and of computer-controlled sewing and knitting machines,- measuring instruments and equipment,"
        },
        {
          "code": "47592",
          "status": "Not Restricted",
          "activites": "Sale/Trade of Electrical and electronic Household appliances",
          "description": "This activity includes wholesale and/or retail trade of all kinds of electrical and electronic household appliances (Radio,TVs, Fridges...etc) It also includes the sale of light batteries used in toys and watches,"
        }
      ],
      "type": "business_activities"
    },
    {
      "data": [
        {
          "code": "7911-1",
          "name": "Travel Agencies Office",
          "local_code": "0521340",
          "description": "Travel office activities - Travel Agencies Office",
          "international_code": "630401"
        }
      ],
      "type": "old_activities_info"
    },
    {
      "data": [
        {
          "issued": "25000",
          "currency": "Bahrain Dinar",
          "authorized": "25000",
          "total_shares": "500",
          "local_investment": "25000",
          "share_nominal_value": "50",
          "paid_capital_in_cash": "25000"
        }
      ],
      "type": "capital_info"
    },
    {
      "data": [
        {
          "name": "ABDULAZIZ ALTAMIMI & SONS",
          "status": "ACTIVE",
          "registration_date": "16-04-1994",
          "registration_number": "10-1",
          "registry_expiry_date": "16-04-2024"
        }
      ],
      "type": "additional_branches_info"
    },
    {
      "data": [
        {
          "name": "ABDULAZIZ ALTAMIMI & SONS",
          "alias": "عبدالعزيز التميمي واولاده",
          "status": "ACTIVE",
          "expiry_date": "23-06-2024",
          "agency_number": "1",
          "agency_status": "ACTIVE",
          "registration_date": "25-06-2014",
          "registration_number": "10-1"
        }
      ],
      "type": "agency_detail"
    },
    {
      "data": [
        {
          "industry": "Sale/Trade in other machinery and equipment and parts",
          "products": "Welding Tools",
          "brand_codes": "345"
        },
        {
          "industry": "Sale/Trade in other machinery and equipment and parts",
          "products": "Tools Mechanical Curiosities",
          "brand_codes": "2345"
        },
        {
          "industry": "Sale/Trade in other machinery and equipment and parts",
          "products": "Mechanical Engineering Tools",
          "brand_codes": "234"
        }
      ],
      "type": "agency_products_or_services_information"
    }
  ],
  "registration_date": "16-04-1994",
  "registration_number": "10-1"
}
```

## Crawler Type
This is a web scraper crawler that uses the `requests` or `selenium` library to crawl and `BeautifulSoup` for parsing.

## Additional Dependencies
- `bs4` (BeautifulSoup)
- `requests`
- `selenium`

## Estimated Processing Time
The processing time for the crawler is estimated 20 days for companies and < one month for agencies.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 kyb_crawlers/custom_crawlers/kyb/bahrain/bahrain_co.py`
Once the script for companies end, run the following script
6. Run the script: `python3 kyb_crawlers/custom_crawlers/kyb/bahrain/bahrain_ag.py`