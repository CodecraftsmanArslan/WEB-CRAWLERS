import requests
import pandas as pd

url = "https://app.loydaasianajaja.fi/api/loyda?lang=fi&"

payload = {}
headers = {
  'Accept': 'application/json, text/javascript, */*; q=0.01',
  'Accept-Language': 'en-US,en;q=0.9',
  'Connection': 'keep-alive',
  'Cookie': 'displayCookieConsent=true; ARRAffinity=1bfafb9976f8d950e9848c31536990a619527c93bf92504a6a0fb3a9f41e5852; ARRAffinitySameSite=1bfafb9976f8d950e9848c31536990a619527c93bf92504a6a0fb3a9f41e5852',
  'Referer': 'https://app.loydaasianajaja.fi/',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"'
}

response = requests.request("GET", url, headers=headers, data=payload)
data=response.json()
fields = ['name','companyName','companyPhone','companyEmail', 'title','lawyerEmail', 'lawyerPhone', 'companyWww','companyAddress', 'municipality']
extracted_data = [{field: entry[field] for field in fields} for entry in data]

# Convert to DataFrame
df = pd.DataFrame(extracted_data)
df.to_excel('finland.xlsx')












