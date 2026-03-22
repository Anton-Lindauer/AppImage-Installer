import faulthandler
faulthandler.enable()

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGroupBox, QRadioButton, QPushButton, QStackedWidget, QLineEdit, QButtonGroup, QMessageBox, QScrollArea, QFileDialog, QComboBox, QHBoxLayout, QStyledItemDelegate
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QUrl
from PySide6.QtGui import QGuiApplication, QDesktopServices

import sys
import os
import pathlib
from main import installer, startmenuEntry

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
    
        self.userDir = pathlib.Path.home()   # User home directory
        self.fileDest = str(self.userDir)+"/AppImages"   # Directory for the AppImages
        self.downloadsDir = os.path.join(str(self.userDir), "Downloads")     # Downloads directory; The AppImages will be extracted from there

        programDir = os.path.dirname(os.path.abspath(__file__))     # Find the path for the stylesheets
        self.lightStylePath = os.path.join(programDir, "stylesheets/lightStyle.qss")
        self.darkStylePath = os.path.join(programDir, "stylesheets/darkStyle.qss")
        
        self.setWindowTitle("AppImage-Installer")   # Window name in the top bar
        self.setMinimumSize(750, 600)   # Minimum window size

        central = QWidget()     # QWidget for everything
        self.setCentralWidget(central)

        mainLayout = QVBoxLayout(central)   # Layout for the QStackedWidget

        # The QStackedWidget that contains all pages 
        self.stackedWidget = QStackedWidget()

        self.page1 = self.createPage1()
        self.stackedWidget.addWidget(self.page1)

        self.page2 = self.createPage2()
        self.stackedWidget.addWidget(self.page2)

        self.page3 = self.createPage3()
        self.stackedWidget.addWidget(self.page3)

        self.page4 = self.createPage4()
        self.stackedWidget.addWidget(self.page4)

        mainLayout.addWidget(self.stackedWidget)    # Add the QStackedWidget to the main windows layout

        optionsBar = self.menuBar()

        fileMenu = optionsBar.addMenu("File")
        themeMenu = optionsBar.addMenu("Theme")
        helpMenu = optionsBar.addMenu("Help")

