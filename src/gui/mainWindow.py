import faulthandler
faulthandler.enable()

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGroupBox, QRadioButton, QPushButton, QStackedWidget, QLineEdit, QButtonGroup, QScrollArea, QTabWidget, QCheckBox, QHBoxLayout, QStyledItemDelegate, QGridLayout, QSizePolicy, QDialog
from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QGuiApplication, QDesktopServices

import sys
import subprocess
import os
import time
from pathlib import Path

from src.core.logic import Installer, Uninstaller, Logging
from src.gui.components import General, Tab1Page1Logic, Tab2Page1Logic, InstallWorker

class MainWindow(QMainWindow):

    def __init__(self, selectedAppImage=None):
        super().__init__()

        self.selectedAppImage = selectedAppImage
    
        self.userDir = Path.home()
        self.fileDest = self.userDir / "AppImages"
        self.symLinkDir = self.userDir / ".local/bin"
        self.startMenuFilePath = self.userDir / ".local" / "share" / "applications"

        self.general = General()
        self.settings = QSettings("Anton-Lindauer", "AppImage-Installer")

        self.logger = Logging()

        self.tab1Page1Handler = Tab1Page1Logic()
        self.tab2Page1Handler = Tab2Page1Logic()

        self.desktopEnv = os.environ.get("XDG_CURRENT_DESKTOP")
        
        self.isKde = self.desktopEnv == "KDE"

# Used to display if the KDE integration is available
        kdeSupport = self.tr("Recommended") if self.isKde else self.tr("Not Supported")
        
        if not self.desktopEnv == "KDE":
            self.general.loadTheme(self.settings.value("theme", "sysTheme", str))
        else:
            self.general.loadTheme(self.settings.value("theme", "kdeTheme", str))
        
        self.setWindowTitle("AppImage-Installer")
        self.setMinimumSize(750, 710)

# QWidget for everything
        central = QWidget()
        self.setCentralWidget(central)

        mainLayout = QVBoxLayout(central)
        mainLayout.setContentsMargins(6, 6, 6, 6)
        mainLayout.setSpacing(0)

# Tab one
        self.tabs = QTabWidget()

        self.tab1 = QWidget()
        self.tab1Layout = QHBoxLayout(self.tab1)

# The QStackedWidget that contains all pages 
        self.tab1StackedWidget = QStackedWidget()

        self.tab1Page1 = self.createTab1Page1()
        self.tab1Page2 = self.createTab1Page2()
        self.tab1Page3 = self.createTab1Page3()
        self.tab1Page4 = self.createTab1Page4()

        self.tab1StackedWidget.addWidget(self.tab1Page1)
        self.tab1StackedWidget.addWidget(self.tab1Page2)
        self.tab1StackedWidget.addWidget(self.tab1Page3)
        self.tab1StackedWidget.addWidget(self.tab1Page4)

        self.tab1Layout.addWidget(self.tab1StackedWidget)

        if not self.selectedAppImage == None:
            self.tab1StackedWidget.setCurrentIndex(1)
            self.selectedAppPath = self.selectedAppImage

# Tab two
        self.tab2 = QWidget()
        self.tab2Layout = QHBoxLayout(self.tab2)

# The QStackedWidget that contains all pages 
        self.tab2StackedWidget = QStackedWidget()

        self.tab2Page1 = self.createTab2Page1()
        self.tab2Page2 = self.createTab2Page2()
        self.tab2Page3 = self.createTab2Page3()

        self.tab2StackedWidget.addWidget(self.tab2Page1)
        self.tab2StackedWidget.addWidget(self.tab2Page2)
        self.tab2StackedWidget.addWidget(self.tab2Page3)

        self.tab2Layout.addWidget(self.tab2StackedWidget)

        self.tabs.addTab(self.tab1, self.tr("Install"))
        self.tabs.addTab(self.tab2, self.tr("Remove"))

        mainLayout.addWidget(self.tabs)



