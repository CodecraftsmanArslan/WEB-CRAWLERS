import pandas as pd
import json,requests,re
from bs4 import BeautifulSoup
import pandas as pd
import os,sys

i = 0
count =50
# d = 0  # Initialize d outside the loop
increment = 25  # Increment value
all_info = []  # Initialize an empty list to store all extracted names
data_list = []

arguments = sys.argv
d = int(arguments[1]) if len(arguments)>1 else 0

while i < count:
    url = "https://lawsocietyontario.search.windows.net/indexes/lsolpindexprd/docs/search?api-version=2017-11-11"

    payload = json.dumps({
        "search": "(/.*ac.*/)",
        "facets": [
            "memberareasofservicenamesenglish,count:50,sort:value",
            "memberlanguagenamesenglish,count:50,sort:value",
            "memberwebstatus,count:50,sort:value",
            "membercitynormalized,count:50,sort:count"
        ],
        "count": True,
        "top": 25,
        "skip": d,
        "filter": "",
        "orderby": "memberlastname, memberfirstname, membermiddlename",
        "queryType": "full",
        "searchFields": "memberfirstname,membermiddlename,memberlastname,memberfullname,membermailname,memberfirstnameclean,membermiddlenameclean,memberlastnameclean,membermailnameclean"
    })
    print(f"___________{d}")


    headers = {
        'authority': 'lawsocietyontario.search.windows.net',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'api-key': '212D535962D4563E62F8EC5D6E1C71CA',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://lso.ca',
        'referer': 'https://lso.ca/',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    count = data['@odata.count']
    links = data['value']
    base_url = "https://lso.ca/public-resources/finding-a-lawyer-or-paralegal/directory-search/member?MemberNumber="

    FILE_PATH = os.path.dirname(os.getcwd()) + "\Canada_link2"

    def extract_info(soup, label_text, class_name):
        info = soup.find('div', class_='member-info-label label-wrapper', text=label_text)
        if info:
            info_text = info.find_next('div', class_='member-info-value').text.strip()
            return info_text
        else:
            return None

    def extract_lawyer_info(soup, link):
        name = soup.find("h2").text
        print(name)

        with open(f"{FILE_PATH}/crawled_record.txt", "r") as crawled_records:
            file_contents = crawled_records.read()
            if name in file_contents:
                return None  # Exit early if the name is already in the file

        # Extract status
        status = soup.find('div', class_='label-wrapper member-info-label')
        if status:
            status_text = status.find_next('div', class_='member-info-value').text.strip()
        else:
            status_text = "Status information not found"

        # Extract other information
        mailing_name = extract_info(soup, 'Mailing Name', 'mail_name')
        law_society_number = extract_info(soup, 'Law Society Number', 'law_society')
        business_name = extract_info(soup, 'Business Name', 'business_name')
        trusteeships = extract_info(soup, 'Trusteeships', 'trust_info')
        current_practice_restrictions = extract_info(soup, 'Current Practice Restrictions', 'current_info')
        current_regulatory_proceedings = extract_info(soup, 'Current Regulatory Proceedings', 'current_regulatory_info')
        regulatory_history = extract_info(soup, 'Regulatory History', 'regulatory_info')
        offers_services_in_french = extract_info(soup, 'Offers Services in French?', 'offer_info')
        business_address = extract_info(soup, 'Business Address', 'address_info')
        phone = extract_info(soup, ' Phone ', 'phone_info')
        if phone:
            phone = "+" + phone

        with open(f"{FILE_PATH}/crawled_record.txt", "a") as crawled_records:
                    crawled_records.write(name + "\n")

        # Return a dictionary with the extracted data
        return {
            'Name': name,
            'Status': status_text,
            'Mailing Name': mailing_name,
            'phone':phone,
            'Law Society Number': law_society_number,
            'Business Name': business_name,
            'Trusteeships': trusteeships,
            'Current Practice Restrictions': current_practice_restrictions,
            'Current Regulatory Proceedings': current_regulatory_proceedings,
            'Regulatory History': regulatory_history,
            'Offers Services in French?': offers_services_in_french,
            'Business Address': business_address,
        }

    # Iterate over each link and extract information
    for link in links:
        url = f"{base_url}{link['membernumber']}"
        response2 = requests.get(url, headers=headers)
        soup = BeautifulSoup(response2.content, "html.parser")
        lawyer_info = extract_lawyer_info(soup, link)
        if lawyer_info is not None:
            data_list.append(lawyer_info)
            print("Data are Extracted")
    # d=25
    d += increment 
    if d == 25:  
        d = 25

    i += increment 
    print(i)

    df = pd.DataFrame(data_list)
    df.to_excel('lawyers_and_paralegals_info.xlsx')

# started from  4045














































# import pandas as pd
# import json
# import requests
# import concurrent.futures
# from bs4 import BeautifulSoup




# def extract_info(link,headers, label_text, class_name):
#     url = f"https://lso.ca/public-resources/finding-a-lawyer-or-paralegal/directory-search/member?MemberNumber={link['membernumber']}"
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.content, "html.parser")
#     info = soup.find('div', class_='member-info-label label-wrapper', text=label_text)
#     if info:
#         info_text = info.find_next('div', class_='member-info-value').text.strip()
#         return info_text
#     else:
#         return ""


