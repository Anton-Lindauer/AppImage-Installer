import faulthandler
faulthandler.enable()

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGroupBox, QRadioButton, QPushButton, QStackedWidget, QLineEdit, QButtonGroup, QMessageBox, QScrollArea, QFileDialog, QComboBox, QHBoxLayout, QStyledItemDelegate, QGridLayout, QSizePolicy, QDialog
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QUrl
from PySide6.QtGui import QGuiApplication, QDesktopServices

import sys
import subprocess
from pathlib import Path

from src.core.logic import Installer, Logging
from src.gui.components import General, Page1Logic, InstallWorker

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
    
        self.userDir = Path.home()
        self.fileDest = self.userDir / "AppImages"

# Stylesheets paths
        fileDir = Path(__file__).resolve()
        projectRoot = fileDir.parent.parent.parent
        self.lightStylePath = projectRoot / "assets" / "stylesheets" / "lightStyle.qss"
        self.darkStylePath = projectRoot / "assets" / "stylesheets" / "darkStyle.qss"

        General.loadTheme(self, "sysTheme")
        
        self.setWindowTitle("AppImage-Installer")
        self.setMinimumSize(750, 700)

# QWidget for everything
        central = QWidget()
        self.setCentralWidget(central)

        mainLayout = QVBoxLayout(central)

# The QStackedWidget that contains all pages 
        self.stackedWidget = QStackedWidget()

        self.page1 = self.createPage1()
        self.page2 = self.createPage2()
        self.page3 = self.createPage3()
        self.page4 = self.createPage4()

        self.stackedWidget.addWidget(self.page1)
        self.stackedWidget.addWidget(self.page2)
        self.stackedWidget.addWidget(self.page3)
        self.stackedWidget.addWidget(self.page4)

# Add the QStackedWidget to the main windows layout
        mainLayout.addWidget(self.stackedWidget)    

# All of the remaining code in this function is for the QMenuBar
        optionsBar = self.menuBar()

        fileMenu = optionsBar.addMenu("File")
        themeMenu = optionsBar.addMenu("Theme")
        helpMenu = optionsBar.addMenu("Help")

        file1 = fileMenu.addAction("Pick a different file")
        file1.triggered.connect(self.page1Validator)

        theme1 = themeMenu.addAction("System theme")
        themeMenu.addSeparator()
        theme2 = themeMenu.addAction("Mint Orchis Dark")
        themeMenu.addSeparator()
        theme3 = themeMenu.addAction("Mint Orchis Light")

        theme1.triggered.connect(lambda: General.loadTheme(self, "sysTheme"))
        theme2.triggered.connect(lambda: General.loadTheme(self, "darkTheme"))
        theme3.triggered.connect(lambda: General.loadTheme(self, "lightTheme"))

        help1 = helpMenu.addAction("Github Repo")
        help1.triggered.connect(General.openRepo)

# Hides the box around the box with the menues; Has to be declared for every menu
        for menu in (fileMenu, themeMenu, helpMenu):
            menu.setWindowFlags(
                menu.windowFlags()
                | Qt.FramelessWindowHint
                | Qt.NoDropShadowWindowHint
                | Qt.Popup
            )
            menu.setAttribute(Qt.WA_TranslucentBackground)

# Only for testing

#        msgBox = QDialog()
#        msgBox.setWindowTitle("Error!")
#        msgBox.setFixedSize(msgBox.sizeHint())
#
#        msgBoxLayout = QVBoxLayout(msgBox)
#
#        msgText = QLabel(f"AppImage-Installer ran into an issue! \nThis error occured:\nerrorMsg\nA more detailed log can be found in logFilePath.")
#
#        msgBoxLayout.addWidget(msgText)
#
#        btnLayout = QHBoxLayout()
#
#        exitBtn = QPushButton("Exit")
#        openLogBtn = QPushButton("Open Log")
#        openLogBtn.setDefault(True)
#        openLogBtn.setAutoDefault(True)
#
#        btnLayout.addWidget(exitBtn)
#        btnLayout.addWidget(openLogBtn)
#
#        msgBoxLayout.addLayout(btnLayout)
#
#        msgBox.exec()
#
#        sys.exit()

    def createPage1(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)

        title = QLabel("AppImage selection")   
        title.setObjectName("title")

# Let the user pick a AppImage from anywhere
        filedialogBtn = QPushButton("Pick a file")
        
        self.page1Handler = Page1Logic()
        self.page1Handler.pickedFile.connect(self.page1Worker)
        filedialogBtn.clicked.connect(lambda: self.page1Handler.userPick(self))

# QScrollArea with a container for all the QRadioButtons with adjustable size to fit up to five QRadioButtons and then enable scrolling
        containerScrollArea = QScrollArea()
        containerScrollArea.setWidgetResizable(True)
        containerScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

