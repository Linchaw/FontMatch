# import os
#
# ocr_dir = '../result/ocr'
#
# ocr_files_list = os.listdir(ocr_dir)
# ocr_files_list.sort(key=lambda x: int(x.split('.')[0]))
# print(ocr_files_list)
# all_chars_list = []
# for file in ocr_files_list[0:8]:
#     with open(os.path.join(ocr_dir, file), 'r') as f:
#         chars_list = f.readlines()
#         all_chars_list.extend(chars_list)
# print(all_chars_list)
#
# chars_list = ''
# for line in all_chars_list:
#     chars_list += line.strip('\n')
# print(chars_list)
#
# for page in range(34):
#     with open('ocr/0_{}.txt'.format(page), 'w') as f:
#         f.write('')
#     for row in range(12):
#         start = page * 96 + row * 8
#         temp = chars_list[start:start + 8]
#         with open('ocr/0_{}.txt'.format(page), 'a') as f:
#             f.write(temp)
#             f.write('\n')

import os

ocr_dir = './ocr'

ocr_files_list = os.listdir(ocr_dir)
print(ocr_files_list)
for file in ocr_files_list:
    if file == '.DS_Store':
        continue
    file_path = os.path.join(ocr_dir, file)
    with open(file_path, 'r') as f:
        temp = f.read()

    new_file = '2' + file[1:]
    new_file_path = os.path.join(ocr_dir, new_file)
    print(new_file_path)

    with open(new_file_path, 'w') as f:
        f.write(temp)



