import cv2
import numpy as np
from scipy import ndimage

"""
opencv 处理图像
"""

"""
1. 不同空间的色彩转换
计算机视觉中常用的色彩空间: 灰度, BGR, HSV(Hue, Saturation, Value)
灰度: 去除色彩信息将其转换为灰阶, 弧度色彩空间对中间处理特别有效, 比如人脸识别

BGR: 蓝-绿-红色彩空间, 每一个像素点由一个三元数组来表示.

HSV: H是色调, S是饱和度, V是黑暗程度
"""

"""
2. 傅里叶变换
高通滤波器(HPF): 检测图像的某个区域, 然后根据像素与邻近像素的亮度差值来提升该像素的
亮度.

kernel:
[
  [  0,  -0.25,  0  ]
  [-0.25,  1,  -0.25]
  [  0,  -0.25,  0  ]
]

kernel是值一组权重的集合, 它会应用在源图像的每一个区域, 并由此生成目标图像的一个像素.
例如, 大小为7的kernel意味着每个49(7*7)个源图像的像素会产生目标图像的一个像素.

在计算玩中央像素与周围临近像素的亮度差值之和以后, 如果亮度变化很大, 中央像素的亮度就会
增加(反之不会). 即, 如果一个像素比他周围的像素更突出, 就会提升它的亮度
"""


def pass_filter():
    kernel_3 = np.array([[-1, -1, -1],
                         [-1, 8, -1],
                         [-1, -1, -1]])

    kernel_5 = np.array([[-1, -1, -1, -1, -1],
                         [-1, 1, 2, 1, -1],
                         [-1, 2, 4, 2, -1],
                         [-1, 1, 2, 1, -1],
                         [-1, -1, -1, -1, -1]])

    img = cv2.imread("images/female.jpg", 0)

    k3 = ndimage.convolve(img, kernel_3)  # 卷积, numpy只接受一位数组, 因此这里使用ndimage
    k5 = ndimage.convolve(img, kernel_5)

    blurred = cv2.GaussianBlur(img, (11, 11), 0)  # 高斯模糊, 低通滤波器
    g_hpf = img - blurred

    cv2.imshow("3*3", k3)  # k3
    cv2.imshow("5*5", k5)  # k5
    cv2.imshow("g_hpf", g_hpf)  # Gauss
    cv2.waitKey()
    cv2.destroyAllWindows()


"""
低通滤波(LPF): 在像素与周围像素亮度差值小于一个特定值时, 平滑该像素的亮度.
主要用于去噪和模糊化. 比如, 高斯模糊是最常用的模糊滤波器之一, 它是一个削减
高频信号强度的低通滤波器.
"""

"""
3. 边缘检测:
opencv提供的边缘检测滤波函数, Laplacian(), Sobel(), Scharr(). 这些滤波
函数都会将非边缘区域转为黑色, 讲边缘区域转为白色或其他饱和的颜色, 但是这些函数很
容易将噪声错误地识别为边缘. 缓解这个问题的方法是在找到边缘之前对图像进行模糊处理.

opencv提供的模糊滤波函数, blur()[简单的算术平均], mediaBlur() 以及 GaussianBlur()

边缘检测函数和模糊滤波函数的参数很多, 但是总有一个ksize参数, 奇数, 表示滤波核的
宽和高(以像素为单位)

mediaBlur() 去除数字化的视频噪声非常有效, 特别是去除彩色图像的噪声

Laplacian() 会产生明显的边缘线条, 灰度图像也是如此
"""


def stroke_edges(src, dst, blurKsize=7, edgeKsize=5):
    if blurKsize >= 3:
        blurredSrc = cv2.medianBlur(src, blurKsize)
        graySrc = cv2.cvtColor(blurredSrc, cv2.COLOR_BGR2GRAY)
    else:
        graySrc = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    cv2.Laplacian(graySrc, cv2.CV_8U, graySrc, ksize=edgeKsize)
    normalizedInverseAlpha = (1.0 / 255) * (255 - graySrc)  # 归一化处理
    channels = cv2.split(src)

    for channel in channels:
        channel[:] = channel * normalizedInverseAlpha
    cv2.merge(channels, dst)


"""
4. 使用定制内核做卷积
核: 一组权重, 它决定如何通过临近像素点来计算新的像素点. 核也称为卷积矩阵, 它对一个区域的
像素做调和(mix up) 或 卷积运算.

opencv提供filter2D()函数, 它产生一个卷积矩阵.

filter2D(src, ddepth, kernel, dst)
    第二个参数指定目标图像每个通道的位深度(比如, cv2.CV_8U表示每个通道为8位), 如果为负
    值, 则表示目标图像和源图像有同样的位深度
    第三个参数指明核大小,是一个奇数

核矩阵权重加起来为1, 不会改变图像的亮度
核矩阵权重加起来为0, 边缘检测核, 把边缘转为白色, 把非边缘转为黑色

锐化, 边缘检测, 模糊等滤波器都使用了高度对称的核
"""

