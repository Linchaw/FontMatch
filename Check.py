
import os
import json

extract_dir = './result/extract'
extract_files = os.listdir(extract_dir)
extract_files.sort(key=lambda x: int(x.split('.')[0]))
ALL_ERROR = 0
for extract_file in extract_files[0:8]:
    file_name = os.path.join(extract_dir, extract_file)
    with open(file_name, 'r') as f:
        extract_info = f.readlines()
    rate = {'errno': 0}
    per_error = 0
    for i in range(0, len(extract_info), 4):
        info = extract_info[i].split('-')
        per_rate = {info[0]: {'00': False, '01': False, '10': False, '11': False}, 'errno': 0}
        temp_num = 0
        for j in range(4):
            temp = extract_info[i+j].split('-')
            if temp_num == 0 and temp[5] == '00\n':
                per_rate[info[0]]['00'] = True
            elif temp_num == 1 and temp[5] == '01\n':
                per_rate[info[0]]['01'] = True
            elif temp_num == 2 and temp[5] == '10\n':
                per_rate[info[0]]['10'] = True
            elif temp_num == 3 and temp[5] == '11\n':
                per_rate[info[0]]['11'] = True
            else:
                per_rate['errno'] += 1
            temp_num += 1

        per_error += per_rate['errno']
        rate.update(per_rate)
    rate['errno'] += per_error
    print(rate)
    ALL_ERROR += rate['errno']
    with open('./result/rate/{}.json'.format(extract_file), 'w') as f:
        json.dump(rate, f)

print(ALL_ERROR)