# Container in the QScrollArea
        container = QWidget() 
        containerScrollArea.setWidget(container)

        containerLayout = QVBoxLayout(container)   
        containerLayout.setContentsMargins(0, 0, 0, 0,)
        containerLayout.setSpacing(0)

# All paths of AppImage files in the Downloads directory
        self.fileList = Installer.listFiles(self.userDir)     
        fileListLen = len(self.fileList)

# Group for all QRadioButtons to later find out which one is checked
        self.groupPage1 = QButtonGroup(self) 

# Create a QRadioButton for each file
        if fileListLen > 0:
             for itemPos, file in enumerate(self.fileList):
                radioBtn = QRadioButton(file)
                containerLayout.addWidget(radioBtn)
                self.groupPage1.addButton(radioBtn)

# Only create a divider if the element isn't the last one and add rounded corners to the first and last element
                suffix = "" if fileListLen <= 5 else "Scroll"

                if fileListLen == 1 and fileListLen <= 5:
                    radioBtn.setProperty("isFirstAndLast", "true")
                elif itemPos == 0:
                    radioBtn.setProperty(f"isFirst{suffix}", "true")
                elif itemPos == fileListLen - 1:
                    radioBtn.setProperty(f"isLast{suffix}", "true")
        else:
            page1NoFileMsg = QLabel("No .AppImage file has been found in your Downloads directory")
            page1NoFileMsg.setObjectName("message")
            containerLayout.addWidget(page1NoFileMsg)

# Set the size of the QScrollArea to the size of the QRadioButtons in the QScrollArea to fix Qt's stupid default behaviour
        containerScrollArea.setFixedHeight(min(fileListLen, 5) * 40)

        submitBtn = QPushButton("Continue")  
        submitBtn.setObjectName("submitBtn")
        submitBtn.clicked.connect(lambda: self.page1Handler.findSeletedRadioBtn(self.groupPage1))

        mainLayout.addWidget(title)
        mainLayout.addWidget(filedialogBtn)
        mainLayout.addWidget(containerScrollArea)
        mainLayout.addWidget(submitBtn)
        mainLayout.addStretch()

        return mainWidget
    
    def page1Validator(self):
        if self.stackedWidget.currentIndex() == 0:
            self.page1Handler.userPick(self)
        
    def page1Worker(self, path):
        self.stackedWidget.setCurrentIndex(1)
        self.selectedFilePath = path



    def createPage2(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)

        title = QLabel("Program information")
        title.setObjectName("title")

# Box for the options for the user; Contains other boxes with the descriptions and QlineEdits
        container = QGroupBox()
        
# Set the layout in the container with no spacing
        containerLayout = QVBoxLayout(container)
        containerLayout.setContentsMargins(0, 0, 0, 0)
        containerLayout.setSpacing(0)

# All the things the user has to enter
        self.programInfo = ["Terminal Command",
                            "Display Name",
                            "Short Description",
                            "Categories"]
        
# More information on what to enter for the user
        programInfoText = ["The command or file path used to launch the application from the terminal.",
                           "The name that will appear in the start menu and application list.",
                           "A brief summary of the application (displayed as a tooltip).",
                           "Determines the placement in the start menu. Some categories can't be combined; combined they create a different category."]
        
        self.categoryList = ["Accessibility;Utility", "Education", "Office", 
                             "Development", "Graphics", "Network", 
                             "AudioVideo", "Utility", "Game", 
                             "System", "Science;Education", "Utility", 
                             "Settings", "System;Settings"]
        
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

# Add QRadioButtons only to the last box, QlineEdits for all other boxes
            if index == index == len(self.programInfo) - 1:
                innerTile = QWidget()
                innerTileLayout = QGridLayout(innerTile)

                innerTileLayout.setContentsMargins(0, 0, 0, 0)
                innerTileLayout.setSpacing(0)

                self.allCategories = ""
                self.page2RadioBtns = QButtonGroup()
                self.page2RadioBtns.setExclusive(False)

# Create a QRadioButton for all 14 categories
                for i, category in enumerate(self.categoryList):
                    radioBtn = QRadioButton(category)
                    radioBtn.setObjectName("categorySel")
                    radioBtn.setAutoExclusive(False)
                    self.page2RadioBtns.addButton(radioBtn)

                    row = i // 3
                    column = i % 3

                    innerTileLayout.addWidget(radioBtn, row, column)

                tileLayout.addWidget(innerTile)

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

        mainLayout.addWidget(title)
        mainLayout.addWidget(container)
        mainLayout.addWidget(self.page2SubmitBtn)
        mainLayout.addWidget(self.page2BackBtn)
        mainLayout.addStretch()    

        return mainWidget



    def createPage3(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)

        title = QLabel("Installation process")
        title.setObjectName("title")

