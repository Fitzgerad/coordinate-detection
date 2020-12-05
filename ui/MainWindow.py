#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import appConfig
import ui.FileList
import ui.ImageArea
import ui.InfoTable
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter, QIcon
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSplitter, QDesktopWidget, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog, QToolBar, QListWidget, QHBoxLayout, QPushButton, QGroupBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.fileList = ui.FileList.FileList(self)
        self.imageArea = ui.ImageArea.ImageArea(self)
        self.infoTable = ui.InfoTable.InfoTable(self)

        # 创建一个QSplitter，用来分割窗口
        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.fileList)
        self.splitter.addWidget(self.imageArea)
        self.splitter.addWidget(self.infoTable)
        # self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 100)
        self.splitter.setStretchFactor(2, 2)
        # self.splitter.setStretchFactor(3, 2)
        # QSplitter按照垂直分割
        # self.splitter.setStyleSheet(
        #     "QSplitter::handle { background-color: rgb(190,231,233) }")
        self.splitter.setOrientation(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        # self.groupBox = QGroupBox()
        # self.hLayout = QHBoxLayout()
        # self.hLayout.addWidget(self.fileList)
        # self.hLayout.addWidget(self.imageArea)
        # self.hLayout.addWidget(self.infoTable)
        # self.hLayout.setStretchFactor(self.fileList, 2)
        # self.hLayout.setStretchFactor(self.imageArea, 3)
        # self.hLayout.setStretchFactor(self.infoTable, 3)
        # self.groupBox.setLayout(self.hLayout)
        # self.setCentralWidget(self.groupBox)

        # self.setWindowFlag(Qt.Tool)
        self.setWindowTitle("地图坐标拾取系统")
        # self.setStyleSheet("QMainWindow::separator { background: rgb(190,231,233) }")
        # self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.setWindowState(Qt.WindowMaximized)
        size = QDesktopWidget().screenGeometry(-1)
        self.setFixedSize(size.width(), size.height())
        self.setWindowIcon(QIcon("ui/images/logo.png"))

def main():
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())