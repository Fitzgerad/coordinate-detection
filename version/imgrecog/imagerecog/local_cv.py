import cv2
import math
import local_cv
import numpy as np
import matplotlib.pyplot as plt
from skimage import filters, img_as_ubyte

def preFilte(img):
    height, width = img.shape[0:2]
    for i in range(height):
        for j in range(width):
            if max(img[i][j]) > 100:
                img[i][j] = np.array([255, 255, 255], dtype=np.int)
    return img

def Sobel(gray):
    edges = filters.sobel(gray)
    edges = img_as_ubyte(edges)
    ret, binary = cv2.threshold(edges, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
    return binary

def dilate(img, element, iterations):
    height, width = img.shape
    MF = np.array(((0, 1, 0),
                   (1, 0, 1),
                   (0, 1, 0)), dtype=np.int)
    out = img.copy()
    for i in range(iterations):
        tmp = np.pad(out, (1, 1), 'edge')
        for y in range(1, height):
            for x in range(1, width):
                if np.sum(MF * tmp[y-1:y+2, x-1:x+2]) >= 255:
                    out[y, x] = 255
    return out

def erode(img, element, iterations):
    height, width = img.shape
    MF = np.array(((0, 1, 0),
                   (1, 0, 1),
                   (0, 1, 0)), dtype=np.int)
    out = img.copy()
    for i in range(iterations):
        tmp = np.pad(out, (1, 1), 'edge')
        for y in range(1, height):
            for x in range(1, width):
                if np.sum(MF * tmp[y-1:y+2, x-1:x+2]) < 255 * 4:
                    out[y, x] = 0
    return out

def minAreaRect(cnt):
    temp = cnt.T
    x0 = min(temp[0][0])
    x1 = max(temp[0][0])
    y0 = min(temp[1][0])
    y1 = max(temp[1][0])
    x = (x0 + x1) / 2
    y = (y0 + y1) / 2
    width = x1 - x0
    height = y1 - y0

    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))