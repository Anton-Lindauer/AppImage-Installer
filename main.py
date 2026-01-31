import os
import sys
import shutil
import subprocess

# Function to find out which user is active
def findUsername():
    username = subprocess.check_output("whoami").decode().strip()
    return username

fileList = []
fileDest = "/home/"+findUsername()+"/Downloads/test"

# Function to move the AppImage File to the right directory
def moveFile(fileList, fileDest):
    print(f"You chose {fileList[choice]}")
    if not os.path.isdir("/home/"+findUsername()+"/Downloads/test"): # Create the directory if it doesn't exist
        os.mkdir("/home/"+findUsername()+"/Downloads/test")
    try:    # Moving the .AppImage file
        shutil.move(fileList[choice], fileDest)
        print("File moved successfully")
        mkExec()
    except Exception as error:
        print(f"This went wrong: \n{error}")

# Function to make the AppImage file executable
def mkExec():
    os.system(f'chmod +x /home/{findUsername()}/Downloads/test/{os.path.basename(fileList[choice])}')
    print("The AppImage file can now be executed")

# List every AppImage file
for file in os.listdir("/home/"+findUsername()+"/Downloads"):
    if file.endswith(".AppImage") and os.path.isfile(os.path.join("/home/"+findUsername()+"/Downloads", file)):
        fileList.append(os.path.join("/home/"+findUsername()+"/Downloads", file))

fileList.sort()    # Sort the list in a alphabetic order

for file in fileList:   # Display every file
    print(f"{fileList.index(file) + 1}. {file}")

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