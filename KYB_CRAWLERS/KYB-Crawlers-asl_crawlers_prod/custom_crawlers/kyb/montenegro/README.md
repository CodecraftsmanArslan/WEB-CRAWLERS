# Crawler: Montenegro

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Central Register of Business Entities](http://www.pretraga.crps.me/). The script employs Selenium to retrieve data from web pages within the indexed range of 10,000,000 to 59,999,999, as part of the search process, processes the retrieved HTML content, and inserts relevant information into a PostgreSQL table named "reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA",
  "type": "AKCIONARSKO DRUŠTVO",
  "status": "Registrovan",
  "meta_detail": {
    "aliases": "CRNOGORSKA KOMERCIJALNA BANKA",
    "capital": "181875220.7828 €",
    "pib_number": "02239108",
    "change_date": "23-06-2023",
    "change_number": "84",
    "mail_receipt_location": "PODGORICA"
  },
  "country_name": "Montenegro",
  "crawler_name": "custom_crawlers.kyb.montenegro.montenegro_kyb.py",
  "jurisdiction": "AKCIONARSKO DRUŠTVO",
  "people_detail": [
    {
      "name": "BERNADETT DANCSNE ENGLER",
      "designation": "Član Nadzornog odbora",
      "meta_detail": {
        "shares": "",
        "responsibility": "KOLEKTIVNO"
      }
    },
    {
      "name": "IGOR NOVELJIĆ",
      "designation": "Član Nadzornog odbora",
      "meta_detail": {
        "shares": "",
        "responsibility": "KOLEKTIVNO"
      }
    },
    {
      "name": "PAL GOMBOS",
      "designation": "Član Nadzornog odbora",
      "meta_detail": {
        "shares": "",
        "responsibility": "KOLEKTIVNO"
      }
    },
    {
      "name": "MARIA FOLDVARI",
      "designation": "Član Nadzornog odbora",
      "meta_detail": {
        "shares": "",
        "responsibility": "KOLEKTIVNO"
      }
    },
    {
      "name": "GYORGY SZILAGYI - SCHREINDORFER",
      "designation": "Član Nadzornog odbora",
      "meta_detail": {
        "shares": "",
        "responsibility": "KOLEKTIVNO"
      }
    },
    {
      "name": "DANIEL GYURIS",
      "designation": "Član Nadzornog odbora",
      "meta_detail": {
        "shares": "",
        "responsibility": "KOLEKTIVNO"
      }
    },
    {
      "name": "KALMAN KISS",
      "designation": "Član Nadzornog odbora",
      "meta_detail": {
        "shares": "",
        "responsibility": "KOLEKTIVNO"
      }
    },
    {
      "name": "NIKOLA PERIŠIĆ",
      "designation": "Član Upravnog odbora",
      "meta_detail": {
        "shares": "",
        "responsibility": "KOLEKTIVNO"
      }
    },
    {
      "name": "MAJA KRSTIĆ",
      "designation": "Član Upravnog odbora",
      "meta_detail": {
        "shares": "",
        "responsibility": "KOLEKTIVNO"
      }
    },
    {
      "name": "IVAN VUČINIĆ",
      "designation": "Član Upravnog odbora",
      "meta_detail": {
        "shares": "",
        "responsibility": "KOLEKTIVNO"
      }
    },
    {
      "name": "SERGEY KAPUSTIN",
      "designation": "Član Upravnog odbora",
      "meta_detail": {
        "shares": "",
        "responsibility": "KOLEKTIVNO"
      }
    },
    {
      "name": "STELA BOŠKOVIĆ",
      "designation": "Član upravnog odbora",
      "meta_detail": {
        "shares": "",
        "responsibility": "KOLEKTIVNO"
      }
    },
    {
      "name": "DINO REDŽEPAGIĆ",
      "designation": "Član upravnog odbora",
      "meta_detail": {
        "shares": "",
        "responsibility": "KOLEKTIVNO"
      }
    },
    {
      "name": "DANIEL GYURIS",
      "designation": "Predsjednik nadzornog odbora",
      "meta_detail": {
        "shares": "",
        "responsibility": "KOLEKTIVNO"
      }
    },
    {
      "name": "TAMAS KAMARASI",
      "designation": "Predsjednik Upravnog odbora",
      "meta_detail": {
        "shares": "",
        "responsibility": "KOLEKTIVNO"
      }
    },
    {
      "name": "DRUŠTVO ZA REVIZIJU\"ERNST & YOUNG MONTENEGRO\"DOO PODGORICA DRUŠTVO ZA REVIZIJU\"ERNST & YOUNG MONTENEGRO\"DOO PODGORICA",
      "designation": "Revizor"
    }
  ],
  "contacts_detail": [
    {
      "type": "website",
      "value": "www.ckb.me"
    },
    {
      "type": "email",
      "value": "info@ckb.me"
    },
    {
      "type": "phone_number",
      "value": "+382/19894"
    }
  ],
  "fillings_detail": [
    {
      "file_url": "http://www.pretraga.crps.me:8083/Home/GenerisiIzvod?REG_BROJ=40001633&BROJ_PROMJENE=84&Param=0"
    }
  ],
  "addresses_detail": [
    {
      "type": "headquarters",
      "address": "BULEVAR REVOLUCIJE 17"
    },
    {
      "type": "postal_address",
      "address": "BULEVAR REVOLUCIJE 17"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "detail": "Ostalo monetarno posredovanje",
          "activity_code": "6419"
        }
      ],
      "type": "activities_info"
    },
    {
      "data": [
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-FILIJALA ULCINJ, BOŠKA STRUGARA BB",
          "address": "BOŠKA STRUGARA BB",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "ULCINJ",
          "representative": "MAJLINDA REDŽOVIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-FILIJALA NIKŠIĆ, TRG SLOBODE BB",
          "address": "TRG SLOBODE BB",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "NIKŠIĆ",
          "representative": "DRAGIŠA ŠLJIVANČANIN"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA NIKŠIĆ-NJEGOŠEVA, NJEGOŠEVA ULICA BR. 8",
          "address": "NJEGOŠEVA ULICA BR. 8",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "NIKŠIĆ",
          "representative": "DRAGIŠA ŠLJIVANČANIN"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA ROŽAJE, MARŠALA TITA BB",
          "address": "MARŠALA TITA BB",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "ROŽAJE",
          "representative": "ALMIR FERIZOVIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA MOJKOVAC, MALIŠE DAMJANOVIĆA BB",
          "address": "MALIŠE DAMJANOVIĆA BB",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "MOJKOVAC",
          "representative": "ŽIVKO FILIPOVIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA - FILIJALA BUDVA, MEDITERANSKA ULICA BR. 7",
          "address": "MEDITERANSKA ULICA BR. 7",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "BUDVA",
          "representative": "IVANA ŠOLJAGA"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-FILIJALA DANILOVGRAD, SAVA BURIĆA BR. 1",
          "address": "SAVA BURIĆA BR. 1",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "DANILOVGRAD",
          "representative": "MILICA PRELEVIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA KOLAŠIN, TRG BORCA BB",
          "address": "TRG BORCA BB",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "KOLAŠIN",
          "representative": "MILICA RAKOČEVIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA BAR-SOHO, BULEVAR REVOLUCIJE 10 A",
          "address": "BULEVAR REVOLUCIJE 10 A",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "BAR",
          "representative": "MARIJA MILIKIĆ VUJOVIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-FILIJALA BAR, MARŠALA TITA BR. 7",
          "address": "MARŠALA TITA BR. 7",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "BAR",
          "representative": "MARJANA MARKOČ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA ŽABLJAK, VUKA KARADŽIĆA BB",
          "address": "VUKA KARADŽIĆA BB",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "ŽABLJAK",
          "representative": "DRAGIŠA ŠLJIVANČANIN"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-FILIJALA BERANE, 29 NOVEMBAR BB",
          "address": "29 NOVEMBAR BB",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "BERANE",
          "representative": "MIOMIR KASTRATOVIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA KOTOR-KAMELIJA, MATA PETROVIĆA SHOP MALL KAMELIJA",
          "address": "MATA PETROVIĆA SHOP MALL KAMELIJA",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "KOTOR",
          "representative": "MILOVAN MILAČIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-FILIJALA KOTOR, TRG OD ORUŽJA BB",
          "address": "TRG OD ORUŽJA BB",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "KOTOR",
          "representative": "MILOVAN MILAČIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-FILIJALA TIVAT, PALIH BORACA 22C",
          "address": "PALIH BORACA 22C",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "TIVAT",
          "representative": "MARKO MRAČEVIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA TIVAT-MAGNOLIJA, TRG MAGNOLIJA BB",
          "address": "TRG MAGNOLIJA BB",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "TIVAT",
          "representative": "VESNA GLIBOTA"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-FILIJALA PLJEVLJA, NIKOLE PAŠIĆA BR. 2",
          "address": "NIKOLE PAŠIĆA BR. 2",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "PLJEVLJA",
          "representative": "BILJANA NINKOVIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-FILIJALA BIJELO POLJE, TRŠOVA ULICA BB",
          "address": "TRŠOVA ULICA BB",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "BIJELO POLJE",
          "representative": "DALIBOR FATIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-FILIJALA HERCEG NOVI, TRG NIKOLE ĐURKOVIĆA BR. 15",
          "address": "TRG NIKOLE ĐURKOVIĆA BR. 15",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "HERCEG NOVI",
          "representative": "DARKO IVANOVIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-ŠALTER HERCEG NOVI-BIJELA , BIJELA BB",
          "address": "BIJELA BB",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "HERCEG NOVI",
          "representative": "MARKO RADOJIČIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA HERCEG NOVI-IGALO, SAVA ILIĆA BR. 42A",
          "address": "SAVA ILIĆA BR. 42A, IGALO",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "HERCEG NOVI",
          "representative": "MARKO RADOJIČIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA HERCEG NOVI-MELJINE, ZEMUNSKA BR. 143",
          "address": "ZEMUNSKA BR. 143",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "HERCEG NOVI",
          "representative": "MARKO RADOJIČIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-FILIJALA CETINJE, V PROLETERSKE BR. 1",
          "address": "V PROLETERSKE BR. 16B",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "CETINJE",
          "representative": "JASMINA ĆERANIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA PODGORICA-VOLI (STARI AERODROM), JOSIPA BROZA BB",
          "address": "JOSIPA BROZA BB, STARI AERODROM",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "PODGORICA",
          "representative": "IRENA MARKOVIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA PODGORICA-TRG NEZAVISNOSTI, TRG NEZAVISNOSTI BR. 35",
          "address": "TRG NEZAVISNOSTI BR. 35",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "PODGORICA",
          "representative": "EVICA  VUKSANOVIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-FILIJALA PODGORICA-CENTAR, NOVAKA MILOŠEVA BR. 6",
          "address": "NOVAKA MILOŠEVA BR. 6",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "PODGORICA",
          "representative": "DAVOR DOBRIČANIN"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-FILIJALA PODGORICA-DELTA CITY, CETINJSKI PUT BB. DELTA SHOP MALL",
          "address": "CETINJSKI PUT BB. DELTA SHOP MALL",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "PODGORICA",
          "representative": "OGNJEN BJELETIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA PODGORICA-CIJEVNA, GOLUBOVCI, MAHALA BB",
          "address": "GOLUBOVCI, MAHALA BB",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "PODGORICA",
          "representative": "VUČETA LAKIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA PODGORICA-ZABJELO, KRALJA NIKOLE BR. 323",
          "address": "KRALJA NIKOLE BR. 323",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "PODGORICA",
          "representative": "EDINA VRBICA"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA FILIJALA-MOSKOVSKA PODGORICA, MOSKOVSKA BB",
          "address": "MOSKOVSKA BB",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "PODGORICA",
          "representative": "DARKO RUBEŽIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA PODGORICA-MOSKOVSKA HQ, MOSKOVSKA 2D",
          "address": "MOSKOVSKA 2D",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "PODGORICA",
          "representative": "DUŠAN RAIČEVIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-EKSPOZITURA PODGORICA-METALKA, KRALJA NIKOLE BR. 21",
          "address": "KRALJA NIKOLE BR. 21",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "PODGORICA",
          "representative": "RADMILA GOPČEVIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-FILIJALA PODGORICA-MAGISTRALA, BRATSTVA I JEDINSTVA BR. 28",
          "address": "BRATSTVA I JEDINSTVA BR. 28",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "PODGORICA",
          "representative": "MIRKO VUJOVIĆ"
        },
        {
          "name": "\"CRNOGORSKA KOMERCIJALNA BANKA\" A.D. PODGORICA, PODRUŽNICA-FILIJALA PODGORICA-BULEVAR, BULEVAR SV. PETRA CETINJSKOG BR. 45",
          "address": "BULEVAR SV. PETRA CETINJSKOG BR. 45",
          "activity": "Ostalo monetarno posredovanje",
          "jurisdiction": "PODGORICA",
          "representative": "JELENA VUKŠIĆ"
        }
      ],
      "type": "branch_offices_info"
    },
    {
      "data": [
        {
          "url": "https://eprijava.tax.gov.me/TaxisPortal"
        }
      ],
      "type": "financial_records"
    }
  ],
  "registration_date": "07-08-2002",
  "registration_number": "40001633"
}
```


## Crawler Type
This is a web scraper crawler that uses the `Selenium` library for scraping and `BeautifulSoup` for HTML parsing.

## Additional Dependencies
- `Selenium`
- `bs4` (BeautifulSoup)

## Estimated Processing Time
The crawler's processing time is estimated to be approximately more than a month.

## How to Run the Crawler
1. Install the required dependencies: `pip install -r requirements.txt`
2. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
3. Set up a virtual environment if necessary.
4. Set the necessary environment variables in a `.env` file.
5. Run the script: `python3 custom_crawlers/kyb/montenegro/montenegro_kyb.py`