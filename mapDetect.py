import cv2
import copy
import numpy as np
import skimage.morphology as sm
from skimage import filters, img_as_ubyte
from detectConfig import *

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

class SubImageProcessor():
    def __init__(self):
        self.num = None
        self.img = None
        self.gray = None
        self.result = None
        self.dilation = None
        self.region = None

    def preprocess(self):
        # edges = filters.sobel(self.gray)
        # edges = img_as_ubyte(edges)
        ret, binary = cv2.threshold(self.gray, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
        binary = 255 - binary
        # if SAVE_IMAGES_TAG:
        #     cv2.imwrite(IMAGE_PATH + str(self.num) + "_binary.png", binary)
        lines = cv2.HoughLinesP(binary, rho=1.0, theta=np.pi/180, threshold=PREPROCESS_THRESHOLD,
                                lines=None, minLineLength=PREPROCESS_MINLINELENGTH,
                                maxLineGap=PREPROCESS_MAXLINEGAP)
        if type(lines) == np.ndarray:
            for line in lines:
                x1, y1, x2, y2 = line[0][0], line[0][1], line[0][2], line[0][3]
                cv2.line(binary, (x1, y1), (x2, y2), 0, PREPROCESS_WIPEWIDTH)
                # cv2.line(self.img, (x1, y1), (x2, y2), (0, 255, 255), 5)
        binary = sm.opening(binary, sm.square(PREPROCESS_FIRSTSQUARE))
        # if SAVE_IMAGES_TAG:
        #     cv2.imwrite(IMAGE_PATH + str(self.num) + "_binary1.png", binary)
        binary = sm.dilation(binary, sm.square(PREPROCESS_FIRSTSQUARE))
        self.dilation = sm.dilation(binary, sm.square(PREPROCESS_SECONDSQUARE))
        # self.dilation = sm.dilation(binary, sm.square(PREPROCESS_FIRSTSQUARE))
        if SAVE_IMAGES_TAG:
            cv2.imwrite(IMAGE_PATH + str(self.num) + ".png", self.img)

    def findTextRegion(self):
        width, height = self.dilation.shape
        bg1 = np.zeros([width, height], np.uint8)
        bg2 = np.zeros([width, height], np.uint8)
        lines = cv2.HoughLinesP(self.dilation, rho=1.0, theta=np.pi / 180, threshold=FINDREGION_THRESHOLD,
                                lines=None, minLineLength=FINDREGION_MINLINELENGTH,
                                maxLineGap=FINDREGION_MAXLINEGAP)
        # print(len(lines))
        if type(lines) == np.ndarray:
            for line in lines:
                x1, y1, x2, y2 = line[0][0], line[0][1], line[0][2], line[0][3]
                if abs(y2 - y1) < SLOPE * abs(x2 - x1):
                    cv2.line(bg1, (x1, y1), (x2, y2), 255, 10)
                elif abs(y2 - y1) > 1 / SLOPE * abs(x2 - x1):
                    cv2.line(bg2, (x1, y1), (x2, y2), 255, 10)
        # bg1 = sm.opening(bg1, sm.square(12))
        # bg2 = sm.opening(bg2, sm.square(12))
        # if SAVE_IMAGES_TAG:
        #     cv2.imwrite(IMAGE_PATH + str(self.num) + "_bg1.png", bg1)
        #     cv2.imwrite(IMAGE_PATH + str(self.num) + "_bg2.png", bg2)
        self.region = []
        _, contours, hierarchy = cv2.findContours(bg1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if area < MIN_AREA or area > MAX_AREA:
                continue
            epsilon = 0.001 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            box = minAreaRect(cnt)
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
            box = minAreaRect(cnt)
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
        # print(len(self.region))
        # for box in self.region:
        #     cv2.drawContours(self.img, [box], 0, (0, 255, 0), 3)
        # if SAVE_IMAGES_TAG:
        #     cv2.imwrite(IMAGE_PATH + str(self.num) + "_result.png", self.img)
        return self.region

class CornerDetector():
    def __init__(self):
        self.img = None
        self.bases = None
        self.areas = None

    def cornerDetect_bk(self):
        height, width = self.img.shape[0:2]
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
        binary = 255 - binary
        _, contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        box = None
        area_max = 0
        for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if area < area_max:
                continue
            area_max = area
            epsilon = 0.001 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            box = minAreaRect(cnt)
            box = np.int0(box)
        return box

    def cornerDetect(self, img):
        self.img = copy.deepcopy(img)
        height, width = self.img.shape[0:2]
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        # edges = filters.sobel(gray)
        # edges = img_as_ubyte(edges)
        # ret, binary = cv2.threshold(edges, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
        ret, binary = cv2.threshold(gray, 10, 255, 1)
        binary = sm.dilation(binary, sm.disk(3))
        _, contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        box = None
        area_max = 0
        for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if area < area_max:
                continue
            area_max = area
            epsilon = 0.001 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            box = minAreaRect(cnt)
            box = np.int0(box)
        ex = 0
        if area_max < 3 / 4 * width * height:
            ex = 350
            box = self.cornerDetect_bk()
        cv2.drawContours(img, [box], 0, (0, 255, 0), 10)
        # cv2.imwrite('test.png', img)
        # quit()
        self.areas = []
        self.bases = []
        self.bases.append((max(0, box[0][1] - SHORT_EXTENSION), max(0, box[0][0] - SHORT_EXTENSION)))
        self.areas.append(self.img[max(0, box[0][1] - SHORT_EXTENSION): min(box[0][1] + LONG_EXTENSION + ex, height),
                                   max(0, box[0][0] - SHORT_EXTENSION): min(box[0][0] + LONG_EXTENSION + ex, width)])
        self.bases.append((max(0, box[1][1] - SHORT_EXTENSION), max(0, box[1][0] - LONG_EXTENSION - ex)))
        self.areas.append(self.img[max(0, box[1][1] - SHORT_EXTENSION): min(box[1][1] + LONG_EXTENSION + ex, height),
                                   max(0, box[1][0] - LONG_EXTENSION - ex): min(box[1][0] + SHORT_EXTENSION, width)])
        self.bases.append((max(0, box[2][1] - LONG_EXTENSION - ex), max(0, box[2][0] - LONG_EXTENSION - ex)))
        self.areas.append(self.img[max(0, box[2][1] - LONG_EXTENSION - ex): min(box[2][1] + SHORT_EXTENSION, height),
                                   max(0, box[2][0] - LONG_EXTENSION - ex): min(box[2][0] + SHORT_EXTENSION, width)])
        self.bases.append((max(0, box[3][1] - LONG_EXTENSION - ex), max(0, box[3][0] - SHORT_EXTENSION)))
        self.areas.append(self.img[max(0, box[3][1] - LONG_EXTENSION - ex): min(box[3][1] + SHORT_EXTENSION, height),
                                   max(0, box[3][0] - SHORT_EXTENSION): min(box[3][0] + LONG_EXTENSION + ex, width)])
        return [self.bases, self.areas]


processor = SubImageProcessor()
detector = CornerDetector()
def getRegionFromSubArea(img, num=''):
    bk = copy.deepcopy(img)
    bases, areas = detector.cornerDetect(img)
    regions = []
    regions_bk = []
    for i in range(len(areas)):
        region = processor.detectSubArea(areas[i], str(num) + '_' + str(i))
        for j in range(len(region)):
            for k in range(len(region[j])):
                region[j][k][0] += bases[i][1]
                region[j][k][1] += bases[i][0]
        regions.extend(region)
        regions_bk.append(region)
    for box in regions:
        cv2.drawContours(bk, [box], 0, (0, 255, 0), 3)
    # if SAVE_IMAGES_TAG:
    #     cv2.imwrite('result/images/' + str(num) + "_result.png", bk)
    print(len(regions))
    return regions_bk

# for i in range(14, 17):
#     name = str(i)
#     if i < 10:
#         name = '0' + str(i)
#     img = cv2.imread(name + ".jpg")
#     region = getRegionFromSubArea(img, i)
#     # quit()
# # img = img[int(img.shape[0]*0):int(img.shape[0]*0.15), int(img.shape[1]* 0.85):int(img.shape[1]* 1)]
