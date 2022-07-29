import os
import json
import requests
import numpy as np
import pandas as pd
from pprint import pprint
from collections import OrderedDict

# Overview of code:
# 1. read json response from an API
# 2. parse json response to extract all the possible columns using BFS algorithm
# 3. create python dictionary to store data from json in dataframe format, each key in dictionary represents a column in dataframe
# 4. loop over all objects in json response and fill data dictionary
# 5. create dataframe using data dictionary
# 6. save dataframe as csv

def BFS(obj, parent, depth):
    """
    BFS stands for Breadth First Search (Searching algorithm for Graphs/Trees).
    This is the main function that recursively looks for columns names in json object returned by API.
    Overview:
    1. if obj is OrderedDict type then use all of its keys to make possible column names (by concatinating with parent column name).
    2. if obj is list type then use all of its indices to make possible column names (by concatinating with parent column name).
    3. iterate over extracted keys, and for each key do following.
    4. if value of key in obj is not list or OrderedDict then its normal value and save key as final_keys only.
    5. else recursively extract keys of obj[key] and concatinate output at the end of final_keys.

    Args:
        obj (list or OrderedDict): The object to extract columns from.
        parent (string): a string representing the column name extracted from parent obj.
        depth (int): used for debugging purposes, can tell which recursion call caused error
    Returns:
        final_keys (list): list containing extracted column names
    
    Example:
    ```
        >> obj = {'a': 'value', 'b': {'c': 'value'}, 'd': [{'e': 'value'}, {'f': 'value'}]}
        >> print(BFS(obj))
        ['a', 'b/c', 'd/0/e', 'd/1/f']
    ```
    """
    TAG = '[BFS]'
    keys = []
    if type(obj) is OrderedDict:
        keys += [str(i) if parent == '' else f'{parent}/{i}' for i in obj.keys()]
    elif type(obj) is list:
        keys += [str(i) if parent == '' else f'{parent}/{i}' for i in range(len(obj))]

    final_keys = []
    for key in keys:
        k = key.split('/')[-1]
        k = k if type(obj) is OrderedDict else int(k)
        if not (type(obj[k]) is OrderedDict or type(obj[k]) is list):
            final_keys.append(key)
            continue
        final_keys += BFS(obj[k], key, depth + 1)
    return final_keys

def unique(array):
    """
    This function takes all extracted column names (from BFS), and returns unique column names

    Args:
        array (list): python list containing possible column names extracted from BFS function
    Returns:
        unique_array (list): python list containing unique values of input array
    """
    unique_array = []
    for elem in array:
        if elem not in unique_array:
            unique_array.append(elem)
    return unique_array

def get_json_from_API(url, api_name, load_from_disk=True):
    if load_from_disk and os.path.exists(f'{apis_response_path}/{api_name}.txt'):
        response_text = open(f'{apis_response_path}/{api_name}.txt', 'r').read()
    else:
        payload = {}
        headers = {'Api-Key': 'dNtr6w4juJTZ9vWhwNmD3bKrAf6TdAsM'}
        response = requests.request("GET", url, headers=headers, data=payload)
        response_text = response.text
        with open(f'{apis_response_path}/{api_name}.txt', 'w') as f:
            f.write(response_text)
    # print('[response_text]', response_text)
    return json.loads(response_text, object_pairs_hook=OrderedDict)

# def get_json_from_API(url, api_name):
#     """
#     This function calls API and returns output as json (or python dictionary)

#     Args:
#         url (string): url of API
#         api_name (string): name of API
#     Returns:
#         response_json (OrderedDict): An OrderedDict object contaning JSON response obtained from API
#     """
#     payload = {}
#     headers = {'Api-Key': 'dNtr6w4juJTZ9vWhwNmD3bKrAf6TdAsM'}
#     response = requests.request("GET", url, headers=headers, data=payload)
#     response_text = response.text
#     # print('[response_text]', response_text)
#     response_json = json.loads(response_text, object_pairs_hook=OrderedDict)
#     # print('[response_json]', json.dumps(response_json, indent=4))
#     return response_json

def extract_data_from_response_list(response_list, column_prefix=None):
    TAG = '[extract_data_from_response_list]'
    # for each API extract column names
    columns = []
    # 1st case: the response coming from API is list then perform BFS function over all objects in that list and accumulate extracted columns from each object
    for obj in response_list:
        columns += BFS(obj, '', 0)
    # as we iterate over all objects so there must be many occurance of same column name, so unique function gives unique columns
    columns = unique(columns)

    # collect data according to extracted columns
    data = {key: [] for key in columns}
    if DEGUB: print(TAG, f'Total {len(response_list)} objects in JSON returned by API.')
    # loop over all objects in API response and fill data dictionary (which will be converted to dataframe)
    for i, obj in enumerate(response_list):
        # loop over all columns
        for column in columns:
            value = obj
            # the column represents the hierarchy of keys that needs to be traversed (in obj) to extract a value, so this loop performs that traversing and extracts value for that column if it exists
            for j, k in enumerate(column.split('/')):
                if type(value) is OrderedDict:
                    value = value[k] if k in value else ''
                elif type(value) is list:
                    value = value[int(k)] if int(k) < len(value) else ''
            # insert extracted value in correct format
            data[column].append(value.strip() if type(value) is str else value)

    # remove columns (if any) that don't contain any data
    data_refined = {}
    for key in data:
        if len(data[key]) > 0:
            data_refined[key] = data[key]

    # create dataframe from collected data
    df_data = pd.DataFrame(data_refined)
    if column_prefix is not None:
        new_columns = {col: f'{column_prefix}/{col}' for col in df_data.columns}
        df_data = df_data.rename(columns=new_columns)
    if DEGUB: print(TAG, f'Total {len(df_data)} objects in Dataframe extracted.')
    if DEGUB: print(df_data)
    if DEGUB: print(TAG, '-' * 10)
    
    return df_data

