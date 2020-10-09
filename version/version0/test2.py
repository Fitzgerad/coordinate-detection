#coding=utf-8
import pytesseract
from PIL import Image
import test

import re
import os
import csv
import modules


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
    else:
        print('no degree finds!')
    return degree

def scalePattern(text):
    pa = r'[ESCALescal]{5,6}\d:[\d\.]+'
    pattern1 = re.compile(pa)
    match1 = pattern1.findall(text)
    scale = ''
    if match1:
        cutIndex = match1[0].index('1')
        scale= match1[0][cutIndex:]
        print(scale)
    else:
        print('no scale finds!')
    return scale

def numberPattern(text):
    pa = r'[A-Za-z0-9\.-]+'
    pattern1 = re.compile(pa)
    match1 = pattern1.findall(text)
    number = ''
    if match1:
        number = match1[0]
        print(number)
    else:
        print('no number finds!')
    return number

def titlePattern(text):
    title=text
    return title

def loadImagePath(foldpath):
    files = os.listdir(foldpath)
    dirpath=[]
    for i in files:
        i=foldpath+'/'+i
        dirpath.append(i)
    print(dirpath)
    return dirpath

def writeInCsv(path,content):
    headers=['number','degree1','degree2','scale']
    with open(path,'w') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)
        f_csv.writerows(content)
    print("wirte success!")


if __name__== '__main__':
    for i in range(len(modules.sub_images)):
        print(i)
        text = image_to_string(modules.sub_images[i])
        degree1 = degreePattern(text)




