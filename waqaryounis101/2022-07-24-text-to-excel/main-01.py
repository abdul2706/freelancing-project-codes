import re
import os
import pandas as pd
from pprint import pprint
from collections import defaultdict

text_base_path = 'z-client-files'
text_files = os.listdir(text_base_path)
excel_base_path = 'z-excel-files'
if not os.path.exists(excel_base_path):
    os.mkdir(excel_base_path)
error_log_file = open('errors.txt', 'w', encoding='utf-8')

for text_file_name in text_files:
    # print(text_file_name)
    text_file_path = os.path.join(text_base_path, text_file_name)
    text_data = open(text_file_path, encoding='utf-8').read()
    # print(text_data)
    data_lines = [[i + 1, line.strip().replace('\t', ' ')] for i, line in enumerate(text_data.split('\n')) if len(line.strip().replace('\t', ' ')) > 1]
    # pprint(data_lines)
    # print(len(data_lines), len(data_lines)/6)

    data_dict = defaultdict(list)
    count = 0
    
    while count < len(data_lines):
        try:
            # question
            question = data_lines[count + 0][1]
            question = re.sub(r'^\d*\)?', '', question).strip()
            # print(count, '[question]', question)

            # optionA
            optionA = data_lines[count + 1][1]
            pattern = r'^[aA][:;.-]'
            if re.search(pattern, optionA) == None:
                raise Exception(f'{data_lines[count + 1][0]}, trying to set optionA = {optionA}')
            optionA = re.sub(pattern, '', optionA).strip()
            # print(count, '[optionA]', optionA)

            # optionB
            optionB = data_lines[count + 2][1]
            pattern = r'^[bB][:;.-]'
            if re.search(pattern, optionB) == None:
                raise Exception(f'{data_lines[count + 2][0]}, trying to set optionB = {optionB}')
            optionB = re.sub(pattern, '', optionB).strip()
            # print(count, '[optionB]', optionB)

            # optionC
            optionC = data_lines[count + 3][1]
            pattern = r'^[cC][:;.-]'
            if re.search(pattern, optionC) == None:
                raise Exception(f'{data_lines[count + 3][0]}, trying to set optionC = {optionC}')
            optionC = re.sub(pattern, '', optionC).strip()
            # print(count, '[optionC]', optionC)

            # optionD
            optionD = data_lines[count + 4][1]
            pattern = r'^[dD][:;.-]'
            if re.search(pattern, optionD) == None:
                raise Exception(f'{data_lines[count + 4][0]}, trying to set optionD = {optionD}')
            optionD = re.sub(pattern, '', optionD).strip()
            # print(count, '[optionD]', optionD)

            # key
            key = data_lines[count + 5][1]
            pattern = r'^[aA][nN][aAsS][:;.-]'
            if re.search(pattern, key) == None:
                raise Exception(f'{data_lines[count + 5][0]}, trying to set key = {key}')
            key = re.sub(pattern, '', key).strip()
            # print(count, '[key]', key)

            # correct-answer
            if key == 'A': correct_answer = optionA
            if key == 'B': correct_answer = optionB
            if key == 'C': correct_answer = optionC
            if key == 'D': correct_answer = optionD
            # print(count, '[correct_answer]', correct_answer)

            data_dict['Question'].append(question)
            data_dict['Correct Answer'].append(correct_answer)
            data_dict['Option A'].append(optionA)
            data_dict['Option B'].append(optionB)
            data_dict['Option C'].append(optionC)
            data_dict['Option D'].append(optionD)
            data_dict['Key'].append(key)

        except Exception as e:
            print('******* ERROR AROUND THESE LINES *******', file=error_log_file)
            print('Error Line:', e, file=error_log_file)
            print('File Name:', text_file_name, file=error_log_file)
            print('Current Question', file=error_log_file)
            print(*data_lines[count + 0], file=error_log_file)
            if (count + 1) < len(data_lines): print(*data_lines[count + 1], file=error_log_file)
            if (count + 2) < len(data_lines): print(*data_lines[count + 2], file=error_log_file)
            if (count + 3) < len(data_lines): print(*data_lines[count + 3], file=error_log_file)
            if (count + 4) < len(data_lines): print(*data_lines[count + 4], file=error_log_file)
            if (count + 5) < len(data_lines): print(*data_lines[count + 5], file=error_log_file)
            print(file=error_log_file)

        finally:
            count += 6

    excel_data = pd.DataFrame(data_dict)
    excel_file_path = os.path.join(excel_base_path, text_file_name[:-4] + '.xlsx')
    print('[excel_file_path]', excel_file_path)
    excel_data.to_excel(excel_file_path, index=False)
    # print(text_file_name, excel_data.shape)








