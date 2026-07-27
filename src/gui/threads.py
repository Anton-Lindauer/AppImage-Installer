# This file contains QThreads; processes that run in parallel to the GUI. This script is not suppossed to be run alone. 

from PySide6.QtCore import QThread, Signal

from src.core.logic import Installer, StartMenuEntry, Uninstaller, AppConfigReader

import time

############################################### Tab 1 QThreads ###############################################
# Returns a list of all AppImage file paths in the Downloads directory
class AppImageListThread(QThread):
    error = Signal(str)
    finished = Signal(list)

    def __init__(self, logger, userDir):
        super().__init__()

        self.logger = logger
        self.userDir = userDir

    def run(self):
        try:
            appImages = Installer.listFiles(self.userDir)
            self.logger.addGeneralEntry(appImages)

            self.finished.emit(appImages)
        except Exception as error:
            print(error)

            self.error.emit(str(error))

# Extracts the metadata of the selected AppImage file; the metadata is inside a .desktop file in the AppImage file
class MetadataThread(QThread):
    progressUpdate = Signal(str)
    error = Signal(str)
    finished = Signal(dict)

    def __init__(self, logger, path):
        super().__init__()

        self.logger = logger
        self.appImagePath = path

    def run(self):
        try:
            Installer.mkExec(self.appImagePath)
            self.logger.addGeneralEntry(f"Made {self.appImagePath} executable")

            metadata = Installer.getAppImageMetadata(self.appImagePath)
            self.logger.addGeneralEntry(f"Extracted \n{metadata}")
            self.finished.emit(metadata)

        except Exception as error:
            print(error)

            self.error.emit(str(error))

# All functionality to actually install the AppImage
class InstallThread(QThread):
    progressUpdate = Signal(str)
    error = Signal(str)
    finished = Signal()

    def __init__(self, logger, selectedFilePath, appImagesDir, userDir, programName,programDescr, programCategory, cmdName, symLinkDir):
        super().__init__()

        self.logger = logger

        self.selectedFilePath = selectedFilePath
        self.appImagesDir = appImagesDir     
        self.userDir = userDir
        self.programName = programName
        self.programDescription = programDescr
        self.programCategory = programCategory
        self.cmdName = cmdName
        self.symLinkDir = symLinkDir

# All installation steps with progress updates
    def run(self):
        try:
            Installer.moveFile(self.selectedFilePath, self.appImagesDir)
            self.logger.addGeneralEntry(f"Moved {self.selectedFilePath} to {self.appImagesDir}")
            self.progressUpdate.emit(self.tr("Moved AppImage file (1/3 tasks finished)"))

            Installer.mkSymLink(self.selectedFilePath, self.cmdName, self.appImagesDir, self.symLinkDir)
            self.logger.addGeneralEntry(f"Created symlink {self.cmdName} in {self.symLinkDir}")
            self.progressUpdate.emit(self.tr("Program has been made executable (2/3 tasks finished)"))

            StartMenuEntry.create(self.selectedFilePath, self.appImagesDir, self.userDir, self.programName, self.programDescription, self.programCategory)
            self.logger.addGeneralEntry(f"Created startmenu entry for {self.programName}")
            self.progressUpdate.emit(self.tr("Startmenu entry has been created (3/3 tasks finished)"))

            self.progressUpdate.emit(self.tr("Installation finished"))

# Wait 1s to let the user see that everything has been completed
            time.sleep(1)

            self.finished.emit()

        except Exception as error:
            print(error)

            self.error.emit(str(error))



############################################### Tab 2 QThreads ###############################################
# Extract the metadata from all installed AppImage programs; Metadata is stored in the .desktop file that is used as startmenu entry
class AppConfigsThread(QThread):
    error = Signal(str)
    finished = Signal(list)

    def __init__(self, logger, desktopEntriesDir):
        super().__init__()

        self.logger = logger
        self.desktopEntriesDir = desktopEntriesDir

    def run(self):
        try:
            appConfigsList = AppConfigReader.getAppsMetadata(self.desktopEntriesDir)
            self.logger.addGeneralEntry(f"Data 2: {appConfigsList}")

            self.finished.emit(appConfigsList)

        except Exception as error:
            print(error)

            self.error.emit(str(error))

# All functionality to actually uninstall a picked AppImage program
class UninstallThread(QThread):
    progressUpdate = Signal(str)
    error = Signal(str)
    finished = Signal()

    def __init__(self, logger, selectedAppPath, symLinkDir, desktopFilePath, ):
        super().__init__()

        self.logger = logger
        self.selectedAppPath = selectedAppPath
        self.symLinkDir = symLinkDir
        self.desktopFilePath = desktopFilePath

    def run(self):
        try:
            symLinkFilePath = Uninstaller.getSymlinkPath(self.selectedAppPath, self.symLinkDir)

            Uninstaller.rmvInstalledFiles(symLinkFilePath)
            self.logger.addGeneralEntry(f"Permanently removed {symLinkFilePath}")
            self.progressUpdate.emit(self.tr("Removed symlink"))

            Uninstaller.rmvInstalledFiles(self.desktopFilePath)
            self.logger.addGeneralEntry(f"Permanently removed {self.desktopFilePath}")
            self.progressUpdate.emit(self.tr("Removed startmenu entry"))

            Uninstaller.rmvInstalledFiles(self.selectedAppPath)
            self.logger.addGeneralEntry(f"Permanently removed {self.selectedAppPath}")
            self.progressUpdate.emit(self.tr("Removed AppImage file"))

            self.progressUpdate.emit(self.tr("Uninstallation finished"))

            time.sleep(1)

            self.finished.emit()

        except Exception as error:
            print(error)

            self.error.emit(str(error))