def extract_data_from_response_object(response_obj):
    TAG = '[extract_data_from_object]'
    dfs = {}
    for key, value in response_obj.items():
        response_list = value if type(value) is list else [value]
        dfs[key] = extract_data_from_response_list(response_list, column_prefix=key)
    
    max_rows = max([len(df) for df in dfs.values()])
    dfs_list = []
    for df in dfs.values():
        if len(df) == 1:
            df_repeated = pd.DataFrame(np.repeat(df.values, max_rows, axis=0), columns=df.columns)
            dfs_list.append(df_repeated)
        else:
            dfs_list.append(df)
    df_combined = pd.concat(dfs_list, axis=1)

    return df_combined

# define some variables
TAG = '[create_dataframes]'
DEGUB = False

urls_type1 = {
    'all_brands': 'https://api.blueboard.io/v1/brands',
    'retailers': 'https://api.blueboard.io/v1/retailers',
    'products': 'https://api.blueboard.io/v1/products',
    'matches': 'https://api.blueboard.io/v1/MATCHES',
    'data': 'https://api.blueboard.io/v1/data',
    'performance': 'https://api.blueboard.io/v1/performance/search/entrypoints',
    # 'performance-search_data': 'https://api.blueboard.io/v1/performance/search/data',
    # 'performance-best_seller': 'https://api.blueboard.io/v1/performance/best-sellers/entrypoints', # no data
    # 'performance-best_sellers_data': 'https://api.blueboard.io/v1/performance/best-sellers/data', # no data
    'content_matches': 'https://api.blueboard.io/v1/content/matches',
    'content_history': 'https://api.blueboard.io/v1/content/history?start=2022-03-20&end=2022-03-22',
}

urls_type2 = {
    'brand-brand_id': ['https://api.blueboard.io/v1/brands/<1>', {'all_brands.csv': [['1', 'id']]}],
    'retailers-retailers_id': ['https://api.blueboard.io/v1/retailers/<1>', {'retailers.csv': [['1', 'id']]}],
    'products-product_id': ['https://api.blueboard.io/v1/products/<1>', {'products.csv': [['1', 'id']]}],
    'data-product_id-retailer_id': ['https://api.blueboard.io/v1/data/<1>/<2>', {'data.csv': [['1', 'product/id'], ['2', 'retailer/id']]}],
    'history_data-product_id-retailer_id': ['https://api.blueboard.io/v1/history/<1>/<2>?start=2022-03-10', {'data.csv': [['1', 'product/id'], ['2', 'retailer/id']]}],
}

# possible cases to handle
# 1. response_json is list of dictionaries with same keys (url_type1)
# 2. response_json is dictionary with one key having value of list and other keys having value of dictionary (url_type2)
# 3. response_json is dictionary with all keys having value of dictionary (url_type2)

# create folders
apis_response_path = 'apis-response'
dataframes_path = 'dataframes-csv'
if not os.path.exists(apis_response_path):
    os.mkdir(apis_response_path)
if not os.path.exists(dataframes_path):
    os.mkdir(dataframes_path)

# # loop over all APIs/URLs of type1
for api_name, url in urls_type1.items():
    try:
        print(f'API -> {api_name} | URL -> {url}')
        # call API and get json response as python dictionary
        # response_list = json.loads(open(f'json_formats/{api_name}.json', 'r').read(), object_pairs_hook=OrderedDict)
        response_list = get_json_from_API(url, api_name)
        df_response_list = extract_data_from_response_list(response_list)
        df_response_list.to_csv(f'{dataframes_path}/{api_name}.csv', index=False)
    except Exception as e:
        print(e)
        continue

# loop over all APIs/URLs of type2
for api_name, value in urls_type2.items():
    try:
        if DEGUB: print(f'API -> {api_name}\nurl_template -> {value[0]}')
        placeholders_dict = value[1]
        if DEGUB: print('[placeholders_dict]', placeholders_dict)
        urls_to_crawl = []
        for filename, placeholders in placeholders_dict.items():
            # print(filename, placeholders)
            df = pd.read_csv(os.path.join(dataframes_path, filename))
            for idx, row in df.iterrows():
                url_template = value[0]
                for [placeholder, column_name] in placeholders:
                    id = row[column_name]
                    url_template = url_template.replace(f'<{placeholder}>', id)
                # print(url_template)
                urls_to_crawl.append(url_template)
        print(f'API -> {api_name} | urls_to_crawl -> {len(urls_to_crawl)}')
        if DEGUB: pprint(urls_to_crawl)

        dfs = {}
        for url in urls_to_crawl[:10]:
            print(f'API -> {api_name} | URL -> {url}')
            response_obj = get_json_from_API(url, api_name, load_from_disk=False)
            dfs[url] = extract_data_from_response_object(response_obj)
            # print('[dfs]', dfs[url].shape, dfs[url].columns)
        
        # make all dfs have same columns
        columns = []
        for df in dfs.values():
            columns += df.columns.tolist()
        columns = unique(columns)
        # print(columns, len(columns))
        for key in dfs:
            # print(dfs[key].columns)
            for col in columns:
                if col not in dfs[key].columns:
                    dfs[key][col] = ''
            # print(dfs[key].shape)
        # print(len(dfs.values()))
        df_combined = pd.concat(dfs.values())
        df_combined.to_csv(f'{dataframes_path}/{api_name}.csv', index=False)
        if DEGUB: print(df_combined)
    except Exception as e:
        print(e)
        continue
