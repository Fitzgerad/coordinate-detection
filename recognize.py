import pytesseract
import re
import os
import cv2
import numpy as np
global i
import appConfig
import mapDetect
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
        # print(i)
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

#if __name__== '__main__':
def main(list_image_path, widget_file_list):
    i=0
    dicts=[]
    # foldpath = readFilePath.getFilePath(0)
    # number = loadImagePath2(list_image_path)
    # dirpath = loadImagePath(foldpath)
    # dirpath = list
    for num in range(len(list_image_path)):#每张图
        try:
            image = list_image_path[num]
            img = cv2.imdecode(np.fromfile(image,dtype=np.uint8),-1)
            region = mapDetect.getRegionFromSubArea(img, str(num), widget_file_list)
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
                all_text.append(texts)
            left,up,right,down= '','','',''
            path1,path2,path3,path4='','','',''
            if all_text[1][0]!='°′″' or  all_text[1][1] != '°′″'  or  all_text[3][0] != '°′″'  or  all_text[3][1] != '°′″':
                left=all_text[3][1]
                right=all_text[1][1]
                up=all_text[1][0]
                down=all_text[3][0]
            else:
                left = all_text[0][1]
                right = all_text[2][1]
                up = all_text[0][0]
                down = all_text[2][0]
            upleft = left + ',' + up
            upright = right + ',' + up
            downleft = left + ',' + down
            downright = right + ',' + down
            path0 = '../img/' + str(num) + '_0' + '.png'
            path1 = '../img/' + str(num) + '_1' + '.png'
            path2 = '../img/' + str(num) + '_2' + '.png'
            path3 = '../img/' + str(num) + '_3' + '.png'
            # dict = {'编号': number[dir], '纬度': latitude, '经度':longtitude,'链接1':path1,'链接2':path2}
            dict = {'类型': '海图','左上坐标':upleft, '右上坐标':upright,
              '左下坐标':downleft, '右下坐标':downright, '左上链接':path0,
              '右上链接':path1, '左下链接':path2, '右下链接':path3}
            dicts.append(dict)
            widget_file_list.item(num).update(20)
        except:

            dict = {'类型': '海图', '左上坐标': '', '右上坐标': '',
                    '左下坐标': '', '右下坐标': '', '左上链接': '',
                    '右上链接': '', '左下链接': '', '右下链接': ''}
            dicts.append(dict)
            widget_file_list.item(num).error()
        print(num)
    insertInfo(dicts)
    sheet.saveSheet(appConfig.ds.tempExcelFile)

