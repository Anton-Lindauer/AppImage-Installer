# This file provides the Python functionality for the Pyside6 GUI. This script is not suppossed to be run alone. 

import os
import shutil
import subprocess
import pathlib
from pathlib import Path
from datetime import datetime

class Installer():
    
    def __init__(self, logger):
        self.logger = logger

# Put every AppImage file into a list
    @staticmethod
    def listFiles(userDir):
        downloadsDir = os.path.join(str(userDir), "Downloads")

        fileList = [file.path 
                    for file in os.scandir(downloadsDir) 
                    if file.name[-9:] == ".AppImage" and file.is_file(follow_symlinks=False)]

        fileList.sort()
        return fileList
       
# Move the AppImage File to the right directory
    def moveFile(self, selectedFilePath, fileDest):
        try:
            if not os.path.isdir(fileDest):
                os.mkdir(fileDest)
# Moving the .AppImage file
            shutil.move(selectedFilePath, fileDest)

            logContent = f"File successfully moved to {fileDest}"
            self.logger.addGeneralEntry(logContent)

        except Exception as error:
            self.logger.addGeneralEntry(str(error))
            raise Exception(error)

# Make the AppImage file executable
    def mkExec(self, selectedFilePath, fileDest):
        fileName = os.path.basename(selectedFilePath)
        path = f"{fileDest}/{fileName}"
        logContent = subprocess.run([f"chmod", "+x", path], check=True, capture_output=True, text=True)

        self.logger.addCmdEntry(logContent)

# Create a symLink file, to execute the .AppImage file with a terminal command systemwide on the user's account
    def mkSymLink(self, selectedFilePath, cmdName, fileDest, userDir):
        if not os.path.isdir(f"{userDir}/.local/bin/"):
            os.mkdir(f"{userDir}/.local/bin/")

        logContent = subprocess.run(["ln", "-s", f"{fileDest}/{os.path.basename(selectedFilePath)}", f"{userDir}/.local/bin/"+cmdName], check=True, capture_output=True, text=True)

        self.logger.addCmdEntry(logContent)

class StartmenuEntry():

    def __init__(self, logger):
        self.logger = logger

    def create(self, selectedFilePath, fileDest, userDir, programName, programDescr, programCategory):
        fileName = os.path.basename(selectedFilePath)

# Extract AppImage in to the temporary directory
        logContent = subprocess.run([f"{fileDest}/{fileName}", "--appimage-extract"], check=True, capture_output=True, text=True)
        self.logger.addCmdEntry(logContent)
        print("Finished extracting data from the .AppImage file")
        
        try:
            if not os.path.isdir(fileDest):
                os.mkdir(f"{userDir}/.local/share/icons")
                print(f"Created {userDir}/.local/share/icons")
                logContent = f"Created {userDir}/.local/share/icons"
                self.logger.addGeneralEntry(logContent)
            else:
                print(f"{userDir}/.local/share/icons/ has been found")

# Find the name of the icon.png file; Used later in the .desktop file 
            programIcon = os.path.basename(next(pathlib.Path("squashfs-root").glob("*.png")))

            logContent = "Found the icon file name"
            self.logger.addGeneralEntry(logContent)

            if not os.path.isdir(f"{userDir}/.local/share/applications/"):
                os.mkdir(f"{userDir}/.local/share/applications")
                print(f"Created {userDir}/.local/share/applications")
                logContent = f"Created {userDir}/.local/share/applications"
                self.logger.addGeneralEntry(logContent)
            else:
                print(f"{userDir}/.local/share/applications has been found")
                logContent = f"{userDir}/.local/share/applications has been found"
                self.logger.addGeneralEntry(logContent)
        
        except Exception as error:
            self.logger.addGeneralEntry(str(error))
            raise Exception(error)
        
# Copy Icon to icons directory
        logContent = subprocess.run(["cp" , next(pathlib.Path("squashfs-root").glob("*.png")), f"{userDir}/.local/share/icons"], check=True, capture_output=True, text=True)
        self.logger.addCmdEntry(logContent)
        print("Finished copying the icon to the icons directory")
        
# Delete squashfs-root; This is a temporary directory and the app icon is extracted to this directory
        logContent = subprocess.run(["rm", "-rf", pathlib.Path("squashfs-root")], check=True, capture_output=True, text=True)
        self.logger.addCmdEntry(logContent)
        print("Finished deleting the squashfs-root")

# .desktop file content
        try:
            desktopFile = f"""[Desktop Entry]
                            Type=Application
                            Name={programName}
                            Comment={programDescr}
                            Exec={fileDest}/{fileName}
                            Icon={userDir}/.local/share/icons/{programIcon}
                            Terminal=false
                            Categories={programCategory}
                            """
            print("Gathered all data for .desktop file creation")
            logContent = "Gathered all data for .desktop file creation"
            self.logger.addGeneralEntry(logContent)

            home = pathlib.Path.home()
            appsDir = home/".local/share/applications"
            desktopEntry = appsDir/f"{programName}.desktop"
            desktopEntry.write_text(desktopFile)
            print("Finished creating the .desktop file")
            logContent = "Finished creating the .desktop file"
            self.logger.addGeneralEntry(logContent)

        except Exception as error:
            self.logger.addGeneralEntry(str(error))
            raise Exception(error)

# Make the .desktop file executable
        logContent = subprocess.run(["chmod", "+x", str(desktopEntry)], check=True, capture_output=True, text=True)
        self.logger.addCmdEntry(logContent)
        print("Made the .desktop file executable")

class Logging():

    def __init__(self):
        logDir = Path.home() / ".local" / "share" / "AppImage-Installer" / "logs"
        logDir.mkdir(parents=True, exist_ok=True)
        currentDate = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.logFilePath = logDir / (currentDate + "Log.txt")

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