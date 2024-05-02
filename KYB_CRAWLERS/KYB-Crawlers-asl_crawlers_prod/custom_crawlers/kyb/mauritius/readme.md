# Crawler: Mauritius

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [Corporate and Business Registration Department (CBRD)](https://onlinesearch.mns.mu/). The script use undetected selenium driver to get the data HTML page, use beautifulsoup to parse, and inserts relevant information into a PosgreSQL data table named "reports". There are two crawlers, first one to extract data of companies and second one for partnerships. Both use same approach.

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"company_data": {
  "name": "ENL Land Ltd",
  "type": "LIMITED BY SHARES",
  "status": "Defunct",
  "meta_detail": {
    "nature": "Public",
    "category": "DOMESTIC"
  },
  "country_name": "Mauritius",
  "crawler_name": "custom_crawlers.kyb.mauritius.mauritius_company.py",
  "inactive_date": "01-01-2019",
  "people_detail": [
    {
      "name": "OOSMAN MUSHTAQ M.OOMAR NOORMOHAMMED",
      "designation": "ALTERNATE DIRECTOR",
      "appointment_date": "10-02-2018"
    },
    {
      "name": "BDO & CO",
      "address": "10 FRERE FELIX DE VALOIS STREET PORT LOUISMAURITIUS",
      "designation": "AUDITOR",
      "appointment_date": "16-09-2010"
    },
    {
      "name": "CORNEILLET VIRGINIE ANNE",
      "designation": "DIRECTOR",
      "appointment_date": "02-01-2016"
    },
    {
      "name": "ESPITALIER NOEL JOSEPH EDOUARD GERARD",
      "designation": "DIRECTOR",
      "appointment_date": "02-01-2016"
    },
    {
      "name": "ESPITALIER NOEL MARIE ANDRE ERIC",
      "designation": "DIRECTOR",
      "appointment_date": "02-01-2016"
    },
    {
      "name": "ESPITALIER NOEL MARIE EDOUARD GILBERT",
      "designation": "DIRECTOR",
      "appointment_date": "02-01-2016"
    },
    {
      "name": "ESPITALIER NOEL MARIE PATRICK ROGER",
      "designation": "DIRECTOR",
      "appointment_date": "02-01-2016"
    },
    {
      "name": "ESPITALIER-NOEL MARIE MAXIME HECTOR",
      "designation": "DIRECTOR",
      "appointment_date": "02-01-2016"
    },
    {
      "name": "HARDY GERARD JEAN RAYMOND",
      "designation": "DIRECTOR",
      "appointment_date": "02-01-2016"
    },
    {
      "name": "HUMBERT NOEL JEAN",
      "address": "ALLEE DES TAMARINIERS MORCELLEMENT CARLOS RIVIERE NOIRE MAURITIUS",
      "designation": "DIRECTOR",
      "appointment_date": "02-01-2016"
    },
    {
      "name": "MONTOCCHIO MARIE JOSEPH JEAN PIERRE",
      "designation": "DIRECTOR",
      "appointment_date": "02-01-2016"
    },
    {
      "name": "OOSMAN MUSHTAQ M.OOMAR NOORMOHAMMED",
      "designation": "DIRECTOR",
      "appointment_date": "02-01-2016"
    },
    {
      "name": "PILOT JOSEPH MARIE JOHAN",
      "address": "C/O ENL PROPERTY LIMITED ENL HOUSE, VIVEA BUSINESS PARK MOKA MAURITIUS",
      "designation": "DIRECTOR",
      "appointment_date": "28-09-2016"
    },
    {
      "name": "REY SIMON PIERRE",
      "address": "25, DOMAINE DE BELLE VUE BUTTE AUX PAPAYES MAPOU MAURITIUS",
      "designation": "DIRECTOR",
      "appointment_date": "28-09-2016"
    },
    {
      "name": "ENL Limited",
      "address": "VIVEA BUSINESS PARK ENL HOUSE MOKA MAURITIUS",
      "designation": "SECRETARY",
      "appointment_date": "02-01-2016"
    }
  ],
  "fillings_detail": [
    {
      "date": "27-12-2018",
      "meta_detail": {
        "return_date": "18-12-2018",
        "meeting_date": "28-11-2018"
      }
    },
    {
      "date": "29-12-2017",
      "meta_detail": {
        "return_date": "27-12-2017",
        "meeting_date": "12-12-2017"
      }
    },
    {
      "date": "01-06-2017",
      "meta_detail": {
        "return_date": "21-12-2016",
        "meeting_date": "12-09-2016"
      }
    }
  ],
  "addresses_detail": [
    {
      "type": "office_address",
      "address": "ENL House, Vivéa Business Park MokaMAURITIUS"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "capital": "7051192830",
          "currency": "Mauritius Rupee",
          "par_value": "0",
          "share_type": "ORDINARY SHARES",
          "amount_unpaid": "0",
          "number_of_shares": "295847036"
        }
      ],
      "type": "shares_information"
    },
    {
      "data": [
        {
          "name": "MORE THAN 25 SHAREHOLDERS",
          "currency": "Mauritius Rupee",
          "type_of_shares": "ORDINARY SHARES",
          "number_of_shares": "295847036"
        }
      ],
      "type": "shareholder_information"
    },
    {
      "data": [
        {
          "end_date": "01-01-2019",
          "start_date": "01-01-2019",
          "winding_type": "REMOVAL - AMALGAMATION",
          "winding_status": "FINALISED"
        }
      ],
      "type": "winding_up_information"
    },
    {
      "data": [
        {
          "date": "27-06-2001",
          "amount": "80000000",
          "volume": "CH 2623/11",
          "currency": "Mauritius Rupee",
          "property": "MOV.  &  IMMOV. ASSETS",
          "date_charged": "04-10-2001",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "15-01-1999",
          "amount": "30000000",
          "volume": "CH2020/28",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE  &  IMMOVABLE PROPERTIES",
          "date_charged": "12-02-1998",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "29-05-2002",
          "amount": "2750000",
          "volume": "CH2803/27",
          "currency": "US Dollar",
          "property": "A PLOT OF LAND OF AN EXTENT OF 649,00HA",
          "date_charged": "15-03-2002",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "29-05-2002",
          "amount": "10000000",
          "volume": "CH2803/40",
          "currency": "US Dollar",
          "property": "A PLOT OF LAND OF AN EXTENT OF 649,00HA",
          "date_charged": "15-03-2002",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "29-05-2002",
          "amount": "2750000",
          "volume": "CH2803/31",
          "currency": "US Dollar",
          "property": "A PLOT OF LAND OF AN EXTENT OF 649,00HA",
          "date_charged": "15-03-2002",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "29-05-2002",
          "amount": "500000",
          "volume": "CH2803/48",
          "currency": "US Dollar",
          "property": "A PLOT OF LAND OF AN EXTENT OF 649,00HA",
          "date_charged": "15-03-2002",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "29-05-2002",
          "amount": "24000000",
          "volume": "CH2803/443",
          "currency": "US Dollar",
          "property": "A PLOT OF LAND OF AN EXTENT OF 64,00HA",
          "date_charged": "15-03-2002",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "29-05-2002",
          "amount": "7000000",
          "volume": "CH2803/44",
          "currency": "US Dollar",
          "property": "A PLOT OF LAND OF AN EXTENT OF 649,00HA",
          "date_charged": "15-03-2002",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "29-05-2002",
          "amount": "1000000",
          "volume": "CH2803/39",
          "currency": "US Dollar",
          "property": "A PLOT OF LAND OF AN EXTENT OF 649,00HA",
          "date_charged": "15-03-2002",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "20-08-2002",
          "amount": "12000000",
          "volume": "CH2913/14",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE  &  IMMOVABLE PROPERTIES",
          "date_charged": "08-06-2002",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "27-06-2013",
          "amount": "4000000",
          "volume": "CH 5867 NO 7",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMOV",
          "date_charged": "04-05-2012",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "27-06-2013",
          "amount": "800000",
          "volume": "CH 5676 NO 30",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMOV",
          "date_charged": "29-08-2011",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "27-06-2013",
          "amount": "1000000",
          "volume": "CH 5362 NO 34",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMOV",
          "date_charged": "29-09-2010",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "27-06-2013",
          "amount": "1600000",
          "volume": "CH 5616 NO 62",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMOV",
          "date_charged": "07-06-2011",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "27-06-2013",
          "amount": "2000000",
          "volume": "CH 5888 NO 42",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMOV",
          "date_charged": "27-04-2012",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "27-06-2013",
          "amount": "250000",
          "volume": "CH 4997 NO 35",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMOV",
          "date_charged": "08-03-2009",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "27-06-2013",
          "amount": "1500000",
          "volume": "CH 52228 NO 18",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMOV",
          "date_charged": "05-03-2010",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "27-06-2013",
          "amount": "3250000",
          "volume": "CH 5646 NO 28",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMOV",
          "date_charged": "08-02-2011",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "27-06-2013",
          "amount": "1100000",
          "volume": "CH 5623 NO 59",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMOV",
          "date_charged": "13-07-2011",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "27-06-2013",
          "amount": "800000",
          "volume": "CH 5665 NO 13",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMOV",
          "date_charged": "18-08-2011",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "27-06-2013",
          "amount": "400000",
          "volume": "CH 5620 NO 69",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMOV",
          "date_charged": "07-11-2011",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "27-06-2013",
          "amount": "1700000",
          "volume": "CH 6203 NO 11",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMOV",
          "date_charged": "14-05-2013",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "26-01-2013",
          "amount": "30000000",
          "volume": "CH 4758/4",
          "currency": "Mauritius Rupee",
          "property": "UNDERTAKING, GOODWILL, MOV & IMMOV",
          "date_charged": "20-10-2008",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "26-01-2013",
          "amount": "20000000",
          "volume": "CH 3382",
          "currency": "Mauritius Rupee",
          "property": "UNDERTAKING, GOODWILL, MOV & IMMOV",
          "date_charged": "22-06-2004",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "26-01-2013",
          "amount": "83000000",
          "volume": "CH 5378/2",
          "currency": "Mauritius Rupee",
          "property": "UNDERTAKING, GOODWILL, MOV & IMMOV",
          "date_charged": "19-10-2010",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "26-01-2013",
          "amount": "35000000",
          "volume": "CH 3618/14",
          "currency": "Mauritius Rupee",
          "property": "UNDERTAKING, GOODWILL, MOV & IMMOV",
          "date_charged": "21-04-2005",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "26-01-2013",
          "amount": "5000000",
          "volume": "CH 3382/79",
          "currency": "Mauritius Rupee",
          "property": "UNDERTAKING, GOODWILL, MOV & IMMOV",
          "date_charged": "22-06-2004",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "26-01-2013",
          "amount": "2500000",
          "volume": "CH3382/77",
          "currency": "Mauritius Rupee",
          "property": "UNDERTAKING, GOODWILL, MOV & IMMOV",
          "date_charged": "22-06-2004",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "26-01-2013",
          "amount": "88000000",
          "volume": "CH 2849/13",
          "currency": "Mauritius Rupee",
          "property": "UNDERTAKING, GOODWILL, MOV & IMMOV",
          "date_charged": "14-05-2002",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "26-01-2013",
          "amount": "45000000",
          "volume": "CH 3303/40",
          "currency": "Mauritius Rupee",
          "property": "UNDERTAKING, GOODWILL, MOV & IMMOV",
          "date_charged": "17-03-2004",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "26-01-2013",
          "amount": "90000000",
          "volume": "CH 2623/04",
          "currency": "Mauritius Rupee",
          "property": "UNDERTAKING, GOODWILL, MOV & IMMOV",
          "date_charged": "06-04-2001",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "26-01-2013",
          "amount": "137000000",
          "volume": "CH 2831/24",
          "currency": "Mauritius Rupee",
          "property": "UNDERTAKING, GOODWILL, MOV & IMMOV",
          "date_charged": "18-04-2002",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "25-02-2013",
          "amount": "12000000",
          "volume": "CH 2998 NO 5",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE & IMMOV",
          "date_charged": "19-11-2002",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "25-02-2013",
          "amount": "83000000",
          "volume": "CH 5378 NO 2",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE & IMMOV",
          "date_charged": "19-10-2010",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "25-02-2013",
          "amount": "31500000",
          "volume": "CH 4785 NO 37",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE & IMMOV",
          "date_charged": "14-11-2008",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "25-02-2013",
          "amount": "95799726",
          "volume": "CH 3876/14",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE & IMMOV",
          "date_charged": "25-01-2006",
          "nature_of_charge": "FLOATING"
        },
        {
          "amount": "23000000",
          "volume": "CH 5591 NO 47",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE & IMMOV",
          "date_charged": "15-06-2011",
          "nature_of_charge": "GAGE SANS DEPLACEMENT"
        },
        {
          "date": "25-02-2013",
          "amount": "7000000",
          "volume": "CH 3391 NO 38",
          "currency": "Mauritius Rupee",
          "property": "COMPANY'S ASSETS",
          "date_charged": "07-02-2004",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "25-02-2013",
          "amount": "80000000",
          "volume": "CH 5577 NO 42",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE & IMMOV",
          "date_charged": "06-03-2011",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "25-02-2013",
          "amount": "14500000",
          "volume": "CH 3391 NO 37",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE & IMMOV",
          "date_charged": "07-02-2004",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "15-10-2014",
          "amount": "871810000",
          "volume": "CH201409/0",
          "currency": "Mauritius Rupee",
          "property": "IMMOV",
          "date_charged": "19-09-2014",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "19-05-2017",
          "amount": "400000",
          "volume": "AA201511/014528",
          "currency": "Mauritius Rupee",
          "date_charged": "11-09-2015",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "27-08-2013",
          "amount": "5000000",
          "volume": "CH 4812 NO 55",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMIV",
          "date_charged": "12-10-2008",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "29-04-2016",
          "amount": "1000000000",
          "volume": "CH201602/000471",
          "currency": "Mauritius Rupee",
          "date_charged": "23-02-2016",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "22-12-2017",
          "amount": "504000000",
          "volume": "CH201710/000293",
          "currency": "Mauritius Rupee",
          "property": "Refer to pages 5 to 8 of the charge document.",
          "date_charged": "10-09-2017",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "05-04-2015",
          "amount": "65000000",
          "volume": "CH201504/000047",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMOV ASSETS",
          "date_charged": "04-02-2015",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "20-07-2015",
          "amount": "500000000",
          "volume": "CH201506/000840",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMOV",
          "date_charged": "24-06-2015",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "22-10-2014",
          "amount": "260000000",
          "volume": "CH201409/001014",
          "currency": "Mauritius Rupee",
          "property": "MOV/IMMOV",
          "date_charged": "25-09-2014",
          "nature_of_charge": "FIXED AND FLOATING"
        },
        {
          "date": "13-05-2016",
          "amount": "500000000",
          "volume": "AA201604/017013",
          "currency": "Mauritius Rupee",
          "property": "Please refer to pages 5 to 24 of the fixed charge document.",
          "date_charged": "04-12-2016",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "10-02-2017",
          "amount": "810000",
          "volume": "CH201709/000312",
          "currency": "Mauritius Rupee",
          "property": "Please refer to Page 3 of the Charge Document.",
          "date_charged": "09-11-2017",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "10-02-2017",
          "amount": "2060000",
          "volume": "CH201607/000719",
          "currency": "Mauritius Rupee",
          "property": "Please refer to Page 3 & 4 of the charge document",
          "date_charged": "27-07-2016",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "16-11-2017",
          "amount": "100000000",
          "volume": "CH201710/000765",
          "currency": "Mauritius Rupee",
          "property": "Please refer to Page 4 of the charge document",
          "date_charged": "24-10-2017",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "28-12-2012",
          "amount": "400000000",
          "volume": "CH 5853",
          "currency": "Mauritius Rupee",
          "property": "MOV/IMMOV",
          "date_charged": "21-03-2012",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "19-07-2011",
          "amount": "8000000",
          "volume": "CH 5424 NO.31",
          "currency": "US Dollar",
          "property": "MOV/IMMOV",
          "date_charged": "12-10-2010",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "07-05-2013",
          "amount": "2479000",
          "volume": "CH5607NO28",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE & IMMOVABLE",
          "date_charged": "28-06-2011",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "07-05-2013",
          "amount": "2970000",
          "volume": "CH6101NO48",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE & IMMOVABLE",
          "date_charged": "24-12-2012",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "07-05-2013",
          "amount": "1600000",
          "volume": "CH5630NO11",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE & IMMOVABLE",
          "date_charged": "19-07-2011",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "07-05-2013",
          "amount": "800000",
          "volume": "CH5665NO12",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE & IMMOVABLE",
          "date_charged": "18-08-2011",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "07-05-2013",
          "amount": "3800000",
          "volume": "5892NO30",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE & IMMOVABLE",
          "date_charged": "05-02-2012",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "07-05-2013",
          "amount": "1700000",
          "volume": "CH5381NO7",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE & IMMOVABLE",
          "date_charged": "21-10-2010",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "06-07-2013",
          "amount": "5000000",
          "volume": "CH 3382/80",
          "currency": "Mauritius Rupee",
          "property": "MOV & IMMOV ASSETS",
          "date_charged": "01-11-2013",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "07-05-2013",
          "amount": "600000",
          "volume": "CH4998NO47",
          "currency": "Mauritius Rupee",
          "property": "IMMOVABLE",
          "date_charged": "08-04-2009",
          "nature_of_charge": "FIXED"
        },
        {
          "date": "24-01-2006",
          "amount": "3081000",
          "volume": "CH3848 NO6",
          "currency": "US Dollar",
          "date_charged": "20-12-2005",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "24-01-2006",
          "amount": "12625000",
          "volume": "CH3843 NO3",
          "currency": "US Dollar",
          "property": "LAND",
          "date_charged": "13-12-2005",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "26-07-2004",
          "amount": "91000000",
          "volume": "CH3390/28",
          "currency": "Mauritius Rupee",
          "property": "MOVABLE  &  IMMOVABLE",
          "date_charged": "07-01-2004",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "15-06-2005",
          "amount": "1342932",
          "volume": "CH3643/62",
          "currency": "US Dollar",
          "property": "MOV/IMMOV",
          "date_charged": "21-04-2005",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "15-06-2005",
          "amount": "35000000",
          "volume": "CH3618/14",
          "currency": "Mauritius Rupee",
          "property": "MOV/IMMOV",
          "date_charged": "21-04-2005",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "17-04-2006",
          "amount": "18356000",
          "volume": "CH3910/77",
          "currency": "Mauritius Rupee",
          "property": "OTHERS",
          "date_charged": "16-03-2006",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "25-01-2007",
          "amount": "215000000",
          "volume": "CH 4133NO.11",
          "currency": "Mauritius Rupee",
          "date_charged": "19-12-2006",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "06-12-2007",
          "amount": "329150",
          "volume": "CH4248 NO10",
          "currency": "US Dollar",
          "property": "MOVABLE/IMMOVABLE PROPERTY",
          "date_charged": "05-10-2007",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "08-12-2010",
          "amount": "69634000",
          "volume": "CH5288/42",
          "currency": "Rand",
          "property": "ALL COMPANY ASSETS",
          "date_charged": "07-12-2010",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "08-12-2010",
          "amount": "300000000",
          "volume": "CH5232/13",
          "currency": "Mauritius Rupee",
          "property": "ALL COMPANY ASSETS",
          "date_charged": "05-07-2010",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "03-03-2011",
          "amount": "100000000",
          "volume": "CH5399/41",
          "currency": "Mauritius Rupee",
          "property": "MOV/IMMOV",
          "date_charged": "16-11-2010",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "08-06-2005",
          "amount": "33000000",
          "volume": "CH3699/35",
          "currency": "Mauritius Rupee",
          "property": "MOV/IMMOV",
          "date_charged": "14-07-2005",
          "nature_of_charge": "FLOATING"
        },
        {
          "date": "21-07-2005",
          "amount": "50000000",
          "volume": "CH3682/8",
          "currency": "Mauritius Rupee",
          "property": "ASSETS",
          "date_charged": "27-06-2005",
          "nature_of_charge": "FLOATING"
        }
      ],
      "type": "charges_information"
    },
    {
      "data": [
        {
          "business_address": "ROYAL ROAD L'ESCALIERMAURITIUS",
          "nature_of_business": "Automotive Workshop employing 10 persons or more",
          "registration_number": "C06000025"
        },
        {
          "business_address": "ROYAL ROAD L'ESCALIERMAURITIUS",
          "nature_of_business": "REGULATORY BODY FOR EVERYTHING CONCERNING SUGAR IN MAURITIUS",
          "registration_number": "C06000025"
        },
        {
          "business_address": "ROYAL ROAD L'ESCALIERMAURITIUS",
          "nature_of_business": "OWNER OF GOODS VEHICLE (CARRIER'S B ) PER VEHICLE",
          "registration_number": "C06000025"
        },
        {
          "business_address": "ROYAL ROAD L'ESCALIERMAURITIUS",
          "nature_of_business": "POULTRY PEN 501 BIRDS TO 5000 BIRDS",
          "registration_number": "C06000025"
        }
      ],
      "type": "branches_and_other_offices"
    },
    {
      "data": [
        {
          "unit": "1000",
          "turnover": "0",
          "tax_expense": "2251",
          "cost_of_sale": "0",
          "finance_cost": "0",
          "gross_profit": "0",
          "other_income": "646381",
          "approval_date": "27-09-2018",
          "currency_type": "Mauritius Rupee",
          "other_expenses": "924722",
          "distribution_cost": "0",
          "administration_cost": "0",
          "financial_year_ended": "30-06-2018",
          "profit_loss_before_tax": "-278341",
          "profit_loss_for_the_period": "-280592"
        }
      ],
      "type": "profit_and_loss_information"
    },
    {
      "data": [
        {
          "total": "31855511",
          "others": "920219",
          "intangible_asset": "295336",
          "other_investment": "2822940",
          "prop_plant_equip": "10368120",
          "biological_assets": "0",
          "invest_properties": "3440025",
          "invest_in_subsidiaries": "14008871"
        }
      ],
      "type": "non_current_asset_information"
    },
    {
      "data": [
        {
          "total": "750796",
          "others": "53960",
          "inventories": "0",
          "total_assets": "32606307",
          "cash_and_cash_eq": "190754",
          "trade_and_other_receivables": "506082"
        }
      ],
      "type": "current_asset_information"
    },
    {
      "data": [
        {
          "total": "27975491",
          "others": "0",
          "share_capital": "7051193",
          "other_reserves": "13541108",
          "retained_earnings": "7383190"
        }
      ],
      "type": "equity_and_liabilities_information"
    },
    {
      "data": [
        {
          "total": "3008450",
          "others": "0",
          "deffered_tax": "0",
          "long_term_borrowings": "2763822",
          "long_term_provisions": "244628"
        }
      ],
      "type": "non_current_liabilities_information"
    },
    {
      "data": [
        {
          "others": "144991",
          "total_liabilities": "4630816",
          "current_tax_payable": "0",
          "short_term_borrowings": "1303433",
          "short_term_provisions": "124256",
          "trade_and_other_payables": "49686",
          "total_current_liabilities": "1622366",
          "total_equity_and_liabilities": "32606307"
        }
      ],
      "type": "current_liabilities_information"
    }
  ],
  "registration_date": "21-05-1913",
  "registration_number": "C25"
}
```

```json
"partnership_data": {
  "name": "LA SOCIETE R.BOOJHARUT-K.L.JAHREE & CIE",
  "type": "",
  "status": "Live",
  "meta_detail": {
    "nature": "Commercial",
    "category": "DOMESTIC"
  },
  "country_name": "Mauritius",
  "crawler_name": "custom_crawlers.kyb.mauritius.mauritius_partnership.py",
  "inactive_date": "",
  "people_detail": [
    {
      "name": "BOOJHARUT RAJ",
      "address": "CLAIRFONDS NO 1 PHOENIXMAURITIUS",
      "designation": "GERANT",
      "appointment_date": "25-05-1998"
    }
  ],
  "addresses_detail": [
    {
      "type": "registered_address",
      "address": "CLAIRFOND NO 1 AVE J.NEHRU PHOENIX MAURITIUS MAURITIUS"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "capital": "10000",
          "currency": "Mauritius Rupee",
          "par_value": "100",
          "share_type": "PART SOCIALE",
          "amount_unpaid": "0",
          "number_of_shares": "100"
        }
      ],
      "type": "shares_information"
    },
    {
      "data": [
        {
          "name": "BOOJHARUT RAJ",
          "currency": "Mauritius Rupee",
          "type_of_shares": "PART SOCIALE",
          "number_of_shares": "99"
        },
        {
          "name": "BHEEROO BHAGWANTEE",
          "currency": "Mauritius Rupee",
          "type_of_shares": "PART SOCIALE",
          "number_of_shares": "1"
        }
      ],
      "type": "associes_information"
    },
    {
      "data": [
        {
          "name": "JB ENTERPRISES",
          "business_address": "P. J NEHRU AVE, PHOENIX MAURITIUS",
          "nature_of_business": "Manufacture of Structural Metal Products (e.g doors, frames, shutters, metal frameworks)",
          "registration_number": "P08000082"
        },
        {
          "name": "JB ENTERPRISES",
          "business_address": "P. J NEHRU AVE, PHOENIX MAURITIUS",
          "nature_of_business": "Job Contractor ( Other Than Grade A,B,C,D or E)",
          "registration_number": "P08000082"
        }
      ],
      "type": "branches_and_other_offices"
    }
  ],
  "registration_date": "19-03-1986",
  "registration_number": "P82"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library to get HTML data from results page and then use `beautifulsoup` to parse and extract required information.

## Additional Dependencies
- `selenium`
- `beautifulsoup4`
- `undetected chrome browser`

## Estimated Processing Time
The processing time for the crawler is estimated > one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/mauritius/mauritius_company.py`
6. Run the script: `python3 custom_crawlers/kyb/mauritius/mauritius_partnership.py`