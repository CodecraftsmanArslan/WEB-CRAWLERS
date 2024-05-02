# Crawler: District of Columbia

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Department of Consumer and Regulatory Affairs](https://opendata.dc.gov/datasets/DCGIS::basic-business-licenses/explore). There are two sources exist in this country source one contain business licenses data and source two contain business enterprise. Both the script fetches data from the specified API endpoint, inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"Source one"
"data":{
  "name": "BIOS LLC; Stephen Tarbuck",
  "meta_detail": {
    "in_state": "Y",
    "customer_id": "400314901149",
    "database_id": "198715048",
    "last_updated": "2023-05-30 14:22:03"
  },
  "country_name": "District of Columbia",
  "crawler_name": "custom_crawlers.kyb.district_columbia.district_columbia_kyb1",
  "people_detail": [
    {
      "last_name": "",
      "first_name": "",
      "designation": "registered_agent",
      "entity_name": "BIOS LLC; NA",
      "middle_name": "",
      "phone_number": "202-683-7510"
    }
  ],
  "addresses_detail": [
    {
      "type": "billing_address",
      "address": "413 8th St. SE Washington  DC 20003 ",
      "meta_detail": {
        "billing_name": "",
        "building_number": "2nd Floor"
      }
    },
    {
      "type": "general_address",
      "address": "413 8TH ST SE  Washington  DC 20003",
      "meta_detail": {
        "ward": "149575.0",
        "district": "6B03",
        "latitude": "1685438523000",
        "longitude": "38.88325459",
        "x_coordinates": "-76.99527559",
        "y_coordinates": "400409.91",
        "master_address": "",
        "police_service_area": "FIRST",
        "neighborhood_cluster": "106",
        "single_member_district": "ANC 6B",
        "business_improvement_district": "Cluster 26",
        "advisory_neighborhood_commission": "6"
      }
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "status": "Abandoned",
          "end_date": "2017-12-31 10:00:00",
          "issue_date": "2022-09-06 09:00:00",
          "start_date": "2016-01-01 10:00:00",
          "sub_category": "General Business Licenses",
          "category_code": "4003",
          "license_number": "400314901149",
          "parent_category": "General Business",
          "tracking_number": "20003",
          "last_modification_date": "1970-01-04 01:46:45.473000"
        }
      ],
      "type": "license_information"
    }
  ],
  "registration_number": "400314901149"
}

"Source Two"
"data":{
  "name": "AFC Management Services",
  "type": "Corporation",
  "meta_detail": {
    "category": "Local Business Enterprise (LBE);Disadvantaged Business Enterprise (DBE);Small Business Enterprise (SBE);Resident Owned Business (ROB);",
    "description": "Aerobodies Inc. dba: AFC Management Services, is an 8(a) Certified, woman-owned small business founded in 1997. AFC provides clients with mission critical, enterprise-level, business and technical support services, across all sectors of the supply chain. Most notably, AFC provides full-service program management, health facilities support and communications services for federal, state and local government as well as the private sector.\r\n\r\nPROGRAM MANAGEMENT AFC specializes in all levels of program management and staff augmentation. Our Operational and Staffing Support areas include: Healthcare, Technology, Logistics and Facilities Support, Financial Services, Acquisition Support and Administration. AFC prequalifies all licensed-professional technicians with rigorous background clearance checks, certification and education verification processes. Certified personnel include emergency service personnel, medical and mental health specialists, occupationaland safety officers and CMMI level technicians.\r\n\r\nFACILITIES SUPPORT SERVICES In its 20-year history AFC has managed over 200,000 employee lives in emergency response, military installations, wellness and healthcare-medical facilities; providing supply chain management and logistics services. AFC has never had a contract cancelled and has maintained the majority of our customers for over 7 years of service. AFC currently manages successful facility operationsfor DOD,DOS, SEC, DOT, and multipleprivate sectorcustomers.\r\n\r\nPROFESSIONAL DEVELOPMENT, TRAINING & EDUCATIONAL SUPPORT Customized and Off-the-Shelf Training, Coaching and Facilitation Solutions are at the core of our business suite of services. Our team of professionals includes education experts, coaches, PHDs, and organizational consultants. These subject matter experts will work closely with your agency leadership to assess and implement training solutions that meet mission requirements and create positive outcomes in communication, organizational development ",
    "certificates": "SBA",
    "proposal_points": "12.0",
    "bid_price_reduction": ".12",
    "gis_last_modified_date": "2023-05-31 10:15:35",
    "small_business_enterprise": "Yes"
  },
  "country_name": "District of Columbia",
  "crawler_name": "custom_crawlers.kyb.district_columbia.district_columbia_kyb2",
  "people_detail": [
    {
      "name": "Frances Dean-Bishop",
      "designation": "principal_owner"
    }
  ],
  "contacts_detail": [
    {
      "type": "email",
      "value": "franb@aerobodies.com",
      "meta_detail": {
        "contact_name": "Frances Dean-Bishop"
      }
    },
    {
      "type": "phone_number",
      "value": "7034028477"
    },
    {
      "type": "website_link",
      "value": "www.aerobodies.com"
    }
  ],
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "1875 K STREET NW Washington DC 20006",
      "meta_detail": {
        "ward": "2.0",
        "latitude": "38.90280597",
        "longitude": "-77.04304382",
        "x_coordinates": "396266.36",
        "y_coordinates": "137217.63",
        "master_address_repository_identifier": "279444.0"
      }
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "end_date": "2024-11-29 05:00:00",
          "start_date": "2021-11-29 05:00:00"
        }
      ],
      "type": "license_information"
    }
  ],
  "registration_date": "1997-10-01 05:00:00",
  "incorporation_date": "2021-11-29 05:00:00",
  "registration_number": "LSDRE91777112024"
}
```

## Crawler Type
This is a web scraper crawler that uses the `Request` and`Pandas` libraries for scraping.

## Additional Dependencies
- `Request`
- `pandas` 

## Estimated Processing Time
The processing time for the both source is estimated 1 day.


## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Set up a virtual environment if necessary.
3. Set the necessary environment variables in a `.env` file.
4. Run the scrip for source 1: `python3 custom_crawlers/kyb/district_columbia/district_columbia_kyb1.py`
5. Run the script for source 2: `python3 custom_crawlers/kyb/district_columbia/district_columbia_kyb2.py`
