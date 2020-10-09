import cv2
import local_cv
import numpy as np
import matplotlib.pyplot as plt
import skimage.morphology as sm
from skimage import data, filters, img_as_ubyte
import pytesseract
import re
import os
from PIL import Image


def image_to_string(image):
    text = pytesseract.image_to_string(image, lang='eng')
    text = text.replace(' ', '')
    print(text)
    return text

def degreePattern(text):
    pa =  r'\d{2,3}[°′″\'\"]\d{2}[°′″\'\"]\d{2}[°′″\'\"][wWENSs§$]'
    pattern1 = re.compile(pa)
    match1 = pattern1.findall(text)
    longitude=''
    latitude = ''
    degree=''
    if match1:
        print('success:',match1)
        list1=['w','W','E']
        for i in match1:
            if i[-1] in list1:
               longitude = i
               cut = re.split('°|′|″|\'|\"',longitude)
               longitude = cut[0]+'°'+cut[1]+'′'+cut[2]+'″'+cut[3]
            else:
               latitude=i
               cut = re.split('°|′|″|\'|\"', latitude)
               latitude = cut[0] + '°' + cut[1] + '′' + cut[2] + '″' + cut[3]
        degree='('+longitude+','+latitude+')'
        print(degree)
    #else:
        #print('no degree finds!')
    return degree

def minAreaRect(cnt):
    temp = cnt.T
    x0 = min(temp[0][0])
    x1 = max(temp[0][0])
    y0 = min(temp[1][0])
    y1 = max(temp[1][0])
    # x = (x0 + x1) / 2
    # y = (y0 + y1) / 2
    # width = x1 - x0
    # height = y1 - y0
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))

def preprocess(gray):
    global img
    edges = filters.sobel(gray)
    edges = img_as_ubyte(edges)
    ret, binary = cv2.threshold(edges, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
    binary = sm.dilation(binary, sm.square(3))
    cv2.imwrite("binary.png", binary)
    lines = cv2.HoughLinesP(binary, rho=1.0, theta=np.pi/180, threshold=100,
                            lines=None, minLineLength=150, maxLineGap=5)
    for line in lines:
        x1, y1, x2, y2 = line[0][0], line[0][1], line[0][2], line[0][3]
        cv2.line(binary, (x1, y1), (x2, y2), 0, 12)
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 255), 5)
    # lines = cv2.HoughLines(binary, rho=1.0, theta=np.pi / 180, threshold=1800)
    # for line in lines:
    #     rho, theta = line[0]
    #     a = np.cos(theta)
    #     b = np.sin(theta)
    #     if (theta < (np.pi / 4.)) or (theta > 3. * np.pi / 4.):
    #         pt1 = (int(rho/a), 0)
    #         pt2 = (int((rho - binary.shape[0] * b) / a), binary.shape[0])
    #     else:
    #         pt1 = (0, int(rho / b))
    #         pt2 = (binary.shape[1], int((rho - binary.shape[1] * a) / b))
    #     cv2.line(binary, pt1, pt2, 0, 13)
    #     cv2.line(img, pt1, pt2, (0, 255, 255), 5)

    # lines = cv2.HoughLinesP(binary, rho=1.0, theta=np.pi / 180, threshold=50,
    #                         lines=None, minLineLength=120, maxLineGap=5)
    # for line in lines:
    #     x1, y1, x2, y2 = line[0][0], line[0][1], line[0][2], line[0][3]
    #     cv2.line(binary, (x1, y1), (x2, y2), 0, 8)
    #     cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 5)

    binary = sm.dilation(binary, sm.square(5))
    binary = sm.dilation(binary, sm.square(6))
    binary = sm.dilation(binary, sm.square(7))
    cv2.imwrite("dilation.png", binary)
    return binary

def findTextRegion(img):
    region = []
    _, contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for i in range(len(contours)):
        cnt = contours[i]
        area = cv2.contourArea(cnt)
        if area < 1000 or area > 25000:
            continue
        epsilon = 0.001 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        box = minAreaRect(cnt)
        box = np.int0(box)
        height = abs(box[0][1] - box[2][1])
        width = abs(box[0][0] - box[2][0])
        ratio = width / height
        if (3 < ratio < 8 or 1/8 < ratio < 1/3) and area < 8000:
            region.append(box)
        elif (1/2 < ratio < 2 and area > 5000):
            region.append(box)
        else:
            continue
    return region

# def findTextRegion(img):
#     width, height = img.shape
#     bg = np.zeros([width, height], np.uint8)
#     lines = cv2.HoughLinesP(img, rho=1.0, theta=np.pi / 180, threshold=100,
#                             lines=None, minLineLength=60, maxLineGap=10)
#     for line in lines:
#         x1, y1, x2, y2 = line[0][0], line[0][1], line[0][2], line[0][3]
#         cv2.line(bg, (x1, y1), (x2, y2), 255, 1)
#     cv2.imwrite("test.png", bg)
#     region = []

def detect(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dilation = preprocess(gray)
    region = findTextRegion(dilation)
    print(len(region))

    for box in region:
        cv2.drawContours(img, [box], 0, (0, 255, 0), 3)
    cv2.imwrite("img.png", img)

    return region

if __name__== '__main__':
    img = cv2.imread("images/900.jpg")
    region = detect(img)
    sub_images = []
    for sub_region in region:
        height, width = sub_region[2][1] - sub_region[0][1], sub_region[2][0] - sub_region[0][0]
        sub_image = img[sub_region[0][1]-2:sub_region[2][1]+2, sub_region[0][0]-2:sub_region[2][0]+2]
        text = image_to_string(sub_image)

        cv2.imshow("img", sub_image)
        cv2.waitKey(100)
        cv2.destroyAllWindows()

        degree1 = degreePattern(text)