import json
import os
from collections import defaultdict
from pathlib import Path
from screenerUtils.CONFIG import _MODIFIED_FACTS

def get_json_object(f):
  try:
    json_data = json.load(f)
    if not json_data:
      print(f"Error reading filename {f}")
    return json_data
  except Exception as e:
    print(f"Error reading filename {f}")
    print(f"Error: {e}")
    return None

def has_all_elements(json_data, element_names):
  return all(k in json_data for k in element_names)

def has_element(json_data, element_name):
  return has_all_elements(json_data,[element_name])

def _lists_have_same_elements(list1,list2):
  return set(list1) == set(list2)

def get_json_files():
  src = Path(_MODIFIED_FACTS)
  json_files = src.glob("*.json")
  return json_files

def ciks_with_element (element_name, break_at=100):
  """
  Retuns a list of dictionaries. Each dictionary has cik and entityName of a company
  Only CIKs with element_name are included in return value. 
  break_at is used to limit the number of CIKs returned for testing purposes. 
  """
  ciks = []
  for file_path in get_json_files():
    if len(ciks) >= break_at:
      break
    with open(file_path, 'r') as f:
      json_data = get_json_object(f)
      if has_element(json_data,element_name):
        ciks.append({json_data['cik'],json_data['entityName']})
  return ciks

def ciks_without_element (element_name, break_at=100):
  """
  Retuns a list of dictionaries. Each dictionary has cik and entityName of a company
  Only CIKs without element_name are included in return value. 
  break_at is used to limit the number of CIKs returned for testing purposes. 
  """
  ciks = []
  for file_path in get_json_files():
    if len(ciks) >= break_at:
      break
    with open(file_path, 'r') as f:
      json_data = get_json_object(f)
      if not has_element(json_data,element_name):
        ciks.append({json_data['cik'],json_data['entityName']})
  return ciks

def all_elements_with_same_period (json_data,element_names):
  """
    Returns the first date for which all element_names are present in json_data with same end date. 
    If no such date is found then returns None
  """
  
  if has_all_elements(json_data,element_names):
    records =[]
    for element_name in element_names:
      facts = json_data[element_name]
      for fact in facts:
        record = {'name':element_name,'date': fact['end']}
        records.append(record)
        # records is a list of type {element_name,end_date}
      dict ={}
      #iterate over each record
      for record in records:
        # check if dict{} already has key associated with this date
        if not dict.get(record['date']):
          #if not found then add they key and value =new list with one entry element_name
          element_list = [record['name']]
          dict[record['date']] = element_list
        else:
          # if found then append the element_name to the list
          dict[record['date']].append(record['name'])
      # now dict{} has keys corresponding to all dates found in facts
      # and associated value is element_names
      for key,value in dict.items():
        # if any of the lists matches element_names passed as parameter then return true
        if _lists_have_same_elements(element_names,value):
          return key,True
  else:
    return None,False

