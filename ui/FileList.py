#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import traceback
import config.appConfig as appConfig
import config.uiConfig as uiConfig
import ui.MainWindow
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter, QIcon
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QHBoxLayout, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog, QToolBar, QListWidget, QWidget, QListWidgetItem, QProgressBar, QVBoxLayout

class FileListItem(QListWidgetItem):
    def __init__(self, listWidget, cpath):
        self.listWidget = listWidget
        self.cpath = cpath
        self.spath = os.path.basename(cpath)
        self.progress = 0
        self.info_dict = {}

        self.widget = QWidget(listWidget)
        self.widget.setStyleSheet("background:transparent;")

        self.frontArea = QWidget(self.widget)
        self.pathLabel = QLabel(self.frontArea)
        self.pathLabel.setText(self.spath)
        # self.pathLabel.setFixedWidth(300)
        self.vFrontLayout = QVBoxLayout()
        self.vFrontLayout.setContentsMargins(0, 0, 0, 0)
        self.vFrontLayout.setSpacing(0)
        self.vFrontLayout.addWidget(self.pathLabel)
        self.frontArea.setLayout(self.vFrontLayout)

        self.backArea = QWidget(self.widget)
        self.progressBar = QProgressBar(self.backArea)
        self.progressBar.setValue(0)
        # self.progressBar.setMinimumWidth(100)
        # self.progressBar.setMaximumWidth(150)
        self.progressBar.setAlignment(Qt.AlignCenter)

        # self.textLabel = QLabel(self.backArea)
        # self.textLabel.setVisible(False)
        self.vBackLayout = QVBoxLayout()
        self.vBackLayout.setContentsMargins(0, 0, 0, 0)
        # self.vBackLayout.setMargin(0)
        self.vBackLayout.setSpacing(0)
        self.vBackLayout.addWidget(self.progressBar)
        # self.vBackLayout.addWidget(self.textLabel)
        self.backArea.setLayout(self.vBackLayout)

        self.hLayout = QHBoxLayout()
        self.hLayout.setContentsMargins(0, 0, 0, 0)
        # self.hLayout.setMargin(0)
        self.hLayout.setSpacing(0)
        self.hLayout.addWidget(self.frontArea)
        self.hLayout.addWidget(self.backArea)
        self.hLayout.setStretch(0, 2)
        self.hLayout.setStretch(1, 1)
        self.widget.setLayout(self.hLayout)

        super().__init__()
        self.listWidget.addItem(self)
        self.listWidget.setItemWidget(self, self.widget)

    def updateProgress(self, progress):
        self.progress = max(0, self.progress + progress)
        self.progress = min(100, self.progress)
        self.progressBar.setValue(self.progress)

    def error(self):
        self.progressBar.setTextVisible(False)
        self.progressBar.setStyleSheet("QProgressBar::chunk{background-color: #F4606C;}")
        # self.textLabel.setVisible(True)
        # self.textLabel.setText("分析错误！")

    def upload(self, info_dict):
        for key in info_dict.keys():
            self.info_dict[key] = info_dict[key]
        self.listWidget.mainWindow.infoTable.insertRecord(info_dict)

