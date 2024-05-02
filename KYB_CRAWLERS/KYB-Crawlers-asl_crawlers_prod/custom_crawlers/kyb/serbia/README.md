# Crawler: Serbia

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Serbian Business Registers Agency (SBRA) - Serbian Business Registry](https://pretraga2.apr.gov.rs/unifiedentitysearch). The script utilizes Selenium to extract data from web pages indexed between 0 to 69000000, as part of the search process, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "translate_reports"

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "EXPRES BANKA   - U STEČAJU",
  "type": "Отворено акционарско друштво",
  "status": "Брисан",
  "tax_number": "",
  "meta_detail": {
    "aliases": "EXPRES BANKA MEŠOVITA BANKA DEONIČARSKO DRUŠTVO BEOGRAD  - U STEČAJU",
    "aliases_1": "EXPRES BANKA MEŠOVITA BANKA DEONIČARSKO DRUŠTVO BEOGRAD  - U STEČAJU",
    "obligated_to_certify_founding_act": "Не"
  },
  "country_name": "Serbia",
  "crawler_name": "custom_crawlers.kyb.serbia.serbia_kyb.py",
  "people_detail": [
    {
      "name": "EKSPRES GRADNJA PO BEOGRAD",
      "address": "/  /, Београд (град)",
      "designation": "Акционар"
    },
    {
      "name": "EKSPRES STAN PO BEOGRAD",
      "address": "/  /, Београд (град)",
      "designation": "Акционар"
    },
    {
      "name": "David John Stanley Lockett",
      "designation": "Акционар"
    },
    {
      "name": "Властимир Ристивојевић",
      "designation": "Акционар"
    },
    {
      "name": "Драгомир Ристивојевић",
      "designation": "Акционар"
    },
    {
      "name": "Зоран Ристивојевић",
      "designation": "Акционар"
    },
    {
      "name": "Милета Андреје Ристивојевић",
      "designation": "Акционар"
    },
    {
      "name": "Милета Арсенија Ристивојевић",
      "designation": "Акционар"
    },
    {
      "name": "Милисав Ристивојевић",
      "designation": "Акционар"
    },
    {
      "name": "Нада Ристивојевић",
      "designation": "Акционар"
    }
  ],
  "fillings_detail": [
    {
      "date": "26-8-2019",
      "file_url": "https://pretraga2.apr.gov.rs/publicdocsvc/doc/getdocbyid?id=0000277945851&hash=0D7C71C3041DE8929F2095A2F1FD0A2DE755FAE0",
      "filing_code": "БДСЛ 25858/2019",
      "filing_type": "Остало",
      "meta_detail": {
        "effective_date": "18-11-2005"
      }
    }
  ],
  "dissolution_date": "",
  "additional_detail": [
    {
      "data": [
        {
          "value": "35.000.000,00  RSD",
          "status": "Уписан"
        },
        {
          "date": "28-7-1992",
          "value": "35.000.000,00  RSD",
          "status": "Уплаћен"
        }
      ],
      "type": "fixed_capital_info"
    },
    {
      "data": [
        {
          "value": "34.180.000,00 RSD",
          "status": "Уписан",
          "shareholder_name": "EKSPRES GRADNJA PO BEOGRAD"
        },
        {
          "date": "28-7-1992",
          "value": "34.180.000,00 RSD",
          "status": "Уплаћен",
          "shareholder_name": "EKSPRES GRADNJA PO BEOGRAD"
        },
        {
          "value": "100.000,00 RSD",
          "status": "Уписан",
          "shareholder_name": "EKSPRES STAN PO BEOGRAD"
        },
        {
          "date": "28-7-1992",
          "value": "100.000,00 RSD",
          "status": "Уплаћен",
          "shareholder_name": "EKSPRES STAN PO BEOGRAD"
        },
        {
          "value": "560.000,00 RSD",
          "status": "Уписан",
          "shareholder_name": "David John Stanley Lockett"
        },
        {
          "date": "28-7-1992",
          "value": "560.000,00 RSD",
          "status": "Уплаћен",
          "shareholder_name": "David John Stanley Lockett"
        },
        {
          "value": "100.000,00 RSD",
          "status": "Уписан",
          "shareholder_name": "Властимир Ристивојевић"
        },
        {
          "date": "28-7-1992",
          "value": "100.000,00 RSD",
          "status": "Уплаћен",
          "shareholder_name": "Властимир Ристивојевић"
        },
        {
          "value": "10.000,00 RSD",
          "status": "Уписан",
          "shareholder_name": "Драгомир Ристивојевић"
        },
        {
          "date": "28-7-1992",
          "value": "10.000,00 RSD",
          "status": "Уплаћен",
          "shareholder_name": "Драгомир Ристивојевић"
        },
        {
          "value": "10.000,00 RSD",
          "status": "Уписан",
          "shareholder_name": "Зоран Ристивојевић"
        },
        {
          "date": "28-7-1992",
          "value": "10.000,00 RSD",
          "status": "Уплаћен",
          "shareholder_name": "Зоран Ристивојевић"
        },
        {
          "value": "10.000,00 RSD",
          "status": "Уписан",
          "shareholder_name": "Милета Андреје Ристивојевић"
        },
        {
          "date": "28-7-1992",
          "value": "10.000,00 RSD",
          "status": "Уплаћен",
          "shareholder_name": "Милета Андреје Ристивојевић"
        },
        {
          "value": "10.000,00 RSD",
          "status": "Уписан",
          "shareholder_name": "Милета Арсенија Ристивојевић"
        },
        {
          "date": "28-7-1992",
          "value": "10.000,00 RSD",
          "status": "Уплаћен",
          "shareholder_name": "Милета Арсенија Ристивојевић"
        },
        {
          "value": "10.000,00 RSD",
          "status": "Уписан",
          "shareholder_name": "Милисав Ристивојевић"
        },
        {
          "date": "28-7-1992",
          "value": "10.000,00 RSD",
          "status": "Уплаћен",
          "shareholder_name": "Милисав Ристивојевић"
        },
        {
          "value": "10.000,00 RSD",
          "status": "Уписан",
          "shareholder_name": "Нада Ристивојевић"
        },
        {
          "date": "28-7-1992",
          "value": "10.000,00 RSD",
          "status": "Уплаћен",
          "shareholder_name": "Нада Ристивојевић"
        }
      ],
      "type": "shareholder_cash_stake_info"
    },
    {
      "data": [
        {
          "date": "23-6-2007",
          "title": "Забележбa 1.",
          "description": "Уписује се у Регистар привредних субјеката Решење Трговинског суда у Београду Л. 388/96 од 09.08.1996 о отварању ликвидационог поступка над EXPRES BANKA MEŠOVITA BANKA DEONIČARSKO DRUŠTVO BEOGRAD, NARODNOG FRONTA 1. Решењем Трговинског суда у Београду Л. 388/96 од 28.03.2002 године за ликвидационог управника одређен је Радован Миљковић из Београда."
        },
        {
          "date": "24-2-2009",
          "title": "Забележбa 2.",
          "description": "Уписује се у Регистар привредних субјеката решење Трговинског суда у Београду број VI Ст. 266/05 од 18.11.2005. године којим се обуставља поступак ликвидације, а покреће поступак стечаја над   EXPRES BANKA MEŠOVITA BANKA DEONIČARSKO DRUŠTVO BEOGRAD, NARODNOG FRONTA 1. Истим решењем се поступак стечаја закључује."
        }
      ],
      "type": "notes"
    },
    {
      "data": [
        {
          "date": "31-3-2019",
          "description": "У складу са одредбом члана 547. Закона о привредним друштвима објављује се оглас о покретању поступка принудне ликвидације у трајању од 60 дана код:\n  Пословно име:  EXPRES BANKA MEŠOVITA BANKA DEONIČARSKO DRUŠTVO BEOGRAD  - U PRINUDNOJ LIKVIDACIJI\n  Матични број: 07803125\n  Разлог принудне ликвидације: нису достављени финансијски извештаји надлежном регистру до краја претходне пословне године (2017.) за претходне две  узастопне године (2015. и 2016.) које претходе години у којој се подносе финансијски извештаји (2017.) \n  Упозорење:  \n  Након истека рока од 60 дана од дана објаве огласа, регистратор који води регистар привредних субјеката, у даљем року од 30 дана, по службеној дужности доноси акт о брисању друштва и брише друштво из регистра, у складу са законом о регистрацији.",
          "date_published": "30-5-2019"
        }
      ],
      "type": "advertisements_and_notices"
    },
    {
      "data": [
        {
          "url": "https://pretraga2.apr.gov.rs/publicdocsvc/doc/getdoc?id=%d0%91%d0%94%d0%a1%d0%9b+25858%2f2019&hash=5ED38D5E8DB3550A7A983D52EE100FBB1CF1B81C&regid=1",
          "title": "Број предмета \nВрста акта \nДатум објаве\n\n\n\n\n\nБДСЛ 25858/2019\nРешење о усвајању\n26.8.2019\nдокумент\n\n\nБДСЛ 9844/2019\nРешење о усвајању\n30.5.2019\nдокумент"
        }
      ],
      "type": "registrar_details"
    }
  ],
  "registration_date": "28-7-1992",
  "registration_number": "07803125"
}
```


## Crawler Type
This is a web scraper crawler that uses the `Selenium` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Selenium`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler's processing time is estimated to be more than a week.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/serbia/serbia_kyb.py`