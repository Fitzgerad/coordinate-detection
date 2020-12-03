#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import appConfig
import ui.uiConfig
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

        self.widget = QWidget(listWidget)
        self.widget.setStyleSheet("background:transparent;")

        self.frontArea = QWidget(self.widget)
        self.pathLabel = QLabel(self.frontArea)
        self.pathLabel.setText(self.spath)
        self.pathLabel.setFixedWidth(300)
        self.vFrontLayout = QVBoxLayout()
        self.vFrontLayout.setContentsMargins(0, 0, 0, 0)
        self.vFrontLayout.setSpacing(0)
        self.vFrontLayout.addWidget(self.pathLabel)
        self.frontArea.setLayout(self.vFrontLayout)

        self.backArea = QWidget(self.widget)
        self.progressBar = QProgressBar(self.backArea)
        self.progressBar.setValue(0)
        self.progressBar.setMinimumWidth(100)
        self.progressBar.setMaximumWidth(150)
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
        self.widget.setLayout(self.hLayout)

        super().__init__()
        self.listWidget.addItem(self)
        self.listWidget.setItemWidget(self, self.widget)

    def update(self, progress):
        self.progress = max(0, self.progress + progress)
        self.progress = min(100, self.progress)
        self.progressBar.setValue(self.progress)

    def error(self):
        self.progressBar.setTextVisible(False)
        self.progressBar.setStyleSheet("QProgressBar::chunk{background-color: #F4606C;}")
        # self.textLabel.setVisible(True)
        # self.textLabel.setText("分析错误！")

class FileList(QListWidget):
    def __init__(self, mainWindow):
        super().__init__()
        self.defaultOpenDir = appConfig.ds.defaultOpenPath
        self.defaultSaveDir = appConfig.ds.defaultSavePath
        self.setStyleSheet(ui.uiConfig.FILELIST_S)

        self.mainWindow = mainWindow

        self.setBackgroundRole(QPalette.Base)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self.createActions()
        self.createToolBar()
        self.itemSelectionChanged.connect(self.openImage)

    def openDir(self):
        dirName = QFileDialog.getExistingDirectory(self, '请选择图片所在文件夹', self.defaultOpenDir,
                                                       QFileDialog.ShowDirsOnly)
        if dirName:
            self.clear()
            self.defaultOpenDir = dirName
            paths = os.listdir(dirName)
            for spath in paths:
                if os.path.splitext(spath)[-1] in ['.png', '.jpeg', '.jpg', '.bmp']:
                    cpath = os.path.join(dirName, spath)
                    cpath = os.path.normpath(cpath)
                    FileListItem(self, cpath)
        self.mainWindow.infoTable.updateActions()

    def addDir(self):
        dirName = QFileDialog.getExistingDirectory(self, '请选择图片所在文件夹', self.defaultOpenDir,
                                                   QFileDialog.ShowDirsOnly)
        if dirName:
            self.defaultOpenDir = dirName
            paths = os.listdir(dirName)
            for spath in paths:
                if os.path.splitext(spath)[-1] in ['.png', '.jpeg', '.jpg', '.bmp']:
                    cpath = os.path.join(dirName, spath)
                    cpath = os.path.normpath(cpath)
                    FileListItem(self, cpath)
        self.mainWindow.infoTable.updateActions()


    def openFile(self):
        options = QFileDialog.Options()
        paths, _ = QFileDialog.getOpenFileNames(self, '请选择图片', '',
                                                  'Images (*.png *.jpeg *.jpg *.bmp)', options=options)
        if paths:
            self.clear()
            for cpath in paths:
                cpath = os.path.normpath(cpath)
                FileListItem(self, cpath)
        self.mainWindow.infoTable.updateActions()

    def addFile(self):
        options = QFileDialog.Options()
        paths, _ = QFileDialog.getOpenFileNames(self, '请选择图片', '',
                                                  'Images (*.png *.jpeg *.jpg *.bmp)', options=options)
        if paths:
            for cpath in paths:
                cpath = os.path.normpath(cpath)
                FileListItem(self, cpath)
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
        self.toolBar.setMovable(False)
        # self.toolBar.addSeparator()
        # self.viewMenu = QMenu("&View", self)
        self.toolBar.addAction(self.openFileAct)
        self.toolBar.addAction(self.addFileAct)
        self.toolBar.addAction(self.openDirAct)
        self.toolBar.addAction(self.addDirAct)
        self.toolBar.setIconSize(QSize(30, 30))
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

    def openImage(self):
        if self.currentRow() >= 0:
            path = self.item(self.currentRow()).cpath
            self.mainWindow.imageArea.open(path)