# Hides the box around the box with the menues; Has to be declared for every menu
        fileMenu.setWindowFlags(fileMenu.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint | Qt.Popup)
        fileMenu.setAttribute(Qt.WA_TranslucentBackground)

        file1 = fileMenu.addAction("Pick a different file")

        file1.triggered.connect(self.userPick)

        themeMenu.setWindowFlags(themeMenu.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint | Qt.Popup)
        themeMenu.setAttribute(Qt.WA_TranslucentBackground)

        theme1 = themeMenu.addAction("System theme")
        themeMenu.addSeparator()
        theme2 = themeMenu.addAction("Mint Orchis Dark")
        themeMenu.addSeparator()
        theme3 = themeMenu.addAction("Mint Orchis Light")

        theme1.triggered.connect(lambda: self.loadTheme("sysTheme"))
        theme2.triggered.connect(lambda: self.loadTheme("darkTheme"))
        theme3.triggered.connect(lambda: self.loadTheme("lightTheme"))

        helpMenu.setWindowFlags(helpMenu.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint | Qt.Popup)
        helpMenu.setAttribute(Qt.WA_TranslucentBackground)

        help1 = helpMenu.addAction("Github Repo")

        help1.triggered.connect(self.openRepo)

    def openRepo(self):
        QDesktopServices.openUrl(QUrl("https://github.com/Anton-Lindauer/AppImage-Installer"))

    def createPage1(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)

        title = QLabel("Select a file to install")   # Title telling the user what to do
        title.setObjectName("title")
        title.setAlignment(Qt.AlignLeft)

        filedialogBtn = QPushButton("Pick a file")
        filedialogBtn.clicked.connect(self.userPick)

        # QScrollArea with a container for all the QRadioButtons with adjustable size to fit up to five QRadioButtons and then enable scrolling
        containerScrollArea = QScrollArea()
        containerScrollArea.setWidgetResizable(True)
        containerScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget() # Container in the QScrollArea
        containerScrollArea.setWidget(container)

        containerLayout = QVBoxLayout(container)   # Set the layout in the Container in the QScrollArea
        containerLayout.setContentsMargins(0, 0, 0, 0,)
        containerLayout.setSpacing(0)

        self.fileList = installer.files(self, self.downloadsDir)     # Return all file paths needed
        fileListLen = len(self.fileList)

        self.groupPage1 = QButtonGroup(self)    # Group for all QRadioButtons to later find out which one is checked

        if fileListLen > 0:
             for file in self.fileList:   # Create a QRadioButton for each file
                itemPos = self.fileList.index(file)
                radioBtn = QRadioButton(file)
                
                containerLayout.addWidget(radioBtn)
                self.groupPage1.addButton(radioBtn)

                if fileListLen == 1:
                    radioBtn.setProperty("isFirstAndLast", "true")
                elif not itemPos == fileListLen - 1:     # Only create a divider if the element isn't the last one
                    radioBtn.setProperty("isLast", "false")
                    if itemPos == 0:
                        radioBtn.setProperty("isFirst", "true")
                else:
                    radioBtn.setProperty("isLast", "true")
        else:
            page1NoFileMsg = QLabel("No .AppImage file has been found in your Downloads directory")
            page1NoFileMsg.setObjectName("message")
            containerLayout.addWidget(page1NoFileMsg)

        # Set the size of the QScrollArea to the size of the QRadioButtons in the QScrollArea to fix Qt's stupid default behaviour
        if fileListLen <= 1:
            containerScrollArea.setMaximumHeight(40)
            containerScrollArea.setMinimumHeight(40)
        elif fileListLen == 2:
            containerScrollArea.setMaximumHeight(80)
            containerScrollArea.setMinimumHeight(80)
        elif fileListLen == 3:
            containerScrollArea.setMaximumHeight(120)
            containerScrollArea.setMinimumHeight(120)
        elif fileListLen == 4:
            containerScrollArea.setMaximumHeight(160)
            containerScrollArea.setMinimumHeight(160)
        elif fileListLen >= 5:
            containerScrollArea.setMaximumHeight(200)
            containerScrollArea.setMinimumHeight(200)

        submitBtn = QPushButton("Continue")  # Button to continue with the selected file
        submitBtn.setObjectName("submitBtn")
        submitBtn.clicked.connect(self.findSeletedRadioBtn)

# Adding every main element to the main window
        mainLayout.addWidget(title)
        mainLayout.addWidget(filedialogBtn)
        mainLayout.addWidget(containerScrollArea)
        mainLayout.addWidget(submitBtn)

        mainLayout.addStretch()    # Increases the window size without increasing the elemet sizes

        return mainWidget
    
    def userPick(self):
        pickedPath, _ = QFileDialog.getOpenFileName(
            self,
            "Pick a AppImage file to install",
            f"{self.userDir}",
            "AppImage files (*.AppImage)"
        )

        if pickedPath:
            print(f"{pickedPath}")

            self.selectedFilePath = pickedPath
            self.stackedWidget.setCurrentIndex(1)
    
    def findSeletedRadioBtn(self):  # Function to find out which file was selected by the user and the user can only continue with a file selected
            selected = self.groupPage1.checkedButton()
            if selected is not None:
                self.selectedFilePath = selected.text()     ## Read out the file path from the selected QRadioButton
                self.stackedWidget.setCurrentIndex(1)   # Continue with the next window
        
    def createPage2(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)

# Title of the current thing the user does
        title = QLabel("Enter the program information")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignLeft)

# Box for the options for the user; Contains other boxes with the descriptions and a QlineEdits
        container = QGroupBox()
        
# Set the layout in the container with no spacing
        containerLayout = QVBoxLayout(container)
        containerLayout.setContentsMargins(0, 0, 0, 0)
        containerLayout.setSpacing(0)

# All the things the user has to enter
        self.programInfo = ["Enter a command to execute the file from the terminal: ",
                            "Enter the name of the program in the startmenu: ",
                            "Enter a description for the program: ",
                            "Pick the categories the program belongs to: "]
        
