# This file provides the Python functionality for the Pyside6 GUI. This script is not suppossed to be run alone. 

# Adds support for Python 3.12
from __future__ import annotations

import os
import shutil
import subprocess
import stat
import tempfile
import shlex
import configparser
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

class Installer():
# Put every AppImage file into a list
    @staticmethod
    def listAppImageFiles(dir: Path) -> list:
        fileList = [file.path 
                    for file in os.scandir(dir) 
                    if file.name.endswith(".AppImage") and file.is_file(follow_symlinks=False)]

        fileList.sort()
        return fileList
    
# Get the content of the .desktop file in the AppImage to later create a startmenu entry    
    @staticmethod
    def getAppImageMetadata(file: str | Path) -> dict:
        workDir = Path(tempfile.mkdtemp())

        try:
# Extract the AppImage to a temporary directory
            subprocess.run(
                [str(file), "--appimage-extract", "*.desktop"],
                cwd=workDir,
                check=True,
                capture_output=True
            )

            squashfsRootDir = workDir / "squashfs-root"

            if not squashfsRootDir.exists():
                raise RuntimeError("Extraction failed: squashfs-root not found")
            
# AppImages contain a .desktop file with the same content as the .desktop file for the startmenu entry
            desktopFilePaths = list(squashfsRootDir.rglob("*.desktop"))

            if not desktopFilePaths:
                raise RuntimeError("No .desktop files found in AppImage")

            desktopFilePath = desktopFilePaths[0]

            metadata = {}

            with open(desktopFilePath, encoding="utf-8") as f:
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
    @staticmethod
    def moveFile(destDir: str | Path, file: str | Path) -> None:
        Path(destDir).mkdir(parents=True, exist_ok=True)

        shutil.move(file, destDir)

