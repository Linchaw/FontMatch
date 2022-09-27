import cv2
import numpy as np
import json
import os
from freetype import *


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


# 生成所有变形字体的编码值所对应的文件
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

    num = 0
    chars_code_file_dict = {}
    for chars_code in chars_code_list:
        for char_code in chars_code:
            temp_file_name = '0_' + str(num).zfill(4) + '_fake_B_png'
            chars_code_file_dict.update({char_code: temp_file_name})
            num += 1
    with open("CharsCodeFile.txt", 'w') as f:
        f.write(json.dumps(chars_code_file_dict))


# 将char_code_list中的所有编码的变形字的像素值以numpy数组的形式返回（原来的）
def get_old_font_bitmap(char_code_list, width=128, height=128):
    bitmap_list = []
    face = Face('./sysfFS.ttf')
    face.set_char_size(width * height)
    slot = face.glyph

    for i, c in enumerate(char_code_list):
        face.load_char(int(c, 16))
        bitmap = slot.bitmap
        w, h = bitmap.width, bitmap.rows
        hanzi = np.array(bitmap.buffer, dtype='ubyte').reshape(h, w)
        bitmap_list.append(hanzi)

    return bitmap_list


# 将char_code_list中的所有编码的变形字的像素值以numpy数组的形式返回
def get_font_bitmap(char_code_list, para=0, width=128, height=128):
    bitmap_list = []
    with open('CharsCodeFile.txt', 'r') as f:
        char_code_file_dict = json.loads(f.read())

    dir = ['./AAConvFont_results/simfs_cond_bg_pix2pix/train_latest/fake',
           './AAConvFont_results/simkai_cond_bg_pix2pix/train_latest/fake',
           './AAConvFont_results/simyy_cond_bg_pix2pix/train_latest/fake']
    # para 代表访问文件的位置， 暂时只考虑对page0：7的图片进行处理

    for i, c in enumerate(char_code_list):
        file_path = os.path.join(dir[para], char_code_file_dict[c])
        img = cv_imread(file_path)
        hanzi = np.array(img, dtype='ubyte')
        bitmap_list.append(hanzi)

    return bitmap_list


# 读取含中文字符的图片路径
def cv_imread(path):
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), -1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


# 原本的匹配算法
def match_fonting(input_image, hz_bitmap):  # 提取水印信息
    cut_input_image = cut_edge(input_image)  # 黑底白字接包围盒
    resize_image = adj_size(cut_input_image)  # 放大到标准尺寸的3倍 360*300
    white_pixel_num = divide_block(resize_image)  # 返回分块中的白色像素数量
    C_Normal = np.around((white_pixel_num / np.sum(white_pixel_num)), 4)
    # print(C_Normal)

    tx, ty = resize_image.shape
    temporary = []
    # t = []
    for i in range(len(hz_bitmap)):  # 标准字切边并调整尺寸
        hz_bitmap[i] = cut_edge(hz_bitmap[i])
        adjust = adjust_size(hz_bitmap[i], ty, tx)
        T_Wpixel = divide_block(adjust)
        T_Normal = np.around((T_Wpixel / np.sum(T_Wpixel)), 4)
        temporary.append(T_Normal)
        # t.append(adjust)
    # print(temporary)

    if len(hz_bitmap) == 4:
        # h_all = np.hstack((Blurimage,t[0],t[1],t[2],t[3]))
        # display(h_all)
        Vectorlist = []  # 获取向量距离
        for i in range(len(temporary)):
            VectorDis = np.around(np.sqrt(np.sum(np.square(temporary[i] - C_Normal))), 6)
            Vectorlist.append(VectorDis)
        minvalue_index = np.argmin(Vectorlist)
        waterinfo = mapping_4(minvalue_index)
        return Vectorlist, waterinfo


# 切割白边
def cut_edge(image):  # 黑底白字包围盒图片(只针对黑底白字图像可切边)
    x = image.sum(axis=1)
    y = image.sum(axis=0)
    edges_x = []
    edges_y = []
    for i, value in enumerate(x):
        if value >= 255:
            edges_x.append(i)
    for i, value in enumerate(y):
        if value >= 255:
            edges_y.append(i)

    left = min(edges_x)
    right = max(edges_x)
    width = right - left
    bottom = min(edges_y)
    top = max(edges_y)
    height = top - bottom
    font_img = image[left:left + width, bottom:bottom + height]
    return font_img


def adj_size(image):
    standHW = cv2.resize(image, (100, 120))
    standHW = cv2.resize(standHW, (standHW.shape[1] * 3, standHW.shape[0] * 3), interpolation=cv2.INTER_LANCZOS4)
    return standHW


def adjust_size(image, h, w):  # 调整图像大小
    dim = (h, w)
    image = cv2.resize(image, dim)
    return image


def divide_block(image):  # 分块并统计块内白色像素个数
    white_pixel = []
    N = 30
    M = 30
    h, w = image.shape
    distance_h = int(np.floor(h / N)) if (N < h) else 1
    distance_w = int(np.floor(w / M)) if (M < w) else 1
    for i in range(N):
        for j in range(M):
            sub_block = image[distance_h * i:distance_h * (i + 1), distance_w * j:distance_w * (j + 1)]
            # display(sub_block)
            count = count_white(sub_block)
            white_pixel.append(count)
    return white_pixel


def mapping_4(minvalue_index):
    if minvalue_index == 0:
        return "00"
    if minvalue_index == 1:
        return "01"
    if minvalue_index == 2:
        return "10"
    if minvalue_index == 3:
        return "11"


def count_white(image):  # 计算白色像素个数
    temp = image // 255
    return np.sum(np.reshape(temp, (temp.size,)))


def main():
    # mk_charcodefile()
    cn_codes = ['e270', 'e271', 'e273', 'e272']
    bitmap = get_font_bitmap(cn_codes)
    # bitmap = get_old_font_bitmap(cn_codes)
    print(bitmap)

    pass


if __name__ == '__main__':
    main()