# More information on what to enter for the user
        programInfoText = ["This command can later be used to launch the program from the terminal.",
                           "The name in the icon in the startmenu.",
                           "The description of the program in the startmenu tooltip.",
                           "The startmenu category the program belongs to. Categories are: AudioVideo;Audio;Video;Development;Education;Game;Graphics;Network;Office;Science;Settings;System;Utility;. You can choose multiple categories."]
        
        self.programInfoList = []
        
# Create all the element in the groupbox
        for index, info in enumerate(self.programInfo):  
# Boxes with the descriptions and the QLineEdits 
            containerTile = QWidget()
            containerTile.setObjectName("page2InnerBox")

            tileLayout = QVBoxLayout(containerTile)
            tileLayout.setContentsMargins(0, 0, 0, 0)
            tileLayout.setSpacing(0)

# Special properties for the first and last boxes; Used in QSS for rounded corners
            if index == 0:
                containerTile.setProperty("isFirst", "true")
            elif index == 3:
                containerTile.setProperty("isLast", "true")
            
# What the user is expected to enter 
            description = QLabel(info)
            description.setObjectName("entry")

# More detailed description for the user
            infoDescription = QLabel(programInfoText[index])
            infoDescription.setObjectName("infoDescription")
            infoDescription.setWordWrap(True)

            tileLayout.addWidget(description)
            tileLayout.addWidget(infoDescription)

# Add a dropdown menu only to the last box
            if index == 3:
                innerTile = QWidget()
                innerTileLayout = QHBoxLayout(innerTile)

                self.allCategories = ""
                rmvCategory = QPushButton("Remove last Category")
                rmvCategory.clicked.connect(self.rmvLastCategory)
                rmvCategory.setObjectName("rmvCategory")

                self.categorySel = QComboBox()
                self.categorySel.setPlaceholderText("Pick Categories")
                self.categorySel.addItems(["AudioVideo", "Audio", "Video", "Development", "Education", "Game", "Graphics", "Network", "Office", "Science", "Settings", "System", "Utility"])
                self.categorySel.setItemDelegate(QStyledItemDelegate())
                self.categorySel.view().window().setAttribute(Qt.WA_TranslucentBackground)
                self.categorySel.view().window().setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
                self.categorySel.currentTextChanged.connect(self.findCategories)

# Disable auto scrolling with mouse hovering
                view = self.categorySel.view()
                view.setAutoScroll(False)

# Activate the scrollbar handle
                view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

                self.pickedCategories = QLabel()
                self.pickedCategories.setObjectName("pickedCategories")
                self.pickedCategoriesList = []

                innerTileLayout.addWidget(self.categorySel)
                innerTileLayout.addWidget(rmvCategory)

                tileLayout.addWidget(innerTile)
                tileLayout.addWidget(self.pickedCategories)

# Add QLineEdit input fields for box one to three
            else:
                usrInput = QLineEdit()
                self.programInfoList.append(usrInput)
                tileLayout.addWidget(usrInput)
                

            containerLayout.addWidget(containerTile)

        self.page2SubmitBtn = QPushButton("Continue")
        self.page2SubmitBtn.setObjectName("submitBtn")
        self.page2SubmitBtn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))

        self.page2BackBtn = QPushButton("Back")
        self.page2BackBtn.setObjectName("backBtn")
        self.page2BackBtn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

# Adding every main element to the main window
        mainLayout.addWidget(title)
        mainLayout.addWidget(container)
        mainLayout.addWidget(self.page2SubmitBtn)
        mainLayout.addWidget(self.page2BackBtn)

# Increases the window size without increasing the element sizes
        mainLayout.addStretch()    

        return mainWidget
    
    def findCategories(self, pickedOption):
# Exit this function if the input is invalid
        if not pickedOption or pickedOption == "Pick Categories" or pickedOption in self.pickedCategoriesList:
            return

        self.pickedCategoriesList.append(pickedOption)

# Update the string with all categories
        self.allCategories = ";".join(self.pickedCategoriesList) + ";"
        self.pickedCategories.setText(self.allCategories)
        self.categorySel.setCurrentIndex(-1)

    def rmvLastCategory(self):
