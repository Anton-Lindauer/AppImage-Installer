# This file provides the Python functionality for the Pyside6 GUI. This script is not suppossed to be run alone. 

import os
import shutil
import subprocess
import pathlib

class Installer():

# Put every AppImage file into a list
    @staticmethod
    def listFiles(userDir):
        downloadsDir = os.path.join(str(userDir), "Downloads")

        fileList = [file.path 
                    for file in os.scandir(downloadsDir) 
                    if file.name[-9:] == ".AppImage" and file.is_file(follow_symlinks=False)]

        fileList.sort()
        return fileList
       
# Function to move the AppImage File to the right directory
    @staticmethod
    def moveFile(selectedFilePath, fileDest):
        if not os.path.isdir(fileDest):
            os.mkdir(fileDest)
# Moving the .AppImage file
        shutil.move(selectedFilePath, fileDest)


# Function to make the AppImage file executable
    @staticmethod
    def mkExec(selectedFilePath, fileDest):
        fileName = os.path.basename(selectedFilePath)
        path = f"{fileDest}/{fileName}"
        subprocess.run([f"chmod", "+x", path], check=True)

# Function to create a symLink file, to execute the .AppImage file with a terminal command systemwide on your account
    @staticmethod
    def mkSymLink(selectedFilePath, cmdName, fileDest, userDir):
        if not os.path.isdir(f"{userDir}/.local/bin/"):
            os.mkdir(f"{userDir}/.local/bin/")

        subprocess.run(["ln", "-s", f"{fileDest}/{os.path.basename(selectedFilePath)}", f"{userDir}/.local/bin/"+cmdName], check=True)

class StartmenuEntry():

    @staticmethod
    def create(selectedFilePath, fileDest, userDir, programName, programDescr, programCategory):
        fileName = os.path.basename(selectedFilePath)

        subprocess.run([f"{fileDest}/{fileName}", "--appimage-extract"], check=True)  # Extract AppImage in to the temporary directory
        print("Finished extracting data from the .AppImage file")
        
        if not os.path.isdir(fileDest): # Create the icons directory if it doesn't exist
            os.mkdir(f"{userDir}/.local/share/icons")
            print(f"Created {userDir}/.local/share/icons")
        else:
            print(f"{userDir}/.local/share/icons/ has been found")

        programIcon = os.path.basename(next(pathlib.Path("squashfs-root").glob("*.png")))   # Find the name of the icon.png file; Used later in the .desktop file 
        
        subprocess.run(["cp" , next(pathlib.Path("squashfs-root").glob("*.png")), f"{userDir}/.local/share/icons"], check=True) # Copy Icon to icons directory
        print("Finished copying the icon to the icons directory")
        
        subprocess.run(["rm", "-rf", pathlib.Path("squashfs-root")], check=True)    # Delete squashfs-root; This is a temporary directory and the app icon is extracted to this directory
        print("Finished deleting the squashfs-root")
        
        if not os.path.isdir(f"{userDir}/.local/share/applications/"): # Create the applications directory if it doesn't exist
            os.mkdir(f"{userDir}/.local/share/applications")
            print(f"Created {userDir}/.local/share/applications")
        else:
            print(f"{userDir}/.local/share/applications has been found")

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
        print("Gathered all data for .desktop file creation")
        
        home = pathlib.Path.home()
        appsDir = home/".local/share/applications"
        desktopEntry = appsDir/f"{programName}.desktop" # Write the .desktop file
        desktopEntry.write_text(desktopFile)
        print("Finished creating the .desktop file")
        
        subprocess.run(["chmod", "+x", str(desktopEntry)], check=True) # Make the .desktop file executable
        print("Made the .desktop file executable")