"""
边缘检测:
Canny()  边缘检测. 高斯滤波器去噪 -> 计算梯度 -> 在边缘上使用NMS(非最大抑制) -> 在检测到的
边缘上使用双阈值去除假阳性 -> 分析所有的边缘及其之间的连接

轮廓检测:
    cv2.threshold(src, thresh, maxval, type) 图像二值化处理
    cv2.findContours(image, mode, method)
        image是输入图像, 输入的图像会被修改
        mode层次类型, cv2.RETR_TREE会得到图像中轮廓的整体层次结果, 以此建立轮廓之间的关系.
        cv2.RETR_EXTERNAL, 只是得到最外面的轮廓
        method轮廓逼近方法

        返回值: 修改后的图像, 图像的轮廓, 层次
    cv2.drawContours(image, contours, contourIdx, color, thickness=None) 轮廓画像
        contours, 轮廓数组
        contourIdx, 要绘制的轮廓数组的, 负数表示绘制全部轮廓
        color, 轮廓颜色
        thickness, 密度
"""


def contour_detected():
    image = cv2.pyrDown(cv2.imread("images/contour.jpg", cv2.IMREAD_UNCHANGED))

    # 二值化处理
    ret, thresh = cv2.threshold(cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY),
                                127, 255, cv2.THRESH_BINARY)

    # 轮廓查找
    _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                              cv2.CHAIN_APPROX_SIMPLE)

    # 轮廓处理
    for c in contours:
        # 计算简单的边界框, 将轮廓信息转换成(x,y)坐标, 并加上矩形的高度和宽度
        x, y, w, h = cv2.boundingRect(c)
        # 画出矩形
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 计算目标的最小矩形区域
        rect = cv2.minAreaRect(c)  # 查找最小矩形
        box = cv2.boxPoints(rect)  # 计算最小矩形的坐标(4个)
        box = np.int0(box)  # 将坐标整数化
        # 画出矩形
        cv2.drawContours(image, [box], 0, (0, 0, 255), 3)

        # 计算目标的最小闭圆区域
        (x, y), radius = cv2.minEnclosingCircle(c)  # 计算最小闭圆的中心坐标和半径
        center = (int(x), int(y))
        radius = int(radius)
        # 画出圆形
        image = cv2.circle(image, center, radius, (0, 255, 0), 2)

    # 轮廓绘画
    cv2.drawContours(image, contours, -1, (255, 0, 0), 1)
    cv2.imshow("c", image)
    cv2.waitKey()
    cv2.destroyAllWindows()


"""
凸轮廓与Douglas-Peucker:
    cv2.approxPolyDP(curve, epsilon, closed) 计算近似的多边形框
        curve, 轮廓
        epsilon, 表示源轮廓周长与近似多边形周长的最大差值(此值越小, 近似多边形与源轮廓越接近)
        closed, 表示这个多边形是否闭合

    epsilon, 使用cv.arcLength(curve, closed)估计

    为了计算凸形状, 需要使用 cv2.convexHull(curve) 处理轮廓

直线和圆检测:
Hough变换是直线和形状检测背后的理论基础
直线检测, 通过HoughLines和HoughLinesP函数完成, HoughLines使用标准的Hough变换, HoughLinesP
使用概率Hough变换.

cv2.HoughLinesP(image, rho, theta, threshold, lines=None, minLineLength=None, maxLineGap=None)
    image, 单通道二值图像(一个经过去噪声并只有边缘的图像比较好).
    rho, theta, 线段的几何表示, 一般分别取1和np.pi/180
    threshold, 阈值, 低于该阈值的直线会被忽略
    minLineLength, 最小直线长度(更短的直线会被删除)
    maxLineGap, 最大线段间隙(一条线段的间隙长度大于这个值会被分成两条分开的线段)

圆检测, 通过HoughCircles函数, 与使用HoughLines函数类似
cv2.HoughCircles(image, method, dp, minDist, circles=None, param1=None, param2=None,
                 minRadius=None, maxRadius=None)
    image, 单通道二值图像
    method, 定义检测图像中圆的方法. 目前唯一实现的方法是cv2.HOUGH_GRADIENT
    dp, 累加器分辨率与图像分辨率的反比. dp获取越大,累加器数组越小. 一般为1
    minDist, 检测到的圆的中心与(x,y)坐标之间的最小距离. 如果minDist太小,
    则可能导致检测到多个相邻的圆. 如果minDist太大,则可能导致很多圆检测不到.

    param1, 用于处理边缘检测的梯度值方法. 一般为100
    param2, cv2.HOUGH_GRADIENT方法的累加器阈值. 阈值越小,检测到的圈子越多. 一般为30
    minRadius, 半径的最小大小(以像素为单位)
    maxRadius, 半径的最大大小(以像素为单位)
"""


def line_detected():
    img = cv2.imread("images/female.jpg")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 120)  # Canny边缘检测滤波器处理过的单通道二值图像
    minLineLength = 20
    maxLineGap = 5

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100,
                            minLineLength=minLineLength,
                            maxLineGap=maxLineGap)

    for x1, y1, x2, y2 in lines[0]:
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.imshow("edges", edges)
    cv2.imshow("lines", img)
    cv2.waitKey()
    cv2.destroyAllWindows()


def circle_detected():
    img = cv2.imread("images/code.png")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    edges = cv2.medianBlur(gray, 11)
    circle_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    cv2.imshow("blur", circle_image)

    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 20,
                               param1=100, param2=30, minRadius=20, maxRadius=60)

    circles = np.uint16(np.around(circles))

    for c in circles[0, :]:
        cv2.circle(img, (c[0], c[1]), c[2], (0, 255, 0), 2)
        cv2.circle(img, (c[0], c[1]), 2, (0, 0, 255), 3)

    cv2.imshow("circle", img)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    circle_detected()