# Only remove the last element from the list if the list has at least one element
        if self.pickedCategoriesList: 
            self.pickedCategoriesList.pop()
        
# Update the string with all categories
        self.allCategories = ";".join(self.pickedCategoriesList) + ";" if self.pickedCategoriesList else ""
        self.pickedCategories.setText(self.allCategories)
        self.categorySel.setCurrentIndex(-1)

#Function for the installation process page 
    def createPage3(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)

        title = QLabel("Installation process")
        title.setObjectName("title")

        container = QGroupBox()    # QGroupBox thats used as a terminal for the status updates, that the user receives
        terminalLayout = QVBoxLayout(container)
        terminalLayout.setContentsMargins(0, 0, 0, 0)
        terminalLayout.setSpacing(0)
        container.setMinimumHeight(200)
        container.setObjectName("page3Container")

        self.terminalUpdateMsg = QLabel()     # Updates that are displayed in the GUIs terminal like UI element
        self.terminalUpdateMsg.setObjectName("terminalText")

        terminalLayout.addWidget(self.terminalUpdateMsg)
        terminalLayout.addStretch()

        self.page3SubmitBtn = QPushButton("Start installation")  # Button to continue with the selected options
        self.page3SubmitBtn.setObjectName("submitBtn")
        self.page3SubmitBtn.clicked.connect(self.installProgram)

        self.page3BackBtn = QPushButton("Back")  # Button to go back to the previously selected options
        self.page3BackBtn.setObjectName("backBtn")
        self.page3BackBtn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))

        mainLayout.addWidget(title)
        mainLayout.addWidget(container)
        mainLayout.addWidget(self.page3SubmitBtn)
        mainLayout.addWidget(self.page3BackBtn)

        mainLayout.addStretch()

        return mainWidget
    
    def installProgram(self):
# Disable the buttons on page 3 
        self.page3SubmitBtn.setEnabled(False)
        self.page3BackBtn.setEnabled(False)

# Get program data from the QLineEdits
        self.cmdName = self.programInfoList[0].text()
        self.programName = self.programInfoList[1].text()
        self.programDescr = self.programInfoList[2].text()
        self.programCategory = self.allCategories

# Function that installs the program
        self.worker = InstallWorker(self.selectedFilePath, self.fileDest, self.userDir, self.programName,self.programDescr, self.programCategory, self.cmdName)

# Process status updates from the installation function
        self.worker.progressUpdate.connect(self.workerProgress)
        self.worker.success.connect(self.workerFinished)
        self.worker.error.connect(self.workerError)

        self.terminalUpdateMsg.setText("Installation in process...")
        self.terminalUpdateMsg.show()

# Start the installation function
        self.worker.start()

# Function for displaying the installers progress
    def workerProgress(self, message):
        currentProgress = self.terminalUpdateMsg.text()

        if currentProgress: 
            newProgress = currentProgress + "\n" + message
        else:
            newProgress = message

        self.terminalUpdateMsg.setText(newProgress)

        QApplication.processEvents()

# Function to process what happens, when the installation finished successfully
    def workerFinished(self):
        self.terminalUpdateMsg.setText("Installation finished")

# Wait 2s to let the user see the last step beeing completed
        #QTimer.singleShot(2000)

        self.stackedWidget.setCurrentIndex(3)   # Go to the installation finished page

# Function for a pop-up window if a error occurs during the installation process
    def workerError(self, errorMsg):

        msg = QMessageBox()
        msg.setWindowTitle("Errror!")
        msg.setText(f"AppImage-Installer ran into an issue! \nThis error occured:\n{errorMsg}")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        
        msg.exec()

        sys.exit()

    def createPage4(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)

        title = QLabel("Finished installing the program")   # Tells the user that the installation was successfull
        title.setObjectName("title")
        title.setAlignment(Qt.AlignLeft)

        submitBtn = QPushButton("Install another program")  # Button to install another program
        submitBtn.setObjectName("submitBtn")
        submitBtn.clicked.connect(self.reloadPage1)     # Reload all pages if the user wants to install another program
        submitBtn.clicked.connect(self.reloadPage2)
        submitBtn.clicked.connect(self.reloadPage3)

