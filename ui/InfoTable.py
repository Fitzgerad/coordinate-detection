#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ui.MainWindow
import threading
import sys
import recognize
import openpyxl
import xlwt, xlrd, csv
import pandas as pd
import copy

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter, QIcon, QStandardItemModel
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog, QToolBar, QTableWidget, QTableWidgetItem

class myThread (threading.Thread):
    def __init__(self, infoTable):
        threading.Thread.__init__(self)
        self.infoTable = infoTable
        self.fileList = infoTable.mainWindow.fileList
        self.imagePath = []

    def getImages(self, imagePath):
        self.imagePath = copy.deepcopy(imagePath)

    def run(self):
        recognize.main(self.imagePath, self.fileList)
        self.infoTable.open("cache/excel/temp.xls")
        self.infoTable.isFree = True
        self.infoTable.updateActions()
        return

class InfoTable(QTableWidget):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        self.isFree = True
        self.mThread = myThread(self)

        self.setColumnCount(0)
        self.setRowCount(0)

        self.setBackgroundRole(QPalette.Dark)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setVisible(True)

        self.createActions()
        self.createToolBar()

    # TODO
    def open(self, fileName):
        if fileName:
            self.clear()
            df = pd.read_excel(fileName, header=0)  # read file and set header row
            print(2)
            self.header = df.columns.ravel().tolist()
            for i in range(len(self.header)):
                self.header[i] = str(self.header[i])
            self.setColumnCount(len(df.columns))
            self.setRowCount(len(df.index))
            self.setHorizontalHeaderLabels(self.header)
            for i in range(len(df.index)):
                for j in range(len(df.columns)):
                    self.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
            self.resizeColumnsToContents()
            self.resizeRowsToContents()

    # TODO
    def analyse(self):
        imagePath = []
        for i in range(self.mainWindow.fileList.count()):
            imagePath.append(self.mainWindow.fileList.item(i).cpath)
        self.mThread.getImages(imagePath)
        self.mThread.start()
        # self.isFree = False
        # self.updateActions()
        return

    def saveAsExcel(self):
        path = QFileDialog.getSaveFileName(self, '保存文件', 'unnamed', ".xls(*.xls)")
        try:
            filename = path[0]
        except:
            return
        wbk = xlwt.Workbook()
        self.sheet = wbk.add_sheet("sheet", cell_overwrite_ok=True)
        row = 0
        col = 0
        for i in range(self.columnCount()):
            self.sheet.write(0, i, self.header[i])
        for i in range(self.columnCount()):
            for x in range(self.rowCount()):
                try:
                    teext = str(self.item(row, col).text())
                    self.sheet.write(row + 1, col, teext)
                    row += 1
                except AttributeError:
                    row += 1
            row = 0
            col += 1
        wbk.save(filename)

    # TODO
    def saveAsWord(self):
        return

    def saveAsCSV(self):
        path = QFileDialog.getSaveFileName(self, 'Save File', 'unnamed', 'CSV(*.csv)')
        try:
            filename = path[0]
        except:
            return
        with open(filename, 'w', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(self.header)
            for row in range(self.rowCount()):
                rowdata = []
                for column in range(self.columnCount()):
                    item = self.item(row, column)
                    if item is not None:
                        rowdata.append(item.text())
                    else:
                        rowdata.append('')
                writer.writerow(rowdata)

    # TODO: Add Icon
    def createActions(self):
        # QIcon("images/control.png")
        self.analyseAct = self.formatAction("ui/images/run.jpg", "开始\n运行", enabled=False, triggered=self.analyse)
        self.saveAsExcelAct = self.formatAction("ui/images/save.jpg", "另存为\nExcel", enabled=False, triggered=self.saveAsExcel)
        self.saveAsWordAct = self.formatAction("ui/images/save.jpg", "另存为\nWord", enabled=False, triggered=self.saveAsWord)
        self.saveAsCSVAct = self.formatAction("ui/images/save.jpg", "另存为\nCSV", enabled=False, triggered=self.saveAsCSV)

    def formatAction(self, imagePath, text, shortcut=None, enabled=False, triggered=None):
        icon = QPixmap(imagePath)
        action = QAction(QIcon(icon), text, self, triggered=triggered)
        action.setEnabled(enabled)
        return action

    def createToolBar(self):
        self.toolBar = QToolBar()
        self.toolBar.addSeparator()
        self.toolBar.setMovable(False)
        # self.toolBar.addSeparator()
        # self.viewMenu = QMenu("&View", self)
        self.toolBar.addAction(self.analyseAct)
        self.toolBar.addAction(self.saveAsExcelAct)
        self.toolBar.addAction(self.saveAsWordAct)
        self.toolBar.addAction(self.saveAsCSVAct)
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolBar.setIconSize(QSize(40, 40))
        self.mainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

    def updateActions(self):
        self.analyseAct.setEnabled(self.mainWindow.fileList.count() and self.isFree)
        isSaveable = self.verticalHeader().count()
        self.saveAsExcelAct.setEnabled(isSaveable)
        self.saveAsWordAct.setEnabled(isSaveable)
        self.saveAsCSVAct.setEnabled(isSaveable)

    # TODO
    def changeContent(self):
        return