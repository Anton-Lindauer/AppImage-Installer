# This file contains QThreads; processes that run in parallel to the GUI. This script is not suppossed to be run alone. 
import faulthandler
faulthandler.enable()

from PySide6.QtCore import QThread, Signal, QSettings

from src.core.logic import Installer, StartMenuEntry, Uninstaller, AppConfigReader

import time
from pathlib import Path

############################################### Tab 1 QThreads ###############################################
# Returns a list of all AppImage file paths in the Downloads directory
class AppImageListThread(QThread):
    error = Signal(str)
    result = Signal(list)

    def __init__(self, logger, downloadsDir: Path) -> list:
        super().__init__()

        self.logger = logger
        self.settings = QSettings("Anton-Lindauer", "AppImage-Installer")
        
        self.downloadsDir = downloadsDir

    def run(self):
        try:
# Old logs should be removed when the program starts
# A seperate QThread would be the perfect solution, but it's unnecessary imo
# Checking for old logs when the list is refreshed should be so fast that nobody notices
            if self.settings.value("autoDelete", True, type=bool):
                self.logger.rmvOldLogs()

            appImages = Installer.listAppImageFiles(self.downloadsDir)
            self.logger.addGeneralEntry(appImages)

            self.result.emit(appImages)
        except Exception as error:
            print(error)

            self.error.emit(str(error))

# Extracts the metadata of the selected AppImage file; the metadata is inside a .desktop file in the AppImage file
class MetadataThread(QThread):
    result = Signal(dict)
    error = Signal(str)

    def __init__(self, logger, path: str | Path) -> list:
        super().__init__()

        self.logger = logger

        self.appImageFile = path

    def run(self):
        try:
            Installer.mkExec(self.appImageFile)
            self.logger.addGeneralEntry(f"Made {self.appImageFile} executable")

            metadata = Installer.getAppImageMetadata(self.appImageFile)
            self.logger.addGeneralEntry(f"Extracted \n{metadata}")

            self.result.emit(metadata)

        except Exception as error:
            print(error)

            self.error.emit(str(error))

# All functionality to actually install the AppImage
class InstallThread(QThread):
    progressUpdate = Signal(str)
    error = Signal(str)

    def __init__(self, logger, userDir: Path, appImagesDir: Path, symLinkDir: Path, desktopEntriesDir: Path, iconsDir: Path, appImageFile: str, programName: str, programDescription: str, programCategories: str, cmdName: str) -> str:
        super().__init__()

        self.logger = logger

        self.userDir = userDir
        self.appImagesDir = appImagesDir
        self.symLinkDir = symLinkDir
        self.desktopEntriesDir = desktopEntriesDir
        self.iconsDir = iconsDir
        self.appImageFile = appImageFile
        self.programName = programName
        self.programDescription = programDescription
        self.programCategories = programCategories
        self.cmdName = cmdName
        self.icon = False

        self.newAppImageFilePath = appImagesDir / Path(self.appImageFile).name
        self.symLinkFilePath = self.symLinkDir / self.cmdName

# All installation steps with progress updates
    def run(self):
        try:
            Installer.moveFile(self.appImagesDir, self.appImageFile)
            self.logger.addGeneralEntry(f"Moved {self.appImageFile} to {self.appImagesDir}")
            self.progressUpdate.emit(self.tr("Moved AppImage file (1/3 tasks finished)"))

            Installer.mkSymLink(self.appImagesDir, self.symLinkDir, self.appImageFile, self.cmdName)
            self.logger.addGeneralEntry(f"Created symlink {self.cmdName} in {self.symLinkDir}")
            self.progressUpdate.emit(self.tr("Program has been made executable (2/3 tasks finished)"))

            StartMenuEntry.create(self.userDir, self.appImagesDir, self.desktopEntriesDir, self.iconsDir, self.appImageFile, self.icon, self.programName, self.programDescription, self.programCategories)
            self.logger.addGeneralEntry(f"Created start menu entry for {self.programName}")
            self.progressUpdate.emit(self.tr("Start menu entry has been created (3/3 tasks finished)"))

            self.progressUpdate.emit(self.tr("Installation finished"))

# Wait 1s to let the user see that everything has been completed
            time.sleep(1)

        except Exception as error:
            print(error)

            self.error.emit(str(error))



############################################### Tab 2 QThreads ###############################################
# Extract the metadata from all installed AppImage programs; Metadata is stored in the .desktop file that is used as startmenu entry
class AppConfigsThread(QThread):
    error = Signal(str)
    result = Signal(list)

    def __init__(self, logger, desktopEntriesDir: Path) -> list:
        super().__init__()

        self.logger = logger

        self.desktopEntriesDir = desktopEntriesDir

    def run(self):
        try:
            appConfigs = AppConfigReader.getAppsMetadata(self.desktopEntriesDir)
            self.logger.addGeneralEntry(f"Extracted AppImage apps configs: \n{appConfigs}")

            self.result.emit(appConfigs)

        except Exception as error:
            print(error)

            self.error.emit(str(error))

