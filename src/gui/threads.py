# This file contains QThreads; processes that run in parallel to the GUI. This script is not suppossed to be run alone. 

from PySide6.QtCore import QThread, Signal

from src.core.logic import Installer, StartmenuEntry
from src.gui.components import PrepInstall

import time

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
            metadata = Installer.getAppimageMetadata(self.path)
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
            self.progressUpdate.emit(self.tr("File moved successfully (1/4 tasks finished)"))

            self.installer.mkExec(self.selectedFilePath, self.fileDest)
            self.progressUpdate.emit(self.tr("File has been made executable (2/4 tasks finished)"))

            self.installer.mkSymLink(self.selectedFilePath, self.cmdName, self.fileDest, self.symLinkDir)
            self.progressUpdate.emit(self.tr("Program has been made executable (3/4 tasks finished)"))

            self.startMenuEntry.create(self.selectedFilePath, self.fileDest, self.userDir, self.programName, self.programDescr, self.programCategory)
            self.progressUpdate.emit(self.tr("Startmenu entry has been created (4/4 tasks finished)"))

# Wait 2s to let the user see that everything has been completed
            time.sleep(1)

            self.finished.emit()

        except Exception as error:
            print(error)

            self.error.emit(str(error))