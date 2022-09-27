import json
import random
import cv2
import numpy as np
import os


# 将FontInfo.txt中char_code的所有变形字体的编码值返回
def lookup_font_codes(char):
    font_list = np.loadtxt("FontInfo.txt", encoding='gbk', dtype=np.str_, delimiter='|')
    for line in font_list:
        lst = line.split('-')
        if lst[0] == char:
            char_code_list = lst[2:]
            total = lst[1]
            return total, char_code_list
    return None, None


def mk_charcodefile():
    ocr_result_dir = './result/ocr'
    chars_string = ''
    for i in range(8):
        file_name = os.path.join(ocr_result_dir, str(i) + '.txt')
        with open(file_name, 'r') as f:
            chars_list = f.readlines()
        for chars in chars_list:
            chars_string += chars.strip('\n')
    # print(chars_string)

    char_string = ''
    for i in range(0, len(chars_string), 4):
        char_string += chars_string[i]

    chars_code_list = []
    chars_code_dict = {}
    for char in char_string:
        total, char_code_list = lookup_font_codes(char)
        chars_code_list.append(char_code_list)
        chars_code_dict.update({char: char_code_list})
    print(chars_code_dict)

    num = 0
    chars_code_file_dict = {}
    for chars_code in chars_code_list:
        for char_code in chars_code:
            temp_file_name = '0_' + str(num).zfill(4) + '_fake_B.png'
            chars_code_file_dict.update({char_code: temp_file_name})
            num += 1
    with open("CharsCodeFile.txt", 'w') as f:
        f.write(json.dumps(chars_code_file_dict))


def test1():
    with open('CharsCodeFile.txt', 'r') as f:
        dict = json.loads(f.read())

    font_list = np.loadtxt("FontInfo.txt", encoding='gbk', dtype=np.str_, delimiter='|')

    ram = random.randint(0, 996)
    font = font_list[ram].split('-')
    if font[1] == '2':
        test1()
        exit()
    tmp = dict[font[3]]
    print(font)
    print(type(tmp))
    dir = ['./AAConvFont_results/simfs_cond_bg_pix2pix/train_latest/fake']
    filename = os.path.join(dir[0], tmp)
    img = cv2.imread(filename)
    cv2.imshow("cs", img)  # 在窗口cs中显示图片
    cv2.waitKey(0)
    cv2.destroyAllWindows()




def main():
    # mk_charcodefile()
    test1()  # 测试生成文件是否对上

if __name__ == '__main__':
    main()