# def extract_lawyer_info(soup, link):
#     name = soup.find("h2").text
#     print(name)

#     # Extract status
#     status = soup.find('div', class_='label-wrapper member-info-label')
#     if status:
#         status_text = status.find_next('div', class_='member-info-value').text.strip()
#     else:
#         status_text = "Status information not found"

#     # Extract other information
#     mailing_name = extract_info(link,headers ,'Mailing Name', 'mail_name')
#     print(mailing_name)
#     # law_society_number = extract_info(soup, 'Law Society Number', 'law_society')
#     # business_name = extract_info(soup, 'Business Name', 'business_name')
#     # trusteeships = extract_info(soup, 'Trusteeships', 'trust_info')
#     # current_practice_restrictions = extract_info(soup, 'Current Practice Restrictions', 'current_info')
#     # current_regulatory_proceedings = extract_info(soup, 'Current Regulatory Proceedings', 'current_regulatory_info')
#     # regulatory_history = extract_info(soup, 'Regulatory History', 'regulatory_info')
#     # offers_services_in_french = extract_info(soup, 'Offers Services in French?', 'offer_info')
#     # business_address = extract_info(soup, 'Business Address', 'address_info')
#     # phone = "+" + extract_info(soup, ' Phone ', 'phone_info')


#     # Return a dictionary with the extracted data
#     return {
#         'Name': name,
#         'Status': status_text,
#         'Mailing Name': mailing_name,
#         # 'phone':phone,
#         # 'Law Society Number': law_society_number,
#         # 'Business Name': business_name,
#         # 'Trusteeships': trusteeships,
#         # 'Current Practice Restrictions': current_practice_restrictions,
#         # 'Current Regulatory Proceedings': current_regulatory_proceedings,
#         # 'Regulatory History': regulatory_history,
#         # 'Offers Services in French?': offers_services_in_french,
#         # 'Business Address': business_address,
#     }


# # Main function
# def main():
#     i = 0
#     count = 50
#     d = 0  # Initialize d outside the loop
#     increment = 25  # Increment value
#     data_list = []

#     with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
#         futures = []

