# This file provides Qt functionality for the Pyside6 GUI. This script is not suppossed to be run alone. 

from PySide6.QtWidgets import QApplication, QFileDialog, QDialog, QVBoxLayout, QLabel, QCheckBox, QComboBox, QListView
from PySide6.QtCore import Qt, QThread, Signal, QUrl, QObject, QSettings
from PySide6.QtGui import QGuiApplication, QDesktopServices

from src.core.logic import Installer, StartmenuEntry

from pathlib import Path
import subprocess
import tempfile
import shutil
import time
import os

# All functions from the menubar
class General(QObject):
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

        settingsPageLayout = QVBoxLayout(settingsPage)
        settingsPageLayout.setContentsMargins(20, 20, 20, 20)
        settingsPageLayout.setSpacing(6)

        title = QLabel(self.tr("General Settings"))
        title.setObjectName("title")

        self.setting1 = QCheckBox(self.tr("Auto delete old logs"))
        self.setting1.setChecked(self.settings.value("autoDelete", True, type=bool))
        self.setting1.toggled.connect(lambda checked: self.settings.setValue("autoDelete", checked))

        title2 = QLabel(self.tr("Language"))
        title2.setObjectName("title")

        infoText2 = QLabel(self.tr("Requires restart to change"))
        infoText2.setObjectName("settingsDescription")

        languageSel = QComboBox()
        languageSel.addItem("Deutsch", "de")
        languageSel.addItem("English", "en")

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

        settingsPageLayout.addWidget(title)
        settingsPageLayout.addWidget(self.setting1)
        settingsPageLayout.addWidget(title2)
        settingsPageLayout.addWidget(infoText2)
        settingsPageLayout.addWidget(languageSel)

        settingsPageLayout.addStretch()

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

    def getAppimageMetadata(path):
        filePath = Path(path).resolve()

        workDir = Path(tempfile.mkdtemp())

        try:
# Extract the AppImage to a temporary directory
            subprocess.run(
                [str(filePath), "--appimage-extract"],
                cwd=workDir,
                check=True
            )

            squashfsRoot = workDir / "squashfs-root"

            if not squashfsRoot.exists():
                raise RuntimeError("Extraction failed: squashfs-root not found")

# AppImages contain a .desktop file with the same content as the .desktop file for the startmenu entry
            desktopFiles = list(squashfsRoot.rglob("*.desktop"))

            if not desktopFiles:
                raise RuntimeError("No .desktop files found in AppImage")

            desktopFile = desktopFiles[0]

            metadata = {}

            with open(desktopFile, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()

                    if "=" not in line:
                        continue

                    key, value = line.split("=", 1)
                    metadata[key] = value

# Return only the needed information from the AppImage's .desktop file
            return {
                "exec": metadata.get("Exec", ""),
                "name": metadata.get("Name", ""),
                "comment": metadata.get("Comment", ""),
                "categories": metadata.get("Categories", ""),
                "icon": metadata.get("Icon", "")
            }

        finally:
            shutil.rmtree(workDir, ignore_errors=True)

# All functions to prepare the uninstallation of an installed AppImage program
class PrepUninstall(QObject):
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

# Extracting a AppImage can take a while, so I temporarely put that code in a QThread (I know it's not the best way to do it like this)
class MetadataWorker(QThread):
    progressUpdate = Signal(str)
    error = Signal(str)
    finished = Signal(dict)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            metadata = PrepInstall.getAppimageMetadata(self.path)
            self.finished.emit(metadata)

        except Exception as e:
            self.error.emit(str(e))

# Class for the installation process
class InstallWorker(QThread):
    progressUpdate = Signal(str)
    error = Signal(str)
    success = Signal()

    def __init__(self, selectedFilePath, fileDest, userDir, programName,programDescr, programCategory, cmdName, logger, symLinkDir):
        super().__init__()

        self.logger = logger
        self.installer = Installer(self.logger)
        self.startMenuEntry = StartmenuEntry(self.logger)

        self.selectedFilePath = selectedFilePath
        self.fileDest = fileDest     
        self.userDir = userDir
        self.programName = programName
        self.programDescr = programDescr
        self.programCategory = programCategory
        self.cmdName = cmdName
        self.symLinkDir = symLinkDir

# All installation steps with progress updates
    def run(self):
        try:
            self.installer.moveFile(self.selectedFilePath, self.fileDest)
            self.progressUpdate.emit(self.tr("File moved successfully (1/4 tasks finished)"))

            self.installer.mkExec(self.selectedFilePath, self.fileDest)
            self.progressUpdate.emit(self.tr("File has been made executable (2/4 tasks finished)"))

            self.installer.mkSymLink(self.selectedFilePath, self.cmdName, self.fileDest, self.symLinkDir)
            self.progressUpdate.emit(self.tr("Program has been made executable (3/4 tasks finished)"))

            self.startMenuEntry.create(self.selectedFilePath, self.fileDest, self.userDir, self.programName, self.programDescr, self.programCategory)
            self.progressUpdate.emit(self.tr("Startmenu entry has been created (4/4 tasks finished)"))

# Wait 2s to let the user see that everything has been completed
            time.sleep(2)

            self.success.emit()

        except Exception as error:
            print(error)

            self.error.emit(str(error))