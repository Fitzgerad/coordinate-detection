import cv2
import copy
import numpy as np
import matplotlib.pyplot as plt
import skimage.morphology as sm
from skimage import filters, img_as_ubyte
from config import *

class SubImageProcessor():
    def __init__(self):
        self.num = None
        self.img = None
        self.gray = None
        self.result = None
        self.dilation = None
        self.region = None

    def minAreaRect(self, cnt):
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

    def preprocess(self):
        edges = filters.sobel(self.gray)
        edges = img_as_ubyte(edges)
        ret, binary = cv2.threshold(edges, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
        lines = cv2.HoughLinesP(binary, rho=1.0, theta=np.pi/180, threshold=PREPROCESS_THRESHOLD,
                lines=None, minLineLength=PREPROCESS_MINLINELENGTH, maxLineGap=PREPROCESS_MAXLINEGAP)
        for line in lines:
            x1, y1, x2, y2 = line[0][0], line[0][1], line[0][2], line[0][3]
            cv2.line(binary, (x1, y1), (x2, y2), 0, PREPROCESS_WIPEWIDTH)
            cv2.line(self.img, (x1, y1), (x2, y2), (0, 255, 255), PREPROCESS_WIPEWIDTH)
        # if SAVE_IMAGES_TAG:
        #     cv2.imwrite(IMAGE_PATH + str(self.num) + "_binary.png", binary)
        binary = sm.dilation(binary, sm.square(PREPROCESS_FIRSTSQUARE))
        self.dilation = sm.dilation(binary, sm.square(PREPROCESS_SECONDSQUARE))
        # if SAVE_IMAGES_TAG:
        #     cv2.imwrite(IMAGE_PATH + str(self.num) + "_dilation.png", self.dilation)

    def findTextRegion(self):
        width, height = self.dilation.shape
        bg1 = np.zeros([width, height], np.uint8)
        bg2 = np.zeros([width, height], np.uint8)
        lines = cv2.HoughLinesP(self.dilation, rho=1.0, theta=np.pi / 180, threshold=FINDREGION_THRESHOLD,
                lines=None, minLineLength=FINDREGION_MINLINELENGTH, maxLineGap=FINDREGION_MAXLINEGAP)
        print(len(lines))
        for line in lines:
            x1, y1, x2, y2 = line[0][0], line[0][1], line[0][2], line[0][3]
            if abs(y2 - y1) < SLOPE * abs(x2 - x1):
                cv2.line(bg1, (x1, y1), (x2, y2), 255, 10)
            elif abs(y2 - y1) > 1 / SLOPE * abs(x2 - x1):
                cv2.line(bg2, (x1, y1), (x2, y2), 255, 10)
        #if SAVE_IMAGES_TAG:
        #    cv2.imwrite(IMAGE_PATH + str(self.num) + "_bg1.png", bg1)
        #    cv2.imwrite(IMAGE_PATH + str(self.num) + "_bg2.png", bg2)
        self.region = []
        _, contours, hierarchy = cv2.findContours(bg1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if area < MIN_AREA or area > MAX_AREA:
                continue
            epsilon = 0.001 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            box = self.minAreaRect(cnt)
            box = np.int0(box)
            height = abs(box[0][1] - box[2][1])
            width = abs(box[0][0] - box[2][0])
            ratio = width / height
            if (MIN_RATIO < ratio < MAX_RATIO):
                self.region.append(box)
            else:
                continue
        _, contours, hierarchy = cv2.findContours(bg2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if area < MIN_AREA or area > MAX_AREA:
                continue
            epsilon = 0.001 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            box = self.minAreaRect(cnt)
            box = np.int0(box)
            height = abs(box[0][1] - box[2][1])
            width = abs(box[0][0] - box[2][0])
            ratio = width / height
            if (1 / MAX_RATIO < ratio < 1 / MIN_RATIO):
                self.region.append(box)
            else:
                continue

    def detectSubArea(self, img, num=''):
        self.num = num
        self.img = copy.deepcopy(img)
        self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.preprocess()
        self.findTextRegion()
        print(len(self.region))
        for box in self.region:
            cv2.drawContours(self.img, [box], 0, (0, 255, 0), 3)
        if SAVE_IMAGES_TAG:
            cv2.imwrite(IMAGE_PATH + str(self.num) + "_result.png", self.img)
        return self.region

processor = SubImageProcessor()

def getRegionFromSubArea(img, num=''):
    region = processor.detectSubArea(img, num)
    return region


