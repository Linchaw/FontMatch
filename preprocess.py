# conding:utf-8
import cv2
import numpy as np
import math

global img, point1, point2, point_all, imgcache


# 二值化
def threshold(x=60):
    global img
    img_threshold = img
    if len(img_threshold.shape) != 2:
        img_threshold = grayscale(img_threshold)
    ret, dest = cv2.threshold(img_threshold, x, 255, cv2.THRESH_BINARY)
    return dest


# OTSU分块二值化
def OSTU_threshold():
    global img
    block = 16
    OSTU_img = img.copy()
    tx, ty = OSTU_img.shape
    row_new = math.floor(tx / block)
    col_new = math.floor(ty / block)
    new_img = np.zeros((tx, ty), dtype=np.float32)
    for i in range(block):
        for j in range(block):
            rowmin = i * row_new
            colmin = j * col_new
            rowmax = (i + 1) * row_new
            colmax = (j + 1) * col_new
            if rowmax > tx:
                rowmax = tx
            if colmax > ty:
                colmax = ty
            tempimg = OSTU_img[rowmin:rowmax, colmin:colmax]
            ret, binary = cv2.threshold(tempimg, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            new_img[rowmin:rowmax, colmin:colmax] = binary
    return new_img


def grayscale(rgbimg):
    grayimg = cv2.cvtColor(rgbimg, cv2.COLOR_BGR2GRAY)
    return grayimg


# 裁剪
def on_mouse(event, x, y, flags, param):
    global img, point1, point2, imgcache
    img2 = img.copy()

    if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
        point1 = (x, y)
        cv2.circle(img2, point1, 10, (0, 255, 0), 5)
        cv2.imshow('image', img2)

    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):  # 按住左键拖曳
        cv2.rectangle(img2, point1, (x, y), (0, 0, 0), 5)
        cv2.imshow('image', img2)

    elif event == cv2.EVENT_LBUTTONUP:  # 左键释放
        point2 = (x, y)
        cv2.rectangle(img2, point1, point2, (0, 0, 255), 5)
        cv2.imshow('image', img2)
        min_x = min(point1[0], point2[0])
        min_y = min(point1[1], point2[1])
        width = abs(point1[0] - point2[0])
        height = abs(point1[1] - point2[1])
        cut_img = img[min_y:min_y + height, min_x:min_x + width]
        cv2.imshow('image', cut_img)
        img = cut_img


# 矫正
def mouse_hande(event, x, y, flags, param):
    global img, point_all, imgcache
    img3 = img.copy()
    h, w = img3.shape[0:2]
    # cv2.imshow('image', img3)
    if event == cv2.EVENT_LBUTTONDOWN:
        point_all.append((x, y))
        # print(point_all[1][1])qq
    if event == cv2.EVENT_MOUSEMOVE and len(point_all) >= 1 and len(point_all) < 4:
        green = (0, 255, 0)
        if len(point_all) == 1:
            cv2.line(img3, point_all[0], (x, y), green, 7)
        elif len(point_all) == 2:
            cv2.line(img3, point_all[0], point_all[1], green, 7)
            cv2.line(img3, point_all[0], (x, y), green, 7)
            cv2.line(img3, point_all[1], (x, y), green, 7)
        elif len(point_all) == 3:
            cv2.line(img3, point_all[0], point_all[1], green, 7)
            cv2.line(img3, point_all[1], point_all[2], green, 7)
            cv2.line(img3, point_all[0], (x, y), green, 7)
            cv2.line(img3, point_all[2], (x, y), green, 7)

        cv2.imshow('image', img3)

    if len(point_all) == 4 and event == cv2.EVENT_LBUTTONUP:
        x = 0
        y = 0
        temp_point_all = [(0, 0)] * 4
        for point in point_all:
            x += point[0]
            y += point[1]
        center_point = (x / 4, y / 4)
        for point in point_all:
            if point[0] < center_point[0] and point[1] < center_point[1]:
                temp_point_all[0] = point
            elif point[0] < center_point[0] and point[1] > center_point[1]:
                temp_point_all[3] = point
            elif point[0] > center_point[0] and point[1] < center_point[1]:
                temp_point_all[1] = point
            elif point[0] > center_point[0] and point[1] > center_point[1]:
                temp_point_all[2] = point
        point_all = temp_point_all
        Mean_w = (math.hypot(point_all[1][0] - point_all[0][0], point_all[1][1] - point_all[0][1]) + math.hypot(
            point_all[2][0] - point_all[3][0], point_all[2][1] - point_all[3][1])) / 2
        Mean_h = (math.hypot(point_all[3][0] - point_all[0][0], point_all[3][1] - point_all[0][1]) + math.hypot(
            point_all[2][0] - point_all[1][0], point_all[2][1] - point_all[1][1])) / 2
        w = 5000
        h = math.ceil(5000 * Mean_h // Mean_w)
        pts1 = np.float32(
            [(point_all[0][0], point_all[0][1]), (point_all[1][0], point_all[1][1]), (point_all[3][0], point_all[3][1]),
             (point_all[2][0], point_all[2][1])])
        pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])

        M = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(img3, M, (w, h))
        cv2.imshow('image', dst)
        img = dst


