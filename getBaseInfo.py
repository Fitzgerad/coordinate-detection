import os
import cv2
import numpy as np

def getBaseInfo():
    npy_path = 'basemap/info.npy'
    img_path = 'basemap/map.jpg'
    if os.path.exists(npy_path):
        return np.load(npy_path)
    else:
        # match = cv2.BFMatcher()
        sift = cv2.xfeatures2d.SIFT_create()
        basemap = cv2.imread(img_path)
        # grapmap = cv2.cvtColor(basemap, cv2.COLOR_BGR2GRAY)
        # del(basemap)
        cv2.imwrite('test.jpg', basemap[3000:4000,5000:6000])
        # kp, des = sift.detectAndCompute(grapmap, None)
        # np.save(npy_path, [kp, des])
        # return [kp, des]

getBaseInfo()