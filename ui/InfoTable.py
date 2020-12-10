#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ui.MainWindow
import config.uiConfig as uiConfig
import config.excelConfig as excelConfig
import sys
import identify
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
    uploadSingal = pyqtSignal(int, dict)
    errorSignal = pyqtSignal(int)
    # excelSignal = pyqtSignal(str)
    closeSignal = pyqtSignal()

    def __init__(self, infoTable):
        QObject.__init__(self)
        self.infoTable = infoTable
        self.fileList = infoTable.mainWindow.fileList
        self.imagePath = []

    def getImages(self, imagePath):
        self.imagePath = copy.deepcopy(imagePath)

    def analyse(self):
        identify.main(self.imagePath, self.errorSignal,
                       self.progressSignal, self.uploadSingal)
        self.infoTable.isFree = True
        self.infoTable.updateActions()
        self.closeSignal.emit()

class TableItem(QTableWidgetItem):
    def __init__(self, content, list_item):
        super().__init__(content)
        self.list_item = list_item

    def modify(self):
        try:
            if self.column() >= 2:
                if self.column() % 2 == 0:
                    self.list_item.info_dict['left'] = \
                        self.text().replace(' ', '').split(',')[0]
                else:
                    self.list_item.info_dict['right'] = \
                        self.text().replace(' ', '').split(',')[0]
                if self.column() <= 3:
                    self.list_item.info_dict['up'] = \
                        self.text().replace(' ', '').split(',')[1]
                else:
                    self.list_item.info_dict['down'] = \
                        self.text().replace(' ', '').split(',')[1]
            elif self.column() == 0:
                self.list_item.info_dict['name'] = self.text()
            elif self.column() == 1:
                self.list_item.info_dict['type'] = self.text()
        except:
            return

class InfoTable(QTableWidget):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        self.isFree = True
        self.isConnected = True
        self.header = []
        self.mThread = QThread()
        self.analyser = Analyser(self)
        self.analyser.moveToThread(self.mThread)
        self.analyser.startSignal.connect(self.analyser.analyse)
        self.analyser.progressSignal.connect(self.analyser.fileList.updateProgress)
        self.analyser.uploadSingal.connect(self.analyser.fileList.upload)
        # self.analyser.excelSignal.connect(self.analyser.infoTable.open)
        self.analyser.errorSignal.connect(self.analyser.fileList.error)
        self.analyser.closeSignal.connect(self.finishAnalyse)
        # self.mThread.started.connect(self.analyser.analyse)

        self.setColumnCount(0)
        self.setRowCount(0)

        self.setStyleSheet(uiConfig.INFOTABLE_S)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self.setVisible(True)

        self.createActions()
        self.createToolBar()
        self.itemSelectionChanged.connect(self.openImage)
        self.itemChanged.connect(self.updateValue)

    def updateValue(self, item):
        self.itemChanged.disconnect(self.updateValue)
        item.modify()
        self.changeItem(item.list_item.info_dict, item.row())
        self.resizeCell()
        if self.isConnected:
            self.itemChanged.connect(self.updateValue)

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
            self.header = df.columns.ravel().tolist()
            for i in range(len(self.header)):
                self.header[i] = str(self.header[i])
            self.setColumnCount(len(df.columns))
            self.setRowCount(len(df.index))
            self.setHorizontalHeaderLabels(self.header)
            for i in range(len(df.index)):
                for j in range(len(df.columns)):
                    self.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
            self.resizeCell()

    def changeItem(self, info_dict, row):
        self.item(row, 0).setText(info_dict['name'])
        self.item(row, 1).setText(info_dict['type'])
        self.item(row, 2).setText(
            info_dict['left'] + ', ' + info_dict['up'])
        self.item(row, 3).setText(
            info_dict['right'] + ', ' + info_dict['up'])
        self.item(row, 4).setText(
            info_dict['left'] + ', ' + info_dict['down'])
        self.item(row, 5).setText(
            info_dict['right'] + ', ' + info_dict['down'])

    def insertRecord(self, info_dict):
        if self.header == [] or self.header == None:
            self.header = excelConfig.COL_TITLES
            self.setColumnCount(len(self.header))
            self.setHorizontalHeaderLabels(self.header)
        row = self.rowCount()
        list_item = self.mainWindow.fileList.item(row)
        self.setRowCount(row + 1)
        try:
            self.itemChanged.disconnect(self.updateValue)
        except:
            pass
        self.setItem(row, 0, TableItem(info_dict['name'],
            list_item))
        self.setItem(row, 1, TableItem(info_dict['type'],
            list_item))
        self.setItem(row, 2, TableItem(
            info_dict['left'] + ', ' + info_dict['up'],
            list_item))
        self.setItem(row, 3, TableItem(
            info_dict['right'] + ', ' + info_dict['up'],
            list_item))
        self.setItem(row, 4, TableItem(
            info_dict['left'] + ', ' + info_dict['down'],
            list_item))
        self.setItem(row, 5, TableItem(
            info_dict['right'] + ', ' + info_dict['down'],
            list_item))
        self.resizeCell()
        if self.isConnected:
            self.itemChanged.connect(self.updateValue)

    def resizeCell(self):
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    # TODO
    def analyse(self):
        imagePath = []
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(0)
        self.header = []
        for i in range(self.mainWindow.fileList.count()):
            self.mainWindow.fileList.item(i).updateProgress(-100)
            imagePath.append(self.mainWindow.fileList.item(i).cpath)
        # self.analyser.getImages(imagePath)
        self.mThread.start()
        self.analyser.getImages(imagePath)
        self.analyser.startSignal.emit()
        self.isFree = False
        self.updateActions()
        return

    def finishAnalyse(self):
        self.mThread.quit()
        self.isFree = True
        self.updateActions()

    def saveAsExcel(self):
        path = QFileDialog.getSaveFileName(self,
                                           '保存文件',
                                           '未命名',
                                           ".xls(*.xls)")
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
        path = QFileDialog.getSaveFileName(self,
                                           '保存文件',
                                           '未命名',
                                           'CSV(*.csv)')
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
        self.toolBar.addAction(self.analyseAct)
        self.toolBar.addAction(self.saveAsExcelAct)
        self.toolBar.addAction(self.saveAsWordAct)
        self.toolBar.addAction(self.saveAsCSVAct)
        self.toolBar.setStyleSheet(uiConfig.TOOLBAR_S)
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