# for excel_file_name in os.listdir(excel_base_path):
#     print(pd.read_excel(os.path.join(excel_base_path, excel_file_name)).shape)

# (133, 7)
# (138, 7)
# (140, 7)
# (130, 7)
# (128, 7)
# (164, 7)
# (137, 7)
# (108, 7)
# (124, 7)
# (79, 7)
# (95, 7)
# (155, 7)
# (146, 7)
# (143, 7)
# (164, 7)
# (113, 7)
# (169, 7)
# (131, 7)
# (86, 7)

# 133 <=> ANASTHESIA February 15, 2022 - Morning.txt
# 138 <=> ANASTHESIA May 17, 2022 - Morning.txt
# 140 <=> GYNAE & OBS February 16, 2022 — Morning.txt
# 130 <=> GYNAE & OBS February 16,2022 - Afternoon.txt
# 128 <=> GYNAE & OBS May 16, 2022 — Afternoon.txt
# 164 <=> MEDCINE February 15, 2022 - Afternoon.txt
# 137 <=> MEDICINE & ALLIED  February 16, 2022 — Night.txt
# 108 <=> MEDICINE & ALLIED  may16, 2022 — Night.txt
# 124 <=> MEDICINE & Allied May 17, 2022 - Afternoon.txt
# 79 <=> MEDICINE & ALLIED May 17, 2022 - Night.txt
# 95 <=> MEDICINE & ALLIED May 17, 2022 — Morning.txt
# 155 <=> RADIOLOGY February 15,2022 - Afternoon.txt
# 146 <=> RADIOLOGY May 17,2022 -Afternoon.txt
# 142 <=> RADIOLOGYMay 17,2022 — Morning.txt
# 161 <=> SURGERY & ALLIED February 16, 2022 — Night.txt
# 113 <=> SURGERY & ALLIED February 16,2022 - Afternoon.txt
# 169 <=> SURGERY & ALLIED May 16, 2022 - Night.txt
# 131 <=> SURGERY & ALLIED May 16, 2022 — Afternoon.txt
# 86 <=> SURGERY & ALLIEDNMay 16, 2022 — Morning.txt

# 133 <=> ANASTHESIA February 15, 2022 - Morning.txt
# 138 <=> ANASTHESIA May 17, 2022 - Morning.txt
# 140 <=> GYNAE & OBS February 16, 2022 — Morning.txt
# 130 <=> GYNAE & OBS February 16,2022 - Afternoon.txt
# 128 <=> GYNAE & OBS May 16, 2022 — Afternoon.txt
# 164 <=> MEDCINE February 15, 2022 - Afternoon.txt
# 137 <=> MEDICINE & ALLIED  February 16, 2022 — Night.txt
# 108 <=> MEDICINE & ALLIED  may16, 2022 — Night.txt
# 124 <=> MEDICINE & Allied May 17, 2022 - Afternoon.txt
# 79 <=> MEDICINE & ALLIED May 17, 2022 - Night.txt
# 95 <=> MEDICINE & ALLIED May 17, 2022 — Morning.txt
# 156 <=> RADIOLOGY February 15,2022 - Afternoon.txt
# 146 <=> RADIOLOGY May 17,2022 -Afternoon.txt
# 142 <=> RADIOLOGYMay 17,2022 — Morning.txt
# 164 <=> SURGERY & ALLIED February 16, 2022 — Night.txt
# 113 <=> SURGERY & ALLIED February 16,2022 - Afternoon.txt
# 169 <=> SURGERY & ALLIED May 16, 2022 - Night.txt
# 131 <=> SURGERY & ALLIED May 16, 2022 — Afternoon.txt
# 86 <=> SURGERY & ALLIEDNMay 16, 2022 — Morning.txt
