import os
fileList = []
numOfFile = 0

for file in os.listdir("C:/Users/primu/Downloads/"):
    if file.endswith(".AppImage"):
        fileList.append(os.path.join("/C:/Users/primu/Downloads/", file))
        numOfFile += 1
        print(f"{numOfFile}. {file}")

fileListLen = len(fileList)
if fileListLen >= 2:
    choice = int(input(f"Select a file(1 - {fileListLen})")) -1
elif fileListLen == 1:
    input("You have only one .AppImage file")
    choice = 0
elif fileListLen <= 0:
    print("No .AppImage file found")

print(f"You choose {fileList[choice]}")