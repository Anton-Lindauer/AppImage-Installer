# This file contains QThreads; processes that run in parallel to the GUI. This script is not suppossed to be run alone. 

from PySide6.QtCore import QThread, Signal

from src.core.logic import Installer, StartmenuEntry, Uninstaller, AppMetadata

import time

class getAppImages(QThread):
    error = Signal(str)
    finished = Signal(list)

    def __init__(self, userDir):
        super().__init__()

        self.userDir = userDir

    def run(self):
        try:
            appImages = Installer.listFiles(self.userDir)

            self.finished.emit(appImages)
        except Exception as error:
            print(error)

            self.error.emit(str(error))

# Extracting a AppImage can take a while, so I temporarely put that code in a QThread (I know it's not the best way to do it like this)
class MetadataWorker(QThread):
    progressUpdate = Signal(str)
    error = Signal(str)
    finished = Signal(dict)

    def __init__(self, path, logger):
        super().__init__()
        self.path = path
        self.logger = logger

        self.installer = Installer(self.logger)

    def run(self):
        try:
            self.installer.mkExec(self.path)

            metadata = self.installer.getAppimageMetadata(self.path)
            self.finished.emit(metadata)

        except Exception as error:
            print(error)

            self.error.emit(str(error))

# Class for the installation process
class InstallWorker(QThread):
    progressUpdate = Signal(str)
    error = Signal(str)
    finished = Signal()

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
            self.progressUpdate.emit(self.tr("Moved AppImage file (1/3 tasks finished)"))

            self.installer.mkSymLink(self.selectedFilePath, self.cmdName, self.fileDest, self.symLinkDir)
            self.progressUpdate.emit(self.tr("Program has been made executable (2/3 tasks finished)"))

            self.startMenuEntry.create(self.selectedFilePath, self.fileDest, self.userDir, self.programName, self.programDescr, self.programCategory)
            self.progressUpdate.emit(self.tr("Startmenu entry has been created (3/3 tasks finished)"))

            self.progressUpdate.emit(self.tr("Installation finished"))

# Wait 2s to let the user see that everything has been completed
            time.sleep(1)

            self.finished.emit()

        except Exception as error:
            print(error)

            self.error.emit(str(error))



class getAppConfigs(QThread):
    error = Signal(str)
    progressUpdate = Signal(list)
    finished = Signal(list)

    def __init__(self, desktopEntriesDir):
        super().__init__()

        self.desktopEntriesDir = desktopEntriesDir

    def run(self):
        try:
            appsMetadata = Uninstaller.getInstalledMetadata(self.desktopEntriesDir)
            self.progressUpdate.emit(appsMetadata)
            
            appsConfigList = AppMetadata.getAppsMetadata(self.desktopEntriesDir)

            self.finished.emit(appsConfigList)

        except Exception as error:
            print(error)
            self.error.emit(str(error))

class UninstallWorker(QThread):
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