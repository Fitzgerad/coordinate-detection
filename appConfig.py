import os
import json
import winreg

class DefaultSettings():
    def __init__(self):
        self.setPrivate()
        self.setPublic()
        self.setExcel()

    def getDesktopPath(self):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                 r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        return winreg.QueryValueEx(key, "Desktop")[0]

    def checkPath(self, path):
        if os.path.exists(path):
            return
        else:
            os.makedirs(path)
            return

    def checkFile(self, path):
        if os.path.exists(path):
            return
        else:
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            f = open(path, 'w')
            f.close()
            return

    def setPublic(self):
        mHistory = True
        f = open(self.configFile, 'r')
        try:
            self.config_dict = json.loads(f.read())
        except:
            mHistory = False
        f.close()

        if mHistory:
            if self.config_dict.get('defaultSavePath') == None:
                self.defaultSavePath = self.getDesktopPath()
                self.changePublic('defaultSavePath', self.defaultSavePath)
            else:
                self.defaultSavePath = self.config_dict['defaultSavePath']
            if self.config_dict.get('defaultOpenPath') == None:
                self.defaultOpenPath = self.getDesktopPath()
                self.changePublic('defaultOpenPath', self.defaultOpenPath)
            else:
                self.defaultOpenPath = self.config_dict['defaultOpenPath']
            if self.config_dict.get('defaultOpenExcel') == None:
                self.defaultOpenExcel = None
            else:
                self.defaultOpenExcel = self.config_dict['defaultOpenExcel']
        else:
            self.defaultSavePath = self.getDesktopPath()
            self.changePublic('defaultSavePath', self.defaultSavePath)
            self.defaultOpenPath = self.getDesktopPath()
            self.changePublic('defaultOpenPath', self.defaultOpenPath)
            self.defaultOpenExcel = None

    def setPrivate(self):
        self.configFile = os.path.normpath('usr\\config.json')
        self.checkFile(self.configFile)
        self.imageSavePath = os.path.normpath('cache\\img')
        self.checkPath(self.imageSavePath)
        self.textSavePath = os.path.normpath('cache\\txt')
        self.checkPath(self.textSavePath)
        self.excelSavePath = os.path.normpath('cache\\excel')
        self.checkPath(self.excelSavePath)
        self.saveImage = True
        self.saveText = False

    def setExcel(self):
        self.defaultExcelSettings = ExcelSettings(self.config_dict)
        self.changePublic('defaultExcelSettings', self.defaultExcelSettings)

    def changePublic(self, key, value):
        self.config_dict[key] = value
        with open(self.configFile, 'w') as outfile:
            json.dump(self.config_dict, outfile)

class ExcelSettings():
    def __init__(self, config_dict):
        if config_dict.get('defaultExcelSettings') != None:
            self.settings = config_dict['defaultExcelSettings']
        else:
            self.settings = {}
        self.completeSettings()

    def completeSettings(self):
        return


ds = DefaultSettings()
