import os
import sys
import shutil
import subprocess
import pathlib

# Find user directory
userDir = pathlib.Path.home()

# Create needed list and file path
fileList = []
fileDest = str(userDir)+"/AppImages"

# Function to move the AppImage File to the right directory
def moveFile(fileList, fileDest):
    print(f"You chose {fileList[choice]}")
    if not os.path.isdir(fileDest): # Create the directory if it doesn't exist
        os.mkdir(fileDest)
    try:    # Moving the .AppImage file
        shutil.move(fileList[choice], fileDest)
        print("File moved successfully")
        mkExec()
    except Exception as error:
        print(f"This went wrong: \n{error}")

# Function to make the AppImage file executable
def mkExec():
    os.system(f'chmod +x {fileDest}/{os.path.basename(fileList[choice])}')
    print("The AppImage file can now be executed")
    mkSymLink()

# Function to create a symLink file, to execute the .AppImage file with a terminal command systemwide on your account
def mkSymLink(): 
    cmdName = input("Enter the command your want to execute the .AppImage file from the terminal: ")
    os.system(f"ln -s ~/AppImages/{os.path.basename(fileList[choice])}""  ~/.local/bin/"+cmdName)
    print(f"You can now use {cmdName} to execute this program from the terminal")
    mkStartmenuEntry()

def mkStartmenuEntry():
    subprocess.run([f"{fileDest}/cura.AppImage", "--appimage-extract"], check=True)  # Extract AppImage
    print("Finished extracting data from the .AppImage file")
    
    if not os.path.isdir(fileDest): # Create the icons directory if it doesn't exist
        os.mkdir(f"{userDir}/.local/share/icons")
        print(f"Created {userDir}/.local/share/icons")
    else:
        print(f"{userDir}/.local/share/icons/ has been found")
    
    subprocess.run(["cp" , next(pathlib.Path("squashfs-root").glob("*.png")), f"{userDir}/.local/share/icons"], check=True) # Copy Icon to icons directory
    print("Finished copying the icon to the icons directory")
    
    subprocess.run(["rm", "-rf", pathlib.Path("squashfs-root")], check=True)    # Delete squashfs-root 
    print("Finished deleting the squashfs-root")
    
    if not os.path.isdir(f"{userDir}/.local/share/applications/"): # Create the applications directory if it doesn't exist
        os.mkdir(f"{userDir}/.local/share/applications")
        print(f"Created {userDir}/.local/share/applications")
    else:
        print(f"{userDir}/.local/share/applications has been found")
    
    desktopFile = f"""[Desktop Entry]
                      Type=Application
                      Name=CuraTest
                      Exec={pathlib.Path.home()}/AppImages/cura.AppImage
                      Icon={pathlib.Path.home()}/.local/share/icons/cura.png
                      Terminal=false
                      Categories=Graphics;Engineering;
                      """
    print("Gathered data for .desktop file creation")
    
    home = pathlib.Path.home()
    appsDir = home/".local/share/applications"
    desktopEntry = appsDir/"curatest.desktop" # Write the .desktop file
    desktopEntry.write_text(desktopFile)
    print("Finished creating the .desktop file")
    
    subprocess.run(["chmod", "+x", str(desktopEntry)], check=True) # Make the .desktop file executable
    print("Made the .desktop file executable")

    print("Everyting has finished successfully, try loging out and back in if the program doesn't show up in the startmenu")

# List every AppImage file
for file in os.listdir(str(userDir)+"/Downloads"):
    if file.endswith(".AppImage") and os.path.isfile(os.path.join(str(userDir)+"/Downloads", file)):
        fileList.append(os.path.join(str(userDir)+"/Downloads", file))

fileList.sort()    # Sort the list in a alphabetic order

for file in fileList:   # Display every file
    print(f"{fileList.index(file) + 1}. {file}")

# Ask user which file to move
def usrSelect():
    fileListLen = len(fileList)
    global choice
    if fileListLen >= 2:    # Execute if there is more than one AppImage file
        choice = int(input(f"Select a file to move (1 - {fileListLen}): ")) - 1
        if choice >= 0:
            moveFile(fileList, fileDest)
        else:
            print(f"Please select a file from the list (1 - {fileListLen}): ")
    elif fileListLen == 1:  # Execute if there is only one AppImage file
        print("This .AppImage file has been found")
        choice = 0 
        fileChoice = input("Enter y to move this file: ").lower()
        if fileChoice == "y":
            moveFile(fileList, fileDest)
        else:
            print("Canceling the operation")
    else:  # Execute if there are no AppImage files
        print("No .AppImage file has been found")
        sys.exit()

if __name__ == "__main__":
    usrSelect()