# This file provides Qt functionality for the Pyside6 GUI. This script is not suppossed to be run alone. 

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGroupBox, QRadioButton, QPushButton, QStackedWidget, QLineEdit, QButtonGroup, QMessageBox, QScrollArea, QFileDialog, QComboBox, QHBoxLayout, QStyledItemDelegate, QGridLayout
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QUrl, QObject
from PySide6.QtGui import QGuiApplication, QDesktopServices

from src.core.logic import Installer, StartmenuEntry

from pathlib import Path
import time

# All functions from the menubar
class General():

    def openRepo():
            QDesktopServices.openUrl(QUrl("https://github.com/Anton-Lindauer/AppImage-Installer"))

    def loadTheme(self, selectedTheme):
            app = QApplication.instance()
            match selectedTheme:
                case "sysTheme":
                    sysStyle = QGuiApplication.instance().styleHints().colorScheme()
                    if sysStyle == Qt.ColorScheme.Dark:
                        themeToLoad = self.darkStylePath
                    else:
                        themeToLoad = self.lightStylePath
                case "darkTheme":
                    themeToLoad = self.darkStylePath
                case "lightTheme":  
                    themeToLoad = self.lightStylePath

# Open the stylesheet with the selected theme
            with open(themeToLoad, "r") as f:  
                            _style = f.read()
                            app.setStyleSheet(_style)


#All functions for page 1
class Page1Logic(QObject):
    pickedFile = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.userDir = Path.home()

# Filedialog window to get a AppImage from outside the Downloads directory
    def userPick(self, parentWindow):
        pickedPath, _ = QFileDialog.getOpenFileName(
            parentWindow,
            "Pick a AppImage file to install",
                str(self.userDir),
            "AppImage files (*.AppImage)"
        )

        if pickedPath:
            self.pickedFile.emit(pickedPath)

# Find the selected file and the user can only continue with a file selected
    def findSeletedRadioBtn(self, groupPage1):
            selected = groupPage1.checkedButton()
            if selected is not None:
                pickedPath = selected.text()
                self.pickedFile.emit(pickedPath)

# Class for the installation process
class InstallWorker(QThread):
    progressUpdate = Signal(str)
    error = Signal(str)
    success = Signal()

    def __init__(self, selectedFilePath, fileDest, userDir, programName,programDescr, programCategory, cmdName):
        super().__init__()

        self.installer = Installer()
        self.startMenuEntry = StartmenuEntry()

        self.selectedFilePath = selectedFilePath
        self.fileDest = fileDest     
        self.userDir = userDir
        self.programName = programName
        self.programDescr = programDescr
        self.programCategory = programCategory
        self.cmdName = cmdName

# All installation steps with progress updates
    def run(self):
        try:
            self.installer.moveFile(self.selectedFilePath, self.fileDest)
            self.progressUpdate.emit("File moved successfully (1/4 tasks finished)")

            self.installer.mkExec(self.selectedFilePath, self.fileDest)
            self.progressUpdate.emit("File has been made executable (2/4 tasks finished)")

            self.installer.mkSymLink(self.selectedFilePath, self.cmdName, self.fileDest, self.userDir)
            self.progressUpdate.emit("Program has been made executable (3/4 tasks finished)")

            self.startMenuEntry.create(self.selectedFilePath, self.fileDest, self.userDir, self.programName, self.programDescr, self.programCategory)
            self.progressUpdate.emit("Startmenu entry has been created (4/4 tasks finished)")

# Wait 2s to let the user see that everything has been completed
            time.sleep(2)

            self.success.emit()

        except Exception as error:
            print(error)

            self.error.emit(str(error))