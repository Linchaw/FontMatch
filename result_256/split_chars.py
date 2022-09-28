import cv2  # 版本为3.3.10，安装4.0及以上版本可能会不兼容


# 获取图像的上下左右边界
def get_img_charinfo(image):
    up_pixel = down_pixel = left_pixel = right_pixel = 0
    margin = 5

    projection_row = cv2.reduce(image, 1, cv2.REDUCE_SUM, dtype=cv2.CV_32S)  # projection
    row_num = len(projection_row)  # 3507
    for i in range(row_num):
        if projection_row[i] != 0:
            up_pixel = i - margin
            break
    for j in range(row_num):
        if projection_row[row_num - j - 1] != 0:
            down_pixel = row_num - j - 1 + margin
            break

    projection_column = cv2.reduce(image, 0, cv2.REDUCE_SUM, dtype=cv2.CV_32S)
    projection_colu = projection_column[0]  #
    colu_num = len(projection_colu)  # 2480
    for i in range(colu_num):
        if projection_colu[i] != 0:
            left_pixel = i - margin
            break
    for i in range(colu_num):
        if projection_colu[colu_num - i - 1]:
            right_pixel = colu_num - i - 1 + margin
            break

    return up_pixel, down_pixel, left_pixel, right_pixel


# 返回分割结果
def get_seg_box(image, row_chars_num=28, column_chars_num=16):

    char_pixel = 100  # 定义汉字的最小像素尺寸

    up_pixel, down_pixel, left_pixel, right_pixel = get_img_charinfo(image)

    row_list_avg = (down_pixel - up_pixel) / row_chars_num
    clu_list_avg = (right_pixel - left_pixel) / column_chars_num

    if row_list_avg <= char_pixel or clu_list_avg <= char_pixel:
        return None

    row_list_list = []
    clu_list_list = []
    for i in range(row_chars_num):
        row_list_list.append(int(up_pixel + i * row_list_avg))
    for i in range(column_chars_num):
        clu_list_list.append(int(left_pixel + i * clu_list_avg))
    # print(row_list_list, clu_list_list)

    seg_box = []
    for i in row_list_list:
        contour_row_new = []
        for j in clu_list_list:
            contour_row_new.append((j, i, int(row_list_avg), int(clu_list_avg)))
        seg_box.append(contour_row_new)
    return seg_box


# 返回分割结果带字符信息
def get_seg_result(chars, boxes):
    seg_result = []
    # 在boxes 中 添加 char 的信息
    for i in range(len(chars)):
        for j in range(len(chars[i])):
            x, y, w, h = boxes[i][j]
            ch = chars[i][j]
            seg_result.append((ch, x, y, w, h))

    return seg_result


# 返回分割结果带字符信息
def get_seg_result2(image, chars):
    seg_result = []
    chars_num = []
    for i in range(len(chars)):
        if chars[i] == '':
            break
        chars_num.append(len(chars[i]))
    # print(chars_num) [16, 16, 12]

    char_pixel = 100
    up_pixel, down_pixel, left_pixel, right_pixel = get_img_charinfo(image)

    row_list_avg = (down_pixel - up_pixel) / len(chars_num)
    clu_list_avg = (right_pixel - left_pixel) / max(chars_num)

    if row_list_avg <= char_pixel or clu_list_avg <= char_pixel:
        return None

    seg_box = []

    for i in range(len(chars)):
        temp = []
        for j in range(len(chars[i])):
            y = int(up_pixel + i * row_list_avg)
            x = int(left_pixel + j * clu_list_avg)
            temp.append((x, y, int(clu_list_avg), int(row_list_avg)))
        seg_box.append(temp)

    seg_result = get_seg_result(chars, seg_box)

    return seg_result


def main():

    pass


if __name__ == '__main__':
    main()