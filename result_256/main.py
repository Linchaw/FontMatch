import os
import cv2
from PIL import Image
import split_chars
import json
import chars_match

origin_dir = ['../AAConvFont_results/simfs_cond_bg_pix2pix/train_latest/fake',
              '../AAConvFont_results/simkai_cond_bg_pix2pix/train_latest/fake',
              '../AAConvFont_results/simyy_cond_bg_pix2pix/train_latest/fake']


# 将字符图像排列生成A4页面 row:28 * column:16
def creat_pages():
    # 定义A4纸张大小，21cm * 29.7cm -> (21/2.54 * 300) * (29.7/2.54 * 300), 1英寸 = 2.54cm， 300dpi像素
    width, height = (2480, 3507)

    # 定义上下边距
    w_start = 150
    h_start = 100

    # 定义字符图像大小 and 间距
    img_size = 256
    gap = 18

    for i in range(len(origin_dir)):
        chars_list = os.listdir(origin_dir[i])
        chars_list.sort(key=lambda x: int(x.split('_')[1]))
        # print(chars_list)
        start = 0  # 当前处理的字符，下标从0开始
        flag = 0  # 标记是否到最后一页

        pages = 34  # 一共生成12页
        for p in range(pages):
            page = Image.new('RGB', (width, height), 'white')  # 创建A4纸张
            for row in range(12):
                if flag == 1:
                    break
                for column in range(8):
                    img = Image.open(os.path.join(origin_dir[i], chars_list[start]))
                    page.paste(img, (w_start + column * (img_size + gap), h_start + row * (img_size + gap)))
                    start += 1
                    if start == len(chars_list):
                        flag = 1
                        break
            page.save('pages/' + str(i) + '_' + str(p) + '.png')
            print('第' + str(p) + '页生成完成')
        break
    print('create pages successfully!')


# 获取文件路径并排序
def get_pages_path():
    page_path = './pages'
    file_list = os.listdir(page_path)
    if '.DS_Store' in file_list:
        file_list.remove('.DS_Store')
    # 排序
    file_list.sort(key=lambda x: int(x.split('.')[0].split('_')[1]))
    file_list.sort(key=lambda x: x.split('_')[0])
    # 生成文件路径
    file_path = []
    for x in file_list:
        tmp = os.path.join(page_path, x)
        file_path.append(tmp)
    return file_path


# 切割字符
def split_pages(pages_path):
    idx = 0  # page序号
    for page_path in pages_path:
        img_input = cv2.imread(page_path, cv2.IMREAD_GRAYSCALE)
        _, img = cv2.threshold(img_input, 0, 255, cv2.THRESH_OTSU)  # 将一幅灰度图二值化 input-one channel
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV)

        # cv2.imshow("cs", img)  # 在窗口cs中显示图片
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        seg_box = split_chars.get_seg_box(img, 12, 8)  # (x, y, w, h) [28][16]

        if idx <=33:
            para = 0
            idxx = idx
        elif idx <= 67:
            para = 1
            idxx = idx - 34
        elif idx <= 101:
            para = 2
            idxx = idx - 68
        with open('ocr/{}_{}.txt'.format(para, idxx), 'r') as f:
            ocr_results = [line.strip() for line in f.readlines()]
        if seg_box is not None:
            seg_result = split_chars.get_seg_result(ocr_results, seg_box)
        else:
            seg_result = split_chars.get_seg_result2(img, ocr_results)

        # 保存供其他模块导入
        with open('split/{}.txt'.format(idx), 'w') as f:
            f.write(json.dumps(seg_result))

        # 显示切分结果
        img_input = cv2.imread(page_path, 1)  # 重新读入干净的图片
        for i in range(len(seg_result)):
            c, x, y, w, h = seg_result[i]
            cv2.rectangle(img_input, (x, y), (x + w, y + h), (0, 0, 255))
        cv2.imwrite("out/{}.png".format(idx), img_input)
        # print("{}-part done".format(idx))
        idx += 1

    pass


# 字体匹配
def match_font(pages_path):
    idx = 0
    for page_path in pages_path:
        img_input = cv2.imread(page_path, cv2.IMREAD_GRAYSCALE)
        _, img = cv2.threshold(img_input, 0, 255, cv2.THRESH_OTSU)  # 将一幅灰度图二值化 input-one channel
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV)

        with open('split/{}.txt'.format(idx), 'r') as f:
            split_result = json.loads(f.read())

        watermark_info = []
        with open('extract/{}.txt'.format(idx), 'w') as f:
            for i in range(len(split_result)):
                hz, x, y, w, h = split_result[i]

                # 对读入的字符图片，依次从字库中找出其四种变形字符
                total, hz_codes = chars_match.lookup_font_codes(hz)
                if total == 0:
                    print("{}-不存在变形".format(hz))
                    continue
                elif total is None:
                    print('{}-不存在在FontInfo中'.format(hz))
                    continue

                hz_img = img[y:y + h, x:x + w]  # 输入图片中截取到的单个汉字

                if idx <= 33:
                    para = 0
                elif idx <= 67:
                    para = 1
                elif idx <= 101:
                    para = 2

                hz_bitmaps = chars_match.get_font_bitmap(hz_codes, para)  # 字符对应的四种标准字形
                # 字符匹配算法，提取出水印信息01比特串
                pixel_info, water_mark = chars_match.match_fonting(hz_img, hz_bitmaps)
                watermark_info.append(water_mark)
                f.write(hz + '-' + str(x) + '-' + str(y) + '-' + str(w) + '-' + str(h) + '-' + water_mark + '\n')

        idx += 1
        watermark_str = ''.join(watermark_info)
        print(len(watermark_str))
        print("文本中提取的所有bit信息为：%s" % watermark_str)


def check_error():
    extract_dir = './extract'
    for num_i in range(3):
        ALL_ERROR = {}
        for num_j in range(34):
            file_name = os.path.join(extract_dir, '{}.txt'.format(str(num_i * 34 + num_j)))
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
                    print(num_i * 34 + num_j)
                    ALL_ERROR.update(hz_check)
        print(ALL_ERROR)
        with open('./error/{}-{}.json'.format(num_i*34, num_i*34+33), 'w') as f:
            f.write(json.dumps(ALL_ERROR))


# 主函数
def main():
    # creat_pages()
    # file_list = get_pages_path()
    # split_pages(file_list)
    # match_font(file_list)
    check_error()
    pass


if __name__ == '__main__':
    main()
