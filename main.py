import os
import sys
import shutil
fileList = []
fileDestination = "C:/Users/primu/Downloads/test/"

# Function to move the AppImage File to the right directory
def moveFile(selectedFile, fileDestination):
    print(f"You choose {fileList[choice]}")
    shutil.move(selectedFile, fileDestination)
    print("File moved successfully")

# List every AppImage file
for file in os.listdir("C:/Users/primu/Downloads/"):
    if file.endswith(".AppImage"):
        fileList.append(os.path.join("C:/Users/primu/Downloads/", file))
        print(f"{len(fileList)}. {file}")

# Ask user what to do
fileListLen = len(fileList)
if fileListLen >= 2:    #Execute if there is more than one AppImage file
    choice = int(input(f"Select a file(1 - {fileListLen})")) - 1
    selectedFile = fileList[choice]
    moveFile(selectedFile, fileDestination)
elif fileListLen == 1:  #Execute if there is one AppImage file
    print("You have only one .AppImage file")
    choice = 0
    selectedFile = fileList[choice] 
    fileChoice = input("Enter y to use this file")
    if fileChoice == "y":
        moveFile(selectedFile, fileDestination)
    else:
        sys.exit()
elif fileListLen <= 0:  #Execute if there are no AppImage files
    print("No .AppImage file found")
    sys.exit()