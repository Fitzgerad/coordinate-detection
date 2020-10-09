#coding=utf-8
import pytesseract
from PIL import Image
import cv2
import numpy as np
from copy import deepcopy

STATE_NONE = 0
STATE_PRESSED = 1
QUIT_KEY = [13, 27, ord('q')]

class MapProcessor:
    def __init__(self):
        self.image = None
        self.bk_image = None
        self.corners = None
        # This part is designed for manually grabbing
        self.initCut()

    def loadImage(self, dir):
        self.image=cv2.imdecode(np.fromfile(dir,dtype=np.uint8),-1)
        #self.image = cv2.imread(cv_img)
        self.bk_image = deepcopy(self.image)

    def initCut(self):
        self.state = STATE_NONE
        self.x0 = -1
        self.y0 = -1
        self.x1 = -1
        self.y1 = -1

    def cutSubImage(self):
        self.initCut()
        cv2.namedWindow("raw_img", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('raw_img', self.drawRectangle)
        while (1):
            cv2.imshow("raw_img", self.image)
            k = cv2.waitKey(1) & 0xFF
            if k in QUIT_KEY:
                break
        cv2.destroyAllWindows()
        self.image = deepcopy(self.bk_image)
        return self.getSubImage()

    def drawRectangle(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.state = STATE_PRESSED
            self.x0 = x
            self.y0 = y
        elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
            if self.state == STATE_PRESSED:
                self.x1 = x
                self.y1 = y
                self.image = deepcopy(self.bk_image)
                cv2.rectangle(self.image, (self.x0, self.y0), (x, y), (0, 255, 0), 10)
            elif event == cv2.EVENT_LBUTTONUP:
                self.state = STATE_NONE

    def getSubImage(self):
        if self.y0 > self.y1:
            self.y0, self.y1 = self.y1, self.y0
        if self.x0 > self.x1:
            self.x0, self.x1 = self.x1, self.x0
        if self.x0 == -1:
            return None
        sub_image = self.image[self.y0:self.y1, self.x0:self.x1]
        #cv2.namedWindow("img", cv2.WINDOW_NORMAL)
        #cv2.imshow("img", sub_image)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        return sub_image

    # TODO
    def detectCorner(self):
        if self.image != None:
            return True
        else:
            return False

    # TODO
    def stretchXtitude(self):
        if self.corners != None:
            return True
        else:
            return False
