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
    def mkSymLink(self, selectedFilePath, cmdName, fileDest, userDir):
        symLinkDir = userDir / ".local/bin/"
        path = fileDest / Path(selectedFilePath).name
        symLinkPath = Path(symLinkDir) / cmdName

        Path(symLinkDir).mkdir(parents=True, exist_ok=True)

        symLinkPath.symlink_to(path)

        logContent = f"Symlink {userDir}/.local/bin/{cmdName} has been created"
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
        subprocess.run(["mv" , next(Path("squashfs-root").glob("*.png")), iconsDir], check=True, capture_output=True, text=True)
        logContent = f"Moved icon to {iconsDir}"
        self.logger.addCmdEntry(logContent)
        
# Delete squashfs-root; This is a temporary directory and the app icon is extracted to this directory
        subprocess.run(["rm", "-rf", Path("squashfs-root")], check=True, capture_output=True, text=True)
        logContent = "Deleted temporary directory squashfs-root"
        self.logger.addCmdEntry(logContent)

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
        subprocess.run(["chmod", "+x", desktopEntryFile], check=True, capture_output=True, text=True)
        logContent = f"Made {desktopEntryFile} executable"
        self.logger.addCmdEntry(logContent)

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

    def addCmdEntry(self, logContent):
        with open(self.logFilePath, "a") as f:
            if logContent.stderr:
                f.write(logContent.stderr + "\n")
                f.write("******************************************************************\n")

            if logContent.stdout:
                f.write(logContent.stdout + "\n")
                f.write("******************************************************************\n")
        
    def addGeneralEntry(self, logContent):
        with open(self.logFilePath, "a") as f:
                f.write(logContent + "\n")
                f.write("******************************************************************\n")

    def rmvOldLogs(self):
        timeNow = datetime.now()
        for log in Path(self.logDir).iterdir():
            if (timeNow - datetime.fromtimestamp(log.stat().st_mtime)).days > 7:
                log.unlink()