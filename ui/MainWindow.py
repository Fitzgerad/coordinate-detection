#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import ui.FileList
import ui.ImageArea
import ui.InfoTable
import config.uiConfig as uiConfig
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter, QIcon
from PyQt5.QtWidgets import QLabel, QSplitter, QDesktopWidget, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog, QToolBar, QSizePolicy, QVBoxLayout, QPushButton, QGroupBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.fileList = ui.FileList.FileList(self)
        self.fileListLabel = self.getLabel(self.fileList, "项目列表")
        self.imageArea = ui.ImageArea.ImageArea(self)
        self.imageAreaLabel = self.getLabel(self.imageArea, "图像预览")
        self.infoTable = ui.InfoTable.InfoTable(self)
        self.infoTableLabel = self.getLabel(self.infoTable, "输出列表")

        # 创建一个QSplitter，用来分割窗口
        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.fileListLabel)
        self.splitter.addWidget(self.imageAreaLabel)
        self.splitter.addWidget(self.infoTableLabel)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setStretchFactor(2, 2)
        # QSplitter按照垂直分割
        self.splitter.setStyleSheet(uiConfig.SPLITER_S)
        self.splitter.setOrientation(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        self.setWindowTitle("地图坐标拾取系统")
        # self.setStyleSheet("QMainWindow::separator { background: rgb(190,231,233) }")
        # self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowState(Qt.WindowMaximized)
        size = QDesktopWidget().screenGeometry(-1)
        self.setFixedSize(size.width(), size.height())
        self.setWindowIcon(QIcon("ui/images/logo.png"))
        self.setStyleSheet(uiConfig.MAINWINDOW_S)

    def getLabel(self, mWidget, text):
        qLabel = QLabel()
        qLabel.setStyleSheet(uiConfig.GRANDLABEL_S)
        vLayout = QVBoxLayout()
        textLabel = QLabel()
        textLabel.setStyleSheet(uiConfig.TEXTLABEL_S)
        textLabel.setText("  " + text)
        textLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        mWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        vLayout.setContentsMargins(0, 0, 0, 0)
        vLayout.setSpacing(0)
        vLayout.addWidget(textLabel)
        vLayout.addWidget(mWidget)
        qLabel.setLayout(vLayout)
        return qLabel

def main():
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())