class FileList(QListWidget):
    def __init__(self, mainWindow):
        super().__init__()
        self.setStyleSheet(uiConfig.FILELIST_S)

        self.mainWindow = mainWindow

        self.setBackgroundRole(QPalette.Base)

        self.createActions()
        self.createToolBar()
        self.itemSelectionChanged.connect(self.openImage)

    def openDir(self):
        dirName = QFileDialog.getExistingDirectory(self, '请选择图片所在文件夹',
                                                   appConfig.ds.config_dict['defaultOpenPath'],
                                                   QFileDialog.ShowDirsOnly)
        if dirName:
            self.clear()
            appConfig.ds.changePublic('defaultOpenPath', dirName)
            paths = os.listdir(dirName)
            for spath in paths:
                if os.path.splitext(spath)[-1] in ['.png', '.jpeg', '.jpg', '.bmp']:
                    cpath = os.path.join(dirName, spath)
                    cpath = os.path.normpath(cpath)
                    FileListItem(self, cpath)
        self.mainWindow.infoTable.updateActions()

    def addDir(self):
        dirName = QFileDialog.getExistingDirectory(self, '请选择图片所在文件夹',
                                                   appConfig.ds.config_dict['defaultOpenPath'],
                                                   QFileDialog.ShowDirsOnly)
        if dirName:
            appConfig.ds.changePublic('defaultOpenPath', dirName)
            paths = os.listdir(dirName)
            for spath in paths:
                if os.path.splitext(spath)[-1] in ['.png', '.jpeg', '.jpg', '.bmp']:
                    cpath = os.path.join(dirName, spath)
                    cpath = os.path.normpath(cpath)
                    FileListItem(self, cpath)
        self.mainWindow.infoTable.updateActions()


    def openFile(self):
        options = QFileDialog.Options()
        paths, _ = QFileDialog.getOpenFileNames(self, '请选择图片',
                                                appConfig.ds.config_dict['defaultOpenPath'],
                                                'Images (*.png *.jpeg *.jpg *.bmp)',
                                                options=options)
        if paths:
            self.clear()
            dirName = appConfig.ds.config_dict['defaultOpenPath'],
            for cpath in paths:
                cpath = os.path.normpath(cpath)
                FileListItem(self, cpath)
                dirName = os.path.abspath(os.path.dirname(cpath) + os.path.sep + ".")
            appConfig.ds.changePublic('defaultOpenPath', dirName)
        self.mainWindow.infoTable.updateActions()

    def addFile(self):
        options = QFileDialog.Options()
        paths, _ = QFileDialog.getOpenFileNames(self, '请选择图片',
                                                appConfig.ds.config_dict['defaultOpenPath'],
                                                'Images (*.png *.jpeg *.jpg *.bmp)',
                                                options=options)
        if paths:
            dirName = appConfig.ds.config_dict['defaultOpenPath'],
            for cpath in paths:
                cpath = os.path.normpath(cpath)
                FileListItem(self, cpath)
                dirName = os.path.abspath(os.path.dirname(cpath) + os.path.sep + ".")
            appConfig.ds.changePublic('defaultOpenPath', dirName)
        self.mainWindow.infoTable.updateActions()

    # TODO: Add Icon
    def createActions(self):
        # QIcon("images/control.png")
        self.openFileAct = self.formatAction("ui/images/image.jpg", "打开\n图片", enabled=True, triggered=self.openFile)
        self.addFileAct = self.formatAction("ui/images/image.jpg", "添加\n图片", enabled=True, triggered=self.addFile)
        self.openDirAct = self.formatAction("ui/images/dir.jpg", "打开\n文件夹", enabled=True, triggered=self.openDir)
        self.addDirAct = self.formatAction("ui/images/dir.jpg", "添加\n文件夹", enabled=True, triggered=self.addDir)

    def formatAction(self, imagePath, text, shortcut=None, enabled=False, triggered=None):
        icon = QPixmap(imagePath)
        action = QAction(QIcon(icon), text, self, triggered=triggered)
        action.setEnabled(enabled)
        return action

    def createToolBar(self):
        self.toolBar = QToolBar()
        self.toolBar.addAction(self.openFileAct)
        self.toolBar.addAction(self.addFileAct)
        self.toolBar.addAction(self.openDirAct)
        self.toolBar.addAction(self.addDirAct)
        self.toolBar.setStyleSheet(uiConfig.TOOLBAR_S)
        self.mainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

    def openImage(self):
        if self.currentRow() >= 0:
            path = self.item(self.currentRow()).cpath
            self.mainWindow.imageArea.open(path)

    def updateProgress(self, index, progress):
        try:
            self.item(index).updateProgress(progress)
        except:
            return

    def upload(self, index, info_dict):
        try:
            self.item(index).upload(info_dict)
        except Exception as e:
            # 这个是输出错误的具体原因，这步可以不用加str，输出
            print('str(e):\t\t', str(e))  # 输出 str(e):		integer division or modulo by zero
            print('repr(e):\t', repr(e))  # 输出 repr(e):	ZeroDivisionError('integer division or modulo by zero',)
            print('traceback.print_exc():')

            # 以下两步都是输出错误的具体位置的
            traceback.print_exc()


    def error(self, index):
        self.item(index).error()