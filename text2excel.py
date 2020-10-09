from excelConfiguration import *

class SheetProcessor():
    def __init__(self):
        self.workbook = openpyxl.Workbook()
        self.worksheet = self.workbook.active
        self.genTable()

    def genTable(self):
        self.worksheet.merge_cells(None, 1, 1, 1, COL_NUM)
        setCell(self.worksheet.cell(1, 1), TITLE_INDEX, TITLE_CONTENT)
        for col in range(1, COL_NUM):
            setCell(self.worksheet.cell(1, col + 1), TITLE_INDEX)
        self.worksheet.merge_cells(None, 2, 1, 2, COL_NUM)
        setCell(self.worksheet.cell(2, 1), AUTHORITY_INDEX, AUTHORITY_CONTENT)
        for col in range(1, COL_NUM):
            setCell(self.worksheet.cell(2, col + 1), AUTHORITY_INDEX)

        com_col_head = [cols[0] for cols in COM_COLS]
        for row in range(ROW_NUM):
            self.worksheet.row_dimensions[row + 1].height = ROW_HEIGHTS[row]
        for col in range(COL_NUM):
            self.worksheet.column_dimensions[getColIndex(col)].width = COL_WIDTHS[col]
            if type(COL_TITLES[col]) != list:
                self.worksheet.merge_cells(None, 3, col + 1, 4, col + 1)
                setCell(self.worksheet.cell(3, col + 1), CTITLE_INDEX, COL_TITLES[col])
                setCell(self.worksheet.cell(4, col + 1), CTITLE_INDEX)
            elif col in com_col_head:
                self.worksheet.merge_cells(None, 3, col + 1, 3,
                    COM_COLS[com_col_head.index(col)][1] + 1)
                setCell(self.worksheet.cell(3, col + 1), CTITLE_INDEX, COL_TITLES[col][0])
                setCell(self.worksheet.cell(4, col + 1), CTITLE_INDEX, COL_TITLES[col][1])
            else:
                setCell(self.worksheet.cell(3, col + 1), CTITLE_INDEX)
                setCell(self.worksheet.cell(4, col + 1), CTITLE_INDEX, COL_TITLES[col][1])

    def insertInfo(self, info):
        row_num = self.worksheet.max_row + 1
        info['序号'] = row_num - 4
        for col in range(0, COL_NUM):
            setCell(self.worksheet.cell(row_num, col + 1), TEXT_INDEX)
        for key in info.keys():
            try:
                col = COL_SIM_TITLES.index(key)
                if '链接' not in key:
                    setCell(self.worksheet.cell(row_num, col + 1), TEXT_INDEX, info[key])
                else:
                    setCell(self.worksheet.cell(row_num, col + 1), LINK_INDEX, info[key])
            except:
                return False
        return True


    def saveSheet(self, file_name):
        self.workbook.save(file_name)
        self.workbook.close()

sheet = SheetProcessor()

def insertInfo(info_list):
    for info in info_list:
        sheet.insertInfo(info)
    return True
# img = openpyxl.drawing.image.Image('01.jpg')
# worksheet.add_image(img, 'A1')