# Adding every main element to the main window
        mainLayout.addWidget(title)
        mainLayout.addWidget(submitBtn)

        mainLayout.addStretch()
        return mainWidget
    
# Function to reload the first page, because the AppImage files in the Downloads directory change after the installation is completed
    def reloadPage1(self):
         oldPage1 = self.stackedWidget.widget(0)    # Remove the already existing version of the first page
         self.stackedWidget.removeWidget(oldPage1)
         oldPage1.deleteLater()

         newPage1 = self.createPage1()      # Generate a new first page and insert it at index 0
         self.stackedWidget.insertWidget(0, newPage1)
         self.stackedWidget.setCurrentIndex(0)  # Go to the first page at index 0
    
    def reloadPage2(self):
         oldPage2 = self.stackedWidget.widget(1)    # Remove the already existing version of the first page
         self.stackedWidget.removeWidget(oldPage2)
         oldPage2.deleteLater()

         newPage2 = self.createPage2()      # Generate a new first page and insert it at index 1
         self.stackedWidget.insertWidget(1, newPage2)

    def reloadPage3(self):
         oldPage3 = self.stackedWidget.widget(2)    # Remove the already existing version of the first page
         self.stackedWidget.removeWidget(oldPage3)
         oldPage3.deleteLater()

         newPage3 = self.createPage3()      # Generate a new first page and insert it at index 2
         self.stackedWidget.insertWidget(2, newPage3)

    def loadTheme(self, selectedTheme):
        match selectedTheme:
# Open the qss style sheet with the same theme as the system
            case "sysTheme":
                sysStyle = QGuiApplication.instance().styleHints().colorScheme()
                if sysStyle == Qt.ColorScheme.Dark:
                    with open(self.darkStylePath, "r") as f:
                        _style = f.read()
                        app.setStyleSheet(_style)
                else:
                    with open(self.lightStylePath, "r") as f:  # Open a qss style sheet
                        _style = f.read()
                        app.setStyleSheet(_style)
# Open the qss style sheet with the dark theme
            case "darkTheme":
                with open(self.darkStylePath, "r") as f:  # Open a qss style sheet
                        _style = f.read()
                        app.setStyleSheet(_style)
# Open the qss style sheet with the light theme
            case "lightTheme":  
                with open(self.lightStylePath, "r") as f:  # Open a qss style sheet
                        _style = f.read()
                        app.setStyleSheet(_style)

# Class for the installation process
class InstallWorker(QThread):
    progressUpdate = Signal(str)
    error = Signal(str)
    success = Signal()

    def __init__(self, selectedFilePath, fileDest, userDir, programName,programDescr, programCategory, cmdName):
        super().__init__()

        self.selectedFilePath = selectedFilePath
        self.fileDest = fileDest     
        self.userDir = userDir
        self.programName = programName
        self.programDescr = programDescr
        self.programCategory = programCategory
        self.cmdName = cmdName

# Function to install the program
    def run(self):
        try:
            installer.moveFile(self, self.selectedFilePath, self.fileDest)
            self.progressUpdate.emit("File moved successfully (1/4 tasks finished)")

            installer.mkExec(self, self.selectedFilePath, self.fileDest)
            self.progressUpdate.emit("File has been made executable (2/4 tasks finished)")

            installer.mkSymLink(self, self.selectedFilePath, self.cmdName, self.fileDest, self.userDir)
            self.progressUpdate.emit("Program has been made executable (3/4 tasks finished)")

            startmenuEntry.create(self, self.selectedFilePath, self.fileDest, self.userDir, self.programName, self.programDescr, self.programCategory)
            self.progressUpdate.emit("Startmenu entry has been created (4/4 tasks finished)")

            self.success.emit()

        except Exception as error:
            print(error)

            self.error.emit(str(error))

if __name__ == "__main__":
    app = QApplication()

    window = MainWindow()
    window.show()

    window.loadTheme("sysTheme")

    sys.exit(app.exec())