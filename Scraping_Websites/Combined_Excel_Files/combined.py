import pandas as pd
import glob

# Path to the directory containing Excel files
excel_files_path = 'C:/Users/Dell/WEB-CRAWLERS/Scraping_Websites/Combined_Excel_Files/*.xlsx'

# Get a list of all Excel files in the directory
excel_files = glob.glob(excel_files_path)

dfs = []

for file in excel_files:
    df = pd.read_excel(file, engine='openpyxl')  # Specify the engine as openpyxl for .xlsx files
    dfs.append(df)

combined_df = pd.concat(dfs, ignore_index=True)
combined_df.to_excel('C:/Users/Dell/WEB-CRAWLERS/Scraping_Websites/final.xlsx', index=False)
print(combined_df)




