# @title Download, extract and modify
import os
import requests
import zipfile
import glob
from pathlib import Path
from datetime import date
import shutil
import json

_DEBUG = False

def modify_json(json_data):
  new_json = {}
  new_json['cik'] = json_data['cik']
  new_json['entityName'] = json_data['entityName']

  elements = json_data.get('facts', {}).get('us-gaap')
  if not elements:
    elements = json_data.get('facts', {}).get('ifrs-full',{})

  if _DEBUG:
    ####### to dump contents of SCRATCH FILE #############
    if os.path.exists('scratch_folder'):
        shutil.rmtree('scratch_folder')
        os.makedirs('scratch_folder')

    with open(f'{_MODIFIED_FACTS}/{SCRATCH_FILE}', 'r') as f:
        print(f"Contents of {SCRATCH_FILE}:")
        print(f"reading....{SCRATCH_FILE} from {_COMPANY_FACTS}")
        json_data = json.load(f)
    with open(f'scratch_folder/{SCRATCH_FILE}','w') as f:
        print(f"writing....{SCRATCH_FILE}/{'scratch_folder'}")
        json.dump(json_data, f)
    ######################################################

  for element_key, element_value in elements.items():
    units = element_value.get('units', {})
    #assumption that units dictionary has only one item
    key,facts = next(iter(units.items()))
    # now key is USD/SHARES and facts is a list
    fact_list = []
    for fact in facts:
      fact_dictionary ={}
      if date.fromisoformat(fact['end']) > date.fromisoformat(_DATE_THRESHOLD) and (fact['form'] in ['10-K','10-Q']):
        fact_dictionary ['end'] = fact['end']
        fact_dictionary ['val'] = fact['val']
        fact_dictionary ['form'] = fact['form']
        fact_dictionary ['accn'] = fact['accn']
        fact_dictionary ['fp'] = fact['fp']
        fact_dictionary ['filed'] = fact['filed']
        fact_dictionary ['unit'] = key
        fact_list.append(fact_dictionary)
      new_json[element_key] = fact_list

  # if no facts were added drop this file  
  if len(new_json) > _MIN_KEYS_IN_MODIFIED_JSON:
    return new_json
  else:
    return None

def setup_company_facts(url=_URL, zip_filename="temp_data.zip", folder_name=_COMPANY_FACTS):
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
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status() # Check for HTTP errors

        with open(zip_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
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

    finally:
        # 4. Delete the original zip file
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
            print(f"Deleted temporary file: {zip_filename}")


def create_modified_facts(source_dir=_COMPANY_FACTS, dest_dir=_MODIFIED_FACTS):
    src = Path(source_dir)
    dest = Path(dest_dir)
    # Create destination directory if it doesn't exist
    dest.mkdir(parents=True, exist_ok=True)

    # 2. Get list of all JSON files
    json_files = list(src.glob("*.json"))

    # 3. Iterate and transform
    for file_path in json_files:
        try:
            # Read the JSON file
            with open(file_path, 'r') as f:
                json_data = json.load(f)
                new_json_data = modify_json(json_data)
                if new_json_data:
                  new_file_path = dest / file_path.name
                  # Write the modified dictionary to the new location
                  with open(new_file_path, 'w') as f:
                      json.dump(new_json_data, f)
                else:
                  print(f"skipping original json {file_path.name}")
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")

########################## Execution block ################################
#setup_company_facts()
#print('download from sec and extraction completed')
create_modified_facts()
print('modified files created')

