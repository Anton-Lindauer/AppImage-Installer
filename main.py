import os
import sys
import shutil

fileList = []
fileDest = "/home/silas/Downloads/test"

# Function to move the AppImage File to the right directory
def moveFile(fileList, fileDest):
    print(f"You chose {fileList[choice]}")
    if not os.path.isdir("/home/silas/Downloads/test"): # Create the directory if it doesn't exist
        os.mkdir("/home/silas/Downloads/test")
    try:    # Moving the .AppImage file
        shutil.move(fileList[choice], fileDest)
        print("File moved successfully")
        mkExec()
    except Exception as error:
        print(f"This went wrong: \n{error}")

# Function to make the AppImage file executable
def mkExec():
    os.system(f'chmod +x /home/silas/Downloads/test/{os.path.basename(fileList[choice])}')
    print("The AppImage file can now be executed")

# List every AppImage file
for file in os.listdir("/home/silas/Downloads"): # .sort():
    if file.endswith(".AppImage"): #and os.path.isfile(file):
        fileList.append(os.path.join("/home/silas/Downloads", file))
        print(f"{len(fileList)}. {file}")

# Ask user which file to move
fileListLen = len(fileList)
if fileListLen >= 2:    # Execute if there is more than one AppImage file
    choice = int(input(f"Select a file to move (1 - {fileListLen}):")) - 1
    if choice >= 0:
        moveFile(fileList, fileDest)
    else:
        print(f"Please select a file from the list (1 - {fileListLen})")
elif fileListLen == 1:  # Execute if there is only one AppImage file
    print("This .AppImage file has been found")
    choice = 0 
    fileChoice = input("Enter y to move this file:").lower()
    if fileChoice == "y":
        moveFile(fileList, fileDest)
    else:
        print("Canceling the operation")
else:  # Execute if there are no AppImage files
    print("No .AppImage file has been found")
    sys.exit()