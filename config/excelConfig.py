import time
import openpyxl.styles
BASE = 1.08

BORDERS_NONE = 0
BORDERS_ALL = 1

def getFont(font_size, font_name,
            font_color = '000000',
            font_line = 'none'):
    font = openpyxl.styles.Font()
    font.size = font_size
    font.name = font_name
    font.color = font_color
    font.underline = font_line
    return font

def getAlignment(alignment_horz, alignment_vert,
                 alignment_wrap):
    alignment = openpyxl.styles.Alignment()
    alignment.horizontal = alignment_horz
    alignment.vertical = alignment_vert
    alignment.wrap_text = alignment_wrap
    return alignment

def getBorder(border_style = BORDERS_NONE):
    side = openpyxl.styles.Side()
    side.border_style = None
    if border_style != BORDERS_NONE:
        side.border_style = 'thin'
    border = openpyxl.styles.Border()
    border.left = border.right = \
        border.top = border.bottom = side
    return border

def getColIndex(i):
    return chr(ord('A') + i)

def setCell(cell, style_index, content=None):
    cell.font = ALL_STYLES[style_index][0]
    cell.alignment = ALL_STYLES[style_index][1]
    cell.border = ALL_STYLES[style_index][2]
    if content != None:
        if style_index != LINK_INDEX:
            cell.value = content
        else:
            cell.value = '=HYPERLINK("{}", "{}")'.\
                format(content, '图像链接')

# TITLE_INDEX = 0
# TITLE_FONT_SIZE = 9
# TITLE_FONT_NAME = u'方正小标宋简体'
# TITLE_ALIGNMENT_HORZ = 'center'
# TITLE_ALIGNMENT_VERT = 'bottom'
# TITLE_ALIGNMENT_WRAP = True
# TITLE_CONTENT = '地图资料目录（更新至{}年{}月）'.\
#     format(time.localtime(time.time()).tm_year,
#            time.localtime(time.time()).tm_mon)
#
# AUTHORITY_INDEX = 1
# AUTHORITY_FONT_SIZE = 9
# AUTHORITY_FONT_NAME = u'方正小标宋简体'
# AUTHORITY_ALIGNMENT_HORZ = 'right'
# AUTHORITY_ALIGNMENT_VERT = 'bottom'
# AUTHORITY_ALIGNMENT_WRAP = True
# AUTHORITY_CONTENT = '制作单位：军委联合参谋部情报分析中心'

CTITLE_INDEX = 0
CTITLE_FONT_SIZE = 9
CTITLE_FONT_NAME = u'黑体'
CTITLE_ALIGNMENT_HORZ = 'center'
CTITLE_ALIGNMENT_VERT = 'center'
CTITLE_ALIGNMENT_WRAP = True

TEXT_INDEX = 1
TEXT_FONT_SIZE = 9
TEXT_FONT_NAME = u'仿宋_GB2312'
TEXT_ALIGNMENT_HORZ = 'left'
TEXT_ALIGNMENT_VERT = 'center'
TEXT_ALIGNMENT_WRAP = True

LINK_INDEX = 2
LINK_FONT_SIZE = 9
LINK_FONT_COLOR = '00AAAA'
LINK_FONT_UNDERLINE = 'single'
LINK_FONT_NAME = u'仿宋_GB2312'
LINK_ALIGNMENT_HORZ = 'left'
LINK_ALIGNMENT_VERT = 'center'
LINK_ALIGNMENT_WRAP = False

ALL_STYLES = []
# ALL_STYLES.append([getFont(TITLE_FONT_SIZE, TITLE_FONT_NAME),
#                    getAlignment(TITLE_ALIGNMENT_HORZ,
#                                 TITLE_ALIGNMENT_VERT,
#                                 TITLE_ALIGNMENT_WRAP),
#                    getBorder(BORDERS_NONE)])
# ALL_STYLES.append([getFont(AUTHORITY_FONT_SIZE, AUTHORITY_FONT_NAME),
#                    getAlignment(AUTHORITY_ALIGNMENT_HORZ,
#                                 AUTHORITY_ALIGNMENT_VERT,
#                                 AUTHORITY_ALIGNMENT_WRAP,),
#                    getBorder(BORDERS_NONE)])
ALL_STYLES.append([getFont(CTITLE_FONT_SIZE, CTITLE_FONT_NAME),
                   getAlignment(CTITLE_ALIGNMENT_HORZ,
                                CTITLE_ALIGNMENT_VERT,
                                CTITLE_ALIGNMENT_WRAP),
                   getBorder(BORDERS_ALL)])
ALL_STYLES.append([getFont(TEXT_FONT_SIZE, TEXT_FONT_NAME),
                   getAlignment(TEXT_ALIGNMENT_HORZ,
                                TEXT_ALIGNMENT_VERT,
                                TEXT_ALIGNMENT_WRAP),
                   getBorder(BORDERS_ALL)])
ALL_STYLES.append([getFont(LINK_FONT_SIZE, LINK_FONT_NAME,
                           LINK_FONT_COLOR, LINK_FONT_UNDERLINE),
                   getAlignment(LINK_ALIGNMENT_HORZ,
                                LINK_ALIGNMENT_VERT,
                                LINK_ALIGNMENT_WRAP),
                   getBorder(BORDERS_ALL)])

ROW_HEIGHTS = [14.4]
ROW_NUM = len(ROW_HEIGHTS)
COL_TITLES = ['编号', '类型', '左上坐标', '右上坐标',
              '左下坐标', '右下坐标']
COL_NUM = len(COL_TITLES)
COL_SIM_TITLES = []
COM_COLS = []
i = 0
while i < COL_NUM:
    if type(COL_TITLES[i]) == list:
        name = COL_TITLES[i][0]
        temp = [i]
        while i < COL_NUM and type(COL_TITLES[i]) == list\
                and COL_TITLES[i][0] == name:
            COL_SIM_TITLES.append(COL_TITLES[i][1])
            i += 1
        temp.append(i-1)
        COM_COLS.append(temp)
    else:
        COL_SIM_TITLES.append(COL_TITLES[i])
        i += 1