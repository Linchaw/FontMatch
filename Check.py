
import os
import json


def check_error():
    extract_dir = './result/extract'
    for num_i in range(3):
        ALL_ERROR = {}
        for num_j in range(8):
            file_name = os.path.join(extract_dir, '{}.txt'.format(str(num_i*8+num_j)))
            with open(file_name, 'r') as f:
                extract_result = [line.strip('\n') for line in f.readlines()]

            # 对每个字符进行检查
            for i in range(0, len(extract_result), 4):
                hz_check = {extract_result[i][0]: {'00': False, '01': False, '10': False, '11': False}}
                for j in range(4):
                    water_mark = extract_result[i + j].split('-')[-1]
                    if water_mark == '00' and j == 0:
                        hz_check[extract_result[i][0]].pop('00')
                    elif water_mark == '01' and j == 1:
                        hz_check[extract_result[i][0]].pop('01')
                    elif water_mark == '10' and j == 2:
                        hz_check[extract_result[i][0]].pop('10')
                    elif water_mark == '11' and j == 3:
                        hz_check[extract_result[i][0]].pop('11')
                if len(hz_check[extract_result[i][0]]) != 0:
                    ALL_ERROR.update(hz_check)
        print(ALL_ERROR)
        with open('result/rate/{}-{}.json'.format(num_i*8, num_i*8+7), 'w') as f:
            f.write(json.dumps(ALL_ERROR))


if __name__ == '__main__':
    check_error()
