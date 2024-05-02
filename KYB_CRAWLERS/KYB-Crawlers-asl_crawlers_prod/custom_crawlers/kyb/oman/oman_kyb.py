"""Set System Path"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
"""Import required libraries"""
import os
import json
import ssl
import shortuuid
import datetime
import traceback
import pandas as pd
from langdetect import detect
from dotenv import load_dotenv
from helpers.logger import Logger
from deep_translator import GoogleTranslator
from helpers.crawlers_helper_func import CrawlersFunctions
ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()

'''create an instance of Crawlers Functions'''
crawlers_functions = CrawlersFunctions()
'''GLOBAL VARIABLES'''
environment = os.getenv('ENVIRONMENT')
# FILE_PATH = os.path.dirname(os.getcwd()) + '/crawlers_metadata/downloads/excel_csv/'
FILENAME = ''
DATA_SIZE = 0
PAGE_COUNT = 0
STATUS_CODE = 00
CONTENT_TYPE = 'N/A'


def googleTranslator(record_):
    """Description: This method is used to translate any language to English. It takes the name as input and returns the translated name.
    @param record_:
    @return: translated_record
    """
    try:
        translated = GoogleTranslator(source='auto', target='en')
        translated_record = translated.translate(record_)
        return translated_record.replace("'", "''").replace('"', '')
    except Exception as e:
        translated_record = ""  # Assign a default value when translation fails
        print("Translation failed:", e)
        return translated_record

def get_listed_object(record):
    '''
    Description: This method is prepare data the whole data and append into an array
    1) If any records does not exist it store empty array.
    2) prepare data complete and cleaned array then pass to get_records method that insert records into database.

    @param record
    @return dict
    '''
    # preparing summary dictionary object
    meta_detail = dict()
    meta_detail["expiry_date"] = record["expiry_date"]
    meta_detail["alternate_name"] = str(record["english_name"]).replace("'", "''").replace("N/A", "")
    meta_detail["aliases"] = str(record["arabic_name"]).replace("'", "''")

    # create data object dictionary containing all above dictionaries
    data_obj = {

        "name": googleTranslator(str(record["arabic_name"]).replace("'", "''")),
        "status": str(record['status']).replace("'", "''"),
        "registration_number": str(int(record['cr_number'])),
        "registration_date": record['registration_date'],
        "dissolution_date": "",
        "type": str(record["legal_type"]).replace("'", "''"),
        "crawler_name": "crawlers.custome_crawlers.insolvency.oman_kyb",
        "country_name": "Oman",
        "company_fetched_data_status": "",
        "meta_detail": meta_detail
    }

    return data_obj


def prepare_data(record, category, country, entity_type, type_, name_, url_, description_):
    '''
    Description: This method is used to prepare the data to be stored into the database
    1) Reads the data from the record
    2) Transforms the data into database writeable format (schema)
    @param record
    @param counter_
    @param schema
    @param category
    @param country
    @param entity_type
    @param type_
    @param name_
    @param url_
    @param description_
    @param dob_field
    @return data_for_db:List<str/json>
    '''
    data_for_db = list()
    data_for_db.append(shortuuid.uuid(
        str(record['cr_number'])+str(record["cr_number"])+str(url)+ "oman_kyb"))  # entity_id
    data_for_db.append(googleTranslator(str(record["arabic_name"]).replace("'", "")))  # name
    data_for_db.append(json.dumps([]))  # dob
    data_for_db.append(json.dumps([category.title()]))  # category
    data_for_db.append(json.dumps([country.title()]))  # country
    data_for_db.append(entity_type.title())  # entity_type
    data_for_db.append(json.dumps([]))  # img
    source_details = {"Source URL": url_,
                      "Source Description": description_.replace("'", "''"), "Name": name_}
    data_for_db.append(json.dumps(get_listed_object(record)))  # data
    data_for_db.append(json.dumps(source_details))  # source_details
    data_for_db.append(name_ + "-" + type_)  # source
    data_for_db.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data_for_db.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        data_for_db.append(detect(data_for_db[1]))
    except:
        data_for_db.append('en')
    data_for_db.append('true')

    return data_for_db


def get_records(source_type, entity_type, country, category, url, name, description):
    '''
    Description: This method is used to Prepare the data to be inserted into the database by parsing the metadata and using parsers mentioned above
    @param source_type:str
    @param category:str
    @param country:str
    @param description:str
    @param url_:str
    @param entity_type:str
    @return data_len:int
    @return status:bool
    '''
    try:
        global DATA_SIZE, STATUS_CODE, CONTENT_TYPE, FILENAME
        FILE_PATH = os.path.dirname(
            os.getcwd()) + '/crawlers_metadata/downloads/custom_scripts'
        SOURCE_URL = url
        # response = requests.get(SOURCE_URL, headers={
        #     'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
        # STATUS_CODE = response.status_code
        # CONTENT_TYPE = response.headers['Content-Type'] if 'Content-Type' in response.headers else 'N/A'
        print(SOURCE_URL)

        df = pd.read_csv(SOURCE_URL, skiprows=1)

        df.rename({'Unnamed: 2': "arabic_name", "Unnamed: 4": "english_name",
                   "Unnamed: 7": "legal_type", "Unnamed: 11": "cr_number",
                   "Unnamed: 13": "registration_date", "Unnamed: 15": "status",
                   "Unnamed: 17": "expiry_date"}, axis=1, inplace=True)

        df.drop(['Unnamed: 0', "ARABIC NAME", "Unnamed: 3", "ENGLISH NAME", "Unnamed: 6",
                 "LEGAL TYPE", "Unnamed: 9", "Unnamed: 14", "STATUS", "EXPIRY DATE",
                 "Unnamed: 19", "REGISTRATION DATE", "CR NUMBER"], axis=1, inplace=True)

        df = df.iloc[:-1]
        df.fillna('',axis=0, inplace=True)
        DATA_SIZE = len(df)

        for record_ in df.iterrows():
            record_for_db = prepare_data(record_[1], category,
                                         country, entity_type, source_type, name, url, description)

            query = """INSERT INTO reports (entity_id,name,birth_incorporation_date,categories,countries,entity_type,image,data,source_details,source,created_at,updated_at,language, is_format_updated) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}') ON CONFLICT (entity_id) DO
            UPDATE SET name='{1}',birth_incorporation_date='{2}',categories='{3}',countries='{4}',entity_type='{5}', image = CASE WHEN reports.image ='[]'::jsonb THEN '{6}'::jsonb
                                WHEN NOT '{6}'::jsonb <@ reports.image THEN reports.image || '{6}'::jsonb ELSE reports.image END,data='{7}',updated_at='{10}'""".format(*record_for_db)

            print("Stored record\n")
            crawlers_functions.db_connection(query)

        return len(df), "success", [], '', DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, ''
    except Exception as e:
        tb = traceback.format_exc()
        print(e, tb)
        return 0, 'fail', [], e, DATA_SIZE, CONTENT_TYPE, STATUS_CODE, FILE_PATH + FILENAME, str(tb).replace("'", "''")


if __name__ == '__main__':
    '''
    Description: CSV Crawler for Oman
    '''
    name = 'Government Open Data'
    description = "The Oman Commercial Register is a public record that contains information about businesses operating in Oman.The register includes details such as the name and type of the company, its legal status, date of establishment. "
    entity_type = 'Company/Organization'
    source_type = 'CSV'
    countries = 'Oman'
    category = 'Official Registry'
    sheet_ids = ['1uCrP7BkzdrAn5jsJ5bHJuY-iVxBKPrCu', '1PqM2rGf9ffVOl7zmLRtC9CvF64KDe7RA', '10Igrb44DfwUVwuknZkhQOLSeqSYkIKOR', '11XR7qpa3mymGBw4hKH9ejL35zGUEvqoH', '1y2mJ2T-vZhoqASLrY3dESSEftuHZrcSY', '1gfhLCE2zwXOM_BM8qFHu83fYqJ98ymu6', '1qQSYiut3EQ6EbV718FSVE01QreuKXuGK', '1Aly8L7q39HFq01sJxA655WznPkqVlKoN', '1OLF59rahOM9oHNJY-TwxPaAnnCZKN6UI', '1UR0eEziShWw5h-sizys5o1XNscYQY1mS', '1WDco_a72WD9gccL6oJut9yfN2cU0FYqb', '1DYvBm9OKwGC8j9lenQAmCzit2MF4SLQf', '1IN7uOdKIF4DbqQz0JYnn1Rt4dfsHeeBP', '1XoYOXebIY4JEg58LuoZNlRfYztOe2NjB', '1s8hU-xLltFnXYH5DChDv2V9BfSmr9Air', '1uu3rK-iG6h1xs6H8irRAvm1MlcujHOZi', '1ehdE7BoqlmVeKbwQFvPJPnPeZh-q5HIR', '175hsypCfyzznStyVKV0DedqPeVgJIZ4a', '1G2mJrmqWkkNqKGtLVKqHkc7IrwHFneOq', '1pCp1XYZZMCSDZE4ZciTxwzGhvjFcg_5l', '1F0hkq4NykrVrCEQAnGLgxkkp6ZfkTh5j', '1P3tDZ_O5NQZoNcqueybbnU2Ee0ng', '1GGhFu26vZQbtqcYFpE_hANyh1eRMpt1Q', '1pafxVybryaCq9ZzcJ_xTDGvmPxvYqDqO', '1Q2vIPaxYR0c-Fl8elOsrOxK8jR81vxRd', '1zMxhKN1Fi_qEUEIexPCmmEVW6ps-W8vh', '1MBjUu-q2c2gCWGSXjDgtJ56vX_Kh9aY4', '1yYOeJfbDCzY2UGYS4BGP4yoBpOeujTNK', '1F6EIktnHfJPr0aoP6s7c9rmSW6KBrnX4', '1Ctdmn9f4iDLqJGF7FX99F_TfBy0NIQH8', '1TDzG5WsKD9pOGidFNOY3sTGmiJVva3ZY', '1UpvF_uTSwiKK_BiccdVu0E7fM06xjFO5', '1bvLQqL6cP6XC2jFCLvZ5YxMRkWNRj3Y1', '1SGhgoUraXPRvEVkTtXoHe-pPErONdhS7', '1NFLQikNVxmPjO_JsphhmEgSGNnF2cbHi', '1PFe8dGBWUPEPXqMXg7UgZmx1f-JjJ1y5', '14WXamY4HPpLrD2sEKAx8Eco9T-4fTYKM', '1jl4fG0ryUOj0ToDron68ch6SY_wJHRdw', '1xGL4uMov0D7TvGy-lXdpFPBYWXVEqvGV', '1SHBvmyFFLfrlYd25vf9o3TwCUYRia5r1', '1x8bxXTzp6whoc_ZzMPivzfpwTvdRSQbX', '157faW5J6DH4i6CS5J3xXLNvIIktVNPI0', '1T9ej_et3CNTZWVYSB8MLs3Hy3oAhvLPE', '1TuA0ij2pofpHE1zB-TKfCUDw5LkWtc7W', '1ZdUZ_VY4z_Xjk0oyIhvoyjcpkC9QZ-ru', '1_hoJtEt83SOa7uZATYwKvptCS_QZckH6', '1Ves_7WQoPiRYVwtCFlj07fh_aENyFhkM', '1Co0jtPO1AVE6NBRZvJbF1PtYRt3rL3QK', '1zlgpkxs9Tud_ZH3tk8P8VETsxY8gFH2E', '1-Xmh5JsEpCMhN3XvdwG8MalDjAQMtHDu', '1TqdI8UaIVaKk5mMzzy2VDb7wDslA8VPJ', '1ww_1Faq3kmWeffc2qDTeKu4Xs9vISW4a', '1A1HPx1fYc1u40FbU3okN4lZJZYi1vq2S', '14cTWLG1kDPesVk1obE69wXkLY0MURZlo', '1bWgVsYOFEUQ9FMudEXOFsHrdlSrIxwZH', '1Ibwlg6Um6PD9PmsE1eMY6dRCln6R6nGs', '1WD_rtvAhOI3Pgl1nO-z53Nqf7TBbgKeU', '1VOYrW1hr1uLyj6yEcV21ciMTMls0nlMb', '152l_GDrgF69_cK7w8yJ100UCgtA7qjUO', '1TtqiDoTpl7xh5RkhJVXlyh0Hl5qFimSy', '10fn3gbO1cLRjNh_kkDP896UHGHrP0N_h', '1arJEtdoIRk2yfji-_B9vXCMJ9hiyYCC1', '1trqFaadMHD3QAMyK9MaDSQFACNEWb9d5', '1VVUH6FLTgHbUnAHJlSiq8GAd6TvlDKaY', '1CK9y7IZ_aZ0AUYM2caizeZV2J3DobXgD', '1bebgiZis_xj44xUI6qOuU3RaxATNx2hB', '1kBNTcktgDxgw4-t4Ak_akW_8JBhvFGis', '1MCIcYjx1iNN7gUDhv85IxYGL6qZnGvp5', '15S1Cb7wEjaudl_g6-ENk9LeDp52IYKOg', '1z_ouP2jEFmVp2hn9tz841d2f3AGIcSjH', '1EbDLJpik62pFfELpHA1N928NfDqt-2A8', '1aMAwo6pNT_ZcsRr-txJpub4tHq3v3ucA', '1n8aLphCJmYKNw1sK-4Gw0BF_vS11mf6C', '1-B3qhV_LqEE9-CnB9nXGKro--nXWew1v', '1oMhrmBjWgCn8GMecUKv-Cell9pcKmMyL', '1zo8H_u3Twn65x4oN8c6zvME98Jd43YSz', '1T9DDYZ9tWQd5XhNkcAZ_WWeyDaeA3CTk', '1VToBbGR1_G5Toq-wBt6PvjtHqKvtO7o_', '1i5RqzFWk8xLY8lKd2KdCLY2ToOCpyCqa', '1ehuwnlYNFpZ3z7FPzfbqzLxnQcz3KgC_', '173QbbrFk-_kieU6MLgG2EX5pA_d9dP0A', '10usQOCiAYOBqNQMVnKTyW9IgF-B2NgAk', '1omxOJ8aVYyG6ZT8pe29U98miT1lEXimI', '1AOjrHGZtHkSI4hQTbNzYj8a4xitlIMCI', '1IRQyuf2_96LfPRVlU9Cet42-TzR9uqKG', '1JHFcW7tUY6VaRPpjBc6jH_BxGLJCFarH', '1w6IbBLe8srZUb_zKnht8ZQotc0CvaAIo', '1U3ZsyVOrKzZ7xDhxB3fIP6vx6ZLhsWf2',
                 '1YO9WVqhe1t9e5pyvfaF97dgKrXYegAvh', '15kxdNd4mhbbC0EBCc65PMJu31OGII1Hy', '1iiO908gm27y07_dpGCJXo6d93ZI-mcTx', '14HKWebRG3etyfRh1QC__VcarrGA67kbw', '1Ia-LnVs1mzD8ccfQMjwMRQGGwUy4z-ug', '14BEE73ediCEMimgghCvvVIWi6uUGAdhg', '1x8Jv3QyrVoV66bOf654wZjMxHMZ9sWeG', '1iDptXsjLUdH6_E72Dazmta1FuvlzElDb', '1Ufsoia-yGAT-VqyL6blkW9d4CBx4hRxD', '1_72WYN9w0cDJsZCHjVo87Ti_bzpNatxI', '1YjyMx3LH_LsfRUiZ2Tgs3EfoiEnHMK7x', '1rzm6t3oMmHq6os9kbaxn2M9Tumqg-aI_', '1_Yxu9DfMKaOKmr_eJCFtwzUKxV9AnChx', '1bptk5z2j47TZWYheSh0RCY3xDbc9hGt6', '1FLuu4v9NTgusQSB4o-tzJbR4XfUrz3jL', '1Sr2LW-YpbKvzbSo-wzL-xL2hyFGvtOKE', '1XyJJExOXdAwZ70i8zSyd0aSehXihedz-', '19BEid9f4hcqvLO-B5g5tpOK7Yxg1r6t4', '1rhKYFjN6sv_jBg50_lvcMcXTbLRNAZTB', '1S6XwZXIRe_8lscCEG18Fp174Ri0eELJD', '10IHLss5nBwkn_q-Ton1CpVpdtN1dB86d', '179cC1Zeyll7T8fV2ANCoP8WJ9ufv4bl8', '1pHprhePYS-rWsCBVjE5k-SaeSQ_jihHk', '1_7ntHz9N6ClH8U0futjVXeHNSPpm8gaz', '1gRgqjQ9HopEGfYsBGlIZAVoJxDdlvoLC', '1_OzqaJTmQsv1XVerDSXz5AVnZ8j-5U8M', '1e9sDO8sbCsmWkQUP58pOEkYXOy6bfzB_', '1xyZbjkxJHS241KDp4ncZyqpuMmWBbSuc', '1NN3j0n4L0eQVULppRXjFIzGgQttH2QyW', '1tNgdT8ab5ksFHZKWTUVEGxvgaIYGS3LD', '1o3fLfr2bNDtE41L2wUuMfUg_IRNUN47y', '1umNfQypiVkZp-wY5f6CId21SQNXvr9ve', '1625tpNH779LB-joud0X55Q8533BQbZAV', '1mI7odjdLaB0Jxob01vJZEMHrZgmvjBBj', '1s31wCYMOcHRo82MmMmVi2dre23WSx-9n', '1zF6ADs21tnfzPtfFJ93objT-7PEsd3A0', '1UFFUz6-UxeNyT0SjxI9k5uARFD2JvaQl', '1EkCkL8pkYY2Pnml6XOZ_vGes5mtTfKTL', '1_teySP764D6zc2YbJb8T_fofWOjGUOyN', '1-tGT8lawf1bgL3u3Q2txXdjWbkvvyAR6', '1P_tT3y6EecqJSNCrE7lh1ia5F5_2N0na', '10jLUku1lnwmadi6MH3wbQjop28mxyClo', '1aPxV1w_VIkqNtShGb1CZIeT6gtaFs35O', '150SHk6tBjpxdD5bsXEB8oVyWEUr3KYhD', '1EvoozScC3aujuaothyZC7xfaUaJ8s_qA', '1IHhQ2CF95hAqRixwdv1qlmth0caL4_iJ', '1GZKLX31PA3f4WeYRER3CxQSqu0tSbTnw', '1_ogbj2D0lOM-teAroSTkHxnSXWayOJk4', '1iEl9eK8TYNIztDEgLil14fkgrIhO4Y2s', '1rNLLruMkQBYWB13K24tgtyCkYBJR4gBq', '1iCV3WdhcJ-0a2MS77AxOPz-VZq8qZtYQ', '1GWRuvhhE1JITzL0aQHL8dfD-2kR7B0k1', '1oz_SZmxKzjrW7HUvCy_dAjc_l1zEEtrk', '1aeR9kOFskgRCtMuYpQhqAcmbefFraA9G', '1MBJETf95LAceA4gu_Jk-wPxamUWuuonl', '1bLXtsYcJJiQBMzJLJmaoArPH3QZA6ycm', '1YwdAA62cPTC38zNF0uSpll3XVjb5v088', '1n5KkJ7cgIYolibMhJTtD1P7A5T_DmTuW', '158EYjxprT8_U4VXrFfSXFc6mTuQlJ0yG', '13UuBDVy4Ski_OHvtHX8VcHrWYACBeBfu', '1sVtsMTN2i-QT-oUD2g-yD9oldnwLoFkn', '18g55AeTFmUHKb0CSwJd4AuZZoF2qy_Cf', '1fnFlIb-X5gYW251yk3ZEhtNIP0_DHqdG', '1cl0pK6gtAStSdNwvJGj81p38EScJ_ZNL', '1KxWwflhKfmUlaY6T043fWXpoOSkGbgLe', '1uZnlC1pPc_E80QxvF8hUJjpF2zXZhreo', '1T7aPIlhKvTbA48H6bGaOTXk8xPWcJRfs', '1hGS7YgKOenNeI3T0xjpge9jIKq7d0EH7', '1P8DzjZxHVhCQSts9m9cVqrQqcOQX5gT1', '15eE2ikvbmjEN7_UdVVX_Dei7juHUVmdp', '1Ba4dR4gCyhxg8xEN1-9F4CLFA3vQ-G_W', '1GLPEOJVAbAAo2E9va-X0bLKb_g4EuEQB', '1uiSEVAJE2evtogvrGPsbcMqS2io4JADP', '1JpOARH4mmGzQH1Uouxx6MQhBUrnhqDez', '147cO0PYeFwV82VQo35IhrZ9eHFTwPMn3', '1rLtDT3leBBA3s4Erb7_62T5sUue_AvFp', '1iVzqjnYjW38bomjetdoI-UghCjUN-4ko', '1wCb4ry39eMjmnNwJXstIbtMG2UnFrTCn', '1Ske5VnOe8SaHdQZ20novBjgDspYKsd5q', '1SWsPVSbjuf_DTPi8jjQ_-y5CZPIMI0hu', '1IXbLCc7j8LcxxfdXSBpFRi5qNHY7u6Fp', '1JF93YjyQbUXl4Wul2XE0v8f1sKshfQ9_', '1TpmTiG49iG8LB-dJo1vNBM65B7xD_Law', '1qAAztvEODddLD1Yo0b1xWfZXjzd52441', '1GCknta3g10v-oqvxr2LtqKcs_xXHhI7V', '1f2qaBR56APV6iEHPbUP5dtBtk8UfTTi0', '1v_3Z97QYDWvVG2WERyGwd3DXZmZfHd_m', '1e2TSJ0JxOyQEDypBHuduoUdQDcISSKqG',
                 '1Gy5VEgfg559mI0PEsBfMkeAq6Dx29zWX', '1vZV-Xg3NKGzxtQCLehlls_scHkNx8K4g', '1hhmjWrvqNawzOONw8Dyp_t1D1emC8fhB', '104FLEEUp_dC0m3aww2FxNc53dOAu670n', '13XyFVTS0n7kDNmSSTwd6Co5wZGZHbfRj', '1CTkdcZ3lVdQ5yGjObDDf8QC020u7oVcS', '1QZjFeQjRZmBKztSxebauNIN5NkDU1mEd', '1U0S3esXJW1-bubkygeoQr-WMbjkQudN0', '1cF9shvZNkJMMDDdZcORRWXfZ0SDiRl_a', '1Jf-I2Mh3W6oeFgyF6-6mJ9PvoglbRsL0', '1pNOzv-9DlaxIcCiJBnfjdvo0-azIvgQI', '1KKCzz1s4tJBRAL9sCTLVi325j508-izL', '1FSgtWCdvZGlsihBOwEBmHW0i576hzZxb',
                 '18PxvdUkFzwfpNTPpB7GoxAWwJL89U_5s', '1qC8fV5XxWSt0eXDdMMzoNc6wM_gjRxht', '1C0U4xe9pcv1uOPGkLxh3gyAOu4pt4aCV', '1bG_p-3h6SudzXlEJs8c1PcRkmCF01PI_', '1rQVFl4XGRyBXZpPF1Rjr_dwzoY3ckNbb', '1So9FhShQRUXPhrTXBs87HjyjsQs1Kau7', '1SvEttqb__wgaW8QEisACh-tsyKhRPO9v', '1owuCnnWHvb2pclenub-YATJ5J1RvDDGu', '1LN36xVhtYcUXbrShKMZInG8zBbgy3gWe', '1Iq3dSVhOVhsk7M3e8Fl9UosrCEVUGBe8', '1okfqexgzC-2csJkqyfyn1S1Bgki8W0CB', '1mijxKC90C-FbILrTbq0sD52R8pYYwqoG', '1-o80BE6jE-F5-OkxEDBr25_5iHRytCpX', '1y03FcSgtQewpZPOvay3xdy4mnOJlC7bI', '11E_NyiLwZFqy5IylrKya8fco9qTPZeEt', '1fQgh1kpeUt4EGtQYTFCqnocMMT6kf6IP', '1WnY9G2c6rOfMb5iAsu2dOFW8JjD8IN2U', '1rN_NzEec9pIp2wKDBdsWU2FYz95Kh5w1', '1AyqXMLOHTaZQelzM1a2mmgJW9H1PLwYR', '1vGg6-gCIbSa8rfN--VaWOP1HC6kG-cIZ', '1D0viKclb-nmTS0R6A6-xonQ_F8cl-L0X', '102iZHOytv3yqbOCHJ-6QhLdfCHEhzea4', '1E1LAuGsup6NbnQQq2ZhKzi_DALS7Tu0h', '19TRKha5d-MvG025kqDYPLHyprQBd96Sd', '1Axcn9kDq1f-JWPszxhtqdbCAJSaEfMgT', '1XEQ3U0QsPt5xoSpTLN9m5Cx1kUpcfjXf', '1jwn7R8EAQRNtNXcJqGlZUQjubgKLybAj', '13ufsedB18uisd60KqFA3XDB6eb50x-2I', '1yVBw4ACnLo_YUcrGpUhDhwWaAAqEUjzA', '1KaNIqz-3Nz7PtDEv1iYNOotOgrm62CG6', '176gevhwg3nzf2BUI2UcPc2bt1Xaf6dwd', '1cnRfpEBxeiGhw8qaz-i-9TA3L1eg1djJ', '1Dt-8t_bI-3qASuNqJrIncHl9sVnwA3iC', '1rDXmsbDVmti8OBXyf9vpzWgCmeNbuxw_', '1CSdIFIddLXeO5nCaf0iQVA4I4cDyd9V7', '1NOLxw-NYDykimQIWkJO5bVcSHCOWur_3', '1CqsFKqHJCp-wZNQn0-2ssqZa0JH5hB_A', '1z7eYzzRdPf1_RmplOe6untncQ3QoV66n', '13A2xahJqs-Aya8qqmCtkSEldE_bcELgn', '166T2EGmHwEl5GKZY3X4hPShy_mWIuH85', '1PLzjqyuqc62Wv-OJgx4w0-3KHL9JK8fx', '1f_42NMxk4kwOA8zWMD3BlJKQAKaJfWCd', '1zfH6GPssLjC2pkYf_t5MZgNW71BWV85Z', '1dXRV8lGjrnNPUTvPgh19UZFrmQI8JlAZ', '1aobzz4BxKVy0uuSC_K6CVes9BdHc8jG-', '1WYp1gC5k5AIicS-YDONPAoTIBMbvMEaK', '1GjwCS5YoBDAzp_rbQMEyx_aZEcpDvmpb', '1AiMk80vkRPsGzH-gTOvbeJcccs-7ys_S', '1eEiM5_iL6WGGbVKSkSvZRpTppMwi2bJ1', '1B1eJ0LkbxTYsFXCIn6E3-OBCbCuLGYuf', '1Rt9ld4H40-yPmlF1sjM7_EpG8Bz-iIUD', '1G1AHpxJMuHs686NyiHnhKFATn1CLkiBu', '10hWVBYCD2bfcuYaIVoMmtiAMrJl_0-Db', '19qxL8KbqzUiSnwbMaR3XF2T5jPYQkXhU', '1jgRQ7PAVVE2AC8ZGzuCfSPdWOwPbGu8G', '10sM8Zy5HsbojMAE6re3nUpygNka9ISqr', '1of_6-fEof5wiSSoCgGHoH9hU8TWgqx6h', '1VnwD3z62EHYI8yDwBUdk5of60O075Epl', '10lOm8MycA3vK1RE1q-J3yDwR79geMsPm', '1pdL4k7UOG0cDstp8WEHL2RxUCgEQ6eVX', '1ZVszYFn5OhELzpREShDCCflhwh2OALpo', '1NLxIVkGnwnhUfdXYjs1sfczVEPiYvakA', '15ndgbgPkeNdeXKAZuHZCVLCc8Ide3l3H', '1DQhKDJctEqK7SQ_6gwL5r7NjLoKrrcKH', '1smYxH6y--IvqZgW8prU_WIYO2Ll16bn1', '1HeY1btW-G66v-RB7hDkGt73NptQ1wU4d', '1HIxhoo5_KBD1CQY93pvYpNnsSKXSK7Cc', '1XYMK30yy9uCsQlQVGLX97uWd2gSmeiTt', '1FU-ccNPKwnxPHBlhkChSt_mLPsfLt9Ni', '1jljIy6UMQ8Ztwv0NhrbduJp-cbjxFskJ', '1Mq0o0gsK0IYpF2upCJXzH8o9KzfSvvu3', '1X4Wh-9rUdf6TlZj42JToRS5sqZ79HWwL', '1a1Sy6WyyQECMfnLlxWKL_ZdDB0Dw9Rz_', '1ulFS74YcoTNzOrOV9ZQOcuz2-1oUhPhJ', '1FB475Ssb4J9XiOzIVCqhILz7Bfk-bO6c', '1MqkL_c4mvPGu4IrtmqNARIcJLwLSm1_o', '1atcfpOm7qcdlJj5NgnJzzB2HCS1lnzhd', '15lTjGQhRrYZHyvvISEtmTY-sf5YRIRs0', '1k4a0A-Nt-ekoJ2Dqqqm1R7cZg0giDNxI', '1An9pznLjh3QDTUfSFW8tLzonYW5FCjqg', '1beGHh2-WLhIQfErHkBik30QOvH2_zAQL', '1twSRRByhT9EWWy9T7RXVDup9Z-UM6_6q', '1AtmnbhOsaY5Lh4yBgC69kQ49sVxJI3fu', '1SnkWhuH5EZBDX5tQg1E_Gu5U7Jh1IET9', '1dA9nnR4DOapfQY63DHeTHHKJaXQJ9qW7', '15RoMC2Qwfj6dcD5w1ThCgKW2LXE3SRcN', '1N7cBrIInNTicDZE46CjgRrWy2eTc0y0k', '1qF_lF0crsZgJvCbNbJovKyZeyN7tF25Y',
                 '1x8GRg7m7pLvhP52IZffmJTDL0giHWOuz', '1gdzL-4dpHJ4ZDGzS3tbfu8NHZcXlMXk2', '1mkAX_MV-Q7HG5B7gbhGfOGIvbQmyv6yS', '1s3z_MX0bMwRe3jR5m_WbwxH3i8Egzvd-', '1U7JQpYb-_Vkoz1b-vl_7xEXGaYaF4Tnc', '1uL9ysSnld2cJJRFqh9UHjxIWLAUllgK8', '18PYvxNCNCBFZpkgxBoBx7guLkrTpwv4f', '1PzcwckDet45ER2w8piaezJd4tquuni5B', '1xJrUxzQl6n9Mj0Jhbsxhp4PBLLYlncWO', '1pihrj5gfne_uVe4aFHkvIb7UJUiNOxp1', '1TIzCTK3KHdyRyy_4f2RoWH6-0RQvB6-c', '1csXtqn0U94FPUvg4wGmSKnRx1ged6OHb', '1lFtf4AZc-QCEdMSHOuPxG_8WbClmzIqL', '1x-4lZyH4-M96alguqkgHVHRbpmMWd2ZH', '1AaOCv3D7ytkTFG6FtsUvgdrgBafOsroX', '1mFkKq6PyRD09xADEWgkODLUWk--UDuYx', '1wwQpwXxgoPpXbmVNMlq3sBym6P2u8Tq1', '1msFUqCVw_wKVGdACUtsrPVK5pPwWl5KM', '1TpRFnN7msFoR5vH5a5_QW5I-h5r1N2kk', '1IgxLRu-AvkkVD-4cMB9OQb1sh1TtKL-L', '1eOiAmGZ28yelx0TTrOkUubzce9EjX0Qy', '1Q9hYyWiXakr1UU3gEYcLmAKUqRepgS66', '1n_bEAXjtpjd0ME_Gsz1z5JzyQPUHndLh', '1HodvlPlDQwt__esSYndoro86rguyuJzz', '1wcehge09fwq6ARC56qzy7SJLEBHdLVwS', '1YYb-jS-VNlTHP1dfTG2F5_wtcj8MgD1i', '16U7NM289csiVseL8P8Cp3JPqgCHjxqUi', '1uolPd5rF-XC630dyBlFoC0VHZFgIwYYg', '1qQf8Y86C9HChb3eRBcGfElgmn50u5A4E', '11He9WYJVhhOJbo4OoNSFiOGEhGvdYk_7', '12IT72yBd0ypSg9E2hUcDMB9sUtOiWtti', '1ZWMX5HvxOiEOdGZqbUzpk3PxeMluQOGu', '1orMlOTU9WSp4lyq3XGNQRLWSNKH2TgWY', '1FRTdDtef_2ZFvx9knzynw2Pfl-ylyXi7', '1reKY7K833d0XWYIZNEkpkowrA6k7fuHz', '15Y7DuNrTAbjD2AziTG-UTzAJ6UbZhDYz', '1g4lhXFYMr8iEnO6kAnptFhH8AFhywKbj', '17Io1DqYUAIFMRTGFWVT1OMRS7YZD1qqF', '1XbIH5pbNjYgBGK_P7p6XQ4ozuqLvTMIu', '1dRlaIuwz6UTx_ELM0NTVmJS5k1EPRgl7', '1WFm1_MNcPQU3Qrk4Ua_PTeHh95xvAyPz', '1eeY4fmfDcUYRgHCq4H0uAulaKoaNp7Y2', '1RuNKDuNxvg3gmuklLCyUIabKTMAIscV4', '1AdhCRRICwv4ayD9v4reynkKYWxOw0asv', '1UFd7jQvnAAGa7XFLP-Xd9CgB25jAR0Xa', '1fxySBA7au_h0bjg_TdgJTK9ErUK2aAeG', '1n0wy5lilXjRinujRMqe718p8ruIglcdN', '1sI5l-rYHDwDWD_bVFjObxtC-i_rhZFt2', '1bVZCK1p6AMUX5PqhGDOXpR5-g0D-j8W9', '1OvalaLzaDuMqmKBT3SgY3ctXq2NE0TbJ', '19MjEdjgfGNrAOKZkGSpQ_-Q4jss_4VXg', '1xdYtjx_ma9-MG9Hj_S7Rz0fW1Olf3qNO', '1j3d3V0nFzS-TTH4FCyfj2Pkf6FZ6UPXd', '1vBUDHXqi3L5GwPbdnBjdfgXBvNAeUQjv', '1kkQD_HtjeGFIu1jYeYp6Koo6N1WZojNc', '1ipzZnLSgj_EtOK3VqBp_4AFZ7pREv7g6', '1SsM5RvFswRWXirokvWeWvhKCHWV73eXL', '1T0RAs79_WcFRCuv-1FdmHyCGoZfKQHCl', '1Nll1LIS5QOEFqd7hHQAR4sXghbi_qOBI', '1k2Q-8nBYEPxCIB-LGNyxT-IIazsWsEC_', '1q0OQscUDoU7OqW6mqq7FhmUs-Vuvbgl1', '1ePkqRLflLBZka0KWmFVbps026ygloLpN', '1yjy_5gnF7s_luNM0FmKMtnAclfbELHtb', '1oWTsMGIrg96x1aT-ortrrihTO1KYAFlo', '1Fw-pTVlPC6YO3UJ20LjFZyJCaFE6nrUQ', '1DNvvqSRz_YD3c-Z6NlfDLGVO5U_BAr3G', '1St_6WySJh4dAsNydvm4RSf7OMRTcIimw', '13xMZQ-vroqpKHK4b5hJJaL34B-kvTSIV', '1i98o5xa8MCZUzEpb6PVq7taNCu0fdgjM', '1GB0-4MBwnD_PhW-CJ6rOAd91pfWrz7C_', '1w_O6v4Wxmdof_4GYEVmJcpiV0-vpTaON', '1DcqCJaIMgZFVRyi9Vhp9LrMIGMl0KBZq', '1GtJdrE2XXySeVoZ_1eTjwRRqm3UtQnAv', '1xaGG127pxNcMhW7UAm7T2KsvLEXRrhwQ', '16wNHWueHOnuXUiEdlk9O1im92C-scFrx', '1LnDFUdmwKJwKIybUEhqsVvYJzTf3Zhgz', '1V5oPKL_0tIbKNOdaTDDJj50WNDgqJS2R', '1My-dAeOQVTntJOMj-uQorRr_r8ajeIUc', '1KIo8eDu_vbBYlFvj5fpuGDMXmAupdiG2', '1orWOYunjxmnvw9qRMI3li2MjTJgxWskB', '177gwtr3VVJsCnz3sYLhvH3tssw1H_W2O', '1xyCrTDLup_l0SSfuX6EqiyNLlnrCI2wy', '14luTd6CgnAGXbTDueLmRAtFuU06r2hXK', '1hfrLFu6G_WgczTZ3QIT3O_DmPSESYD6W', '1XPUATw7t47BN2NEN5hXy35Q8nPDPLXyu', '12vyZKJtAzi9NhyI6P8QjVH8XNpgUR1i1', '15uYmskt9oMOiUKsKOfllCSd1aJ39GSkG', '1LMxbAjWRLZ8c-VBuKekUK9ai5HDhdKgA',
                 '10byxLdRvR8S7n95koxzL3ixHlk5veL3q', '1QwQuaSJspzovEAeKc_0vszUdyl_N23Ti', '1dTeR9oFvyQHzEMMm_FA5FjMaoYwQtYM0', '1BR3-rEgOcbqUhYcb-aiGocnVIqMVEtxn', '12YKY5dNU5FyWLTdqwilATq9mDDsD7N4B', '1t0n7Zttc0Oge3JJxIIzLNek2h20cBWoR', '1vAe-RO_73L5UE5EXYc4qoEnHLYRMe1pt', '19GAy2jYPXNsFYi65C8iyq54ncj07pw2H', '1ewE3Dt8xOnW-92ShEaTJqo_EqDnQQRSm', '18HcLq3dFPzSjm91M7vV1oFeuZsw2xehU', '1vgduUjWjljBEuYQ_dDGFdpzWy2AX7swo', '1mJUgvX_AnUnLrgKZqHpFioFgjo-J2WTb', '1lp0yRYPlSYNl9WY6s2xjCCwexla0yS37', '15oZEAKvXv1llV_0f8vwQ06Hi5dGOipJ6', '1XNN-ixdXV3WcdY3beWpgG83Pt-739UJU', '1jAtblySManPHMIXMTku9rQBeQU2qIBrY', '1HpdEMEjt1mACcusgZoyGNDcFzcN9ImCq', '1N6_3Pd4rBWTRYu4OJKuL9vzdVNgxQ-LJ', '1ccwzKSF79m86ILWTOPj0nrZ3N2Rg_kZH', '1eelESKZvpbrhJWkxPJdqqYEg0LwKoBVu', '1FVzCo-uAoO-PIFr9OjD2xdwa23dnShqJ', '1SmP6ZMluHcXr7CoOtMv-b6BkMioufJyN', '1y7zWT_LmNR1NrqXOFjLT-QU4wFXN2PDs', '1eVcBUc1E5YOcK_GG8M8cLGSCS1RfZ9O1',
                 '1itQd96v20jQgmZkR-soQzpWk-nw4Ji3F', '1rmWpCHZSF_aJNXw2VMu1WVAiFPNae2nX', '1SYibSMna-Bypnl7pHE6e_hTxnmATtjun', '1Fz6jBKHBeVHvHpy1McrC5DEMUDgGgddP', '1-Ny4gawP5ectrV_hd4vH42QbOKvtiVEG', '1jR4Mssykgg7_xmzWY2ygtiWZsVtx2yXN', '10T2s5faoyNc85rz7gJRmhvj-JSMShXrz', '1bnb9PIP4D8tHmMzJxegk9R9HNGCP6rBv', '16khZmjkG3wSQHOfuOiM2HO4SBjmN07Lt', '1ytpD3K-RUCpQhe4QqxfLB2gwT09j7dLX', '1oT_yAnMGK8ANXctsH6ZR2dEHd1Ube0no', '103pdtJjxHz4SW7Nf-OjUbfuirZshpYFg', '1YyYRjp3lrCDZHMJ3ozTWZnFoQY5RKIBw', '1cISWT74bTc-tcZ7FtOkOK3Oo18fc-0Jc', '14VJE6lqkHjspsoXrT-6mfUcb-WvKhHuS', '1dxD20MaZYO6vBWRdX-WTfK-fdYvOexb3', '1aIT2shvi9tAWtaObPXa0ZHSUjTM93hZg', '1vpq9Npl1apO4uuJGb6d_fHmFEce3BKFW', '1E9XpCWt9-EhNtmTo_aMKHsTPjPrqToGY', '1XMZPvUp2BYSViYZDl052LWUJ7VECsclJ', '1yxMmeRkII-3U9i80ATxnISWWL6UmXbc5', '1fiajL2rLK4MYTGCoNUA7Kr6-cnciAYve', '1Rwwg8Ph8aBkHv4Ff56cm8Xm2LSMMhCFN', '1PJRcM2er4haoXF8uFxYQW3uKPlJw9-dI', '1PzBfmjI4nJNZ3hrCScgyCJrrxuHz7K-x', '1pXHOXHTotYEnuutTm1Pi7be5UUUyiU8n', '1gi70SpMU32zaRpzoNIorAxRH6XZJFAbY', '1lTY83cB_rqVnlbIMu2p_Uofd6s-JMhIQ', '1ygnUNYSWhpNC9-AXqJDmwViZANKUzexb', '1kZS2tqk6Ehh_LIGdsl43KbvaCxeXEgts', '1nKa9Rbn3M1-HKHFo30OAV4bahytwmNEf', '1QSevSfpIvRLv4YDr5N499LYYaQz1ulbl', '12icALlMTGBNScwrLsIa-lNIEy0uH4_KI', '19MQ4lByP_DhLI3uJcWokNxbDL1AGnqLd', '17qHXm_l-AE_o0cPAdwxHtyl9HiGLUDcg', '1wSImAiWdMZ3KYOOwxVhE__0qhawB7tQ2', '1V_mm9hTHYDONmJB9BMswucVzoXzrVREr', '1sVOF2plfrRoicXgPWNN1B5M7WDu-7tA_', '1kLGSQZo07UtXj4rOBPehYGcD__go-dxc', '1tW_A909V3Uj29vIU175vhnTTTk2zQz8b', '1dBzQEfroV8np8rer06dF3zqfSkD_2fJd', '1_PVocx5NMI62ULXQ_IJ2LTXusB5cTiVX', '1iSjrkrgW71al12UUFfEgTjrV9VLT0DII', '1VeatR4jqfzK8QdqCOIZgZYQSLoAC4xlj', '1OGtaM7msQaGrXBlVRtgk8s1_2T-5lCNw', '1jumMzDA2vWkX00umb-XjlDMAFUZ01Yko', '1HOSXKiLQulJyuxcrKhBmN1I31WPdqsbX', '1ln_1-qcyLpfKsXdkoefryRej1FF_1-pR', '1mFVF5uyGhDnG9Z-T3IAEWYcUGyn0fDPa', '1K_Qa7IwRTZLYGmh16Ui3Il8y1kNQCONI', '1OhXAdpda6W_zOtPByOeFmsQ-_tT2YwIP', '/1TV9E-WodapB1xVyE0Cesi3Ag1f5Xb9gP', '1VUwd5Q0kf93wkdpEVvi4WJsjH4Hk9r0d', '1HjREJTucok9k1SjFheS7qfmEfrR6jVr_', '1BlOXV6J0lV2COv_1S0DXWndRbz5jGfSB', '1GQSAu1orLMg7wDsD0-r-HFAg9VFh1FrK', '1l7MRnxmFgffqsadako2lOqFBlkG9cy8l', '/14C__WV5iv_EzoVyv8-TElALjWFUKaslK', '12sZea4HLQ_3A9qb3y3IAvvXIwXrxlEQ2', '1ReomLxFuabC8_c7RP24W-xlOMPBVMqhY', '1j1GFbNN6-ChkCIQR4vbpoN_MzO005gu2', '1JXWmCYHDcYEbrFBfwp9ZCP5hTYdxGL-y', '1F0NwwWGvU-Y-_lAi3YHowfuzEKpwPYTR', '1MkAG75Z4Pub7SZdkdnoIOm2gbv_UQiah', '1FuMM9WuhyhKFaodmqOhPvWQe2S5KXDgE', '1jOaf6jBx1SIZu3Zv0uTWKYxK_mJXBL-t', '1mw-ZfNVoO9ps42xPMk9M35PNyMYd7T3x', '1jlypsSX37kiEDRxGQv7-HZOe5VcChoVK', '1o25E0QMTc9FbJIz6A5pQZ7tgyRyKrIJG', '1gUoGrnNlZsmXvdGSxbs9_h8YC-XlcZ8j', '1EGTk61KBZV-5JviaMgvYPfZ_CT4s37zx', '1OtKwgmoiOhJ7PsiWCjCwY4Z1cOwsDuz2', '1PnsF7iAsM5d6VmOmKI_yFxZmaK0QknIP', '10N8C-3ic9jAAYYoEwySOysARt7ABF6o3', '1gALsc2gGtVBZ0qWs2dQmP33knKY-JzBw', '1QcJJ5vQTt6R9mZXJiwtDoq37MpADNtyV', '1mLXe4qumnZypVM18UMkJ9bCQZsaMxp6T', '1Nf6ivRQRM-3Q7eeOfDGyvH5IFMTjl-mq', '1tiRvMW66Q-_k1-89iX4_Pk5gO2zAe9hw', '1Pz0wNC4AFcOpE_aNTrWPJjU_vUFU9t2e', '1GOjdI-NLyCdbNbtyxQAKbuIo0oWmFuLk', '12gbOv3_I3XTPDSDwl9PooTDTBNLyIbOv', '1NnFPxlxOy9RFM1dlmmVM8MD3bd0DBFi3', '1A3XrTQbbIKzY2eWz1o8D_lEVsspYm8t7', '1Kj8eXmOScnx35ggSzowl9XA7vl4gF06i', '1RidcgDXigkhDnrNCx0Ukzg_OriaAlbrq', '1YHZstmUAb3RMybhMYMu0D3CrCTvD9ngd', '1vRBiIJ9k89xRIS1nD_46InL788dR4axv',
                 '11WnvqhECEhcxSJzy5A_t-mZbyTkV_P-Y', '1CctBa9qckZ5r-E5njqiALG6tFSvVjMCt', '1I4164S6f0ZX8NjjwzWUGh73_TsQnuJXW', '1BnIk5-jDFAKcfW_2pq4atwO4cDzDlwYk', '1cEvxod-dYNSKgyEu5-O9hVRNC-KMNR3m', '1InLkl66GD7fC-k92MydMiNEPB0KPY56N', '1qQ_bxNZsni4_DHOCaT_P90tK34D0EwqW', '1-16qcLEWBH9B4sLcfUvr3DG7X6w8XHa6', '1s0pL3JLd92vFTY23OqOUX1Of03_D_I5V', '1efqOkD2UhjubHtPHRA_KIR9_MIQRwBiJ', '1D39UKTUPK0GBkaLKmGXqz4MOr_n7Pdb9', '1S4fnwZWJS_EPbb7jNtXojG9pSwRqzP75', '1NeCKqtKFPFF9n2ick3LAkBz7pBrq5JwA', '1pE4t-q70hVO5-aREQBGedudQQ3_-1Usv', '11NqWzjUb38yg4pRwzyqxMMs9gj8FGaDU', '1xeAGK3cIWBYL0689se5qaG7cQ2wvn2ZO', '1B-emPUCTppRY6BrJyoa_HMAPyFVhpZY1', '1RxiV7ONvDR0Fedym2Jw1A9tJLCnYNjcR', '1JRQB8mxRnHDt7ysAyVhZPjtMlI0G1FMp', '1_mRt7mu00MeICKLxw8_Eh7dsz_dqSeJS', '1ISDFUOaKckViN_TqYruymutPBdAlzZeF', '1k_9ROJuzl-P7GTN4_tt0DzzuRQRUCdeR', '14aTkNpGOpseDo12zrIOIfWgg3568OgjS', '1YD5LYESuCbmULuId4fhauItj9HEvKrjW', '1pWI_YAe6Tz7xD9GuJiKTswaSRPEK0mup', '1bS51905vYTHPLGruXRYq7piA54BPHZ3G', '1_B4VSoZWRR3IEWLIMmfuUCujTAwnhqu_', '1Qv8ZvrX_k514rrnJdpkgiTygDhE0KWhb',
                 '19-NMAVsWkDWLrjKi32Pl_G40xvKNaA2w', '1hVJmCmfhBXNstSjAgaQikx2CpoaeQWjj', '1HDDgsvcNUsetrk2CFeB0G0Mnf2leMkH3', '1T0YBolwbyo6GbhDZslD6XBMLmdXUDz4A', '1KU6ojStvqSMah4gqi3aZfog59znvaezP', '19WrKg_HijyyXkidy24G5rsgQ88yhSmK7', '17BL87bmg3STZmZm_1sIbVe6k8xX092Sl', '193JS9b6PfSAC5YvfCQbZKEqy72Uo2T93', '1IxqUqRDEs_jW-FpOoj_QQ6SJmlBczYQw', '1sD9hAUOTYuxnk2F7XM3J5xoyK-_6o0iF', '17nSCXWkTIdnZIysp7bVGG_RFyg56imUF', '1TN1DsuFu9jEzFnBBNcICSx7jhVZuA_Yw', '1J8-VeL1PZSS8KjnAn1t96m-CoRcW73hk', '10elv-F3uyFvM8g8ewlIDJXAvtP35fYv-', '1Fg0IBGnEmlFPG9l6m2HiXcvIg7ED93qd', '1g4yLnUEl9qdaKu7wztY-6ql6cqpAfyES', '1CcJlG2RtHM9AePt1p6Okr4YQLqLqEBCN', '1l7ORkseDR14KzvvBHXkLcpLxOKaRhCku', '1d_iWRhMv-OMX_7BOW0U7bkatQG-LEbCa', '1REYdaCxcKbIVzs2EiEsdkBQcUhKhrBDz', '11fCX_q3eD017y2o4uG8fdrhykApRyBXw', '1WXEW-q8ZNp_lgxGOfBUSgI1eX80UX21B', '1PnbkQOw6z4mICB_nSdDAXOAb04QkcfxS', '1qTgOQKgX72KZDt4RPeN8fqsiYKqM0JC_', '1HIH_cyBJPPIQVU7V4c7M_wIjrdd0sm5v', '1eeyACRHWUY0opaVVEBLhgNQ0izhC8g7U', '1brw4fjQ1v3zpe1dAlkehT-WuFj7bv5nr', '1EPr_fyVBZJgp-ABToocHQE21qUS8CjKR', '1VH1VcIExnAdgFC0jMOyHEKAu2gNwzE4Q', '1MFbMPMU3d2Cvpuuu_0eREAKGgma3vCSs', '1hoapANKexKuThJw7RRJFSkby3pPjjo_m', '1f802YZyUuLVHQTuCuK3_NMwYJs5bBAjg', '1YRbjWSOGcdJd4m31776T7gmNWbzDY_kj', '1fQOy5O_fRHYv-MLJDrGl5LBnrJXHy4_R', '1cgXBpPCX_7VXFDr3Zocdn3kDeFuBjb81', '1aRiPgyGd8Sq4LhLQliwF7j5Ft-7nKqJN', '11OB3UaVcDhIC4pboinKifwlUGWdOJHB3', '1x2ikI6ZigQ9Fp-twPmM_gUuw4L7nICBm', '1rpYiDqvvaC5na_uQliJ8Cm7BuexVL9O5', '1tcw6rBJK7yuRcJusAGSX8JInlsoQ3Dws', '1xKJu384tQFOEAKnrXzdqPbsb9BBxoyO6', '1s4Frq8PE3LB5XwmC4OQhUQcRGHKgKkmc', '1uyUdYdtEwgsGA-vg56MTXUQE536h0IYc', '1FE2ewIHsV_u5ukYzgKbpzEtHm91JLdsy', '1LRBYuF5SdFJ5Da96MW9MbiZpPseXtsnp', '1aEPxlCahGqRdN_VrDC2NnnsQxuKCQmw2', '1OFDGuB_2HW-mBnAi9Qa6Jsg6fNenHsGs1dvg60FV_ZsQcYXlUdMQVtMMh1Ye6idsv', '1yzsvatA9LPP54d5Z4Lzzn4ZJH4-7ctAS', '1b0aqyV4ZIMNcIW03LT7cmlskNGy2dFW8', '1Pj1jhwahTOYTFlr2hTaQNy37_2YpscC01GZa8zp41rWBsVr5G_9Ug2NoGTodzCKuy', '1cUUr_Yo6mEqLt8z0KrjTZWEPNTJB_YF3', '1dib0sYNzdKyHcnREDBOfFSjPl5-yyEdO', '1_D19CpnSnZjAHpZa38M2KBzRSO_KThZB', '1bdsVzqpRnBOgSA33Jn3cw-otXhjg00XQ', '1Ym_6ARoA9uDc6LPIabFSFpPN7dirg1LR', '1TQWt6VXid9xRguBr4q6QMm7vqqEFvYMg', '1DSNN9dSIN9kKKK3NtVBWDPzvQ9xDrZpn', '1hWF41-3TuBkMFwDIlIJVNTAQbh_532uj', '1dWdV-W4WfDXYekxcezx7FE0erZZqW7yI', '1n9kj6x_Y8E9syi6G66Orzcis0awnT8I1']

    sheet_name = 'sheet0'
    for sheet_id in sheet_ids:
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        number_of_records, status, missing_keys, error, data_size, content_type, status_code, file_path, trace_back = get_records(source_type, entity_type, countries,
                                                                                                                                  category, url, name, description)
        logger = Logger({"number_of_records": number_of_records, "status": status,
                        "missing_keys": missing_keys, "error": error, "url": url, "source_type": source_type, "data_size": data_size, "content_type": content_type, "status_code": status_code, "file_path": file_path, "trace_back": trace_back,  "crawler": "HTML"})
        logger.log()