# Make the AppImage file executable
    @staticmethod
    def mkExec(appImageFile: str | Path) -> None:
        appImageFilePath = Path(appImageFile)
        
        appImageFilePath.chmod(appImageFilePath.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

# Create a symLink file, to execute the .AppImage file with a terminal command systemwide on the user's account
    @staticmethod
    def mkSymLink(appImagesDir: Path, symLinkDir: Path, appImageFile: str | Path, cmdName: str) -> None:
        newAppImageFilePath = appImagesDir / Path(appImageFile).name
        symLinkFilePath = symLinkDir / cmdName

        symLinkDir.mkdir(parents=True, exist_ok=True)

        symLinkFilePath.symlink_to(newAppImageFilePath)


class StartMenuEntry():
    @staticmethod
    def create(userDir: Path, appImagesDir: str | Path, desktopEntriesDir: Path, iconsDir: Path, appImageFile: str | Path, icon: str | Path | bool, programName: str , programDescription: str, programCategories: str) -> None:
        fileName = Path(appImageFile).name

        iconsDir.mkdir(parents=True, exist_ok=True)
        desktopEntriesDir.mkdir(parents=True, exist_ok=True)

# Only extract the icon if the user selected it or if there is no icon
        if not icon:

            workDir = Path(tempfile.mkdtemp())

# Extract the icon.png to a temporary squashfs directory
            subprocess.run(
                [str(appImagesDir / fileName), "--appimage-extract", "*.png"],
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

            iconPath = iconsDir / programIcon

# Only move the icon if it doesn't already exist; allows for multiple installations of the same program
            if not iconPath.exists():
                shutil.move(iconFile, iconsDir)
        
            shutil.rmtree(workDir, ignore_errors=True)
            print("new app icon")

        else:
            programIcon = Path(icon).name
            print("old app icon")

# .desktop file content
        desktopFile = "\n".join([
            "[Desktop Entry]",
            "Type=Application",
            f"Name={programName}",
            f"Comment={programDescription}",
            f'Exec="{appImagesDir}/{fileName}"',
            f"Icon={userDir}/.local/share/icons/{programIcon}",
            "Terminal=false",
            f"Categories={programCategories}",
        ])

        desktopEntryFile = desktopEntriesDir / f"{programName}.desktop"
        desktopEntryFile.write_text(desktopFile)

# Make the .desktop file executable
        subprocess.run(["chmod", "+x", desktopEntryFile],
            check=True,
            capture_output=True)

    def updateLaunchFlags(desktopFile: str, newFlags: str) -> None:
        config = configparser.ConfigParser(interpolation=None)
        config.optionxform = str
        config.read(desktopFile)

        execLine = config["Desktop Entry"]["Exec"]

        parts = shlex.split(execLine)
        appImagePath = parts[0] if parts else ""

        newExecLine = shlex.quote(appImagePath)
        flagsStripped = newFlags.strip()
        if flagsStripped:
            newExecLine += " " + flagsStripped

        config["Desktop Entry"]["Exec"] = newExecLine

        with open(desktopFile, "w") as f:
            config.write(f, space_around_delimiters=False)


class AppConfigReader():
    @staticmethod
    def getAppsMetadata(desktopEntriesDir: Path) -> list[AppsData]:
        appConfigs = []

        for entry in os.scandir(desktopEntriesDir):
            if not (entry.is_file(follow_symlinks=False) and entry.name.endswith(".desktop")):
                continue

            appName = ""
            appDescription = ""
            appImageFilePath = ""
            appImageFileSize = None
            appIconPath = ""
            desktopFilePath = entry.path
            categories = ""

            with open(entry.path, encoding="utf-8") as f:
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
                        valueParts = shlex.split(value)

                        appImageFilePath = valueParts[0]
# Mark not AppImage programs to later filter them out
                        if not appImageFilePath.endswith(".AppImage"):
                            appImageFilePath = False

                        launchFlags = valueParts[1:]

                    elif key == "Icon":
                        appIconPath = value

                    elif key == "Categories":
                        categories = value

# Size of the .AppImage file in bytes
                if appImageFilePath:
                    appImageFileSize = Path(appImageFilePath).stat().st_size

# Filter out incomplete or not AppImage installs
                if appName and appDescription and appImageFilePath and appImageFileSize:
                    appConfig = AppsData(
                        name=appName,
                        description=appDescription,
                        filePath=appImageFilePath,
                        fileSize=appImageFileSize,
                        iconFile=appIconPath,
                        desktopFile=desktopFilePath,
                        launchFlagString=launchFlags,
                        startMenuCategories=categories
                    )
                    appConfigs.append(appConfig)
                
        appConfigs.sort(key=lambda app: app.name.lower())

        return appConfigs

@dataclass
class AppsData():
    name: str
    description: str
    filePath: str
    fileSize: int
    iconFile: str
    desktopFile: str
    launchFlagString: str
    startMenuCategories: str


class Uninstaller():    
    @staticmethod
    def getSymlinkPath(symLinkDir: Path, appImageFile: str | Path) -> Path:
        for file in symLinkDir.iterdir():
            if file.is_symlink() and str(file.resolve()) == str(appImageFile):
                return file

    @staticmethod
    def rmvInstalledFile(filePath: str | Path) -> None:
        if Path(filePath).exists(follow_symlinks=False):
            os.remove(filePath)


class Logging():

    def __init__(self, logsDir: Path) -> None:
        self.logsDir = logsDir

        self.logsDir.mkdir(parents=True, exist_ok=True)
        currentDate = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.logFilePath = self.logsDir / (currentDate + "Log.txt")

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
    def addGeneralEntry(self, logContent: str):
        with open(self.logFilePath, "a") as f:
                f.write(str(logContent) + "\n")
                f.write("******************************************************************\n")

# Delete old log files after seven days
    def rmvOldLogs(self):
        timeNow = datetime.now()
        for log in self.logsDir.iterdir():
            if (timeNow - datetime.fromtimestamp(log.stat().st_mtime)).days > 7:
                log.unlink()