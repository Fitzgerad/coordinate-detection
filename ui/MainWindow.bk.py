#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import FileList
import ImageArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter, QIcon
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog, QToolBar, QListWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.centralWidget = QWidget(self)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralWidget.sizePolicy().hasHeightForWidth())
        self.centralWidget.setSizePolicy(sizePolicy)

        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)

        self.fileList = FileList.FileList(self)
        self.horizontalLayout.addWidget(self.fileList)
        self.imageArea = ImageArea.ImageArea(self)
        self.horizontalLayout.addWidget(self.imageArea)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.setCentralWidget(self.centralWidget)

        self.setWindowTitle("System")
        self.resize(800, 600)

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    # imageViewer = FileList(window)
    window.show()
    sys.exit(app.exec_())
    # TODO QScrollArea support mouse