# All of the remaining code in this function is for the QMenuBar
        optionsBar = self.menuBar()

        fileMenu = optionsBar.addMenu(self.tr("File"))
        settingsMenu = optionsBar.addMenu(self.tr("Settings"))
        helpMenu = optionsBar.addMenu(self.tr("Help"))

        file1 = fileMenu.addAction(self.tr("Pick a file to install"))
        fileMenu.addSeparator()
        file2 = fileMenu.addAction(self.tr("Refresh file list"))

        file1.triggered.connect(self.tab1Page1Validator)
        file2.triggered.connect(lambda: self.reloadTab1Page1() if self.tab1StackedWidget.currentIndex() == 0 and self.tabs.currentIndex() == 0 else None)
        file2.triggered.connect(lambda: self.tab1StackedWidget.setCurrentIndex(0) if self.tabs.currentIndex() == 0 else None)
        file2.triggered.connect(lambda: self.reloadTab2Page1() if self.tab2StackedWidget.currentIndex() == 0 and self.tabs.currentIndex() == 1 else None)
        file2.triggered.connect(lambda: self.tab2StackedWidget.setCurrentIndex(0) if self.tabs.currentIndex() == 1 else None)

        
        setting1 = settingsMenu.addMenu(self.tr("Theme"))
        settingsMenu.addSeparator()
        setting2 = settingsMenu.addAction(self.tr("Configure"))

# Qt doesn't immediately close a menu inside a menu when hovering over a different element.
# Therefore you have to force Qt to do it
        setting2.hovered.connect(lambda: setting1.hide())

        setting2.triggered.connect(self.general.settingsWindow)

        theme1 = setting1.addAction(self.tr("System theme"))
        setting1.addSeparator()
        theme2 = setting1.addAction(self.tr("Modern Blue Dark"))
        setting1.addSeparator()
        theme3 = setting1.addAction(self.tr("Modern Dark"))
        setting1.addSeparator()
        theme4 = setting1.addAction(self.tr("Modern Light"))
        setting1.addSeparator()
        theme5 = setting1.addAction(self.tr(f"Use KDE theme ({kdeSupport})"))

# Reloading tab 1 page 2 because it uses a different layout for QSS and KDE themes
        theme1.triggered.connect(lambda: self.general.loadTheme("sysTheme"))
        theme1.triggered.connect(lambda: self.reloadTab1() if self.isKde else None)
        theme2.triggered.connect(lambda: self.general.loadTheme("modernBlueDarkTheme"))
        theme2.triggered.connect(lambda: self.reloadTab1() if self.isKde else None)
        theme3.triggered.connect(lambda: self.general.loadTheme("modernDarkTheme"))
        theme3.triggered.connect(lambda: self.reloadTab1() if self.isKde else None)
        theme4.triggered.connect(lambda: self.general.loadTheme("modernLightTheme"))
        theme4.triggered.connect(lambda: self.reloadTab1() if self.isKde else None)
        theme5.triggered.connect(lambda: self.general.loadTheme("kdeTheme"))
        theme5.triggered.connect(lambda: self.reloadTab1() if self.isKde else None)

        help1 = helpMenu.addAction("Github Repo")
        help1.triggered.connect(General.openRepo)

