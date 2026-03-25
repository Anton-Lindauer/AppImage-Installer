# This file provides Qt functionality for the Pyside6 GUI. This script is not suppossed to be run alone. 
# Yes I know that OOP is missing, but getting this far already was a pain.

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGroupBox, QRadioButton, QPushButton, QStackedWidget, QLineEdit, QButtonGroup, QMessageBox, QScrollArea, QFileDialog, QComboBox, QHBoxLayout, QStyledItemDelegate, QGridLayout
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QUrl
from PySide6.QtGui import QGuiApplication, QDesktopServices


# All functions from the menubar

def openRepo():
        QDesktopServices.openUrl(QUrl("https://github.com/Anton-Lindauer/AppImage-Installer"))

def loadTheme(self, selectedTheme):
        app = QApplication.instance()
        match selectedTheme:
# Open the qss style sheet with the same theme as the system
            case "sysTheme":
                sysStyle = QGuiApplication.instance().styleHints().colorScheme()
                if sysStyle == Qt.ColorScheme.Dark:
                    themeToLoad = self.darkStylePath
                else:
                    themeToLoad = self.lightStylePath
# Load path for the dark theme
            case "darkTheme":
                themeToLoad = self.darkStylePath
# Load path for the light theme
            case "lightTheme":  
                themeToLoad = self.lightStylePath
        
# Open the stylesheet with the selected theme
        with open(themeToLoad, "r") as f:  
                        _style = f.read()
                        app.setStyleSheet(_style)