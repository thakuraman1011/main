# @title Modify and rewrite
import os
import glob
from pathlib import Path
from datetime import date
import shutil
import json
import CONFIG
import zipfile
import urllib.request

def _transform_instance(json_data):
  """
  Transforms SEC json file structure to a more flat structure and also filters facts based on end date and form type.
  Transformed structure is {cik,entityName,element[]}
  element[] = {end,val,form,accn,fp,filed,unit}
  """
  new_json = {}
  new_json['cik'] = json_data['cik'].zfill(10)
  new_json['entityName'] = json_data['entityName']

  elements = json_data.get('facts', {}).get('ifrs-full')
  if not elements:
    elements = json_data.get('facts', {}).get('us-gaap')
    if not elements:
      elements = {}

  for element_key, element_value in elements.items():
    units = element_value.get('units', {})
    #assumption that units dictionary has only one item
    key,facts = next(iter(units.items()))
    # now key is EUR/USD/SHARES and facts is a list
    fact_list = []
    dup_avoiding_dictionary ={}
    for fact in facts:
      if dup_avoiding_dictionary.get(fact['end']):
        continue
      else:
        fact_dictionary ={}
        if date.fromisoformat(fact['end']) > date.fromisoformat(CONFIG._DATE_THRESHOLD) and (fact['form'] in ['10-K','10-Q','20-F','6-K']):
          fact_dictionary ['end'] = fact['end']
          fact_dictionary ['val'] = fact['val']
          fact_dictionary ['form'] = fact['form']
          fact_dictionary ['accn'] = fact['accn']
          fact_dictionary ['fp'] = fact['fp']
          fact_dictionary ['filed'] = fact['filed']
          fact_dictionary ['unit'] = key
          fact_list.append(fact_dictionary)
          dup_avoiding_dictionary[fact['end']] = True
    # Add element only if there was at least one fact.
    if len(fact_list) > 0:
        new_json[element_key] = fact_list

  # if the only facts are CIK and entityName then return None
  if len(new_json) > CONFIG._MIN_KEYS_IN_MODIFIED_JSON:
    return new_json
  else:
    return None

def process_sec_data(url=CONFIG._URL, zip_filename=CONFIG._TEMP_ZIP_FILE, folder_name=CONFIG._COMPANY_FACTS):
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

def transform(file_name = None, source_dir=CONFIG._COMPANY_FACTS, dest_dir=CONFIG._MODIFIED_FACTS):
  """
  iterates over all json files in source_dir
  1. Read file
  2. Load to json
  3. Transform it
  4. Write modify json to dest_dir
  Files with no facts after THRESHOLD_DATE are skipped as are files which result in errors
  """
  src = Path(source_dir)
  dest = Path(dest_dir)
  # Create destination directory if it doesn't exist
  dest.mkdir(parents=True, exist_ok=True)
  json_files = None

  if file_name:
    json_files = list(src.glob(file_name))
  else:
    json_files = list(src.glob("*.json"))

  # 3. Iterate and transform
  for file_path in json_files:
    try:
      # Read the JSON file
      with open(file_path, 'r') as f:
        json_data = json.load(f)
        new_json_data = _transform_instance(json_data)
        if new_json_data:
          new_file_path = dest / file_path.name
          # Write the modified dictionary to the new location
          with open(new_file_path, 'w') as f:
              json.dump(new_json_data, f)
        else:
          print(f"skipping original json {file_path.name}")
    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")

