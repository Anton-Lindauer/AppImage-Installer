import os
import sys
import shutil
import subprocess
import pathlib

def showFiles():
    global fileList
    global fileDest
    global userDir
    global downloadsDir

    # Find user directory
    userDir = pathlib.Path.home()

    # Filepaths to the directories for and of the .AppImage files 
    fileDest = str(userDir)+"/AppImages"
    downloadsDir = os.path.join(str(userDir), "Downloads")

    # Put every AppImage file into a list
    fileList = [file.path 
                for file in os.scandir(downloadsDir) 
                if file.name[-9:] == ".AppImage" and file.is_file(follow_symlinks=False)]

    fileList.sort()    # Sort the list in a alphabetic order

    for file in fileList:   # Display every file
        print(f"{fileList.index(file) + 1}. {file}")

# Ask user which file to install
def userChoice():
    fileListLen = len(fileList)
    global choice
    while True:
        if fileListLen >= 2:    # Execute if there is more than one AppImage file
            choice = int(input(f"Select a file to move (1 - {fileListLen}): ")) - 1
            if choice >= 0:
                fileChoice = input('Enter "y" to move this file or cancel with anything else: ').lower()
                if fileChoice == "y":
                    break
                else:
                    print("Canceling the operation")
                    sys.exit()
                break
            else:
                print(f"Please select a file from the list (1 - {fileListLen}): ")
        elif fileListLen == 1:  # Execute if there is only one AppImage file
            print("This .AppImage file has been found")
            choice = 0 
            fileChoice = input('Enter "y" to move this file or cancel with anything else: ').lower()
            if fileChoice == "y":
                break
            else:
                print("Canceling the operation")
                sys.exit()
        else:  # Execute if there are no AppImage files
            print("No .AppImage file has been found")
            sys.exit()
        
# Function to move the AppImage File to the right directory
def moveFile():
    print(f"You chose {fileList[choice]}")
    if not os.path.isdir(fileDest): # Create the directory if it doesn't exist
        os.mkdir(fileDest)
    try:    # Moving the .AppImage file
        shutil.move(fileList[choice], fileDest)
        print("File moved successfully")
    except Exception as error:
        print(f"This went wrong: \n{error}")

# Function to make the AppImage file executable
def mkExec():
    global fileName
    fileName = os.path.basename(fileList[choice])
    os.system(f'chmod +x {fileDest}/{fileName}')
    print("The AppImage file can now be executed")

# Function to create a symLink file, to execute the .AppImage file with a terminal command systemwide on your account
def mkSymLink(): 
    cmdName = input("Enter the command your want to execute the .AppImage file from the terminal: ")
    os.system(f"ln -s ~/AppImages/{os.path.basename(fileList[choice])}""  ~/.local/bin/"+cmdName)
    print(f"You can now use {cmdName} to execute this program from the terminal")

def mkStartmenuEntry():
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

    programName = input("Enter the name of the program in the startmenu: ")     # Name of the program in the startmenu
    programDescr = input("Enter a description for the program: ")   # Description of the program in the tooltip 

    print("Categories: AudioVideo;Audio;Video;Development;Education;Game;Graphics;Network;Office;Science;Settings;System;Utility;")     # Startmenu categories 
    print("Use ';' to seperate them and at the end")
    programCategory = input("Enter the categories the program belongs to: ")

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

    print("Everyting has finished successfully, try loging out and back in if the program doesn't show up in the startmenu")

def main():
    showFiles()
    userChoice()
    moveFile()
    mkExec()
    mkSymLink()
    mkStartmenuEntry()

if __name__ == "__main__":
    main()