#         # Iterate over each link and submit a thread for extraction
#         while d < count:
#             url = "https://lawsocietyontario.search.windows.net/indexes/lsolpindexprd/docs/search?api-version=2017-11-11"
#             payload = json.dumps({
#                 "search": "(/.*aa.*/)",
#                 "facets": [
#                     "memberareasofservicenamesenglish,count:50,sort:value",
#                     "memberlanguagenamesenglish,count:50,sort:value",
#                     "memberwebstatus,count:50,sort:value",
#                     "membercitynormalized,count:50,sort:count"
#                 ],
#                 "count": True,
#                 "top": 25,
#                 "skip": d,
#                 "filter": "",
#                 "orderby": "memberlastname, memberfirstname, membermiddlename",
#                 "queryType": "full",
#                 "searchFields": "memberfirstname,membermiddlename,memberlastname,memberfullname,membermailname,memberfirstnameclean,membermiddlenameclean,memberlastnameclean,membermailnameclean"
#             })
#             headers = {
#                 'authority': 'lawsocietyontario.search.windows.net',
#                 'accept': 'application/json',
#                 'accept-language': 'en-US,en;q=0.9',
#                 'api-key': '212D535962D4563E62F8EC5D6E1C71CA',
#                 'cache-control': 'no-cache',
#                 'content-type': 'application/json',
#                 'origin': 'https://lso.ca',
#                 'referer': 'https://lso.ca/',
#                 'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
#                 'sec-ch-ua-mobile': '?0',
#                 'sec-ch-ua-platform': '"Windows"',
#                 'sec-fetch-dest': 'empty',
#                 'sec-fetch-mode': 'cors',
#                 'sec-fetch-site': 'cross-site',
#                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
#             }

#             response = requests.request("POST", url, headers=headers, data=payload)
#             data = response.json()
#             links = data['value']

#             for link in links:
#                 futures.append(executor.submit(extract_info, link, headers,label_text, class_name))

#             d += increment
#             if d == 25:
#                 d = 25
#                 i += increment
#                 print(i)

#         # Gathering results from threads
#         for future in concurrent.futures.as_completed(futures):
#             data_list.append(future.result())
#             print("Data Extracted")

#     df = pd.DataFrame(data_list)
#     df.to_excel('lawyers_and_paralegals_info.xlsx')
#     print(df)

# if __name__ == "__main__":
#     main()








# import pandas as pd
# import json
# import requests
# import concurrent.futures
# from bs4 import BeautifulSoup




# def extract_info(soup, label_text, class_name):
#     info = soup.find('div', class_='member-info-label label-wrapper', text=label_text)
#     if info:
#         info_text = info.find_next('div', class_='member-info-value').text.strip()
#         return info_text
#     else:
#         return ""

# def extract_lawyer_info(soup, link):
#     name = soup.find("h2").text
#     # print(name)

#     # Extract status
#     status = soup.find('div', class_='label-wrapper member-info-label')
#     if status:
#         status_text = status.find_next('div', class_='member-info-value').text.strip()
#     else:
#         status_text = ""

#     # Extract other information
#     mailing_name = extract_info(soup, 'Mailing Name', 'mail_name')
#     law_society_number = extract_info(soup, 'Law Society Number', 'law_society')
#     business_name = extract_info(soup, 'Business Name', 'business_name')
#     trusteeships = extract_info(soup, 'Trusteeships', 'trust_info')
#     current_practice_restrictions = extract_info(soup, 'Current Practice Restrictions', 'current_info')
#     current_regulatory_proceedings = extract_info(soup, 'Current Regulatory Proceedings', 'current_regulatory_info')
#     regulatory_history = extract_info(soup, 'Regulatory History', 'regulatory_info')
#     offers_services_in_french = extract_info(soup, 'Offers Services in French?', 'offer_info')
#     business_address = extract_info(soup, 'Business Address', 'address_info')
#     phone = "+" + extract_info(soup, ' Phone ', 'phone_info')


#     # Return a dictionary with the extracted data
#     return {
#         'Name': name,
#         'Status': status_text,
#         'Mailing Name': mailing_name,
#         'phone':phone,
#         'Law Society Number': law_society_number,
#         'Business Name': business_name,
#         'Trusteeships': trusteeships,
#         'Current Practice Restrictions': current_practice_restrictions,
#         'Current Regulatory Proceedings': current_regulatory_proceedings,
#         'Regulatory History': regulatory_history,
#         'Offers Services in French?': offers_services_in_french,
#         'Business Address': business_address,
#     }


