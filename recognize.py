import pytesseract
import re
import os
import cv2
import numpy as np
global i
import readFilePath
import mapDetect
from config import *
from text2excel import *
from openpyxl import load_workbook,Workbook
import xlsxwriter

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
    files = os.listdir(foldpath)
    dirpath = []
    for i in files:
        print(i)
        if i[-4:] == '.jpg':
            dirpath.append(i[:-4])
    return dirpath

def writeTextInexcel(path,data):
    workbook=Workbook()
    worksheet=workbook.active
    worksheet.title='sheet1'
    for row in data:
        worksheet.append(row)
    workbook.save(filename=path)

# def insertimg2excel(imagelists,path):
#     imagesize=(720/4,1280/4)
#     list=['J','K','L','M','N','O','P','Q']
#     wb=load_workbook(path)
#     ws=wb.active
#     for i in range(len(imagelists)):
#         for j in range(len(imagelists[i])):
#             cell=list[j]+str(i+1)
#             ws.add_imge(j, cell)
#     # ws.column_dimensions['J'].width=imagesize[0]*0.14
#
#     # ws.add_imge(img,'A1')
#     #ws.row_dimensions[1].height=imagesize[1]*0.78
#     wb.save(filename=path)


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
    pattern1 = re.compile(pa1)
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

if __name__== '__main__':

    i=0
    dicts=[]
    foldpath = readFilePath.getFilePath(0)
    textpath = 'result/texts/'
    number = loadImagePath2(foldpath)
    # deleteFile(textpath)
    dirpath = loadImagePath(foldpath)
    for dir in range(len(dirpath)):#每张图
        image = dirpath[dir]
        print(image)
        if image[-4:] == '.jpg':
            print('picture'+str(dir+1) + " is processing")
            img = cv2.imdecode(np.fromfile(image,dtype=np.uint8),-1)
            #img = img[int(img.shape[0]*0):int(img.shape[0]*0.2), int(img.shape[1]* 0.8):int(img.shape[1]* 1)]
            region = cut_and_detect.getRegionFromSubArea(img, number[dir])
            #path = textpath + "text" + str(i)+ ".txt"
            all_text = []
            for sub in region:#每个子区域
                texts = ['°′″','°′″']
                for sub_region in sub:#每个矩形框
                        d=0
                        if sub_region[0][1]>d:
                            sub_region[0][1]=sub_region[0][1]-d
                        if sub_region[0][0]>d:
                            sub_region[0][0]=sub_region[0][0]-d
                        sub_image = img[sub_region[0][1]:sub_region[2][1]+d, sub_region[0][0]:sub_region[2][0]+d]
                        height, width = sub_region[2][1] - sub_region[0][1], sub_region[2][0] - sub_region[0][0]
                        # cv2.imshow("img", sub_image)
                        # cv2.waitKey(100)
                        # cv2.destroyAllWindows()
                        if height>width:
                            sub_image1 = np.rot90(sub_image, -1)
                            text = image_to_string(sub_image1)
                            if len(text) > 8:
                                texts[1]=text
                            sub_image2 = np.rot90(sub_image, 1)
                            text = image_to_string(sub_image2)
                            if len(text) > 8:
                                texts[1]=text
                        else:
                            text = image_to_string(sub_image)
                            if len(text) > 8:
                                texts[0]=text
                #         if text!='':
                #             file_path = subimagesPath + str(dir)
                #             if not os.path.exists(file_path):
                #                 os.makedirs(file_path)
                #             cv2.imwrite(os.path.join(file_path, str(k)+ ".png"),sub_image)
                #             imagelist.append(sub_image)
                all_text.append(texts)
            latitude,longtitude='',''
            path1,path2='',''
            if all_text[1][0]!='°′″' or  all_text[1][1] != '°′″'  or  all_text[3][0] != '°′″'  or  all_text[3][1] != '°′″':
                latitude = all_text[3][0] + ',' + all_text[1][0]
                longtitude  = all_text[3][1] + ',' + all_text[1][1]
                path1 = 'file://'+IMAGE_PATH+number[dir]+'_3'+'.png'
                path2 = 'file://'+IMAGE_PATH+number[dir]+'_1'+'.png'
            else:
                latitude = all_text[2][0] + ',' + all_text[2][0]
                longtitude = all_text[0][1] + ',' + all_text[0][1]
                path1 = 'file://'+ IMAGE_PATH + number[dir] + '_2' + '.png'
                path2 = 'file://'+ IMAGE_PATH + number[dir] + '_0' + '.png'
            dict = {'编号': number[dir], '纬度': latitude, '经度':longtitude,'链接1':path1,'链接2':path2}
            print(dict)
            dicts.append(dict)
    insertInfo(dicts)
    sheet.saveSheet(os.path.join(ROOT_PATH, 'test.xlsx'))
    # dirpath = loadImagePath(textpath)
    # for i in range(len(dirpath)):
    #     f = open(dirpath[i], 'r+', encoding='utf-8')
    #     lines=f.readlines()
    #     #print(lines)
    #     #左下右上右下左上
    #     lines=[lines[3],lines[1],lines[2],lines[0]]
    #
    #     dict={'编号':number[i],'left_down':lines[3],'right_up':lines[1],'right_down':lines[2],'left_up':lines[0],}
