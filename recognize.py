import pytesseract
import re
import os
import cv2
import numpy as np
global i
import mapDetect
import traceback
from detectConfig import *
from text2excel import *
from openpyxl import load_workbook,Workbook
def deleteFile(path):
    if not os.path.exists(path):
        os.makedirs(path)
    for i in os.listdir(path):
        pathFile = os.path.join(path,i)
        if os.path.isfile(pathFile):
            os.remove(pathFile)
        else:
            for f in os.listdir(pathFile):
                pathFile2 = os.path.join(pathFile,f)
                if os.path.isfile(pathFile2):
                    os.remove(pathFile2)

def loadImagePath(foldpath):
    files = os.listdir(foldpath)
    dirpath=[]
    for i in files:
        i=foldpath+'/'+i
        dirpath.append(i)
    return dirpath

def loadImagePath2(foldpath):
    dirpath = []
    for i in foldpath:
        if True:
            j=i.rfind('\\')
            dirpath.append(i[j+1:-4])
    return dirpath

def writeTextInexcel(path,data):
    workbook=Workbook()
    worksheet=workbook.active
    worksheet.title='sheet1'
    for row in data:
        worksheet.append(row)
    workbook.save(filename=path)

def image_to_string(image):
    text = pytesseract.image_to_string(image, lang='eng')
    text = text.replace(' ', '')
    text = text.replace('\n','')
    pattern=r'[0-9°′″”’,.\'\"wWENSs§$]{6,13}'
    pattern=re.compile(pattern)
    match = pattern.findall(text)
    if match:
        #print(match)
        if not '°' in match[0]:
            text = ''
        else:
            text =match[0]+' '
    else:
        text=''
    return text

def degreePattern(text):
    degree = []
    d = []
    if text==None:
        degree.append('nothing')
        return degree
    pa1 =  r'[0-9S§]{2,3}[°′″”’\'\"0479]\S{2}[°′″”’\'\"0479]\S{2,3}\d?[°′″’”\'\",，0479][wWENSs§$5]?'
    pa2 = r'[0-9S§]{2,3}[°′″”’\'\"0479]\S{2}[°′″”’\'\"0479][wWENSs§$5]'
    pattern1 = re.compileim(pa1)
    match1 = pattern1.findall(text)
    pattern2=re.compile(pa2)
    match2 = pattern2.findall(text)
    if match1:
        match1=set(match1)
        #print('success:',match1)
        list=['w','W','E','S','s','$','§','5','N']
        list0 = ['°','′','″','’','”','\'','\"','7']
        list1 = [',','，','.']
        for i in match1:
            if len(i)==10 and i[-1]in list:
                newi=i[:2]+'°'+i[3:5]+'′'+i[6:8]+'″'+i[-1]
                degree.append(newi)
            elif len(i)==11 and i[-1]in list and i[-3] not in list0:
                newi = i[:3] + '°' + i[4:6] + '′' + i[7:9] + '″' + i[-1]
                degree.append(newi)
            elif len(i)==12 and i[-4] in list1:
                newi =i[:2]+'°'+i[3:5]+'′'+i[6:8]+'.'+i[9]+'″'+i[-1]
                degree.append(newi)
            elif len(i)==13 and i[-4] in list1:
                newi =i[:3]+'°'+i[4:6]+'′'+i[7:9]+'.'+i[10]+'″'+i[-1]
                degree.append(newi)
            else:
                d.append(i)
                degree.append(i)
        print('1',d)
    elif match2:
        match2 = set(match2)
        list = ['w', 'W', 'E', 'S', 's', '$', '§', '5', 'N']
        list0 = ['°', '′', '″', '’', '”', '\'', '\"', '7']
        for i in match2:
            if len(i)==7 and i[-1]in list:
                newi=i[:2]+'°'+i[3:5]+'′'+i[-1]
                degree.append(newi)
            elif len(i)==8 and i[-1]in list:
                newi = i[:3] + '°' + i[4:6] + '′' +i[-1]
                degree.append(newi)
            else:
                d.append(i)
                degree.append(i)
        print('2',d)
    else:
        degree.append('nothing')
    return degree

def getAllCoor(all_text):
    if len(all_text[0][0]) >= len(all_text[3][0]):
        left=all_text[0][0]
    else:
        left = all_text[3][0]

    if len(all_text[1][0]) >= len(all_text[2][0]):
        right = all_text[1][0]
    else:
        right = all_text[2][0]

    if len(all_text[0][1]) >= len(all_text[1][1]):
        up = all_text[0][1]
    else:
        up = all_text[1][1]

    if len(all_text[2][1]) >= len(all_text[3][1]):
        down = all_text[2][1]
    else:
        down = all_text[3][1]
    upleft = left + ',' + up
    upright = right + ',' + up
    downleft = left + ',' + down
    downright = right + ',' + down
    coorlist = [upleft, upright, downleft, downright]
    return coorlist

def main(list_image_path, xSingal, pSignal, eSignal):
    i=0
    dicts=[]
    image=[]
    for num in range(len(list_image_path)):#每张图
        try:
            image = list_image_path[num]
            img = cv2.imdecode(np.fromfile(image,dtype=np.uint8),-1)
            region = mapDetect.getRegionFromSubArea(img, str(num), pSignal)
            all_text = []
            for sub in range(len(region)):#每个子区域
                texts = ['°′″','°′″']
                for sub_region in region[sub]:#每个矩形框
                        d=0
                        if sub_region[0][1]>d:
                            sub_region[0][1]=sub_region[0][1]-d
                        if sub_region[0][0]>d:
                            sub_region[0][0]=sub_region[0][0]-d
                        sub_image = img[sub_region[0][1]:sub_region[2][1]+d, sub_region[0][0]:sub_region[2][0]+d]
                        height, width = sub_region[2][1] - sub_region[0][1], sub_region[2][0] - sub_region[0][0]
                        if height>width:
                            if sub==0 or sub == 2:
                                sub_image1 = np.rot90(sub_image, -1)
                                text = image_to_string(sub_image1)
                                if len(text) !=0:
                                    texts[0]=text
                            else:
                                sub_image2 = np.rot90(sub_image, 1)
                                text = image_to_string(sub_image2)
                                if len(text) !=0:
                                    texts[0]=text
                        else:
                            text = image_to_string(sub_image)
                            if len(text) !=0:
                                texts[1]=text
                all_text.append(texts)
                pSignal.emit(int(num), 10)
            coorlist = getAllCoor(all_text)
            print('最终坐标：',coorlist)
            dict = {'编号': ' ', '类型': '海图','左上坐标':coorlist[0], '右上坐标':coorlist[1],
              '左下坐标':coorlist[2], '右下坐标':coorlist[3]}
            dicts.append(dict)
        except Exception as e:
            # 这个是输出错误的具体原因，这步可以不用加str，输出
            print('str(e):\t\t', str(e))  # 输出 str(e):		integer division or modulo by zero
            print('repr(e):\t', repr(e))  # 输出 repr(e):	ZeroDivisionError('integer division or modulo by zero',)
            print('traceback.print_exc():')
            # 以下两步都是输出错误的具体位置的
            traceback.print_exc()
            # print('traceback.format_exc():\n%s' % traceback.format_exc())

            dict = {'类型': '海图', '左上坐标': ' ', '右上坐标': ' ',
                    '左下坐标': ' ', '右下坐标': ' '}
            dicts.append(dict)
            xSingal.emit(int(num))
        print(num)
    insertInfo(dicts)
    sheet.saveSheet(appConfig.ds.tempExcelFile)
    eSignal.emit("cache/excel/temp.xls")

