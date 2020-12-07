#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ui.MainWindow
import ui.uiConfig as uiConfig
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter, QIcon
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog, QToolBar

class ImageArea(QScrollArea):
    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow
        self.scaleFactor = 0.0

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Light)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        # self.setBackgroundRole(QPalette.Dark)
        # self.setAlignment(Qt.AlignCenter)
        self.setWidget(self.imageLabel)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setVisible(True)
        self.setStyleSheet(uiConfig.IMAGEAREA_S)
        # self.mainWindow.setCentralWidget(self)

        self.createActions()
        self.createToolBar()

    def open(self, fileName):
        # options = QFileDialog.Options()
        # fileName, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', '',
        #                                           'Images (*.png *.jpeg *.jpg *.bmp *.gif)', options=options)
        if fileName:
            image = QImage(fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "无法打开 %s." % fileName)
                return

            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.scaleFactor = 1.0

            self.setVisible(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        factor = min(self.width() / self.imageLabel.pixmap().width(),
                    self.height() / self.imageLabel.pixmap().height())
        # self.setWidgetResizable(fitToWindow)
        self.scaleImage(factor / self.scaleFactor)
        if not fitToWindow:
            self.normalSize()
        self.updateActions()

    # TODO: Add Icon
    def createActions(self):
        # QIcon("images/control.png")
        self.zoomInAct = self.formatAction("ui/images/zIn.jpg", "放大\n25%", enabled=False, triggered=self.zoomIn)
        self.zoomOutAct = self.formatAction("ui/images/zOut.jpg", "缩小\n25%", enabled=False, triggered=self.zoomOut)
        self.normalSizeAct = self.formatAction("ui/images/image.jpg", "还原\n尺寸", enabled=False, triggered=self.normalSize)
        self.fitToWindowAct = self.formatAction("ui/images/fulfill.jpg", "适应\n画布", enabled=False, triggered=self.fitToWindow, checkable = True)
            # QAction("填充", self, enabled=False, checkable=True,

    def formatAction(self, imagePath, text, shortcut=None, enabled=False, triggered=None, checkable = False):
        icon = QPixmap(imagePath)
        action = QAction(QIcon(icon), text, self, triggered=triggered, checkable=checkable)
        action.setEnabled(enabled)
        return action

    def createToolBar(self):
        self.toolBar = QToolBar()
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.zoomInAct)
        self.toolBar.addAction(self.zoomOutAct)
        self.toolBar.addAction(self.normalSizeAct)
        self.toolBar.addAction(self.fitToWindowAct)
        self.toolBar.setStyleSheet(uiConfig.TOOLBAR_S)
        self.mainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                               + ((factor - 1) * scrollBar.pageStep() / 2)))