def cashi(event, x, y, flags, param):
    global img, radius, imgcache
    img9 = img.copy()
    cv2.imshow('image', img9)
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(img, (x, y), radius, (255, 255, 255), -1)
    if event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
        cv2.circle(img, (x, y), radius, (255, 255, 255), -1)
    elif event == cv2.EVENT_LBUTTONUP:
        cv2.circle(img, (x, y), radius, (255, 255, 255), -1)
    cv2.imshow('image', img9)


# 锐化
def custom_blur_demo():
    global img
    img4 = img.copy()
    img4 = cv2.cvtColor(img4, cv2.COLOR_GRAY2BGR)
    # kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32) #锐化
    # dst = cv2.filter2D(img4, -1, kernel=kernel)
    # cv2.imshow("custom_blur_demo", dst)
    blur_img = cv2.GaussianBlur(img4, (0, 0), 25)
    usm = cv2.addWeighted(img4, 1.5, blur_img, -0.5, 0)
    img4 = cv2.cvtColor(usm, cv2.COLOR_BGR2GRAY)
    return img4


# 加粗
def makefat():
    global img
    img5 = img.copy()
    h, w = img5.shape[0:2]
    # img5 = cv2.resize(img5,(w*2,h*2),interpolation=cv2.INTER_LANCZOS4 )
    return img5


# 变细
def makethin():
    global img
    img6 = img.copy()
    h, w = img6.shape[0:2]
    # img6 = cv2.resize(img6,(w//2,h//2))
    return img6


# 膨胀
def dilate_demo():
    global img
    image = img.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))  # 指定结构元
    dilate_image = cv2.dilate(image, kernel)
    return dilate_image


# 腐蚀
def erode_demo():
    global img
    image = img.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    erode_image = cv2.erode(image, kernel)
    return erode_image


