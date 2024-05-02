"""Import required library"""
import sys, traceback,time,re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from helpers.load_env import ENV
from dateutil import parser
from CustomCrawler import CustomCrawler
import json,requests

meta_data = {
    'SOURCE': 'The Central Union of Chambers - Commercial Registry',
    'COUNTRY': 'Greece',
    'CATEGORY': 'Official Registry',
    'ENTITY_TYPE': 'Company/Organization',
    'SOURCE_DETAIL': {"Source URL": "https://www.businessregistry.gr/publicity/index",
                      "Source Description": "The General Commercial Register (G.E.M.I.), combined with the upgrading of the role of the Chambers of Commerce through their transformation into “one-stop-shop”, constitute decisive changes in the axis of simplification of the general procedures of the business environment, which aim both to meet the needs and requirements of all kinds of stakeholders, as well as the effective use and exploitation of the information collected."},
    'SOURCE_TYPE': 'HTML',
    'URL': 'https://www.businessregistry.gr/publicity/index'
}

crawler_config = {
    'TRANSLATION_REQUIRED': False,
    'PROXY_REQUIRED': False,
    'CAPTCHA_REQUIRED': False,
    'CRAWLER_NAME': "Greece Official Registry"
}

"""Global Variables"""
STATUS_CODE = 0
DATA_SIZE = 0
CONTENT_TYPE = 'N/A'
ARGUMENTS = sys.argv

greece_crawler = CustomCrawler(meta_data=meta_data, config=crawler_config, ENV=ENV)
request_helper = greece_crawler.get_requests_helper()

start_number = int(ARGUMENTS[1]) if len(ARGUMENTS) > 1 else 0
end_number = 999999999999

headers = {
  'Accept': 'application/json, text/plain, */*',
  'Content-Type': 'application/json',
  'Host': 'publicity.businessportal.gr',
  'Origin': 'https://publicity.businessportal.gr',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
}

def format_date(timestamp):
    date_str = ""
    try:
        datetime_obj = parser.parse(timestamp)
        date_str = datetime_obj.strftime("%d-%m-%Y")
    except Exception as e:
        pass
    return date_str

