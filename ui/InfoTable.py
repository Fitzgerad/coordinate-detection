#!/usr/bin/python3
# -*- coding: utf-8 -*-
import MainWindow
import openpyxl
import xlwt, xlrd, csv
import pandas as pd

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter, QIcon, QStandardItemModel
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog, QToolBar, QTableWidget, QTableWidgetItem


class InfoTable(QTableWidget):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow

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
        self.open("combined.xls")
        self.updateActions()
        return

    def saveAsExcel(self):
        path = QFileDialog.getSaveFileName(self, 'Save File', 'unnamed', ".xls(*.xls)")
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
        self.analyseAct = QAction("&Analyse", self, shortcut="Ctrl+A", enabled=False, triggered=self.analyse)
        self.saveAsExcelAct = QAction("Save as Excel", self, enabled=False, triggered=self.saveAsExcel)
        self.saveAsWordAct = QAction("Save as Word", self, enabled=False, triggered=self.saveAsWord)
        self.saveAsCSVAct = QAction("Save as CSV", self, enabled=False, triggered=self.saveAsCSV)

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

        self.mainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

    def updateActions(self):
        self.analyseAct.setEnabled(self.mainWindow.fileList.count())
        isSaveable = self.verticalHeader().count()
        self.saveAsExcelAct.setEnabled(isSaveable)
        self.saveAsWordAct.setEnabled(isSaveable)
        self.saveAsCSVAct.setEnabled(isSaveable)

    # TODO
    def changeContent(self):
        return