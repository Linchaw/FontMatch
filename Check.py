
import os
import json

extract_dir = './result/extract'
extract_files = os.listdir(extract_dir)
extract_files.sort(key=lambda x: int(x.split('.')[0]))
for extract_file in extract_files:
    file_name = os.path.join(extract_dir, extract_file)
    with open(file_name, 'r') as f:
        extract_info = f.readlines()
    rate = {}
    for i in range(0, len(extract_info), 4):
        info = extract_info[i].split('-')
        per_rate = {info[0]: {'00': False, '01': False, '10': False, '11': False}}
        temp_num = 0
        for j in range(4):
            temp = extract_info[i+j].split('-')
            if temp_num == 0 and temp[5] == '00\n':
                per_rate[info[0]].pop('00')
            elif temp_num == 1 and temp[5] == '01\n':
                per_rate[info[0]].pop('01')
            elif temp_num == 2 and temp[5] == '10\n':
                per_rate[info[0]].pop('10')
            elif temp_num == 3 and temp[5] == '11\n':
                per_rate[info[0]].pop('11')
            temp_num += 1
        rate.update(per_rate)
    with open('./result/rate/{}.json'.format(extract_file), 'w+') as f:
        json.dump(rate, f)

ALL_ERROR = 0
for i in range(24):
    with open('./result/rate/{}.txt.json'.format(str(i)), 'r') as f:
        rate = json.loads(f.read())
        for key in rate.keys():
            ALL_ERROR += len(rate[key])
print(ALL_ERROR)