def crawl():
    for i in range(start_number, end_number):
        search_number = str(i).zfill(12)
        url = f"https://publicity.businessportal.gr/api/company/details"
        payload = json.dumps(
            {"query":{"arGEMI":search_number},"language":"en"}
        )

        while True:
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 504 or response.status_code == 404:
                print(f"No data for: {search_number}")
                break
            elif response.status_code == 200:
                data = response.json()
                break
            else:
                print(f"Initial Error Code: {response.status_code}")
                time.sleep(10)

        if response.status_code == 504 or response.status_code == 404:
            continue
        elif response.status_code == 200:
            print(f"Scrapping data for: {search_number}")

        def get_data(variable, search):
            data_value = variable.get(search, "") if variable.get(search, "") else ""
            return data_value

        all_title_data = []
        all_shares_data = []
        all_KAD_data = []
        all_finance_data = []
        all_suspension_data = []
        all_history_data = []
        all_alias_data = []
        all_chamber_data = []
        all_people_data = []

        company_not_found = data.get("message", "") if data.get("message", "") else ""
        if company_not_found:
            print(f"No data for: {search_number}")
            time.sleep(1)
            continue

        all_company_details = data.get("newInfo", "") if data.get("newInfo", "") else ""

        if all_company_details:
            all_company_details = all_company_details.get("payload", "") if all_company_details.get("payload", "") else ""
            company_detail = all_company_details.get("company", "") if all_company_details.get("company", "") else ""
            if company_detail:
                company_name = get_data(company_detail, "name")
                registration_number = get_data(company_detail, "id")
                eu_id = "ELGEMI." + str(registration_number)
                name_in_latin = get_data(company_detail, "namei18n")
                aliases = get_data(company_detail, "titles")
                for aliase in aliases:
                    if get_data(aliase, "language_id") == "2":
                        alias_dict = {
                            "name": get_data(aliase, "title") + " (rendered in Latin characters)"
                        }
                        if get_data(aliase, "title"):
                            all_alias_data.append(alias_dict)
                    else:
                        alias_dict = {
                            "name": get_data(aliase, "title")
                        }
                        if get_data(aliase, "title"):
                            all_alias_data.append(alias_dict)


                tax_number = get_data(company_detail, "afm")
                registration_date = format_date(get_data(company_detail, "dateStart"))
                company_type_ = get_data(company_detail, "legalType")
                if company_type_:
                    company_type = get_data(company_type_, "desc")
                else:
                    company_type = ""
                company_status_ = get_data(company_detail, "companyStatus")
                if company_status_:
                    company_status = get_data(company_status_, "status")
                else:
                    company_status = ""
                address_line_1 = get_data(company_detail, "company_street")
                address_line_2 = get_data(company_detail, "company_street_number")
                address_line_3 = get_data(company_detail, "company_municipality")
                address_zip = get_data(company_detail, "company_zip_code")
                complete_address = address_line_1 + " " + address_line_2 + ", " + address_line_3 + ", " + address_zip
                website = get_data(company_detail, "companyWebsite")
                e_shop = get_data(company_detail, "companyEshop")
                more_info = get_data(all_company_details, "moreInfo")
                if more_info:
                    telephone = get_data(more_info, "telephone")
                    email = get_data(more_info, "email")
                else:
                    telephone = ""
                    email = ""

                chamber_ = get_data(all_company_details, "chamberInfo")
                if chamber_:
                    for chamber in chamber_:
                        shiping_service = get_data(chamber, "chamberName")
                        chamber_department = get_data(chamber, "chamberDepartment")
                        chamber_registry = get_data(chamber, "chamberRegistrationNumber")
                        chamber_phone = get_data(chamber, "chamberContactNumber")
                        chamber_webiste = get_data(chamber, "chamberContactUrl")
                        chamber_registration_date = get_data(chamber, "companyDateRegisteredToChamber")
                        chamber_dict = {
                            "shipping_service": shiping_service,
                            "chamber_department": chamber_department,
                            "chamber_registry_number": chamber_registry,
                            "chamber_phone": chamber_phone,
                            "chamber_webiste": chamber_webiste,
                            "chamber_registration_date": format_date(chamber_registration_date)
                        }
                        if shiping_service or chamber_department or chamber_registry or chamber_phone or chamber_registration_date:
                            all_chamber_data.append(chamber_dict)

            titles_ = get_data(all_company_details, "titles")
            if titles_:
                title_data = titles_[0].get("titles", "")
                if title_data:
                    title_data = json.loads(title_data)
                    for tdata in title_data:
                        if get_data(tdata, "isI18n") == 1:
                            title_name = get_data(tdata, "title") + " (rendered in Latin characters)"
                        else:
                            title_name = get_data(tdata, "title")

                        title_status_ = get_data(tdata, "isEnable")
                        if title_status_ == 1:
                            title_status = "Active"
                        elif title_status_ == 0:
                            title_status = "Inactive"
                        else:
                            title_status = ""
                        last_updated = get_data(tdata, "until")
                        title_dict = {
                            "name": title_name,
                            "status": title_status,
                            "last_updated": format_date(last_updated)
                        }
                        all_title_data.append(title_dict)

            capital_ = get_data(all_company_details, "capital")
            if capital_:
                for capital_data_ in capital_:
                    capital = get_data(capital_data_, "capital_stock")
                    share_type = get_data(capital_data_, "descr")
                    no_of_shares = get_data(capital_data_, "amount")
                    share_value = get_data(capital_data_, "nominal_price")
                    currency = get_data(capital_data_, "currency")
                    share_dict = {
                        "capital": capital,
                        "share_type": share_type,
                        "number_of_shares": no_of_shares,
                        "share_value": share_value,
                        "currency": currency
                    }
                    if capital or share_type or no_of_shares or share_value:
                        all_shares_data.append(share_dict)

            kad_ = get_data(all_company_details, "kadData")
            if kad_:
                for kad_data_ in kad_:
                    kad_description = get_data(kad_data_, "objective")
                    kad_type = get_data(kad_data_, "activities")
                    kad_code = get_data(kad_data_, "kad")
                    kad_desc = get_data(kad_data_, "descr")
                    kad_dict = {
                        "KAD_Type": kad_type,
                        "KAD_code": kad_code,
                        "KAD_description": kad_desc,
                    }
                    if kad_description or kad_code or kad_desc:
                        all_KAD_data.append(kad_dict)
                kad_dict["description"] = kad_description.replace("\n", " ").replace("\r", "")

            mp_ = get_data(all_company_details, "managementPersons")
            if mp_:
                for mp in mp_:
                    first_name = get_data(mp, "firstName")
                    last_name = get_data(mp, "lastName")
                    full_name_mp = first_name + " " + last_name
                    mp_status_ = get_data(mp, "active")
                    if mp_status_ == 1:
                        mp_status = "Active"
                    elif mp_status_ == 0:
                        mp_status = "Inactive"
                    else:
                        mp_status = ""
                    mp_date_from = get_data(mp, "dateFrom")
                    mp_date_to = get_data(mp, "dateTo")
                    mp_designation = get_data(mp, "tableName")
                    mp_authority = get_data(mp, "capacityDescr")
                    mp_ownership = get_data(mp, "percentage")
                    if "." in mp_ownership:
                        mp_ownership = (int(float(mp_ownership) * 100))
                    else:
                        mp_ownership = int(mp_ownership)
                    mp_dict = {
                        "name": full_name_mp,
                        "designation": mp_designation,
                        "meta_detail": {
                            "status": mp_status,
                            "appointment_period": format_date(mp_date_from) + " - " + format_date(mp_date_to),
                            "authority": mp_authority,
                            "ownership": mp_ownership
                        }
                    }
                    if first_name or mp_status or mp_designation or mp_authority or mp_ownership or mp_date_from:
                        all_people_data.append(mp_dict)

            management_ = get_data(all_company_details, "representation")
            if management_:
                for manag in management_:
                    manag_name = get_data(manag, "name")
                    manag_status_ = manag["active"] if 'active' in manag else ""
                    if manag_status_ == 0:
                        manag_status = "Inactive"
                    elif manag_status_ == 1:
                        manag_status = "Active"
                    else:
                        manag_status = ""
                    manag_date_from = get_data(manag, "activeFrom")
                    # manag_date_to = get_data(manag, "activeTo")
                    management_dict = {
                        "name": manag_name,
                        "meta_detail": {
                            "status": manag_status,
                            "appointment_date": format_date(manag_date_from),
                        }
                    }
                    if manag_name or manag_status or manag_date_from:
                        all_people_data.append(management_dict)

            financial_ = get_data(all_company_details, "companyFinancial")
            if financial_:
                for financ in financial_:
                    reporting_period = get_data(financ, "referencePeriod")
                    aud_data_ = get_data(financ, "FilesAndAuditors")
                    for all_bs_data_ in aud_data_:
                        bs_data = get_data(all_bs_data_, "balancesheet")
                        for bs in bs_data:
                            bs_submission_date = get_data(bs, "bal_date").split("T")[0]
                            bal_id = get_data(bs, "id")
                            bs_url = f"https://publicity.businessportal.gr/api/download/financial/{bal_id}"
                            bs_title = get_data(bs, "bal_file_system_file_path").split("/")[-1]
                            bs_dict = {
                                "reporting_period": reporting_period.replace("/", "-"),
                                "submission_date": format_date(bs_submission_date),
                                "title": bs_title,
                                "url": bs_url
                            }
                            all_finance_data.append(bs_dict)

            suspension_ = get_data(all_company_details, "suspension")
            if suspension_:
                for sus in suspension_:
                    suspension_reason = get_data(sus, "criterionDescr")
                    suspension_date = get_data(sus, "date_of_suspension")
                    sus_dict = {
                        "suspension_date": format_date(suspension_date),
                        "suspension_reason": suspension_reason
                    }
                    if suspension_date or suspension_reason:
                        all_suspension_data.append(sus_dict)

            history_ = get_data(all_company_details, "ModificationHistoryData")
            if history_:
                for his in history_:
                    announcment_date = get_data(his, "announcement_date")
                    his_description = get_data(his, "descr")
                    url_id = get_data(his, "id")
                    his_url = f"https://publicity.businessportal.gr/api/download/Modifications/{url_id}"
                    history_dict = {
                        "date": format_date(announcment_date),
                        "description": his_description,
                        "meta_detail":{
                            "url": his_url
                        }
                    }
                    if announcment_date or his_description:
                        all_history_data.append(history_dict)

                
            OBJ = {
                "name": company_name,
                "registration_number": registration_number,
                "eu_id": eu_id,
                "name_in_latin": name_in_latin,
                "additional_detail": [
                    {
                        "type": "aliases_info",
                        "data": all_alias_data
                    },
                    {
                        "type": "distinctive_titles_detail",
                        "data": all_title_data
                    },
                    {
                        "type": "capital_info",
                        "data": all_shares_data
                    },
                    {
                        "type": "activity_info",
                        "data": all_KAD_data
                    },
                    {
                        "type": "financial_statements",
                        "data": all_finance_data
                    },
                    {
                        "type": "suspension_details",
                        "data": all_suspension_data
                    },
                    {
                        "type": "competent_local_service_info",
                        "data": all_chamber_data
                    }
                ],
                "tax_number": tax_number,
                "registration_date": registration_date,
                "type": company_type,
                "status": company_status,
                "addresses_detail": [
                    {
                        "type": "general_address",
                        "address": complete_address
                    }
                ],
                "contacts_detail": [
                    {
                        "type": "website",
                        "value": website
                    },
                    {
                        "type": "e_shop",
                        "value": e_shop
                    },
                    {
                        "type": "email",
                        "value": email
                    },
                    {
                        "type": "phone",
                        "value": telephone
                    }
                ],
                "people_detail": all_people_data,
                "announcements_detail": all_history_data
            }

            OBJ = greece_crawler.prepare_data_object(OBJ)
            ENTITY_ID = greece_crawler.generate_entity_id(OBJ.get('registration_number'), OBJ['name'])
            NAME = OBJ['name'].replace("%","%%")
            BIRTH_INCORPORATION_DATE = OBJ.get('incorporation_date', "")
            ROW = greece_crawler.prepare_row_for_db(ENTITY_ID, NAME, BIRTH_INCORPORATION_DATE, OBJ)
            greece_crawler.insert_record(ROW)

            time.sleep(1)

    return STATUS_CODE, DATA_SIZE, CONTENT_TYPE

try:
    crawl()
    log_data = {"status": "success",
                "error": "", "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": "",  "crawler": "HTML"}
    greece_crawler.db_log(log_data)
    greece_crawler.end_crawler()

except Exception as e:
    tb = traceback.format_exc()
    print(e, tb)
    log_data = {"status": "fail",
                "error": e, "url": meta_data['URL'], "source_type": meta_data["SOURCE_TYPE"], "data_size": DATA_SIZE,
                "content_type": CONTENT_TYPE, "status_code": STATUS_CODE, "trace_back": tb.replace("'", "''"),  "crawler": "HTML"}

    greece_crawler.db_log(log_data)
