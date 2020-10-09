import pytesseract
import re
import os
import cut_and_detect
import cv2
import numpy as np
global i
import csv

def loadImagePath(foldpath):
    files = os.listdir(foldpath)
    dirpath=[]
    for i in files:
        i=foldpath+'/'+i
        dirpath.append(i)
    print(dirpath)
    return dirpath

def writeInCsv(path,data):
    with open(path,'a',newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(data)
    print("wirte success!")


def image_to_string(image):
    text = pytesseract.image_to_string(image, lang='eng')
    text = text.replace(' ', '')
    #print(text)
    return text

def degreePattern(text):
    pa =  r'[0-9S§]{2,3}[°′″”’\'\"0479]\S{2}[°′″”’\'\"0479]\S{2,3}\d?[°′″’”\'\",，0479][wWENSs§$5]?'
    pattern1 = re.compile(pa)
    match1 = pattern1.findall(text)
    longitude=''
    latitude = ''
    degree=[]
    if match1:
        match1=set(match1)
        print('success:',match1)
        list1=['w','W']
        list2=['E']
        list3=['S','s','$','$','5']
        list4=['N']
        for i in match1:
            if i[-1] in list1 + list2:
                longitude = i
                cut = re.split('°|′|”|’|″|\'|\"',longitude)
                if cut[-1]in list1:
                    longitude = cut[0]+'°'+cut[1]+'′'+cut[2]+'″'+'W'
                else:
                    longitude = cut[0] + '°' + cut[1] + '′' + cut[2] + '″' + 'E'
                degree.append(longitude)
            else:
                latitude=i
                cut = re.split('°|′|”|’|″|\'|\"', latitude)
                if cut[-1] in list3:
                    latitude = cut[0] + '°' + cut[1] + '′' + cut[2] + '″' + 'S'
                else:
                    latitude = cut[0] + '°' + cut[1] + '′' + cut[2] + '″' + 'N'
                degree.append(latitude)
        print(degree)
    else:
        degree.append('nothing')
    return degree

if __name__== '__main__':

    i=0
    foldpath = 'images'
    textpath="result/text1"
    '''
    dirpath = loadImagePath(foldpath)
    for dir in range(len(dirpath)):
        print(str(i)+"is processing")
        image = dirpath[dir]
        img = cv2.imdecode(np.fromfile(image,dtype=np.uint8),-1)
        #img = img[int(img.shape[0]*0):int(img.shape[0]*0.2), int(img.shape[1]* 0.8):int(img.shape[1]* 1)]
        region = cut_and_detect.getRegionFromSubArea(img, i)
        sub_images = []
        for sub_region in region:
            with open(textpath+"/text" + str(i)+".txt", 'a',encoding='utf-8')as f:
                d=10
                if sub_region[0][1]>10:
                    sub_region[0][1]=sub_region[0][1]-d
                if sub_region[0][0]>10:
                    sub_region[0][0]=sub_region[0][0]-d
                sub_image = img[sub_region[0][1]:sub_region[2][1]+d, sub_region[0][0]:sub_region[2][0]+d]
                #sub_image=sub_image.convert('L')
                height, width = sub_region[2][1] - sub_region[0][1], sub_region[2][0] - sub_region[0][0]
                cv2.imshow("img", sub_image)
                cv2.waitKey(100)
                cv2.destroyAllWindows()
                if height>width:
                    sub_image = np.rot90(sub_image, -1)
                    text = image_to_string(sub_image)
                    if len(text) > 9:
                        f.write(text)
                    sub_image = np.rot90(sub_image, 1)
                    text = image_to_string(sub_image)
                    if len(text) > 9:
                        f.write(text)
                else:
                    text = image_to_string(sub_image)
                    if len(text) > 9:
                        f.write(text)
                f.close()
        i=i+1
    '''
    dirpath = loadImagePath(textpath)
    for i in range(len(dirpath)):
        with open(textpath + "/text" + str(i) + ".txt", 'r+', encoding='utf-8')as fp:
            text=fp.read()
            degree = degreePattern(text)
            writeInCsv('data2.csv', degree)
