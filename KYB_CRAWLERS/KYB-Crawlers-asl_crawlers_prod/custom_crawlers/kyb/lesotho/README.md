# Crawler: Lesotho

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Ministry of Trade and Industry in Lesotho](https://www.companies.org.ls/lesotho-master/viewInstance/view.html?id=13c857736aeecb0aabf20e7b8722181a7cb1a9382dd6ad0c&_timestamp=89472254731593). The script utilizes Selenium to extract data from web pages indexed between January 1, 1996, and December 31, 2023, as part of the search process, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "IN-GRACE PTY LTD",
  "type": "Private Company",
  "status": "Active",
  "meta_detail": {
    "aliases": "IN-GRACE",
    "end_date": "06-18-2021",
    "start_date": "06-18-2021",
    "share_capital": "1000",
    "annual_takeover": "Less than M. 850,000",
    "previous_status": "Awaiting LRA",
    "annual_filing_day": "18",
    "annual_filing_month": "June",
    "number_of_employees": "Yes",
    "single_or_multiple_shareholders": "Single",
    "does_the_company_adopt_its_own_articles?": "No"
  },
  "country_name": "Lesotho",
  "crawler_name": "custom_crawlers.kyb.lesotho.lesotho_kyb.py",
  "people_detail": [
    {
      "name": "Mr Mpiti Elisher MOSOTHOANE",
      "address": "Mataelo Matsoso, Ha Tsautse Pela Ha Ntate City, Maseru, 100, Lesotho",
      "designation": "Director",
      "meta_detail": {
        "appointment_date": "06-18-2021",
        "required_to_accept_service?": "Yes"
      },
      "nationality": "Lesotho",
      "postal_address": "P O Box 15718, Maseru, 100, Lesotho"
    },
    {
      "name": "Mr Mpiti Elisher MOSOTHOANE",
      "address": "Mataelo Matsoso, Ha Tsautse Pela Ha Ntate City, Maseru, 100, Lesotho",
      "designation": "shareholder",
      "meta_detail": {
        "appointed": "06-18-2021",
        "also_a_director": "Yes"
      },
      "postal_address": "P O Box 15718, Maseru, 100, Lesotho"
    },
    {
      "name": "Mr Mpiti Elisher MOSOTHOANE",
      "designation": "shareholder",
      "meta_detail": {
        "number_of_shares": "1000"
      }
    }
  ],
  "contacts_detail": [
    {
      "type": "phone_number",
      "value": "(+266) -62999509"
    },
    {
      "type": "phone_number_2",
      "value": "(+266) -62999509"
    },
    {
      "type": ":e_mail",
      "value": "mosothoanempiti@gmail.com"
    },
    {
      "type": "phone_number",
      "value": "(+266) -62999509"
    },
    {
      "type": "phone_number_2",
      "value": "(+266) -62999509"
    },
    {
      "type": ":e_mail",
      "value": "mosothoanempiti@gmail.com"
    }
  ],
  "addresses_detail": [
    {
      "type": "physical_address",
      "address": "Mataelo Matsoso, Ha Tsautse Pela Ha Ntate City, Maseru, Maseru, 100, Lesotho",
      "meta_detail": {
        "start_date": "06-18-2021"
      }
    },
    {
      "type": "postal_address",
      "address": "P O Box 15718, Maseru, 100, Lesotho",
      "meta_detail": {
        "start_date": "18-Jun-2021"
      }
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "code": "0115",
          "description": "Growing of tobacco"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "0121",
          "description": "Growing of grapes"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "0125",
          "description": "Growing of other tree and bush fruits and nuts"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "0128",
          "description": "Growing of spices, aromatic, drug and pharmaceutical crops"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "0130",
          "description": "Plant propagation"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "0141",
          "description": "Raising of cattle and buffaloes"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "0149",
          "description": "Raising of other animals"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "0150",
          "description": "Mixed farming"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "0162",
          "description": "Support activities for animal production"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "0220",
          "description": "Logging"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "0510",
          "description": "Mining of hard coal"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "0710",
          "description": "Mining of iron ores"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "0721",
          "description": "Mining of uranium and thorium ores"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "0810",
          "description": "Quarrying of stone, sand and clay"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "0910",
          "description": "Support activities for petroleum and natural gas extraction"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "1040",
          "description": "Manufacture of vegetables and animal oils and fats"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "1105",
          "description": "Manufacture of ice"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "1312",
          "description": "Weaving of textiles"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "1391",
          "description": "Manufacture of knitted and crocheted fabrics"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "1511",
          "description": "Tanning and dressing of leather; dressing and dyeing of fur"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "2100",
          "description": "Manufacture of pharmaceuticals, medicinal chemical and botanical products"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "2397",
          "description": "Manufacture of bricks and concrete blocks"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "2620",
          "description": "Manufacture of computers and peripheral equipment"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "2815",
          "description": "Manufacture of ovens, furnaces and furnace burners"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "3100",
          "description": "Manufacture of furniture"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "3290",
          "description": "Other manufacturing"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "3312",
          "description": "Repair of machinery"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "3318",
          "description": "Repair of computer hardware and software"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "3600",
          "description": "Waste collection and treatment supply"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4001",
          "description": "Other water supply & treatment activities"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4002",
          "description": "Water engineering activities"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4100",
          "description": "Construction of buildings"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4290",
          "description": "Construction of other civil engineering projects"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4311",
          "description": "Demolition"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4329",
          "description": "Other construction installation"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4390",
          "description": "Other specialized construction activities"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4510",
          "description": "Sale of motor vehicles"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4530",
          "description": "Sale of motor vehicle parts and accessories"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4649",
          "description": "Wholesale of other household goods"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4661",
          "description": "Wholesale of solid, liquid and gaseous fuels and related products"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4721",
          "description": "Retail sale in specialized stores"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4723",
          "description": "Retail sale of tobacco products in specialized stores"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4724",
          "description": "Retail sale of ice in specialized stores"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4725",
          "description": "Retail sale of fruits & vegetables"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4727",
          "description": "Retail of livestock & mohair"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4754",
          "description": "Retail sale of construction materials in specialized stores"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4759",
          "description": "Retail sales of electrical household appliances, furniture, lightning equipment and other household articles in specialized stores"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4761",
          "description": "Retail sale of books, newspapers and stationary in specialized stores"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4771",
          "description": "Retail sale of clothing, footwear and leather articles in specialized stores"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4774",
          "description": "Retail sale of second-hand goods"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "4799",
          "description": "Other retail sale not in stores, stalls or markets"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "5320",
          "description": "Courier activities"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "5610",
          "description": "Restaurants and mobile food service activities"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "6810",
          "description": "Real estate activities with own or leased property"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "code": "9609",
          "description": "Other personal service activities"
        }
      ],
      "type": "industry_detail"
    },
    {
      "data": [
        {
          "at_the_registered_office": "Yes",
          "at_the_main_business_address": "No",
          "on_a_director_or_officer_accepting_service": "Yes"
        }
      ],
      "type": "document_submission_address"
    }
  ],
  "incorporation_date": "06-18-2021",
  "registration_number": ""
}
```


## Crawler Type
This is a web scraper crawler that uses the `Selenium` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Selenium`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler is anticipated to require more than a week for processing.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
6. Run the script: `python3 custom_crawlers/kyb/lesotho/lesotho_kyb.py`