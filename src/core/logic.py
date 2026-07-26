# This file provides the Python functionality for the Pyside6 GUI. This script is not suppossed to be run alone. 

import os
import shutil
import subprocess
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

class Installer():
# Put every AppImage file into a list
    @staticmethod
    def listFiles(userDir):
        downloadsDir = userDir / "Downloads"

        fileList = [file.path 
                    for file in os.scandir(downloadsDir) 
                    if file.name[-9:] == ".AppImage" and file.is_file(follow_symlinks=False)]

        fileList.sort()
        return fileList
    
# Get the content of the .desktop file in the AppImage to later create a startmenu entry    
    def getAppimageMetadata(self, filePath):
        workDir = Path(tempfile.mkdtemp())

        try:
# Extract the AppImage to a temporary directory
            subprocess.run(
                [str(filePath), "--appimage-extract", "*.desktop"],
                cwd=workDir,
                check=True,
                capture_output=True
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

            return {
                "exec": metadata.get("Exec", ""),
                "name": metadata.get("Name", ""),
                "comment": metadata.get("Comment", ""),
                "categories": metadata.get("Categories", "")
            }
       
        finally:
            shutil.rmtree(workDir, ignore_errors=True)
    
# Move the AppImage File to the right directory
    def moveFile(self, selectedFilePath, fileDest):
        Path(fileDest).mkdir(parents=True, exist_ok=True)

        shutil.move(selectedFilePath, fileDest)

# Make the AppImage file executable
    def mkExec(self, path):
        path = Path(path)

        path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

# Create a symLink file, to execute the .AppImage file with a terminal command systemwide on the user's account
    def mkSymLink(self, selectedFilePath, cmdName, fileDest, symLinkDir):
        path = fileDest / Path(selectedFilePath).name
        symLinkPath = Path(symLinkDir) / cmdName

        Path(symLinkDir).mkdir(parents=True, exist_ok=True)

        symLinkPath.symlink_to(path)

class StartmenuEntry():
    def create(self, selectedFilePath, fileDest, userDir, programName, programDescr, programCategory):
        fileName = Path(selectedFilePath).name
        iconsDir = userDir / ".local/share/icons"
        applicationsDir = userDir / ".local/share/applications"

        iconsDir.mkdir(parents=True, exist_ok=True)
        applicationsDir.mkdir(parents=True, exist_ok=True)

        workDir = Path(tempfile.mkdtemp())

# Extract the icon.png to a temporary squashfs directory
        subprocess.run(
            [str(userDir / "AppImages" / fileName), "--appimage-extract", "*.png"],
            cwd=workDir,
            check=True,
            capture_output=True,
            text=True
        )
        
        squashfsRoot = workDir / "squashfs-root"

        if not squashfsRoot.exists():
            raise RuntimeError("Extraction failed: squashfs-root not found")
            
# AppImages contain a icon.png which will be used as program icon 
        iconFile = next(squashfsRoot.rglob("*.png"), None)

        if iconFile is None:
            raise RuntimeError("No .png files found in AppImage")

        programIcon = Path(iconFile).name

        iconPath = Path(iconsDir / programIcon)

# Only move the icon if it doesn't already exist; allows for multiple installations of the same program
        if not  iconPath.exists():
            shutil.move(iconFile, iconsDir)
        
        shutil.rmtree(workDir, ignore_errors=True)

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

        desktopEntryFile = applicationsDir / f"{programName}.desktop"
        desktopEntryFile.write_text(desktopFile)

# Make the .desktop file executable
        subprocess.run(["chmod", "+x", desktopEntryFile],
            check=True,
            capture_output=True)

class AppMetadata():
    def getAppsMetadata(desktopPath) -> list[AppsData]:
        appsMetadata = []

        for file in os.scandir(desktopPath):
            if not (file.is_file(follow_symlinks=False) and file.name[-8:] == ".desktop"):
                continue

            appName = ""
            appDescription = ""
            appImageFilePath = ""
            appImageFileSize = None

            with open(file.path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()

                    if "=" not in line:
                        continue

                    key, value = line.split("=", 1)

                    if key == "Name":
                        appName = value
                    elif key == "Comment":
                        appDescription = value
                    elif key == "Exec":
                        appImageFilePath = value
# Mark not AppImage programs to later filter them out
                        if not value.endswith(".AppImage"):
                            appImageFilePath = False

# Size of the .AppImage file in bytes
                    if appImageFilePath:
                        appImageFileSize = Path(appImageFilePath).stat().st_size

# Filter out incomplete or not AppImage installs
                if appName and appDescription and appImageFilePath and appImageFileSize:
                    appMetadata = AppsData(
                        name=appName,
                        description=appDescription,
                        filePath=appImageFilePath,
                        fileSize=appImageFileSize
                    )
                    appsMetadata.append(appMetadata)
                
        appsMetadata.sort(key=lambda app: app.name.lower())

        return appsMetadata

@dataclass
class AppsData():
    name: str
    description: str
    filePath: str
    fileSize: int


class Uninstaller():
# Store metadata from .desktop files in a list of dataclasses
    @staticmethod
    def getInstalledMetadata(desktopPath) -> list[UninstallData]:
        installedProgramsMetadata = []
        
        for file in os.scandir(desktopPath):
            if not (file.is_file(follow_symlinks=False) and file.name[-8:] == ".desktop"):
                continue

            programName = ""
            execPath = ""
            iconFilePath = ""
            desktopFilePath = file.path

            with open(file.path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()

                    if "=" not in line:
                        continue

                    key, value = line.split("=", 1)
                    
                    if key == "Name":
                        programName = value
                    elif key == "Exec":
                        execPath = value
# Mark not AppImage programs to later filter them out
                        if not value.endswith(".AppImage"):
                            execPath = False
                    elif key == "Icon":
                        iconFilePath = value

# Filter out incomplete or not AppImage installs
                if programName and execPath and iconFilePath and desktopFilePath:
                    programMetadata = UninstallData(
                        name=programName,
                        path=execPath,
                        iconPath=iconFilePath,
                        desktopPath=desktopFilePath
                    )
                    installedProgramsMetadata.append(programMetadata)
                
        installedProgramsMetadata.sort(key=lambda app: app.name.lower())

        return installedProgramsMetadata
    
# Returns the path of the terminal symlink of the selected AppImage
    @staticmethod
    def getSymlinkPath(installedPath, symLinkDir):
        for file in symLinkDir.iterdir():
            if file.is_symlink() and str(file.resolve()) == str(installedPath):
                return file

    @staticmethod
    def rmvInstalledFiles(path):
        if path == None:
            return
        
        os.remove(path)

# Stores the content of each .desktop file for the uninstallation
@dataclass
class UninstallData:
    name: str
    path: str
    iconPath: str
    desktopPath: str

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
                f.write(str(logContent) + "\n")
                f.write("******************************************************************\n")

# Delete old log files after seven days
    def rmvOldLogs(self):
        timeNow = datetime.now()
        for log in Path(self.logDir).iterdir():
            if (timeNow - datetime.fromtimestamp(log.stat().st_mtime)).days > 7:
                log.unlink()