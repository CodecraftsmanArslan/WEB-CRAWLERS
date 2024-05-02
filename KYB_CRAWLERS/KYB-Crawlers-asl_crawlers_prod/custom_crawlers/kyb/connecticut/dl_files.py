import os
import io
from googleapiclient.discovery import build, service_account
from googleapiclient.http import MediaIoBaseDownload


# Output
OUTPUT_DIR = 'input'
# Enter your Google Drive API credentials path
credentials_path = 'cred.json'
# Enter the ID of the Google Drive folder containing the CSV files
folder_id = '1IdDroORBVaKhbD-p1pPJphCoZvikYrKJ'
credentials = service_account.Credentials.from_service_account_file('cred.json')
# Create a service instance
service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
# Function to download a file
def download_file(file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False

    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%")

    with open(file_name, 'wb') as f:
        f.write(fh.getbuffer())

# Retrieve all CSV files from the folder
results = service.files().list(
    q=f"'{folder_id}' in parents",
    fields="files(id, name)").execute()
# print(results)
folders = results.get('files', [])

# Download each CSV file
for folder in folders:
    folder_id = folder['id']
    folder_name = folder['name']
    
    if not os.path.exists(f'{OUTPUT_DIR}/{folder_name}'):
        os.mkdir(f'{OUTPUT_DIR}/{folder_name}')
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name)").execute()
    # print(results)
    files = results.get('files', [])
    for file in files:
        file_id = file['id']
        file_name = file['name']
        if file_name.find('.csv')!=-1:
            download_file(file_id, f'{OUTPUT_DIR}/{folder_name}/{file_name}')
            print(f"Downloaded {file_name}")

print("All files downloaded successfully.")
