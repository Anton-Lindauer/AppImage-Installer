# This file provides Qt functionality for the Pyside6 GUI. This script is not suppossed to be run alone. 

from PySide6.QtWidgets import QApplication, QFileDialog, QDialog, QVBoxLayout, QLabel, QCheckBox, QComboBox, QListView
from PySide6.QtCore import Qt, Signal, QUrl, QObject, QSettings, QDir
from PySide6.QtGui import QGuiApplication, QDesktopServices, QPalette

from pathlib import Path
import os

# All menubar exclusive functionality
class MenuBarUtils(QObject):
    def __init__(self):
        super().__init__()

        self.settings = QSettings("Anton-Lindauer", "AppImage-Installer")

        currentFilePath = Path(__file__).resolve()
        projectRoot = currentFilePath.parent.parent.parent
        assetsPath = projectRoot / "assets"

        self.modernLightStylePath = assetsPath / "stylesheets" / "modern_light_style.qss"
        self.modernBlueDarkStylePath = assetsPath / "stylesheets" / "modern_blue_dark_style.qss"
        self.modernDarkStylePath = assetsPath / "stylesheets" / "modern_dark_style.qss"
        self.kdeStylePath = assetsPath / "stylesheets" / "kde_style.qss"

        self.desktopEnv = os.environ.get("XDG_CURRENT_DESKTOP")

# Fix for icon paths in QSS being wrong in the snap
        QDir.addSearchPath("assets", str(assetsPath))

    @staticmethod
    def openRepo():
        QDesktopServices.openUrl(QUrl("https://github.com/Anton-Lindauer/AppImage-Installer"))

    def loadTheme(self, selectedTheme):
        app = QApplication.instance()
        match selectedTheme:
            case "sysTheme":
                self.settings.setValue("theme", "sysTheme")
                
                systemColorScheme = QGuiApplication.palette().color(QPalette.ColorRole.Window)

                themeToLoad = (
                    self.modernBlueDarkStylePath
                    if systemColorScheme.lightness() < 128
                    else self.modernLightStylePath
                )

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
                if self.desktopEnv != "KDE":
                    print("Not supported on your desktop environment")
                    return
                self.settings.setValue("theme", "kdeTheme")
                themeToLoad = self.kdeStylePath

        with open(themeToLoad, "r") as f:
            styleSheetContent = f.read()
            app.setStyleSheet(styleSheetContent)

    def openSettingsWindow(self):
        settingsDialog = QDialog()
        settingsDialog.setWindowTitle(self.tr("AppImage-Installer Settings"))

        settingsLayout = QVBoxLayout(settingsDialog)
        settingsLayout.setContentsMargins(20, 20, 20, 20)
        settingsLayout.setSpacing(6)

        generalSettingsTitle = QLabel(self.tr("General Settings"))
        generalSettingsTitle.setObjectName("title")

        autoDeleteLogsCheckbox = QCheckBox(self.tr("Auto delete old logs"))
        autoDeleteLogsCheckbox.setChecked(self.settings.value("autoDelete", True, type=bool))
        autoDeleteLogsCheckbox.toggled.connect(lambda checked: self.settings.setValue("autoDelete", checked))

        languageSectionTitle = QLabel(self.tr("Language"))
        languageSectionTitle.setObjectName("title")

        languageRestartHint = QLabel(self.tr("Requires restart to change"))
        languageRestartHint.setObjectName("settingsDescription")

        languageComboBox = QComboBox()
        languageComboBox.addItem("Deutsch", "de")
        languageComboBox.addItem("English", "en")

 # KDE doesn't have problems with the QComboBox
        if self.settings.value("theme") != "kdeTheme":

# Fix to properly load the stylesheets
            languageListView = QListView(languageComboBox)
            languageComboBox.setView(languageListView)

# Fix for items not wanting to align to the right side
            for i in range(languageComboBox.count()):
                languageComboBox.setItemData(
                    i,
                    int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                    Qt.ItemDataRole.TextAlignmentRole
                )

        savedLanguage = self.settings.value("language", "en", type=str)
        languageComboBox.setCurrentIndex(languageComboBox.findData(savedLanguage))
        languageComboBox.currentTextChanged.connect(lambda: self.settings.setValue("language", languageComboBox.currentData()))

        settingsLayout.addWidget(generalSettingsTitle)
        settingsLayout.addWidget(autoDeleteLogsCheckbox)
        settingsLayout.addWidget(languageSectionTitle)
        settingsLayout.addWidget(languageRestartHint)
        settingsLayout.addWidget(languageComboBox)
        settingsLayout.addStretch()

        settingsDialog.exec()


#All functions to prepare the installation of a AppImage file
class InstallFileSelector(QObject):
    pickedFile = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.userDir = Path.home()

# Filedialog window to get a AppImage from outside the Downloads directory
    def openFileDialog(self, parentWindow):
        pickedPath, _ = QFileDialog.getOpenFileName(
            parentWindow,
            self.tr("Pick a AppImage file to install"),
            str(self.userDir),
            self.tr("AppImage files (*.AppImage)")
        )
 
        if pickedPath:
            self.pickedFile.emit(pickedPath)

# Find the selected file and the user can only continue with a file selected
    def emitSelectedRadioBtn(self, radioGroupTab1Page1):
        selectedButton = radioGroupTab1Page1.checkedButton()
        if selectedButton is not None:
            pickedPath = selectedButton.text()
            self.pickedFile.emit(pickedPath)


class UpdateFileSelector(QObject):
    newFile = Signal(str)

    def __init__(self, parent=None):
            super().__init__(parent)
            self.userDir = Path.home()

# Filedialog window to let the user pick a AppImage file to replace the one of the current installation
# Intended as one way of updating AppImage programs without a build in updater
    def openFileDialog(self, parentWindow):
        pickedPath, _ = QFileDialog.getOpenFileName(
            parentWindow,
            self.tr("Pick a AppImage file to update the current installation"),
            str(self.userDir),
            self.tr("AppImage files (*.AppImage)")
        )

        if pickedPath:
            self.newFile.emit(pickedPath)