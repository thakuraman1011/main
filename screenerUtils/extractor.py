import os
import urllib.request
import zipfile
import glob
from pathlib import Path
from datetime import date
import shutil
import json
from google import colab
import screenerUtils.CONFIG as CONFIG

def setup_company_facts(url=CONFIG._URL, zip_filename=CONFIG._TEMP_ZIP_FILE, folder_name=CONFIG._COMPANY_FACTS):
    """Download and extract company facts from SEC EDGAR.
    This function performs the following steps:
    1. Deletes the target folder if it already exists to ensure a clean state.
    2. Creates a target folder to store the extracted files.
    3. Downloads the ZIP file containing company facts from the specified URL.
    4. Extracts the contents of the ZIP file into the target folder.
    5. Logs the number of JSON files extracted for verification.
    """
    try:
        # 1. Delete folder if it exists and recreate
        if os.path.exists(folder_name):
            shutil.rmtree(folder_name)
            print(f"Deleted existing folder: {folder_name}")

        # Make folder again
        os.makedirs(folder_name)
        print(f"Created folder: {folder_name}")

        # 2. Download the zip file
        print(f"Downloading from {url}...")
        headers = {'User-Agent': 'amanthakur@gmail.com'}
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)
        if response.getcode() != 200:
            raise ValueError(f"Failed to download from URL: {url}")


        with open(zip_filename, 'wb') as f:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                f.write(chunk)

        # 3. Extract the contents
        print(f"Extracting to {folder_name}...")
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall(folder_name)

        dir_path = Path(folder_name)
        file_count = len(list(dir_path.glob('*.json')))
        print(f"Extracted {file_count} files.")

    except Exception as e:
        print(f"An error occurred: {e}")

# setup_company_facts()
# print('download from sec and extraction completed')