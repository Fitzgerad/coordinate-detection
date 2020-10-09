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
def preprocess(gray):
    #　sobel = cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize=3)
    edges = local_cv.Sobel(gray)
    dst1 = sm.dilation(edges, sm.square(3))
    dst2 = sm.dilation(dst1, sm.square(3))
    return dst2

def findTextRegion(img):
    region = []
    _, contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for i in range(len(contours)):
        cnt = contours[i]
        area = cv2.contourArea(cnt)
        if area < 1000 or area > 5000:
            continue
        epsilon = 0.001 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        box = local_cv.minAreaRect(cnt)
        box = np.int0(box)
        height = abs(box[0][1] - box[2][1])
        width = abs(box[0][0] - box[2][0])
        ratio = width / height
        if ratio < 4 or ratio > 8:
            if ratio > 1 / 4 or ratio < 1 / 8:
                continue

        region.append(box)
    return region

def detect(img):
    # pre_img = local_cv.preFilte(img)
    # pre_img = cv2.imread('global.png')

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dilation = preprocess(gray)

    # dilation = cv2.imread('dilation.png')
    # dilation = cv2.cvtColor(dilation, cv2.COLOR_BGR2GRAY)
    # region = findTextRegion(dilation)
    region = findTextRegion(dilation)
    print(len(region))

    for box in region:
        cv2.drawContours(img, [box], 0, (0, 255, 0), 1)
    cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    cv2.imshow("img", img)
    cv2.imwrite("img.png", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return region
if __name__== '__main__':
    img = cv2.imread("images/12800.jpg")
    region = detect(img)
    sub_images = []
    for sub_region in region:
        height, width = sub_region[2][1] - sub_region[0][1], sub_region[2][0] - sub_region[0][0]
        sub_image = img[sub_region[0][1]-4:sub_region[2][1]+4, sub_region[0][0]-4:sub_region[2][0]+4]
        if height > width:
            if sub_region[2][1]>5000:
                sub_image = np.rot90(sub_image,-1)
            else:
                sub_image = np.rot90(sub_image, 1)
        text = image_to_string(sub_image)

        cv2.imshow("img", sub_image)
        cv2.waitKey(100)
        cv2.destroyAllWindows()

        degree1 = degreePattern(text)
