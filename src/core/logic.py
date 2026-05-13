# This file provides the Python functionality for the Pyside6 GUI. This script is not suppossed to be run alone. 

import os
import shutil
import subprocess
import stat
from pathlib import Path
from datetime import datetime

class Installer():
    
    def __init__(self, logger):
        self.logger = logger

# Put every AppImage file into a list
    @staticmethod
    def listFiles(userDir):
        downloadsDir = userDir / "Downloads"

        fileList = [file.path 
                    for file in os.scandir(downloadsDir) 
                    if file.name[-9:] == ".AppImage" and file.is_file(follow_symlinks=False)]

        fileList.sort()
        return fileList
       
# Move the AppImage File to the right directory
    def moveFile(self, selectedFilePath, fileDest):
        Path(fileDest).mkdir(parents=True, exist_ok=True)

        shutil.move(selectedFilePath, fileDest)

        logContent = f"File successfully moved to {fileDest}"
        self.logger.addGeneralEntry(logContent)

# Make the AppImage file executable
    def mkExec(self, selectedFilePath, fileDest):
        fileName = Path(selectedFilePath).name
        path = fileDest / fileName
        path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

        logContent = f"AppImage file at {path} has been made executable"
        self.logger.addGeneralEntry(logContent)

# Create a symLink file, to execute the .AppImage file with a terminal command systemwide on the user's account
    def mkSymLink(self, selectedFilePath, cmdName, fileDest, symLinkDir):
        path = fileDest / Path(selectedFilePath).name
        symLinkPath = Path(symLinkDir) / cmdName

        Path(symLinkDir).mkdir(parents=True, exist_ok=True)

        symLinkPath.symlink_to(path)

        logContent = f"Symlink {symLinkDir}/{cmdName} has been created"
        self.logger.addGeneralEntry(logContent)

class StartmenuEntry():

    def __init__(self, logger):
        self.logger = logger

    def create(self, selectedFilePath, fileDest, userDir, programName, programDescr, programCategory):
        fileName = Path(selectedFilePath).name
        iconsDir = userDir / ".local/share/icons"
        applicationsDir = userDir / ".local/share/applications"

        Path(iconsDir).mkdir(parents=True, exist_ok=True)
        Path(applicationsDir).mkdir(parents=True, exist_ok=True)

# Extract AppImage in to the temporary directory
        logContent = subprocess.run([f"{fileDest}/{fileName}", "--appimage-extract"], check=True, capture_output=True, text=True)
        self.logger.addCmdEntry(logContent)

# Find the name of the icon.png file; Used later in the .desktop file 
        programIcon = Path(next(Path("squashfs-root").glob("*.png"))).name
        logContent = "Found the icon file name"
        self.logger.addGeneralEntry(logContent)
        
# Copy icon to icons directory
        subprocess.run(["mv" , next(Path("squashfs-root").glob("*.png")), iconsDir], check=True)
        logContent = f"Moved icon to {iconsDir}"
        self.logger.addGeneralEntry(logContent)
        
# Delete squashfs-root; This is a temporary directory and the app icon is extracted to this directory
        subprocess.run(["rm", "-rf", Path("squashfs-root")], check=True)
        logContent = "Deleted temporary directory squashfs-root"
        self.logger.addGeneralEntry(logContent)

# .desktop file content
        desktopFile = f"""[Desktop Entry]
                        Type=Application
                        Name={programName}
                        Comment={programDescr}
                        Exec={fileDest}/{fileName}
                        Icon={userDir}/.local/share/icons/{programIcon}
                        Terminal=false
                        Categories={programCategory}
                        """
        logContent = "Gathered all data for .desktop file creation"
        self.logger.addGeneralEntry(logContent)

        desktopEntryFile = applicationsDir / f"{programName}.desktop"
        desktopEntryFile.write_text(desktopFile)
        logContent = "Finished creating the .desktop file"
        self.logger.addGeneralEntry(logContent)

# Make the .desktop file executable
        subprocess.run(["chmod", "+x", desktopEntryFile], check=True)
        logContent = f"Made {desktopEntryFile} executable"
        self.logger.addGeneralEntry(logContent)

class Uninstaller():
# Returns a list with all AppImages in the AppImages directory
    @staticmethod
    def listInstalls(installDir):
        fileList = [file.path 
                    for file in os.scandir(installDir) 
                    if file.name[-9:] == ".AppImage" and file.is_file(follow_symlinks=False)]

        fileList.sort()
        return fileList
    
# Returns the path of the terminal symlink of the selected AppImage
    @staticmethod
    def listSymlinks(installedPath, symLinkDir):
        for file in symLinkDir.iterdir():
            if file.is_symlink() and str(file.resolve()) == str(installedPath):
                return file

# Returns the path of the startmenu .desktop file of the selected AppImage
    @staticmethod
    def findDesktopFile(desktopDir, appImagePath):
        for file in os.scandir(desktopDir):
            if not (file.name.endswith(".desktop") and file.is_file(follow_symlinks=False)):
                continue

            with open(file) as f: 
                for line in f:
                    line = line.strip()

                    if not line.startswith("Exec="):
                        continue

                    linkPath = line.removeprefix("Exec=")

                    if linkPath == appImagePath:
                        return file.path
                
    def rmvInstalledFiles(path):
        if path == None:
            return
        
        os.remove(path)

class Logging():

    def __init__(self):
        self.logDir = Path.home() / ".local" / "share" / "AppImage-Installer" / "logs"
        self.logDir.mkdir(parents=True, exist_ok=True)
        currentDate = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.logFilePath = self.logDir / (currentDate + "Log.txt")

        with open(self.logFilePath, "a") as f:
            f.write("These log files are only there to store an error message if one occurs.\n")
            f.write("Just ignore them if no error occured.\n")
            f.write("******************************************************************\n")

# Logs a terminal output of a terminal command
    def addCmdEntry(self, logContent):
        with open(self.logFilePath, "a") as f:
            if logContent.stderr:
                f.write(logContent.stderr + "\n")
                f.write("******************************************************************\n")

            if logContent.stdout:
                f.write(logContent.stdout + "\n")
                f.write("******************************************************************\n")

# Logs custom messages
    def addGeneralEntry(self, logContent):
        with open(self.logFilePath, "a") as f:
                f.write(logContent + "\n")
                f.write("******************************************************************\n")

# Delete old log files after seven days
    def rmvOldLogs(self):
        timeNow = datetime.now()
        for log in Path(self.logDir).iterdir():
            if (timeNow - datetime.fromtimestamp(log.stat().st_mtime)).days > 7:
                log.unlink()