# 旋转校正
def rotate(event, x, y, flags, param):
    global img, point_two
    img10 = img.copy()
    # cv2.imshow("img10", img10)
    if event == cv2.EVENT_LBUTTONDOWN:
        point_two.append((x, y))
    if event == cv2.EVENT_MOUSEMOVE and len(point_two) == 1:
        cv2.line(img10, point_two[0], (x, y), (0, 255, 0), 2)
        cv2.imshow('image', img10)
    if len(point_two) == 2 and event == cv2.EVENT_LBUTTONUP:
        (h, w) = img10.shape[:2]
        (cX, cY) = (w // 2, h // 2)
        angle = math.atan2((y - point_two[0][1]), (x - point_two[0][0]))
        angle = int(angle * 180 / math.pi)
        M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        nW = int((h * sin) + (w * cos))
        nH = h
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY
        rotated = cv2.warpAffine(img10, M, (nW, nH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.imshow("image", rotated)
        img = rotated


# 光照处理，暗部提亮
def Light_treatment(gamma):
    global img
    gamma_corrected = adjust_gamma(img, gamma)
    return gamma_corrected


def adjust_gamma(image, gamma=1, gain=1):
    dtype = image.dtype.type
    scale = float(dtype_limits(image, True)[1] - dtype_limits(image, True)[0])

    out = ((image / scale) ** gamma) * scale * gain
    return dtype(out)


def dtype_limits(image, clip_negative=False):
    _integer_types = (np.byte, np.ubyte,  # 8 bits
                      np.short, np.ushort,  # 16 bits
                      np.intc, np.uintc,  # 16 or 32 or 64 bits
                      np.int_, np.uint,  # 32 or 64 bits
                      np.longlong, np.ulonglong)  # 64 bits
    _integer_ranges = {t: (np.iinfo(t).min, np.iinfo(t).max)
                       for t in _integer_types}
    dtype_range = {np.bool_: (False, True),
                   np.bool8: (False, True),
                   np.float16: (-1, 1),
                   np.float32: (-1, 1),
                   np.float64: (-1, 1)}
    dtype_range.update(_integer_ranges)
    imin, imax = dtype_range[image.dtype.type]
    if clip_negative:
        imin = 0
    return imin, imax


def main():
    global point_all, img, point_two
    path = input('输入图像路径:')
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    h, w = img.shape[0:2]
    img = cv2.resize(img, (5000, h * 5000 // w), interpolation=cv2.INTER_LANCZOS4)
    cv2.namedWindow('image', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.imshow('image', img)

    print(
        '0、二值化 1、中值滤波 2、锐化 3、裁剪 4、矫正 5、加粗 6、变细 7、腐蚀 8、膨胀 9、擦拭 L、光照处理 r、旋转校正 w、OTSU分块二值化 s、保存 o、打开 q、退出')
    print('输入如果是截图的图片，依次经过以下处理可以获得满意效果：0二值化，[可不选：8膨胀，7腐蚀]')
    print('输入如果是扫描的图片，依次经过以下处理可以获得满意效果：0二值化，8膨胀，2锐化，7腐蚀，[可选：1中值滤波]')
    print('需要透视校正的图片，依次经过以下处理可以获得满意效果：4校正，2锐化，0二值化')
    while 1:
        keyvalue = cv2.waitKey(0) & 0xFF
        if keyvalue == ord('0'):
            print("进行自适应二值化")
            _ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU, 0)
            cv2.imshow('image', img)

        if keyvalue == ord('1'):
            print('进行中值滤波：输入3、5或7')
            kenelsize = int(input())
            img = cv2.medianBlur(img, kenelsize)
            cv2.imshow('image', img)

        if keyvalue == ord('2'):
            print('进行锐化')
            img = custom_blur_demo()
            cv2.imshow('image', img)

        if keyvalue == ord('3'):
            print('进行裁剪')
            cv2.setMouseCallback('image', on_mouse)
            # cv2.imshow('image', img)

        if keyvalue == ord('4'):
            point_all = []
            print('进行矫正')
            cv2.setMouseCallback('image', mouse_hande)
            # cv2.imshow('image', img)

        if keyvalue == ord('5'):
            print('加粗，代码还未实现')
            img = makefat()
            cv2.imshow("image", img)

        if keyvalue == ord('6'):
            print('变细，代码还未实现')
            img = makethin()
            cv2.imshow("image", img)

        if keyvalue == ord('7'):
            print('腐蚀')
            img = dilate_demo()
            cv2.imshow("image", img)

        if keyvalue == ord('8'):
            print('膨胀')
            img = erode_demo()
            cv2.imshow("image", img)

        if keyvalue == ord('9'):
            global radius
            print('擦拭')
            radius = int(input('输入橡皮擦半径:'))
            cv2.setMouseCallback('image', cashi)
            # cv2.imshow('image', img)

        if keyvalue == ord('r'):
            point_two = []
            print('旋转校正，画出参考直线')
            cv2.setMouseCallback('image', rotate)
            # cv2.imshow('image', img)

        if keyvalue == ord('L'):
            print('进行gamma校正：输入gamma值（暗部提亮gamma值在0~1，亮部加黑gamma值>1）')
            gamma = float(input())
            img = Light_treatment(gamma)
            cv2.imshow('image', img)

        if keyvalue == ord('w'):
            print('进行OTSU分块二值化')
            img = OSTU_threshold()
            cv2.imshow('image', img)

        if keyvalue == ord('s'):
            print('保存图片')
            cv2.imwrite('./pre_img.png', img)

        if keyvalue == ord('o'):
            print('重新读入图片')
            path = input('输入图像路径:')
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            img5 = img.copy()
            h, w = img.shape[0:2]
            img = cv2.resize(img5, (5000, h * 5000 // w), interpolation=cv2.INTER_LANCZOS4)
            cv2.imshow('image', img)

        if keyvalue == ord('q'):
            print('退出')
            break


if __name__ == '__main__':
    main()
