import pandas as pd
import xml.etree.ElementTree as ET
from collections import defaultdict

# load XML file
tree = ET.parse('heba_test_1_final.xml')
root = tree.getroot()

# XML to JSON (list of python dictionaries)
data_json = []
columns = []
for i, child_G_1 in enumerate(list(root.iter('G_1'))):
    data_dict = {}
    for j, child in enumerate(child_G_1):
        if child.tag not in columns:
            columns.append(child.tag)
        data_dict[child.tag] = child.text.strip() if child.text else ''
    data_json.append(data_dict)

print('[columns]', len(columns), columns)
print('[data_json]', len(data_json))

# JSON (python dictionary) to CSV
data_csv = defaultdict(list)
for obj in data_json:
    for column in columns:
        value = obj[column] if column in obj else ''
        data_csv[column].append(value)

# save CSV file
df_data = pd.DataFrame(data_csv)
df_data.to_csv('output.csv', index=False)
print('CSV file saved at: output.csv')

# load and convert dtypes to object
df_data = pd.read_csv('output.csv')
print('[df_data]\n', df_data.dtypes)
df_data = df_data.astype(object)
print('[df_data]\n', df_data.dtypes)
