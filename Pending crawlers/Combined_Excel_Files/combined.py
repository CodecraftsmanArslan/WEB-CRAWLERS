# import pandas as pd
# import glob

# # Path to the directory containing Excel files
# excel_files_path = 'D:/WEB-CRAWLERS/Scraping_Websites/Hawaii/*.xlsx'

# # Get a list of all Excel files in the directory
# excel_files = glob.glob(excel_files_path)

# dfs = []

# for file in excel_files:
#     df = pd.read_excel(file, engine='openpyxl')  # Specify the engine as openpyxl for .xlsx files
#     dfs.append(df)
# combined_df = pd.concat(dfs, ignore_index=True)
# combined_df.to_excel('D:/WEB-CRAWLERS/Scraping_Websites/Hawaii/full_final.xlsx', index=False)
# print(combined_df)





# import pandas as pd
# import json

# # Read the Excel file
# df = pd.read_excel('denmark1.xlsx')

# def extract_info(company_info):
#     info_list = json.loads(company_info)
#     addresses = []
#     companies = []
#     telephones = []
    
#     for info in info_list:
#         addresses.append(info['address'])
#         companies.append(info['company'])
#         telephones.append(info['telephone'])
    
#     return addresses, companies, telephones

# df['address'], df['company'], df['telephone'] = zip(*df['company_info'].apply(extract_info))
# df.drop(columns=['company_info'], inplace=True)

# max_addresses = max(df['address'].apply(len))

# for i in range(max_addresses):
#     df[f'address{i+1}'] = df['address'].apply(lambda x: x[i] if len(x) > i else None)

# max_companies = max(df['company'].apply(len))
# for i in range(max_companies):
#     df[f'company{i+1}'] = df['company'].apply(lambda x: x[i] if len(x) > i else None)

# max_telephones = max(df['telephone'].apply(len))
# for i in range(max_telephones):
#     df[f'telephone{i+1}'] = df['telephone'].apply(lambda x: x[i] if len(x) > i else None)

# df.drop(columns=['address', 'company', 'telephone'], inplace=True)
# df.to_excel('denmar2.xlsx')







import pandas as pd
import json
from itertools import zip_longest


# Read the Excel file
df = pd.read_excel('denmark1.xlsx')

def extract_info(company_info):
    info_list = json.loads(company_info)
    addresses = []
    companies = []
    telephones = []
    
    for info in info_list:
        addresses.append(info['address'])
        companies.append(info['company'])
        telephones.append(info['telephone'])
    
    return addresses, companies, telephones

df['address'], df['company'], df['telephone'] = zip(*df['company_info'].apply(extract_info))
df.drop(columns=['company_info'], inplace=True)


max_addresses = max(df['address'].apply(len))
max_companies = max(df['company'].apply(len))
max_telephones = max(df['telephone'].apply(len))

# Iterate over the series simultaneously using zip_longest
for i, j, k in zip_longest(range(max_addresses), range(max_companies), range(max_telephones)):
    df[f'company{j+1}'] = df['company'].apply(lambda x: x[j] if len(x) > j else None)
    df[f'telephone{k+1}'] = df['telephone'].apply(lambda x: x[k] if len(x) > k else None)
    df[f'address{i+1}'] = df['address'].apply(lambda x: x[i] if len(x) > i else None)

df.drop(columns=['address', 'company', 'telephone'], inplace=True)
df.to_excel('denmar2.xlsx')






