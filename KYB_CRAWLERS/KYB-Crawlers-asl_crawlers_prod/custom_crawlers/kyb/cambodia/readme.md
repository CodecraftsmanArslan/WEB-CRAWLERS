# Crawler: Cambodia

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Cambodia Ministry of Commerce](https://www.businessregistration.moc.gov.kh/). The script use selenium module to crawl website, use BeautifulSoup for parsing, and inserts relevant information into a PosgreSQL data table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "ZHONG TE JIAN ZHU (CAMBODIA) CO., LTD.",
  "type": "Private Limited Company",
  "status": "Registered",
  "tax_number": "L001-901905011",
  "meta_detail": {
    "aliases": "ហ្សុង តេ ជាន ហ៊្សូ (ខេមបូឌា) ឯ.ក",
    "tax_registration date": "03-Jul-2020",
    "last_annual_return_filed": "21-Jan-2021",
    "previous_registration_number": " "
  },
  "country_name": "Cambodia",
  "crawler_name": "custom_crawlers.kyb.cambodia.cambodia.py",
  "people_detail": [
    {
      "name": "Ren, HONGKANG",
      "address": "159-112 Kunyu Jiuli, Hong Qiao, Yushan Town, Xian Shan City, Jiang Su Province, China, China",
      "designation": "director",
      "phone_number": "(+855) [No Area Code]-010239380"
    },
    {
      "name": "Liu, WEI",
      "address": "Xushen Group 3, Weiji Town, Shang Shui County, Henan Province, China, China",
      "designation": "director",
      "phone_number": "(+855) [No Area Code]-010239380"
    },
    {
      "name": "Pan, YONGWU",
      "address": "On1003, Heaven and Earth Huacheng, Road 1188, Former, Xian Shan City, Jiang su Province, China, China",
      "designation": "director",
      "phone_number": "(+855) [No Area Code]-010239380"
    }
  ],
  "contacts_detail": [
    {
      "type": "email",
      "value": "dept.br@moc.gov.kh"
    },
    {
      "type": "phone_number",
      "value": "(+855) [No Area Code]-010239380"
    }
  ],
  "addresses_detail": [
    {
      "type": "Office_address",
      "address": "(Currently: # 129E0E1, Street 09, Kraing Svay Village, Sangkat Prek Kampus, Khan Dangkor, Phnom Penh.), None, Phum Krang Svay, Krang Pongro, Dangkao, Phnom Penh, 12412, Cambodia"
    },
    {
      "type": "postal_address",
      "address": "Postal Address is the same as the Registered Office Address"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "objectives": "410 Construction of buildings",
          "main_activities": "41001 Residential buildings(2)"
        },
        {
          "objectives": "410 Construction of buildings",
          "main_activities": "41002 Non-residential buildings(3)"
        },
        {
          "objectives": "421 Construction of roads and railways",
          "main_activities": "42101 Construction of streets, roads, bridges and tunnels(2)"
        },
        {
          "objectives": "421 Construction of roads and railways",
          "main_activities": "42102 Construction of railways"
        },
        {
          "objectives": "422 Construction of utility projects",
          "main_activities": "42201 Construction of utility projects for water, sewage, oil and gas"
        },
        {
          "objectives": "422 Construction of utility projects",
          "main_activities": "42202 Construction of utility projects for electricity and telecommunications"
        },
        {
          "objectives": "429 Construction of other civil engineering projects",
          "main_activities": "42900 Construction of waterways, harbours, dams and other civil engineering projects, except buildings"
        },
        {
          "objectives": "465 Wholesale of machinery, equipment and supplies",
          "main_activities": "46529 Wholesale of other electronic equipment(5)"
        },
        {
          "objectives": "465 Wholesale of machinery, equipment and supplies",
          "main_activities": "46531 Wholesale of agricultural machinery, equipment and supplies(2)"
        },
        {
          "objectives": "466 Other specialized wholesale",
          "main_activities": "46633 Wholesale of construction materials & tools(3)"
        },
        {
          "objectives": "466 Other specialized wholesale",
          "main_activities": "46634 Wholesale of fittings and fixtures"
        },
        {
          "objectives": "466 Other specialized wholesale",
          "main_activities": "46644 Wholesale of plastic materials in primary forms"
        },
        {
          "objectives": "451 Sale of motor vehicles",
          "main_activities": "45101 Wholesale and retail of new motor vehicles"
        },
        {
          "objectives": "451 Sale of motor vehicles",
          "main_activities": "45102 Wholesale and retail of used motor vehicles"
        },
        {
          "objectives": "452 Maintenance and repair of motor vehicles",
          "main_activities": "45201 Maintenance and repair of motor vehicles including towing"
        },
        {
          "objectives": "453 Sale of motor vehicle parts and accessories",
          "main_activities": "45300 Wholesale and retail sale of all kinds of parts, components, supplies, tools and accessories for motor vehicles(5)"
        },
        {
          "objectives": "469 Non-specialized wholesale trade",
          "main_activities": "46900 Wholesale of a variety of goods without any particular specialization n.e.c."
        },
        {
          "objectives": "492 Other land transport",
          "main_activities": "49230 Freight transport by road"
        },
        {
          "objectives": "551 Short term accommodation activities",
          "main_activities": "55101 Hotels and resort hotels"
        },
        {
          "objectives": "561 Restaurants and mobile food service activities",
          "main_activities": "56101 Restaurants and restaurant cum night clubs"
        },
        {
          "objectives": "631 Data processing, hosting and related activities; web portals",
          "main_activities": "63110 Data processing, hosting and related activities(1)"
        },
        {
          "objectives": "631 Data processing, hosting and related activities; web portals",
          "main_activities": "63120 Web portals(2)"
        },
        {
          "objectives": "682 Real estate activities on a fee or contract basis",
          "main_activities": "68201 Activities of real estate agents and brokers(5)"
        },
        {
          "objectives": "682 Real estate activities on a fee or contract basis",
          "main_activities": "68202 Management of real estate on a fee or contract basis"
        },
        {
          "objectives": "682 Real estate activities on a fee or contract basis",
          "main_activities": "68203 Appraisal services for real estate(6)"
        },
        {
          "objectives": "682 Real estate activities on a fee or contract basis",
          "main_activities": "68209 Real estate activities on a fee or contract basis n.e.c.(7)"
        },
        {
          "objectives": "702 Management consultancy activities",
          "main_activities": "70200 Management consultancy activities"
        },
        {
          "objectives": "711 Architectural and engineering activities and related technical consultancy",
          "main_activities": "71101 Architectural services(2)"
        },
        {
          "objectives": "711 Architectural and engineering activities and related technical consultancy",
          "main_activities": "71102 Engineering services and other technical consultancy(3)"
        },
        {
          "objectives": "731 Advertising",
          "main_activities": "73100 Advertising(1)"
        },
        {
          "objectives": "741 Specialized design activities",
          "main_activities": "74100 Specialized design activities"
        },
        {
          "objectives": "802 Security systems service activities",
          "main_activities": "80200 Security systems service activities(4)"
        },
        {
          "objectives": "812 Cleaning activities",
          "main_activities": "81210 General cleaning of buildings"
        },
        {
          "objectives": "813 Landscape care and maintenance service activities",
          "main_activities": "81300 Landscape care and maintenance service activities(6)"
        }
      ],
      "type": "activities_information"
    },
    {
      "data": [
        {
          "male": "0",
          "female": "0",
          "foreign_employees": "0",
          "domestic_employees": "0"
        }
      ],
      "type": "employee_information"
    }
  ],
  "registration_date": "",
  "incorporation_date": "03-Jul-2019",
  "registration_number": "00044407"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library to crawl and `BeautifulSoup` for parsing.

## Additional Dependencies
- `bs4` (BeautifulSoup)
- `selenium`

## Estimated Processing Time
The processing time for the crawler is estimated 15 days.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/cambodia/cambodia.py`