# # Main function
# def main():
#     count = 50
#     d = 0  # Initialize d outside the loop
#     increment = 25  # Increment value
#     data_list = []

#     with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:  
#         futures = []

#         # Iterate over each link and submit a thread for extraction
#         while d < count:
#             url = "https://lawsocietyontario.search.windows.net/indexes/lsolpindexprd/docs/search?api-version=2017-11-11"
#             payload = json.dumps({
#                 "search": "(/.*aa.*/)",
#                 "facets": [
#                     "memberareasofservicenamesenglish,count:50,sort:value",
#                     "memberlanguagenamesenglish,count:50,sort:value",
#                     "memberwebstatus,count:50,sort:value",
#                     "membercitynormalized,count:50,sort:count"
#                 ],
#                 "count": True,
#                 "top": 25,
#                 "skip": d,
#                 "filter": "",
#                 "orderby": "memberlastname, memberfirstname, membermiddlename",
#                 "queryType": "full",
#                 "searchFields": "memberfirstname,membermiddlename,memberlastname,memberfullname,membermailname,memberfirstnameclean,membermiddlenameclean,memberlastnameclean,membermailnameclean"
#             })

#             headers = {
#                 'authority': 'lawsocietyontario.search.windows.net',
#                 'accept': 'application/json',
#                 'accept-language': 'en-US,en;q=0.9',
#                 'api-key': '212D535962D4563E62F8EC5D6E1C71CA',
#                 'cache-control': 'no-cache',
#                 'content-type': 'application/json',
#                 'origin': 'https://lso.ca',
#                 'referer': 'https://lso.ca/',
#                 'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
#                 'sec-ch-ua-mobile': '?0',
#                 'sec-ch-ua-platform': '"Windows"',
#                 'sec-fetch-dest': 'empty',
#                 'sec-fetch-mode': 'cors',
#                 'sec-fetch-site': 'cross-site',
#                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
#             }

#             response = requests.request("POST", url, headers=headers, data=payload)
#             data = response.json()
#             links = data['value']
#             count = data['@odata.count']


#             for link in links:
#                 lawyer_url = f"https://lso.ca/public-resources/finding-a-lawyer-or-paralegal/directory-search/member?MemberNumber={link['membernumber']}"
#                 lawyer_response = requests.get(lawyer_url, headers=headers)
#                 lawyer_soup = BeautifulSoup(lawyer_response.content, "html.parser")
#                 futures.append(executor.submit(extract_lawyer_info, lawyer_soup, link))

#             d += increment
#             print(d)

#         # Gathering results from threads
#         for future in concurrent.futures.as_completed(futures):
#             data_list.append(future.result())
#             # print("Data Extracted")

#     df = pd.DataFrame(data_list)
#     df.to_excel('lawyers_and_paralegals_info.xlsx')
#     print(df)

# if __name__ == "__main__":
#     main()














































# import pandas as pd
# import json
# import requests
# import concurrent.futures
# from bs4 import BeautifulSoup


# def extract_info(link, headers):
#     url = f"https://lso.ca/public-resources/finding-a-lawyer-or-paralegal/directory-search/member?MemberNumber={link['membernumber']}"
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.content, "html.parser")
#     info = soup.find('div', class_='member-info-label')
#     if info:
#         info_text = info.find_next('div', class_=class_name).text.strip()
#         return info_text
#     else:
#         return ""


# def extract_lawyer_info(soup, link):
#     name = soup.find("h2").text
#     print(name)

#     # Extract status
#     status = soup.find('div', class_='label-wrapper member-info-label')
#     if status:
#         status_text = status.find_next('div', class_='member-info-value').text.strip()
#     else:
#         status_text = "Status information not found"

