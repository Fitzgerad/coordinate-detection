#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import FileList
import ImageArea
import InfoTable
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter, QIcon
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog, QToolBar, QListWidget, QHBoxLayout, QPushButton, QGroupBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.groupBox = QGroupBox()
        self.vLayout = QHBoxLayout()
        self.fileList = FileList.FileList(self)
        self.imageArea = ImageArea.ImageArea(self)
        self.infoTable = InfoTable.InfoTable(self)
        self.vLayout.addWidget(self.fileList)
        self.vLayout.addWidget(self.imageArea)
        self.vLayout.addWidget(self.infoTable)
        self.groupBox.setLayout(self.vLayout)

        self.setCentralWidget(self.groupBox)

        self.setWindowTitle("System")
        self.resize(800, 600)

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())