# Hides the box around the box with the menues; Has to be declared for every menu
        for menu in (fileMenu, settingsMenu, setting1, helpMenu):
            menu.setWindowFlags(
                menu.windowFlags()
                | Qt.FramelessWindowHint
                | Qt.NoDropShadowWindowHint
                | Qt.Popup
            )
            menu.setAttribute(Qt.WA_TranslucentBackground)

            

    def createTab1Page1(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        title = QLabel(self.tr("AppImage selection"))
        title.setObjectName("title")

# Let the user pick an AppImage from anywhere
        filedialogBtn = QPushButton(self.tr("Pick a file to install"))
        
        self.tab1Page1Handler.pickedFile.connect(self.tab1Page1Worker)
        filedialogBtn.clicked.connect(lambda: self.tab1Page1Handler.userPick(self))

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
            page1NoFileMsg = QLabel(self.tr("No .AppImage file has been found in your Downloads directory"))
            page1NoFileMsg.setObjectName("message")
            containerLayout.addWidget(page1NoFileMsg)

# Set the size of the QScrollArea to the size of the QRadioButtons in the QScrollArea to fix Qt's stupid default behaviour
        containerScrollArea.setFixedHeight(min(fileListLen, 6) * 39)

        submitBtn = QPushButton(self.tr("Continue"))  
        submitBtn.setObjectName("submitBtn")
        submitBtn.clicked.connect(lambda: self.tab1Page1Handler.findSeletedRadioBtn(self.groupPage1))

        mainLayout.addWidget(title)
        mainLayout.addWidget(filedialogBtn)
        mainLayout.addWidget(containerScrollArea)
        mainLayout.addWidget(submitBtn)
        mainLayout.addStretch()

        return mainWidget
    
    def tab1Page1Validator(self):
        if self.tab1StackedWidget.currentIndex() == 0:
            self.tab1Page1Handler.userPick(self)
        
    def tab1Page1Worker(self, path):
        self.tab1StackedWidget.setCurrentIndex(1)
        self.selectedAppPath = path



    def createTab1Page2(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        title = QLabel(self.tr("Program information"))
        title.setObjectName("title")

# Box for the options for the user; Contains other boxes with the descriptions and QlineEdits
        container = QGroupBox()
        
# Set the layout in the container
# I have to do it like this to enable hover effects for the custom QSS styles,
# because margin isn't affected by hover effects
        containerLayout = QVBoxLayout(container)
        if self.isKde and self.settings.value("theme", "sysTheme", str) == "kdeTheme":
            containerLayout.setContentsMargins(10, 10, 10, 10)
            containerLayout.setSpacing(6)
        else:
            containerLayout.setContentsMargins(0, 0, 0, 0)
            containerLayout.setSpacing(0)

# All the things the user has to enter
        self.programInfo = [self.tr("Terminal Command"),
                            self.tr("Display Name"),
                            self.tr("Short Description"),
                            self.tr("Categories")]
        
# More information on what to enter for the user
        programInfoText = [self.tr("The command used to launch the application from the terminal."),
                           self.tr("The name that will appear in the start menu and application list."),
                           self.tr("A brief summary of the application (displayed as a tooltip)."),
                           self.tr("Determines the placement in the start menu. Some categories can't be combined; combined they create a different category.")]
        
        self.categoryList = ["Accessibility;Utility", "Education", "Office", 
                             "Development", "Graphics", "Network", 
                             "AudioVideo", "Game", "System",
                             "Science;Education", "Utility", 
                             "Settings", "System;Settings"]
        
        self.programInfoList = []
        
# Create all the element in the groupbox
        for index, info in enumerate(self.programInfo):  
# Boxes with the descriptions and the QLineEdits 
            containerTile = QWidget()
            containerTile.setObjectName("page2InnerBox")

            tileLayout = QVBoxLayout(containerTile)
            tileLayout.setContentsMargins(0, 0, 0, 0)
            tileLayout.setSpacing(6)

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

# Add QRadioButtons only to the last box, QLineEdits for all other boxes
            if index == index == len(self.programInfo) - 1:
                innerTile = QWidget()
                innerTileLayout = QGridLayout(innerTile)
                innerTileLayout.setContentsMargins(0, 0, 0, 6)
                innerTileLayout.setSpacing(6)

                self.allCategories = ""
                self.page2RadioBtns = QButtonGroup()
                self.page2RadioBtns.setExclusive(False)

# Create a QRadioButton for all 13 categories
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

        self.page2SubmitBtn = QPushButton(self.tr("Continue"))
        self.page2SubmitBtn.setObjectName("submitBtn")
        self.page2SubmitBtn.clicked.connect(self.page2Validator)

        self.page2BackBtn = QPushButton(self.tr("Back"))
        self.page2BackBtn.setObjectName("backBtn")
        self.page2BackBtn.clicked.connect(lambda: self.tab1StackedWidget.setCurrentIndex(0))

        mainLayout.addWidget(title)
        mainLayout.addWidget(container)
        mainLayout.addWidget(self.page2SubmitBtn)
        mainLayout.addWidget(self.page2BackBtn)
        mainLayout.addStretch()    

        return mainWidget
    
    def page2Validator(self):
        if all(edit.text().strip() for edit in self.programInfoList) and self.page2RadioBtns.checkedButton() is not None:
            self.tab1StackedWidget.setCurrentIndex(2)



    def createTab1Page3(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        title = QLabel(self.tr("Installation process"))
        title.setObjectName("title")

# QGroupBox thats used as a terminal for the status updates, that the user receives
        container = QGroupBox()    
        terminalLayout = QVBoxLayout(container)
        terminalLayout.setContentsMargins(6, 6, 6, 6)
        terminalLayout.setSpacing(0)

        container.setMinimumHeight(200)
        container.setObjectName("page3Container")

# Updates that are displayed in the GUIs terminal like UI element
        self.terminalUpdateMsg = QLabel()     
        self.terminalUpdateMsg.setObjectName("terminalText")

        terminalLayout.addWidget(self.terminalUpdateMsg)
        terminalLayout.addStretch()

        self.page3SubmitBtn = QPushButton(self.tr("Start installation"))
        self.page3SubmitBtn.setObjectName("submitBtn")
        self.page3SubmitBtn.clicked.connect(self.installProgram)

        self.page3BackBtn = QPushButton(self.tr("Back"))
        self.page3BackBtn.setObjectName("backBtn")
        self.page3BackBtn.clicked.connect(lambda: self.tab1StackedWidget.setCurrentIndex(1))

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

# Temporary way of deleting old logs
        if self.settings.value("autoDelete", True, type=bool):
                self.logger.rmvOldLogs()

# Function that installs the program
        self.worker = InstallWorker(self.selectedAppPath, self.fileDest, self.userDir, self.programName,self.programDescr, self.programCategory, self.cmdName, self.logger, self.symLinkDir)

# Process status updates from the installation function
        self.worker.progressUpdate.connect(self.workerProgress)
        self.worker.success.connect(self.workerFinished)
        self.worker.error.connect(self.workerError)

        self.terminalUpdateMsg.setText(self.tr("Installation in process..."))
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
        self.terminalUpdateMsg.setText(self.tr("Installation finished"))

# Rebuild page four to display the program name
# Easier to maintain to just rebuild the entire page than updating every element one by one
        self.reloadTab1Page4()

        self.tab1StackedWidget.setCurrentIndex(3)

    def workerError(self, errorMsg):
        logFilePath = self.logger.logFilePath

        self.logger.addGeneralEntry(errorMsg)
# A pop-up window if a error occurs during the installation process
        msgBox = QDialog()
        msgBox.setWindowTitle("Error!")

        msgBoxLayout = QVBoxLayout(msgBox)
        msgBoxLayout.setContentsMargins(20, 20, 20, 20)
        msgBoxLayout.setSpacing(6)

        textContainer = QWidget()
        textContainerLayout = QVBoxLayout(textContainer)

        msgTitle = QLabel(self.tr("AppImage-Installer ran into an issue!"))
        msgTitle.setObjectName("msgTitle")

        msgText = QLabel(self.tr(f"This error occured:\n{errorMsg}\nA more detailed log can be found in {logFilePath}."))

        textContainerLayout.addWidget(msgTitle)
        textContainerLayout.addWidget(msgText)

        msgBoxLayout.addWidget(textContainer, alignment=Qt.AlignHCenter)

        btnLayout = QHBoxLayout()
        btnLayout.setContentsMargins(0, 0, 0, 0,)
        btnLayout.setSpacing(0)

        exitBtn = QPushButton(self.tr("Exit"))
        exitBtn.setObjectName("leftBtn")
        exitBtn.clicked.connect(lambda: sys.exit())

        openLogBtn = QPushButton(self.tr("Open Log"))
        openLogBtn.setObjectName("rightBtn")
        openLogBtn.setDefault(True)
        openLogBtn.setAutoDefault(True)

# I didn't want to write a function for one command
        openLogBtn.clicked.connect(lambda: subprocess.Popen(
                ["xdg-open", str(logFilePath)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            ))

        btnLayout.addWidget(exitBtn)
        btnLayout.addWidget(openLogBtn)

        msgBoxLayout.addLayout(btnLayout)

        msgBox.exec()

        sys.exit()



    def createTab1Page4(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        title = QLabel(self.tr(f"Finished installing {self.programInfoList[1].text()}"))
        title.setObjectName("title")

# Reload all pages if the user wants to install another program
        submitBtn = QPushButton(self.tr("Install another program"))
        submitBtn.setObjectName("submitBtn")
        submitBtn.clicked.connect(self.reloadTab1Page1)     
        submitBtn.clicked.connect(self.reloadTab1Page2)
        submitBtn.clicked.connect(self.reloadTab1Page3)
        submitBtn.clicked.connect(lambda: self.tab1StackedWidget.setCurrentIndex(0))

        mainLayout.addWidget(title)
        mainLayout.addWidget(submitBtn)
        mainLayout.addStretch()
        
        return mainWidget
    
# Functions to rebuild all pages; to remove all previous user input
# Easier to maintain than to clear all elements one by one
    def reloadTab1Page1(self):
        oldPage1 = self.tab1StackedWidget.widget(0)
        self.tab1StackedWidget.removeWidget(oldPage1)
        oldPage1.deleteLater()

        newPage1 = self.createTab1Page1()
        self.tab1StackedWidget.insertWidget(0, newPage1)
    
    def reloadTab1Page2(self):
        oldPage2 = self.tab1StackedWidget.widget(1)
        self.tab1StackedWidget.removeWidget(oldPage2)
        oldPage2.deleteLater()

        newPage2 = self.createTab1Page2()
        self.tab1StackedWidget.insertWidget(1, newPage2)

    def reloadTab1Page3(self):
        oldPage3 = self.tab1StackedWidget.widget(2)
        self.tab1StackedWidget.removeWidget(oldPage3)
        oldPage3.deleteLater()

        newPage3 = self.createTab1Page3()
        self.tab1StackedWidget.insertWidget(2, newPage3)

    def reloadTab1Page4(self):
        oldPage4 = self.tab1StackedWidget.widget(3)
        self.tab1StackedWidget.removeWidget(oldPage4)
        oldPage4.deleteLater()

        newPage4 = self.createTab1Page4()
        self.tab1StackedWidget.insertWidget(3, newPage4)

    def reloadTab1(self):
        currentIndex = self.tab1StackedWidget.currentIndex()

        #self.reloadTab1Page1()
        self.reloadTab1Page2()
        #self.reloadTab1Page3()
        #self.reloadTab1Page4()

        self.tab1StackedWidget.setCurrentIndex(currentIndex)




    def createTab2Page1(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        title = QLabel(self.tr("AppImage selection"))
        title.setObjectName("title")

# Let the user pick a AppImage from anywhere
        filedialogBtn = QPushButton(self.tr("Pick a AppImage program to uninstall"))
        
        self.tab2Page1Handler.pickedFile.connect(self.tab2Page1Worker)
        filedialogBtn.clicked.connect(lambda: self.tab2Page1Handler.userPick(self))

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
        self.installedList = Uninstaller.listInstalls(self.fileDest)     
        installedListLen = len(self.installedList)

# Group for all QRadioButtons to later find out which one is checked
        self.groupTab2Page1 = QButtonGroup(self) 

# Create a QRadioButton for each file
        if installedListLen > 0:
             for itemPos, file in enumerate(self.installedList):
                radioBtn = QRadioButton(file)
                containerLayout.addWidget(radioBtn)
                self.groupTab2Page1.addButton(radioBtn)

# Only create a divider if the element isn't the last one and add rounded corners to the first and last element
                suffix = "" if installedListLen <= 5 else "Scroll"

                if installedListLen == 1 and installedListLen <= 5:
                    radioBtn.setProperty("isFirstAndLast", "true")
                elif itemPos == 0:
                    radioBtn.setProperty(f"isFirst{suffix}", "true")
                elif itemPos == installedListLen - 1:
                    radioBtn.setProperty(f"isLast{suffix}", "true")
        else:
            tab2Page1NoFileMsg = QLabel(self.tr("No AppImage installation has been found"))
            tab2Page1NoFileMsg.setObjectName("message")
            containerLayout.addWidget(tab2Page1NoFileMsg)

# Set the size of the QScrollArea to the size of the QRadioButtons in the QScrollArea to fix Qt's stupid default behaviour
        containerScrollArea.setFixedHeight(min(installedListLen, 6) * 39)

        checkBox1 = QCheckBox(self.tr("Remove all symlinks (Recommended)"))
        checkBox1.setChecked(self.settings.value("rmvSymlinks", True, type=bool))
        checkBox1.toggled.connect(lambda checked1: self.settings.setValue("rmvSymlinks", checked1))
        checkBox2 = QCheckBox(self.tr("Remove startmenu entry (Recommended)"))
        checkBox2.setChecked(self.settings.value("rmvStartmenuEntry", True, type=bool))
        checkBox2.toggled.connect(lambda checked2: self.settings.setValue("rmvStartmenuEntry", checked2))

        submitBtn = QPushButton(self.tr("Continue"))
        submitBtn.setObjectName("submitBtn")
        submitBtn.clicked.connect(lambda: self.tab2Page1Handler.findSeletedRadioBtn(self.groupTab2Page1))
        submitBtn.clicked.connect(lambda: self.tab2StackedWidget.setCurrentIndex(1))

        mainLayout.addWidget(title)
        mainLayout.addWidget(filedialogBtn)
        mainLayout.addWidget(containerScrollArea)
        mainLayout.addWidget(checkBox1)        
        mainLayout.addWidget(checkBox2)
        mainLayout.addWidget(submitBtn)
        mainLayout.addStretch()

        return mainWidget
    
    def tab2Page1Validator(self):
        if self.tab2StackedWidget.currentIndex() == 0:
            self.tab2Page1Handler.userPick(self)
        
    def tab2Page1Worker(self, path):
        self.tab2StackedWidget.setCurrentIndex(1)
        self.selectedAppPath = path

    def createTab2Page2(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        title = QLabel(self.tr("Uninstallation process"))
        title.setObjectName("title")

# QGroupBox thats used as a terminal for the status updates, that the user receives
        container = QGroupBox()    
        terminalLayout = QVBoxLayout(container)
        terminalLayout.setContentsMargins(6, 6, 6, 6)
        terminalLayout.setSpacing(0)

        container.setMinimumHeight(200)
        container.setObjectName("page3Container")

# Updates that are displayed in the GUIs terminal like UI element
        self.tab2TerminalUpdateMsg = QLabel()     
        self.tab2TerminalUpdateMsg.setObjectName("terminalText")

        terminalLayout.addWidget(self.tab2TerminalUpdateMsg)
        terminalLayout.addStretch()

        self.tab2Page2SubmitBtn = QPushButton(self.tr("Start uninstallation"))
        self.tab2Page2SubmitBtn.setObjectName("submitBtn")
        self.tab2Page2SubmitBtn.clicked.connect(self.uninstallProgram)

        self.tab2Page2BackBtn = QPushButton(self.tr("Back"))
        self.tab2Page2BackBtn.setObjectName("backBtn")
        self.tab2Page2BackBtn.clicked.connect(lambda: self.tab2StackedWidget.setCurrentIndex(0))

        mainLayout.addWidget(title)
        mainLayout.addWidget(container)
        mainLayout.addWidget(self.tab2Page2SubmitBtn)
        mainLayout.addWidget(self.tab2Page2BackBtn)
        mainLayout.addStretch()

        return mainWidget
    
    def uninstallProgram(self):
        self.tab2Page2SubmitBtn.setEnabled(False)
        self.tab2Page2BackBtn.setEnabled(False)

        symLinkFilePath = Uninstaller.listSymlinks(self.selectedAppPath, self.symLinkDir)
        desktopFilePath = Uninstaller.findDesktopFile(self.startMenuFilePath, self.selectedAppPath)

        self.tab2TerminalUpdateMsg.setText(self.tr("Uninstallation in process..."))
        self.tab2TerminalUpdateMsg.show()

        if self.settings.value("rmvSymlinks", True, bool):
            Uninstaller.rmvInstalledFiles(symLinkFilePath)
            self.logger.addGeneralEntry(f"Permanently removed {symLinkFilePath}")
            self.terminalUpdate(self.tr("Removed symlink"))

        if self.settings.value("rmvStartmenuEntry", True, bool):
            Uninstaller.rmvInstalledFiles(desktopFilePath)
            self.logger.addGeneralEntry(f"Permanently removed {desktopFilePath}")
            self.terminalUpdate(self.tr("Removed startmenu entry"))

        Uninstaller.rmvInstalledFiles(self.selectedAppPath)
        self.logger.addGeneralEntry(f"Permanently removed {self.selectedAppPath}")
        self.terminalUpdate(self.tr("Removed AppImage file"))

        QTimer.singleShot(2000, self.terminalFinished)

    def terminalUpdate(self, msg):
        currentProgress = self.tab2TerminalUpdateMsg.text()

# Update the terminal if a new progress update arrived
        if currentProgress: 
            newProgress = currentProgress + "\n" + msg
        else:
            newProgress = msg

        self.tab2TerminalUpdateMsg.setText(newProgress)
        self.tab2TerminalUpdateMsg.show()

    def terminalFinished(self):
        self.tab2StackedWidget.setCurrentIndex(2)
    

    def createTab2Page3(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        title = QLabel(self.tr("Uninstallation finished"))
        title.setObjectName("title")

# Reload all pages if the user wants to install another program
        submitBtn = QPushButton(self.tr("Remove another AppImage program"))
        submitBtn.setObjectName("submitBtn")
        submitBtn.clicked.connect(self.reloadTab2Page1)     
        submitBtn.clicked.connect(self.reloadTab2Page2)
        submitBtn.clicked.connect(lambda: self.tab2StackedWidget.setCurrentIndex(0))

        mainLayout.addWidget(title)
        mainLayout.addWidget(submitBtn)
        mainLayout.addStretch()
        
        return mainWidget
    


    def reloadTab2Page1(self):
        oldPage1 = self.tab2StackedWidget.widget(0)
        self.tab2StackedWidget.removeWidget(oldPage1)
        oldPage1.deleteLater()

        newPage1 = self.createTab2Page1()
        self.tab2StackedWidget.insertWidget(0, newPage1)

    def reloadTab2Page2(self):
        oldPage2 = self.tab2StackedWidget.widget(1)
        self.tab2StackedWidget.removeWidget(oldPage2)
        oldPage2.deleteLater()

        newPage2 = self.createTab2Page2()
        self.tab2StackedWidget.insertWidget(1, newPage2)