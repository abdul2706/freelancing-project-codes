import os
import json
import requests
import pandas as pd
from collections import OrderedDict

# this is the main function that recursively looks for columns names in json object returned by API
# BFS -> Breadth First Search (Searching algorithm for Graphs/Trees)
def BFS(obj, parent, depth):
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

# this function calls API and returns output as json (or python dictionary)
def get_json_from_API(url, api_name):
    if os.path.exists(f'api-dumps/{api_name}.txt'):
        response_text = open(f'api-dumps/{api_name}.txt', 'r').read()
    else:
        payload = {}
        headers = {'Api-Key': 'dNtr6w4juJTZ9vWhwNmD3bKrAf6TdAsM'}
        response = requests.request("GET", url, headers=headers, data=payload)
        response_text = response.text
        with open(f'api-dumps/{api_name}.txt', 'w') as f:
            f.write(response_text)
    return json.loads(response_text, object_pairs_hook=OrderedDict)

# this function takes all extracted column names and returns unique column names
def unique(array):
    unique_array = []
    for elem in array:
        if elem not in unique_array:
            unique_array.append(elem)
    return unique_array

TAG = '[create_dataframes]'
urls = {
    'DATA_API': 'https://api.blueboard.io/v1/data', 
    'MATCHES_API': 'https://api.blueboard.io/v1/MATCHES', 
    'PERFORMANCE_API': 'https://api.blueboard.io/v1/performance/search/entrypoints', 
    'PRODUCT_PAGE_CONTENT_API1': 'https://api.blueboard.io/v1/content/matches', 
    'PRODUCT_PAGE_CONTENT_API2': 'https://api.blueboard.io/v1/content/history?start=2022-03-20&end=2022-03-22', 
    'PRODUCTS_API1': 'https://api.blueboard.io/v1/products', 
    'PRODUCTS_API2': 'https://api.blueboard.io/v1/products/c38a65857699dc2ed4', 
    'RETAILERS_API': 'https://api.blueboard.io/v1/retailers/c09a0b91619bdb24d8',
    'BRANDS_API': 'https://api.blueboard.io/v1/brands/d8801c881596bd26cd',
}

dataframes_path = 'dataframes-csv'
if not os.path.exists(dataframes_path):
    os.mkdir(dataframes_path)

# loop over all APIs
for api_name, url in urls.items():
    print(f'API -> {api_name}\nURL -> {url}')
    response_json = get_json_from_API(url, api_name)
    
    # for each API extract column names
    columns = []
    main_key = None
    if type(response_json) is list:
        for obj in response_json:
            columns += BFS(obj, '', 0)
    else:
        for key in response_json.keys():
            response_obj = response_json[key]
            if type(response_obj) is list:
                main_key = key
                for obj in response_obj:
                    columns += BFS(obj, '', 0)
    columns = unique(columns)

    # collect data according to extracted columns
    data = {key: [] for key in columns}
    if main_key is not None:
        response_json = response_json[main_key]
    print(f'Total {len(response_json)} objects in JSON returned by API.')
    for i, obj in enumerate(response_json):
        for column in columns:
            value = obj
            for j, k in enumerate(column.split('/')):
                if type(value) is OrderedDict:
                    value = value[k] if k in value else ''
                elif type(value) is list:
                    value = value[int(k)] if int(k) < len(value) else ''
            data[column].append(value.strip() if type(value) is str else value)

    # remove columns (if any) that don't contain any data
    data_refined = {}
    for key in data:
        if len(data[key]) > 0:
            data_refined[key] = data[key]

    # create dataframe from collected data
    df_data = pd.DataFrame(data_refined)
    print(f'Total {len(df_data)} objects in Dataframe extracted.')
    df_data.to_csv(f'{dataframes_path}/{api_name}.csv', index=False)
    print('-' * 10)
