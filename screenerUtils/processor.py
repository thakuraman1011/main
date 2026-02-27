# @title Modify and rewrite
import os
import glob
from pathlib import Path
from datetime import date
import shutil
import json
from CONFIG import _DATE_THRESHOLD, _COMPANY_FACTS, _MODIFIED_FACTS, _MIN_KEYS_IN_MODIFIED_JSON

def transform_instance(json_data):
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
        if date.fromisoformat(fact['end']) > date.fromisoformat(_DATE_THRESHOLD) and (fact['form'] in ['10-K','10-Q','20-F','6-K']):
          fact_dictionary ['end'] = fact['end']
          fact_dictionary ['val'] = fact['val']
          fact_dictionary ['form'] = fact['form']
          fact_dictionary ['accn'] = fact['accn']
          fact_dictionary ['fp'] = fact['fp']
          fact_dictionary ['filed'] = fact['filed']
          fact_dictionary ['unit'] = key
          fact_list.append(fact_dictionary)
          dup_avoiding_dictionary[fact['end']] = True
    new_json[element_key] = fact_list

  # if no facts were added drop this file
  if len(new_json) > _MIN_KEYS_IN_MODIFIED_JSON:
    return new_json
  else:
    return None


def transform(file_name = None, source_dir=_COMPANY_FACTS, dest_dir=_MODIFIED_FACTS):
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
        new_json_data = transform_instance(json_data)
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
transform()
print('modified files created')