# QGroupBox thats used as a terminal for the status updates, that the user receives
        container = QGroupBox()    
        terminalLayout = QVBoxLayout(container)
        terminalLayout.setContentsMargins(0, 0, 0, 0)
        terminalLayout.setSpacing(0)
        container.setMinimumHeight(200)
        container.setObjectName("page3Container")

# Updates that are displayed in the GUIs terminal like UI element
        self.terminalUpdateMsg = QLabel()     
        self.terminalUpdateMsg.setObjectName("terminalText")

        terminalLayout.addWidget(self.terminalUpdateMsg)
        terminalLayout.addStretch()

        self.page3SubmitBtn = QPushButton("Start installation")  
        self.page3SubmitBtn.setObjectName("submitBtn")
        self.page3SubmitBtn.clicked.connect(self.installProgram)

        self.page3BackBtn = QPushButton("Back")  
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

# Get all selected categories
        self.programCategory = ""
        allCategories = self.page2RadioBtns.buttons()

        selected = [rb.text() for rb in allCategories if rb.isChecked()]

        if selected:
            self.programCategory = ";".join(selected)

        self.logger = Logging()

# Function that installs the program
        self.worker = InstallWorker(self.selectedFilePath, self.fileDest, self.userDir, self.programName,self.programDescr, self.programCategory, self.cmdName, self.logger)

# Process status updates from the installation function
        self.worker.progressUpdate.connect(self.workerProgress)
        self.worker.success.connect(self.workerFinished)
        self.worker.error.connect(self.workerError)

        self.terminalUpdateMsg.setText("Installation in process...")
        self.terminalUpdateMsg.show()

        self.worker.start()

    def workerProgress(self, message):
        currentProgress = self.terminalUpdateMsg.text()

# Update the terminal if a new progress update arrived
        if currentProgress: 
            newProgress = currentProgress + "\n" + message
        else:
            newProgress = message

        self.terminalUpdateMsg.setText(newProgress)

        QApplication.processEvents()

    def workerFinished(self):
        self.terminalUpdateMsg.setText("Installation finished")

# Rebuild page four to display the program name
# Easier to maintain to just rebuild the entire page than updating every element one by one
        self.reloadPage4()

        self.stackedWidget.setCurrentIndex(3)

    def workerError(self, errorMsg):
        logFilePath = self.logger.logFilePath

        self.logger.addGeneralEntry(errorMsg)
# A pop-up window if a error occurs during the installation process
        msg = QMessageBox()
        msg.setWindowTitle("Error!")
        msg.setText(f"AppImage-Installer ran into an issue! \nThis error occured:\n{errorMsg}\nA more detailed log can be found in {logFilePath}.")

        exitBtn = msg.addButton("Exit", QMessageBox.ActionRole)
        openLogBtn = msg.addButton("Open Log", QMessageBox.ActionRole)

        msg.exec()

        if msg.clickedButton() == openLogBtn:
# Without this subprocess configuration, the program doesn't properly close and throws warnings
            subprocess.Popen(
                ["xdg-open", str(logFilePath)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        self.worker.quit()
        self.worker.wait()
        QApplication.instance().quit()



    def createPage4(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)

        title = QLabel(f"Finished installing {self.programInfoList[1].text()}")
        title.setObjectName("title")

# Reload all pages if the user wants to install another program
        submitBtn = QPushButton("Install another program")
        submitBtn.setObjectName("submitBtn")
        submitBtn.clicked.connect(self.reloadPage1)     
        submitBtn.clicked.connect(self.reloadPage2)
        submitBtn.clicked.connect(self.reloadPage3)

        mainLayout.addWidget(title)
        mainLayout.addWidget(submitBtn)
        mainLayout.addStretch()
        
        return mainWidget
    
# Functions to rebuild all pages; to remove all previous user input
# Easier to maintain than to clear all elements one by one
    def reloadPage1(self):
        oldPage1 = self.stackedWidget.widget(0)
        self.stackedWidget.removeWidget(oldPage1)
        oldPage1.deleteLater()

        newPage1 = self.createPage1()
        self.stackedWidget.insertWidget(0, newPage1)
        self.stackedWidget.setCurrentIndex(0)
    
    def reloadPage2(self):
        oldPage2 = self.stackedWidget.widget(1)
        self.stackedWidget.removeWidget(oldPage2)
        oldPage2.deleteLater()

        newPage2 = self.createPage2()
        self.stackedWidget.insertWidget(1, newPage2)

    def reloadPage3(self):
        oldPage3 = self.stackedWidget.widget(2)
        self.stackedWidget.removeWidget(oldPage3)
        oldPage3.deleteLater()

        newPage3 = self.createPage3()
        self.stackedWidget.insertWidget(2, newPage3)

    def reloadPage4(self):
        oldPage4 = self.stackedWidget.widget(3)
        self.stackedWidget.removeWidget(oldPage4)
        oldPage4.deleteLater()

        newPage4 = self.createPage4()
        self.stackedWidget.insertWidget(3, newPage4)