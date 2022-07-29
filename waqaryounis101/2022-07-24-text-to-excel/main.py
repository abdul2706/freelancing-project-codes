import re
import os
import pandas as pd
from pprint import pprint
from collections import defaultdict

def print_list(data_list):
    for i, line in enumerate(data_list):
        print(i + 1, len(line))

def extract_options(string):
    matches = re.findall(r'[a-dA-D][:;.-] ', string)
    indices = [string.find(match) for match in matches] + [len(string)]
    options = [string[indices[k]:indices[k+1]].strip() for k in range(len(indices) - 1)]
    return options

text_base_path = 'text-files'
text_files = os.listdir(text_base_path)
excel_base_path = 'excel-files'
if not os.path.exists(excel_base_path):
    os.mkdir(excel_base_path)
error_log_file = open('errors.txt', 'w', encoding='utf-8')

for text_file_name in text_files:
    text_file_path = os.path.join(text_base_path, text_file_name)
    data_text = open(text_file_path, encoding='utf-8').read()
    
    data_lines = data_text.replace('\t', ' ').split('\n')
    current_list = []
    data_list = []
    for i, data_line in enumerate(data_lines):
        data_line = data_lines[i].strip()
        # print(text_file_name, '[data_line]', data_line)
        if len(data_line) < 2:
            if len(current_list) > 0:
                data_list.append(current_list)
                current_list = []
        else:
            current_list.append([i + 1, data_line])
            if len(current_list) == 6 and 'ans' in data_line.lower():
                data_list.append(current_list)
                current_list = []

    # print(text_file_name, len(data_list))
    # print_list(data_list)
    # continue
    
    data_dict = defaultdict(list)
    key_to_option = {'A': 'optionA', 'B': 'optionB', 'C': 'optionC', 'D': 'optionD'}
    for i, data_question in enumerate(data_list):
        if len(data_question) == 6:
            try:
                # extract data
                question = re.sub(r'^\d*\)?', '', data_question[0][1]).strip()
                optionA = re.sub(r'^[a-dA-D][:;.-]', '', data_question[1][1]).strip()
                optionB = re.sub(r'^[a-dA-D][:;.-]', '', data_question[2][1]).strip()
                optionC = re.sub(r'^[a-dA-D][:;.-]', '', data_question[3][1]).strip()
                optionD = re.sub(r'^[a-dA-D][:;.-]', '', data_question[4][1]).strip()
                key = re.sub(r'^[a-zA-Z]{3,}[:;.-]?', '', data_question[5][1]).strip()
                correct_answer = eval(key_to_option[key])
                # insert data
                data_dict['Question'].append(question)
                data_dict['Correct Answer'].append(correct_answer)
                data_dict['Option A'].append(optionA)
                data_dict['Option B'].append(optionB)
                data_dict['Option C'].append(optionC)
                data_dict['Option D'].append(optionD)
                data_dict['Key'].append(key)
            except Exception as e:
                print('*************** ERROR ALERT ***************', file=error_log_file)
                print('File Name:', text_file_name, file=error_log_file)
                print(f'Something is wrong around following {len(data_question)} lines:', file=error_log_file)
                for line in data_question:
                    print(*line, file=error_log_file)
                print(file=error_log_file)

        elif len(data_question) == 5:
            try:
                # handle exceptions
                dq0, dq1, dq2, dq3, dq4 = data_question
                is_option = re.search(r'^[a-dA-D][:;.-]', dq0[1])
                if is_option != None: raise Exception()
                is_key = re.search(r'^[a-zA-Z]{3,}[:;.-]?', dq4[1])
                if is_key == None: raise Exception()
                options = []
                options.extend(extract_options(dq1[1]))
                options.extend(extract_options(dq2[1]))
                options.extend(extract_options(dq3[1]))
                if len(options) != 4: raise Exception()
                # extract data
                question = re.sub(r'^\d*\)?', '', dq0[1]).strip()
                optionA, optionB, optionC, optionD = options
                key = re.sub(r'^[a-zA-Z]+[:;.-]?', '', dq4[1]).strip()
                correct_answer = eval(key_to_option[key])
                # insert data
                data_dict['Question'].append(question)
                data_dict['Correct Answer'].append(correct_answer)
                data_dict['Option A'].append(optionA)
                data_dict['Option B'].append(optionB)
                data_dict['Option C'].append(optionC)
                data_dict['Option D'].append(optionD)
                data_dict['Key'].append(key)
            except Exception as e:
                print('*************** ERROR ALERT ***************', file=error_log_file)
                print('File Name:', text_file_name, file=error_log_file)
                print(f'Something is wrong around following {len(data_question)} lines:', file=error_log_file)
                for line in data_question:
                    print(*line, file=error_log_file)
                print(file=error_log_file)

        else:
            print('*************** ERROR ALERT ***************', file=error_log_file)
            print('File Name:', text_file_name, file=error_log_file)
            print(f'Something is wrong around following {len(data_question)} lines:', file=error_log_file)
            for line in data_question:
                print(*line, file=error_log_file)
            print(file=error_log_file)

    excel_data = pd.DataFrame(data_dict)
    excel_file_path = os.path.join(excel_base_path, text_file_name[:-4] + '.xlsx')
    # print('[excel_data.shape]', excel_data.shape)
    print('Saving File:', excel_file_path)
    excel_data.to_excel(excel_file_path, index=False)