# All functionality to actually uninstall a picked AppImage program
class UninstallThread(QThread):
    progressUpdate = Signal(str)
    error = Signal(str)

    def __init__(self, logger, symLinkDir: Path, appImageFile: str | Path, desktopFile: str | Path, icon: str | Path | bool):
        super().__init__()

        self.logger = logger

        self.symLinkDir = symLinkDir
        self.appImageFile = appImageFile
        self.desktopFile = desktopFile
        self.icon = icon

    def run(self):
        try:
            symLinkFilePath = Uninstaller.getSymlinkPath(self.symLinkDir, self.appImageFile)

            Uninstaller.rmvInstalledFile(symLinkFilePath)
            self.logger.addGeneralEntry(f"Permanently removed {symLinkFilePath}")
            self.progressUpdate.emit(self.tr("Removed symlink"))

            Uninstaller.rmvInstalledFile(self.desktopFile)
            self.logger.addGeneralEntry(f"Permanently removed {self.desktopFile}")
            self.progressUpdate.emit(self.tr("Removed start menu entry"))

            Uninstaller.rmvInstalledFile(self.appImageFile)
            self.logger.addGeneralEntry(f"Permanently removed {self.appImageFile}")
            self.progressUpdate.emit(self.tr("Removed AppImage file"))

            if self.icon:
                Uninstaller.rmvInstalledFile(self.icon)
                self.logger.addGeneralEntry(f"Permanently removed {self.icon}")
                self.progressUpdate.emit(self.tr("Removed AppImage icon"))

            self.progressUpdate.emit(self.tr("Uninstallation finished"))

            time.sleep(1)

        except Exception as error:
            print(error)

            self.error.emit(str(error))

class UpdateAppConfigThread(QThread):
    error = Signal(str)

    def __init__(self, logger, userDir: Path, appImagesDir: Path, symLinkDir: Path, desktopEntriesDir: Path, iconsDir: Path, newAppImageFile: str, oldAppImageFile: str, oldDesktopFile: str, newAppName: str, newAppDescription: str, newLaunchConfig: str, categories: str, icon: str | bool):
        super().__init__()

        self.logger = logger

        self.userDir = userDir
        self.appImagesDir = appImagesDir
        self.symLinkDir = symLinkDir
        self.desktopEntriesDir = desktopEntriesDir
        self.iconsDir = iconsDir
        self.newAppImageFile = newAppImageFile
        self.oldAppImage = oldAppImageFile
        self.oldDesktopFile = oldDesktopFile
        self.newAppName = newAppName
        self.newAppDescription = newAppDescription
        self.newLaunchConfig = newLaunchConfig
        self.categories = categories
        self.icon = icon

        self.newAppImageFilePath = self.appImagesDir / Path(self.newAppImageFile).name
        self.newDesktopFilePath = self.desktopEntriesDir / f"{self.newAppName}.desktop"

    def run(self):
        try:
            Uninstaller.rmvInstalledFile(self.oldDesktopFile)
            self.logger.addGeneralEntry(f"Permanently removed {self.oldDesktopFile}")

            if self.newAppImageFile:
                symLinkFilePath = Uninstaller.getSymlinkPath(self.symLinkDir, self.oldAppImage)
                cmdName = symLinkFilePath.name

                Uninstaller.rmvInstalledFile(self.oldAppImage)
                self.logger.addGeneralEntry(f"Permanently removed {self.oldAppImage}")

                Uninstaller.rmvInstalledFile(symLinkFilePath)
                self.logger.addGeneralEntry(f"Permanently removed {symLinkFilePath}")

                Installer.mkExec(self.newAppImageFile)
                self.logger.addGeneralEntry(f"Made {self.newAppImageFile} executable")
            
                Installer.moveFile(self.appImagesDir, self.newAppImageFile)
                self.logger.addGeneralEntry(f"Moved {self.newAppImageFile} to {self.appImagesDir}")

                Installer.mkSymLink(self.appImagesDir, self.symLinkDir, self.newAppImageFile, cmdName)
                self.logger.addGeneralEntry(f"Created symlink {cmdName} in {self.symLinkDir}")

                StartMenuEntry.create(self.userDir, self.appImagesDir, self.desktopEntriesDir, self.iconsDir, self.newAppImageFilePath, self.icon, self.newAppName, self.newAppDescription, self.categories)
                self.logger.addGeneralEntry(f"Created startmenu entry for {self.newAppName}")
            else:
                StartMenuEntry.create(self.userDir, self.appImagesDir, self.desktopEntriesDir, self.iconsDir, self.oldAppImage, self.icon, self.newAppName, self.newAppDescription, self.categories)
                self.logger.addGeneralEntry(f"Created startmenu entry for {self.newAppName}")

            StartMenuEntry.updateLaunchFlags(self.newDesktopFilePath, self.newLaunchConfig)
            self.logger.addGeneralEntry(f"Updated {self.newAppName} launch flags to {self.newLaunchConfig}")

        except Exception as error:
            print(error)

            self.error.emit(str(error))