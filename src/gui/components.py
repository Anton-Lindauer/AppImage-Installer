# This file provides Qt functionality for the Pyside6 GUI. This script is not suppossed to be run alone. 

from PySide6.QtWidgets import QApplication, QFileDialog, QDialog, QVBoxLayout, QLabel, QCheckBox, QComboBox, QListView
from PySide6.QtCore import Qt, Signal, QUrl, QObject, QSettings
from PySide6.QtGui import QGuiApplication, QDesktopServices

from pathlib import Path
import os

# All functions from the menubar
class MenuBarUtils(QObject):
    def __init__(self):
        super().__init__()

        self.settings = QSettings("Anton-Lindauer", "AppImage-Installer")

        fileDir = Path(__file__).resolve()
        projectRoot = fileDir.parent.parent.parent
        self.modernLightStylePath = projectRoot / "assets" / "stylesheets" / "modernLightStyle.qss"
        self.modernBlueDarkStylePath = projectRoot / "assets" / "stylesheets" / "modernBlueDarkStyle.qss"
        self.modernDarkStylePath = projectRoot / "assets" / "stylesheets" / "modernDarkStyle.qss"
        self.kdeStylePath = projectRoot / "assets" / "stylesheets" / "kdeStyle.qss"

        self.desktopEnv = os.environ.get("XDG_CURRENT_DESKTOP")

    def openRepo():
            QDesktopServices.openUrl(QUrl("https://github.com/Anton-Lindauer/AppImage-Installer"))

    def loadTheme(self, selectedTheme):
            app = QApplication.instance()
            match selectedTheme:
                case "sysTheme":
                    self.settings.setValue("theme", "sysTheme")
                    sysStyle = QGuiApplication.instance().styleHints().colorScheme()
                    if sysStyle == Qt.ColorScheme.Dark:
                        themeToLoad = self.modernBlueDarkStylePath
                    else:
                        themeToLoad = self.modernLightStylePath
                case "modernBlueDarkTheme":
                    self.settings.setValue("theme", "modernBlueDarkTheme")
                    themeToLoad = self.modernBlueDarkStylePath
                case "modernDarkTheme":  
                    self.settings.setValue("theme", "modernDarkTheme")
                    themeToLoad = self.modernDarkStylePath
                case "modernLightTheme":  
                    self.settings.setValue("theme", "modernLightTheme")
                    themeToLoad = self.modernLightStylePath
                case "kdeTheme":
                    if self.desktopEnv == "KDE":
                        self.settings.setValue("theme", "kdeTheme")
                        themeToLoad = self.kdeStylePath
                    else:
                        print("Not supported on your desktop environment")
                        return

# Open the stylesheet with the selected theme
            with open(themeToLoad, "r") as f:
                            _style = f.read()
                            app.setStyleSheet(_style)

    def settingsWindow(self):
        settingsPage = QDialog()
        settingsPage.setWindowTitle(self.tr("AppImage-Installer Settings"))

        settingsWindowLayout = QVBoxLayout(settingsPage)
        settingsWindowLayout.setContentsMargins(20, 20, 20, 20)
        settingsWindowLayout.setSpacing(6)

        title = QLabel(self.tr("General Settings"))
        title.setObjectName("title")

        setting1 = QCheckBox(self.tr("Auto delete old logs"))
        setting1.setChecked(self.settings.value("autoDelete", True, type=bool))
        setting1.toggled.connect(lambda checked: self.settings.setValue("autoDelete", checked))

        title2 = QLabel(self.tr("Language"))
        title2.setObjectName("title")

        infoText2 = QLabel(self.tr("Requires restart to change"))
        infoText2.setObjectName("settingsDescription")

        languageSel = QComboBox()
        languageSel.addItem("Deutsch", "de")
        languageSel.addItem("English", "en")

# KDE doesn't have those problems
        if not self.settings.value("theme") == "kdeTheme":

# Fix to properly load the stylesheets
            view = QListView(languageSel)
            languageSel.setView(view)

# Fix for items not wanting to align to the left side
            for i in range(languageSel.count()):
                languageSel.setItemData(
                    i,
                    int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                    Qt.ItemDataRole.TextAlignmentRole
                )

        savedLanguage = self.settings.value("language", "en", type=str)
        languageIndex = languageSel.findData(savedLanguage)
        languageSel.setCurrentIndex(languageIndex)

        languageSel.currentTextChanged.connect(lambda: self.settings.setValue("language", languageSel.currentData()))

        settingsWindowLayout.addWidget(title)
        settingsWindowLayout.addWidget(setting1)
        settingsWindowLayout.addWidget(title2)
        settingsWindowLayout.addWidget(infoText2)
        settingsWindowLayout.addWidget(languageSel)

        settingsWindowLayout.addStretch()

        settingsPage.exec()

#All functions to prepare the installation of a AppImage file
class PrepInstall(QObject):
    pickedFile = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.userDir = Path.home()

# Filedialog window to get a AppImage from outside the Downloads directory
    def userPick(self, parentWindow):
        pickedPath, _ = QFileDialog.getOpenFileName(
            parentWindow,
            self.tr("Pick a AppImage file to install"),
                str(self.userDir),
            self.tr("AppImage files (*.AppImage)")
        )

        if pickedPath:
            self.pickedFile.emit(pickedPath)

# Find the selected file and the user can only continue with a file selected
    def findSelectedRadioBtn(self, groupPage1):
            selected = groupPage1.checkedButton()
            if selected is not None:
                pickedPath = selected.text()
                self.pickedFile.emit(pickedPath)

# All functions to prepare the uninstallation of an installed AppImage program
class PrepUninstall(QObject):
    pickedFile = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.userDir = Path.home()

# Filedialog window to get a AppImage from outside the AppImage directory
    def userPick(self, parentWindow):
        pickedPath, _ = QFileDialog.getOpenFileName(
            parentWindow,
            self.tr("Pick a AppImage file to uninstall"),
                str(self.userDir),
            self.tr("AppImage files (*.AppImage)")
        )

        if pickedPath:
            self.pickedFile.emit(pickedPath)

# Find the selected file and the user can only continue with a file selected
    def findSelectedRadioBtn(self, groupPage1):
            selected = groupPage1.checkedButton()
            if selected is not None:
                pickedPath = selected.text()
                self.pickedFile.emit(pickedPath)