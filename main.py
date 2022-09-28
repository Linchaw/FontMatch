import os
import json
import cv2
from PIL import Image
import split_chars
import chars_match


# 将字符图像排列生成A4页面 row:28 * column:16
def creat_pages():
    # 定义A4纸张大小，21cm * 29.7cm -> (21/2.54 * 300) * (29.7/2.54 * 300), 1英寸 = 2.54cm， 300dpi像素
    width, height = (2480, 3507)

    # 定义上下边距
    w_start = 250
    h_start = 200

    # 定义字符图像大小 and 间距
    img_size = 96
    gap = 18

    # 字符图像路径
    abs_dir = ['/Users/hlc/Documents/FontPageCode/AAConvFont_results/simfs_cond_bg_pix2pix/train_latest',
               '/Users/hlc/Documents/FontPageCode/AAConvFont_results/simkai_cond_bg_pix2pix/train_latest',
               '/Users/hlc/Documents/FontPageCode/AAConvFont_results/simyy_cond_bg_pix2pix/train_latest']
    sub_dir = './fake'
    or_dir = os.getcwd()
    for num in range(len(abs_dir)):
        os.chdir(abs_dir[num])
        file_list = os.listdir(sub_dir)
        img_paths = [os.path.join(sub_dir, x) for x in file_list]
        img_paths.sort(key=lambda x: int(x.split('_')[1]))

        # 当前处理的字符，下标从0开始
        start = 0
        # 标记是否到最后一页
        flag = 0

        # 可能产生的页数，需要通过字符resize后的大小、页边距以及行列间距来计算一页能放几个字符，这里是至少8页，
        pages = 8
        for p in range(pages):
            # 生成A4大小的空白页
            page = Image.new('RGB', (width, height), 'white')
            # 行数28，同理需要通过字符resize后的大小、页边距以及行列间距来计算

            for i in range(28):
                # 列数，即每一行的字数，同理需要通过字符resize后的大小、页边距以及行列间距来计算
                for j in range(16):
                    os.chdir(abs_dir[num])
                    # 读取图片
                    img = Image.open(img_paths[start])
                    # resize
                    resize_img = img.resize((img_size, img_size))
                    # 将字符图像贴在空白页，box是字符图像左上角在空白页的起始位置px
                    #
                    page.paste(resize_img, box=(w_start + (img_size + gap) * j, h_start + (img_size + gap) * i))
                    # 读取下一张字符图像
                    start += 1
                    # print(start)
                    # pages.save("./result/page_{}.pdf".format())
                    # 最后一页可能放不满，需要特殊处理
                    if start > 3179:
                        # pages.save("./result/page_7.pdf")
                        os.chdir(or_dir)
                        page.save("./result/pages/{}_7.png".format(num))
                        flag = 1
                        break
                if flag == 1:
                    break

            os.chdir(or_dir)
            # pages.save("./result/page_{}.pdf".format(p))
            page.save("./result/pages/{}_{}.png".format(num, p))

    print('create pages successfully!')


# 获取文件路径并排序
def get_pages_path():
    page_path = './result/pages'
    file_list = os.listdir(page_path)
    if '.DS_Store' in file_list:
        file_list.remove('.DS_Store')
    # 排序
    file_list.sort(key=lambda file_name: file_name[2])
    file_list.sort(key=lambda file_name: file_name[0])

    # 生成文件路径
    file_path = []
    for x in file_list:
        tmp = os.path.join(page_path, x)
        file_path.append(tmp)
    return file_path


# 显示图像
def display(img):
    cv2.imshow("1", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# 切割字符
def split_pages(pages_path):
    idx = 0  # page序号

    for page_path in pages_path:
        img_input = cv2.imread(page_path, cv2.IMREAD_GRAYSCALE)
        _, img = cv2.threshold(img_input, 0, 255, cv2.THRESH_OTSU)  # 将一幅灰度图二值化 input-one channel
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV)
        seg_box = split_chars.get_seg_box(img)  # (x, y, w, h) [28][16]

        with open('result/ocr/{}.txt'.format(idx), 'r') as f:
            ocr_results = [line.strip() for line in f.readlines()]
        if seg_box is not None:
            seg_result = split_chars.get_seg_result(ocr_results, seg_box)
        else:
            seg_result = split_chars.get_seg_result2(img, ocr_results)

        # 保存供其他模块导入
        with open('result/split/{}.txt'.format(idx), 'w') as f:
            f.write(json.dumps(seg_result))

        # 显示切分结果
        img_input = cv2.imread(page_path, 1)  # 重新读入干净的图片
        for i in range(len(seg_result)):
            c, x, y, w, h = seg_result[i]
            cv2.rectangle(img_input, (x, y), (x + w, y + h), (0, 0, 255))
        cv2.imwrite("result/out/{}.png".format(idx), img_input)

        idx += 1

    pass


# 字体匹配
def match_font(pages_path):
    idx = 0
    for page_path in pages_path:
        img_input = cv2.imread(page_path, cv2.IMREAD_GRAYSCALE)
        _, img = cv2.threshold(img_input, 0, 255, cv2.THRESH_OTSU)  # 将一幅灰度图二值化 input-one channel
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV)

        with open('result/split/{}.txt'.format(idx), 'r') as f:
            split_result = json.loads(f.read())

        watermark_info = []
        with open('result/extract/{}.txt'.format(idx), 'w') as f:
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

                if idx <= 7:
                    para = 0
                elif idx <= 15:
                    para = 1
                elif idx <= 23:
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


# 主函数
def main():
    # creat_pages()
    file_list = get_pages_path()
    # split_pages(file_list)
    # match_font(file_list)
    check_error()
    pass


if __name__ == '__main__':
    main()