#     # Extract other information
#     mailing_name = extract_info(link, headers, 'Mailing Name', 'mail_name')
#     law_society_number = extract_info(link, headers, 'Law Society Number', 'law_society')
#     business_name = extract_info(link, headers, 'Business Name', 'business_name')
#     trusteeships = extract_info(link, headers, 'Trusteeships', 'trust_info')
#     current_practice_restrictions = extract_info(link, headers, 'Current Practice Restrictions', 'current_info')
#     current_regulatory_proceedings = extract_info(link, headers, 'Current Regulatory Proceedings', 'current_regulatory_info')
#     regulatory_history = extract_info(link, headers, 'Regulatory History', 'regulatory_info')


#     # Return a dictionary with the extracted data
#     return {
#         'Name': name,
#         'Status': status_text,
#         'Mailing Name': mailing_name,
#         'phone':phone,
#         'Law Society Number': law_society_number,
#         'Business Name': business_name,
#         'Trusteeships': trusteeships,
#         'Current Practice Restrictions': current_practice_restrictions,
#         'Current Regulatory Proceedings': current_regulatory_proceedings,
#         'Regulatory History': regulatory_history,
#         'Offers Services in French?': offers_services_in_french,
#         'Business Address': business_address,
#     }


# # Main function
# def main():
#     i = 0
#     count = 50
#     d = 0  # Initialize d outside the loop
#     increment = 25  # Increment value
#     data_list = []

#     with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
#         futures = []

#         # Iterate over each link and submit a thread for extraction
#         while d < count:
#             url = "https://lawsocietyontario.search.windows.net/indexes/lsolpindexprd/docs/search?api-version=2017-11-11"
#             payload = json.dumps({
#                 "search": "(/.*aa.*/)",
#                 "facets": [
#                     "memberareasofservicenamesenglish,count:50,sort:value",
#                     "memberlanguagenamesenglish,count:50,sort:value",
#                     "memberwebstatus,count:50,sort:value",
#                     "membercitynormalized,count:50,sort:count"
#                 ],
#                 "count": True,
#                 "top": 25,
#                 "skip": d,
#                 "filter": "",
#                 "orderby": "memberlastname, memberfirstname, membermiddlename",
#                 "queryType": "full",
#                 "searchFields": "memberfirstname,membermiddlename,memberlastname,memberfullname,membermailname,memberfirstnameclean,membermiddlenameclean,memberlastnameclean,membermailnameclean"
#             })
#             headers = {
#                 'authority': 'lawsocietyontario.search.windows.net',
#                 'accept': 'application/json',
#                 'accept-language': 'en-US,en;q=0.9',
#                 'api-key': '212D535962D4563E62F8EC5D6E1C71CA',
#                 'cache-control': 'no-cache',
#                 'content-type': 'application/json',
#                 'origin': 'https://lso.ca',
#                 'referer': 'https://lso.ca/',
#                 'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
#                 'sec-ch-ua-mobile': '?0',
#                 'sec-ch-ua-platform': '"Windows"',
#                 'sec-fetch-dest': 'empty',
#                 'sec-fetch-mode': 'cors',
#                 'sec-fetch-site': 'cross-site',
#                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
#             }

#             response = requests.request("POST", url, headers=headers, data=payload)
#             data = response.json()
#             links = data['value']

#             for link in links:
#                 futures.append(executor.submit(extract_info, link, headers))

#             d += increment
#             if d == 25:
#                 d = 25
#                 i += increment
#                 print(i)

#         # Gathering results from threads
#         for future in concurrent.futures.as_completed(futures):
#             data_list.append(future.result())
#             print("Data Extracted")

#     df = pd.DataFrame(data_list)
#     df.to_excel('lawyers_and_paralegals_info.xlsx')
#     print(df)

# if __name__ == "__main__":
#     main()
