# import os
# import pandas as pd

# # Function to read a text file and return its content as a DataFrame
# def read_text_file(file, encoding='utf-8'):
#     with open(file, 'r', encoding=encoding) as f:
#         content = f.read()
#     return pd.DataFrame({'text': [content]})

# # Directory containing the text files
# directory = 'D:\WEB-CRAWLERS\Pending crawlers\Testing'

# # List text files in the directory
# text_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.txt')]

# for file in text_files:
#     # Read text file and create DataFrame
#     df = read_text_file(file)
    
#     # Convert DataFrame to JSON with an indentation of 4
#     json_data = df.to_json(orient='records', indent=4)
    
#     # Create output file name
#     output_file = os.path.splitext(file)[0] + '.json'
    
#     # Write JSON data to a file
#     with open(output_file, 'w', encoding='utf-8') as f:
#         f.write(json_data)







# import requests

# url = "https://hls-c.udemycdn.com/898082/8851920/2017-06-30_22-31-48-00afeddecf63055b0d97db244acbe780/1/hls/AVC_1920x1080_1600k_AAC-HE_64k/aa0024fa611068b9f11f30bfc967d33d307f18.ts?Expires=1713823872&Signature=qV0ydY7LvdY1BJ3mQdywjRoUyN8MSPR9Q-M4hFLNBo17irEBuKRx2Dbma1HbfGFtzdZ1YXe4zUfkwDgoltxpclINjZh7sOhZkZQqMzwto~~m2zRpIr4al7SEpZzxConucgtV2fbCUUCSYy4G5YunKXAuovPaT0FI~k3hH06NhvjKXNsf1nTCniNsYRFjo~OxxplG9tC3SUsOdOtZAKNuxoBfgl97EuDsSndsick4fPlsmXhJJVvwApiaTrsg-Dh8sQIgxP~JLVV-5pZJ2c5GM3ZCzl7Nbyf5ildUcRADyWUHchczL706fhxVqa2u7UZfHqrIIEbV9kxq5LEZGekVQw__&Key-Pair-Id=K3MG148K9RIRF4"
# r = requests.get(url)

# if r.status_code == 200:
#     with open("video.ts", "wb") as f:
#         for chunk in r.iter_content(chunk_size=8192):
#             f.write(chunk)
#     print("Video downloaded successfully!")
# else:
#     print("Failed to download video:", r.status_code)



# import requests
# import m3u8


# url = "https://www.udemy.com/assets/8851920/files/898082/8851920/2017-06-30_22-31-48-00afeddecf63055b0d97db244acbe780/1/hls/AVC_1280x720_800k_AAC-HE_64k/aa0024fa611068b9f11f30bfc967d33d307f.m3u8?provider=cloudfront&token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXRoIjoiODk4MDgyLzg4NTE5MjAvMjAxNy0wNi0zMF8yMi0zMS00OC0wMGFmZWRkZWNmNjMwNTViMGQ5N2RiMjQ0YWNiZTc4MC8xLyIsImV4cCI6MTcxMzgyMzc5M30._tVpH6C3icnZ5dPWFEFMC3O6CQmkOKnsy5kzNL7917w&v=1"
# r = requests.get(url)
# m3u8_master = m3u8.loads(r.text)
# playlist_uri=m3u8_master.data['segments'][0]['uri']
# playlist = m3u8.loads(r.text)

# with open("video.ts", "wb") as f:
#     for segment in playlist.data['segments']:
#         url=segment['uri']
#         r=requests.get(url)
#         f.write(r.content)





from selenium import webdriver
import psycopg2
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time,sys
import requests
import json
from bs4 import BeautifulSoup

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://gpulist.ai/")







































# import requests
# import m3u8
# import subprocess

# # Function to download .ts segments
# def download_ts_segments(url):
#     r = requests.get(url)
#     if r.status_code == 200:
#         playlist = m3u8.loads(r.text)
#         with open("video.ts", "ab") as f:
#             for segment in playlist.data['segments']:
#                 url = segment['uri']
#                 r = requests.get(url)
#                 f.write(r.content)
#         print("Segments downloaded successfully!")
#         return True
#     else:
#         print("Failed to download segments:", r.status_code)
#         return False

# # Function to convert .ts to .mp4
# def convert_to_mp4(input_file, output_file):
#     subprocess.run(['ffmpeg', '-i', input_file, '-c', 'copy', output_file])
#     print("Conversion completed!")

# # Main function
# def main():
#     # URL of the M3U8 playlist
#     url = "https://www.udemy.com/assets/8851920/files/898082/8851920/2017-06-30_22-31-48-00afeddecf63055b0d97db244acbe780/1/hls/AVC_1280x720_800k_AAC-HE_64k/aa0024fa611068b9f11f30bfc967d33d307f.m3u8?provider=cloudfront&token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXRoIjoiODk4MDgyLzg4NTE5MjAvMjAxNy0wNi0zMF8yMi0zMS00OC0wMGFmZWRkZWNmNjMwNTViMGQ5N2RiMjQ0YWNiZTc4MC8xLyIsImV4cCI6MTcxMzgyMzc5M30._tVpH6C3icnZ5dPWFEFMC3O6CQmkOKnsy5kzNL7917w&v=1"
    
#     # Download .ts segments
#     if download_ts_segments(url):
#         # Convert .ts to .mp4
#         convert_to_mp4("video.ts", "video.mp4")
# main()
















# m3u8_segment_uris = [segment['uri'] for segment in playlist.data['segments']]
# print(playlist)