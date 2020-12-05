#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ui.MainWindow
import sys
import recognize
import openpyxl
import xlwt, xlrd, csv
import pandas as pd
import copy
import os

from PyQt5.QtCore import Qt, QSize, QThread, QMutex, QWaitCondition, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter, QIcon, QStandardItemModel
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog, QToolBar, QTableWidget, QTableWidgetItem

class Analyser(QObject):
    startSignal = pyqtSignal()
    progressSignal = pyqtSignal(int, int)
    errorSignal = pyqtSignal(int)
    excelSignal = pyqtSignal(str)

    def __init__(self, infoTable):
        QObject.__init__(self)
        self.infoTable = infoTable
        self.fileList = infoTable.mainWindow.fileList
        self.imagePath = []

    def getImages(self, imagePath):
        self.imagePath = copy.deepcopy(imagePath)

    def analyse(self):
        recognize.main(self.imagePath, self.fileList,
                       self.progressSignal, self.excelSignal)
        self.infoTable.isFree = True
        self.infoTable.updateActions()
        return


# class MyThread (QThread):
#     def __init__(self, infoTable):
#         # super.__init__(self, daemon=True)
#         super().__init__()
#         self.mutex = QMutex()
#         self.condition = QWaitCondition()
#         self.infoTable = infoTable
#         self.fileList = infoTable.mainWindow.fileList
#         self.imagePath = []
#
#     def getImages(self, imagePath):
#         self.imagePath = copy.deepcopy(imagePath)
#
#     def run(self):
#         self.mutex.lock()
#         recognize.main(self.imagePath, self.fileList)
#         self.mutex.unlock()
#         self.infoTable.open("cache/excel/temp.xls")
#         self.infoTable.isFree = True
#         self.infoTable.updateActions()
#         return

class InfoTable(QTableWidget):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        self.isFree = True
        self.mThread = QThread()
        self.analyser = Analyser(self)
        self.analyser.moveToThread(self.mThread)
        self.analyser.startSignal.connect(self.analyser.analyse)
        self.analyser.progressSignal.connect(self.analyser.fileList.update)
        self.analyser.excelSignal.connect(self.analyser.infoTable.open)
        self.analyser.errorSignal.connect(self.analyser.fileList.error)
        # self.mThread.started.connect(self.analyser.analyse)

        self.setColumnCount(0)
        self.setRowCount(0)

        self.setBackgroundRole(QPalette.Dark)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setVisible(True)

        self.createActions()
        self.createToolBar()
        self.itemSelectionChanged.connect(self.openImage)

    def openImage(self):
        row, col = self.currentRow(), self.currentColumn()
        if row >= 0:
            path = ''
            if col >= 2:
                if col == 4:
                    col = 5
                elif col == 5:
                    col = 4
                path = 'cache/img/' + str(row) + '_' + str(col - 2) + '.png'
            # else:
            #     path = self.mainWindow.fileList.item(row).cpath
            if os.path.exists(path):
                self.mainWindow.imageArea.open(path)


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
            self.resizeRowsToContents()
            self.resizeColumnsToContents()


    # TODO
    def analyse(self):
        imagePath = []
        for i in range(self.mainWindow.fileList.count()):
            imagePath.append(self.mainWindow.fileList.item(i).cpath)
        # self.analyser.getImages(imagePath)
        self.mThread.start()
        self.analyser.getImages(imagePath)
        self.analyser.startSignal.emit()
        self.isFree = False
        self.updateActions()
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
        self.toolBar.setIconSize(QSize(30, 30))
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