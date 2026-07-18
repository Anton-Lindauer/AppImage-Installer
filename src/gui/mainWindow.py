import faulthandler
faulthandler.enable()

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGroupBox, QRadioButton, QPushButton, QStackedWidget, QLineEdit, QButtonGroup, QScrollArea, QTabWidget, QCheckBox, QHBoxLayout, QGridLayout, QDialog
from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QPixmap

import sys
import subprocess
import os
from pathlib import Path

from src.core.logic import Installer, Uninstaller, Logging
from src.gui.components import MenuBarUtils, PrepInstall, PrepUninstall
from src.gui.threads import MetadataWorker, InstallWorker

class MainWindow(QMainWindow):

    def __init__(self, selectedAppImage=None):
        super().__init__()

        self.selectedAppImage = selectedAppImage
    
        self.userDir = Path.home()
        self.fileDest = self.userDir / "AppImages"
        self.symLinkDir = self.userDir / ".local" / "bin"
        self.startMenuFilePath = self.userDir / ".local" / "share" / "applications"

        self.menubarUtils = MenuBarUtils()
        self.settings = QSettings("Anton-Lindauer", "AppImage-Installer")

        self.logger = Logging()

        self.tab1Page1Handler = PrepInstall()
        self.tab2Page1Handler = PrepUninstall()

        self.tab1Page1Handler.pickedFile.connect(self.tab1Page1Worker)

        self.desktopEnv = os.environ.get("XDG_CURRENT_DESKTOP")
        
        self.isKde = self.desktopEnv == "KDE"

# Used to display if the KDE integration is available
        kdeSupport = self.tr("Recommended") if self.isKde else self.tr("Not Supported")
        
        if not self.desktopEnv == "KDE":
            self.menubarUtils.loadTheme(self.settings.value("theme", "sysTheme", str))
        else:
            self.menubarUtils.loadTheme(self.settings.value("theme", "kdeTheme", str))
        
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
        file2.triggered.connect(lambda: self.populatePage1FileList() if self.tab1StackedWidget.currentIndex() == 0 and self.tabs.currentIndex() == 0 else None)
        file2.triggered.connect(lambda: self.tab1StackedWidget.setCurrentIndex(0) if self.tabs.currentIndex() == 0 else None)
        file2.triggered.connect(lambda: self.reloadTab2Page1() if self.tab2StackedWidget.currentIndex() == 0 and self.tabs.currentIndex() == 1 else None)
        file2.triggered.connect(lambda: self.tab2StackedWidget.setCurrentIndex(0) if self.tabs.currentIndex() == 1 else None)

        
        setting1 = settingsMenu.addMenu(self.tr("Theme"))
        settingsMenu.addSeparator()
        setting2 = settingsMenu.addAction(self.tr("Configure"))

# Qt doesn't immediately close a menu inside a menu when hovering over a different element.
# Therefore you have to force Qt to do it
        setting2.hovered.connect(lambda: setting1.hide())

        setting2.triggered.connect(self.menubarUtils.settingsWindow)

        theme1 = setting1.addAction(self.tr("System theme"))
        setting1.addSeparator()
        theme2 = setting1.addAction(self.tr("Modern Blue Dark"))
        setting1.addSeparator()
        theme3 = setting1.addAction(self.tr("Modern Dark"))
        setting1.addSeparator()
        theme4 = setting1.addAction(self.tr("Modern Light"))
        setting1.addSeparator()
        theme5 = setting1.addAction(self.tr("Use KDE theme ({Support})").format(Support=kdeSupport))

# Reloading tab 1 page 2 because it uses a different layout for QSS and KDE themes
        theme1.triggered.connect(lambda: self.menubarUtils.loadTheme("sysTheme"))
        theme1.triggered.connect(lambda: self.reloadTab1() if self.isKde else None)
        theme2.triggered.connect(lambda: self.menubarUtils.loadTheme("modernBlueDarkTheme"))
        theme2.triggered.connect(lambda: self.reloadTab1() if self.isKde else None)
        theme3.triggered.connect(lambda: self.menubarUtils.loadTheme("modernDarkTheme"))
        theme3.triggered.connect(lambda: self.reloadTab1() if self.isKde else None)
        theme4.triggered.connect(lambda: self.menubarUtils.loadTheme("modernLightTheme"))
        theme4.triggered.connect(lambda: self.reloadTab1() if self.isKde else None)
        theme5.triggered.connect(lambda: self.menubarUtils.loadTheme("kdeTheme"))
        theme5.triggered.connect(lambda: self.reloadTab1() if self.isKde else None)

        help1 = helpMenu.addAction("Github Repo")
        help1.triggered.connect(self.menubarUtils.openRepo)

# Hides the box around the box with the menues; Has to be declared for every menu
        for menu in (fileMenu, settingsMenu, setting1, helpMenu):
            menu.setWindowFlags(
                menu.windowFlags()
                | Qt.FramelessWindowHint
                | Qt.NoDropShadowWindowHint
                | Qt.Popup
            )
            menu.setAttribute(Qt.WA_TranslucentBackground)

            
############################################### Tab 1 - Page 1 ###############################################
# This is the static part of the page, it's only generated once, when the app launches
    def createTab1Page1(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        title = QLabel(self.tr("AppImage selection"))
        title.setObjectName("title")

# Let the user pick an AppImage from anywhere
        filedialogBtn = QPushButton(self.tr("Pick a file to install"))
        filedialogBtn.clicked.connect(lambda: self.tab1Page1Handler.userPick(self))

# QScrollArea with a container for all the QRadioButtons with adjustable size to fit up to five QRadioButtons and then enable scrolling
        self.tab1Page1ContainerScrollArea = QScrollArea()
        self.tab1Page1ContainerScrollArea.setWidgetResizable(True)
        self.tab1Page1ContainerScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

# Container in the QScrollArea
        container = QWidget()
        self.tab1Page1ContainerScrollArea.setWidget(container)

        self.tab1Page1ContainerLayout = QVBoxLayout(container)   
        self.tab1Page1ContainerLayout.setContentsMargins(0, 0, 0, 0,)
        self.tab1Page1ContainerLayout.setSpacing(0)

# The radiobutton selection has to be a seperate funktion to be able to update it, without updating the entire UI
        self.populatePage1FileList()

        self.tab1Page1SubmitBtn = QPushButton(self.tr("Continue"))  
        self.tab1Page1SubmitBtn.setObjectName("submitBtn")
        self.tab1Page1SubmitBtn.clicked.connect(lambda: self.tab1Page1Handler.findSelectedRadioBtn(self.groupPage1))

        mainLayout.addWidget(title)
        mainLayout.addWidget(filedialogBtn)
        mainLayout.addWidget(self.tab1Page1ContainerScrollArea)
        mainLayout.addWidget(self.tab1Page1SubmitBtn)
        mainLayout.addStretch()

        return mainWidget

# This is the dynamic part. By calling this function, the QRadioButtons in the QScrollArea get updated 
    def populatePage1FileList(self):
        self.clearLayout(self.tab1Page1ContainerLayout)

        if hasattr(self, "groupPage1"):
            self.groupPage1.deleteLater()
        self.groupPage1 = QButtonGroup(self)

# All paths of AppImage files in the Downloads directory
        self.fileList = Installer.listFiles(self.userDir)     
        fileListLen = len(self.fileList)

# Create a QRadioButton for each file
        if fileListLen > 0:
             for file in self.fileList:
                radioBtn = QRadioButton(file)
                self.tab1Page1ContainerLayout.addWidget(radioBtn)
                self.groupPage1.addButton(radioBtn)

        else:
            page1NoFileMsg = QLabel(self.tr("No .AppImage file has been found in your Downloads directory"))
            page1NoFileMsg.setObjectName("message")
            self.tab1Page1ContainerLayout.addWidget(page1NoFileMsg)

# Set the size of the QScrollArea to the size of the QRadioButtons in the QScrollArea to fix Qt's stupid default behaviour
        self.tab1Page1ContainerScrollArea.setFixedHeight(min(max(fileListLen, 1), 6) * 39)

# Disable the Scrollbar when you cannot scroll
        if fileListLen <= 6:
            self.tab1Page1ContainerScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

# General method to delete all the content of a layout, currently only used for the QScrollArea on page 1
    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

# Only accept a file from the menubar selector if the user is on the first page
    def tab1Page1Validator(self):
        if self.tab1StackedWidget.currentIndex() == 0:
            self.tab1Page1Handler.userPick(self)

# The worker that extracts the AppImages metadata
    def tab1Page1Worker(self, path):
        self.selectedAppPath = path

        self.tab1Page1SubmitBtn.setEnabled(False)

        self.metadataWorker = MetadataWorker(self.selectedAppPath, self.logger)

        self.metadataWorker.finished.connect(self.metadataLoader)
        self.metadataWorker.error.connect(self.workerError)

        self.metadataWorker.start()

# Loads the AppImages metadata in the QLineEdits and QRadiobuttons
    def metadataLoader(self, metadata):
        self.tab1StackedWidget.setCurrentIndex(1)

        self.programInfoList[0].setText(metadata["exec"].lower())
        self.programInfoList[1].setText(metadata["name"])
        self.programInfoList[2].setText(metadata["comment"])
        
# Activate the QRadioButtons when they are in the AppImages category string
        categories = metadata["categories"].split(";")

        for button in self.page2RadioBtns.buttons():
            button.setChecked(button.text() in categories)



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
# Has to be dynamic, because the layout is different for QSS and KDE themes
        self.tab1Page2ContainerLayout = QVBoxLayout(container)

        self.loadTab1Page2Container()

# All the things the user has to enter
        self.programInfo = [self.tr("Terminal Command"),
                            self.tr("Display Name"),
                            self.tr("Short Description"),
                            self.tr("Categories")]
        
# More information on what to enter for the user
        programInfoText = [self.tr("The command used to launch the application from the terminal."),
                           self.tr("The name that will appear in the start menu and application list."),
                           self.tr("A brief summary of the application (displayed as a tooltip)."),
                           self.tr("Determines the placement in the start menu.")]
        
# All main categories from freedesktop.org
        self.categoryList = ["AudioVideo", "Audio", "Video", 
                             "Development", "Education", "HealthFitness", 
                             "Game", "Graphics", "Network",
                             "Office", "Science", "Settings", 
                             "System", "Utility"]
        
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
                

            self.tab1Page2ContainerLayout.addWidget(containerTile)

        self.page2SubmitBtn = QPushButton(self.tr("Continue"))
        self.page2SubmitBtn.setObjectName("submitBtn")
        self.page2SubmitBtn.clicked.connect(self.page2Validator)

        self.page2BackBtn = QPushButton(self.tr("Back"))
        self.page2BackBtn.setObjectName("backBtn")
        self.page2BackBtn.clicked.connect(lambda: self.tab1StackedWidget.setCurrentIndex(0))
        self.page2BackBtn.clicked.connect(lambda: self.tab1Page1SubmitBtn.setEnabled(True))

        mainLayout.addWidget(title)
        mainLayout.addWidget(container)
        mainLayout.addWidget(self.page2SubmitBtn)
        mainLayout.addWidget(self.page2BackBtn)
        mainLayout.addStretch()    

        return mainWidget
    
    def page2Validator(self):
        if all(edit.text().strip() for edit in self.programInfoList) and self.page2RadioBtns.checkedButton() is not None:
            self.tab1StackedWidget.setCurrentIndex(2)

    def loadTab1Page2Container(self):
        if self.isKde and self.settings.value("theme", "sysTheme", str) == "kdeTheme":
            self.tab1Page2ContainerLayout.setContentsMargins(10, 10, 10, 10)
            self.tab1Page2ContainerLayout.setSpacing(6)
        else:
            self.tab1Page2ContainerLayout.setContentsMargins(0, 0, 0, 0)
            self.tab1Page2ContainerLayout.setSpacing(0)



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
        self.installWorker = InstallWorker(self.selectedAppPath, self.fileDest, self.userDir, self.programName,self.programDescr, self.programCategory, self.cmdName, self.logger, self.symLinkDir)

# Process status updates from the installation function
        self.installWorker.progressUpdate.connect(self.workerProgress)
        self.installWorker.finished.connect(self.workerFinished)
        self.installWorker.error.connect(self.workerError)

        self.terminalUpdateMsg.setText(self.tr("Installation in process..."))
        self.terminalUpdateMsg.show()

        self.installWorker.start()

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
        self.tab1Page4Title.setText(self.tr("Finished installing {name}").format(name=self.programInfoList[1].text()))

        self.tab1StackedWidget.setCurrentIndex(3)

        self.terminalUpdateMsg.setText("")

        self.page3SubmitBtn.setEnabled(True)
        self.page3BackBtn.setEnabled(True)



    def createTab1Page4(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        self.tab1Page4Title = QLabel(self.tr("Finished installing"))
        self.tab1Page4Title.setObjectName("title")

        submitBtn = QPushButton(self.tr("Install another program"))
        submitBtn.setObjectName("submitBtn")
# Reload the filelist, if the user wants to install more AppImages
        submitBtn.clicked.connect(self.populatePage1FileList)
        submitBtn.clicked.connect(lambda: self.tab1Page1SubmitBtn.setEnabled(True)) 
        submitBtn.clicked.connect(lambda: self.tab1StackedWidget.setCurrentIndex(0))

        mainLayout.addWidget(self.tab1Page4Title)
        mainLayout.addWidget(submitBtn)
        mainLayout.addStretch()
        
        return mainWidget

# Only reloads parts of pages with different layouts for QSS and KDE themes
    def reloadTab1(self):
        currentIndex = self.tab1StackedWidget.currentIndex()

        self.loadTab1Page2Container()

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

        self.appsMetadata = Uninstaller.getInstalledMetadata(self.startMenuFilePath)

        numOfApps = len(self.appsMetadata)

# Group for all QRadioButtons to later find out which one is checked
        self.groupTab2Page1 = QButtonGroup(self) 

# Create a QRadioButton for each file
        if numOfApps > 0:
             for index, app in enumerate(self.appsMetadata):
                radioBtn = QRadioButton(app.name)
                containerLayout.addWidget(radioBtn)
                self.groupTab2Page1.addButton(radioBtn)

                iconPath = app.iconPath

                radioBtnContainer = QWidget()
                #radioBtnContainer.setObjectName("radioBtnContainer")

                layout = QHBoxLayout(radioBtnContainer)
                layout.setContentsMargins(0, 0, 0, 0)

                iconLabel = QLabel()
                iconLabel.setObjectName("iconLabel")
                pixmap = QPixmap(iconPath)
                iconLabel.setPixmap(pixmap.scaled(22, 22, aspectMode=Qt.AspectRatioMode.KeepAspectRatio))

                layout.addWidget(iconLabel)
                layout.addWidget(radioBtn)

                containerLayout.addWidget(radioBtnContainer)

# Only create a divider if the element isn't the last one and add rounded corners to the first and last element
                suffix = "" if numOfApps <= 5 else "Scroll"

                if numOfApps == 1 and numOfApps <= 5:
                    radioBtn.setProperty("isFirstAndLast", "true")
                    radioBtnContainer.setProperty("isFirstAndLast", "true")
                elif index == 0:
                    radioBtn.setProperty(f"isFirst{suffix}", "true")
                    radioBtnContainer.setProperty(f"isFirst{suffix}", "true")
                elif index == numOfApps - 1:
                    radioBtn.setProperty(f"isLast{suffix}", "true")
                    radioBtnContainer.setProperty(f"isLast{suffix}", "true")
        else:
            tab2Page1NoFileMsg = QLabel(self.tr("No AppImage installation has been found"))
            tab2Page1NoFileMsg.setObjectName("message")
            containerLayout.addWidget(tab2Page1NoFileMsg)

# Set the size of the QScrollArea to the size of the QRadioButtons in the QScrollArea to fix Qt's stupid default behaviour
        containerScrollArea.setFixedHeight(min(numOfApps, 6) * 39)

        checkBox1 = QCheckBox(self.tr("Remove all symlinks (Recommended)"))
        checkBox1.setChecked(self.settings.value("rmvSymlinks", True, type=bool))
        checkBox1.toggled.connect(lambda checked1: self.settings.setValue("rmvSymlinks", checked1))
        checkBox2 = QCheckBox(self.tr("Remove startmenu entry (Recommended)"))
        checkBox2.setChecked(self.settings.value("rmvStartmenuEntry", True, type=bool))
        checkBox2.toggled.connect(lambda checked2: self.settings.setValue("rmvStartmenuEntry", checked2))

        submitBtn = QPushButton(self.tr("Continue"))
        submitBtn.setObjectName("submitBtn")
        submitBtn.clicked.connect(lambda: self.tab2Page1Handler.findSelectedRadioBtn(self.groupTab2Page1))
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
        
    def tab2Page1Worker(self, name):
        self.tab2StackedWidget.setCurrentIndex(1)
        for app in self.appsMetadata:
            if app.name == name:
                self.selectedAppPath = app.path
                self.desktopFilePath = app.desktopPath


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

        self.tab2TerminalUpdateMsg.setText(self.tr("Uninstallation in process..."))
        self.tab2TerminalUpdateMsg.show()

        if self.settings.value("rmvSymlinks", True, bool):
            Uninstaller.rmvInstalledFiles(symLinkFilePath)
            self.logger.addGeneralEntry(f"Permanently removed {symLinkFilePath}")
            self.terminalUpdate(self.tr("Removed symlink"))

        if self.settings.value("rmvStartmenuEntry", True, bool):
            Uninstaller.rmvInstalledFiles(self.desktopFilePath)
            self.logger.addGeneralEntry(f"Permanently removed {self.desktopFilePath}")
            self.terminalUpdate(self.tr("Removed startmenu entry"))

        Uninstaller.rmvInstalledFiles(self.selectedAppPath)
        self.logger.addGeneralEntry(f"Permanently removed {self.selectedAppPath}")
        self.terminalUpdate(self.tr("Removed AppImage file"))

        QTimer.singleShot(1000, self.terminalFinished)

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



# Error handler for all QThread workers; A pop up window with the error message and a button to open the error log
    def workerError(self, errorMsg):
        logFilePath = self.logger.logFilePath

        self.logger.addGeneralEntry(errorMsg)

        msgBox = QDialog()
        msgBox.setWindowTitle("Error!")

        msgBoxLayout = QVBoxLayout(msgBox)
        msgBoxLayout.setContentsMargins(20, 20, 20, 20)
        msgBoxLayout.setSpacing(6)

        textContainer = QWidget()
        textContainerLayout = QVBoxLayout(textContainer)

        msgTitle = QLabel(self.tr("AppImage-Installer ran into an issue!"))
        msgTitle.setObjectName("msgTitle")

        msgText = QLabel(self.tr("This error occured:\n{error}\nA more detailed log can be found in {logFile}.").format(error=errorMsg, logFile=logFilePath))

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

# Open the log file with the default file editor
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




from PySide6.QtGui import QPainterPath, QRegion
from PySide6.QtCore import QRectF

class RoundedScrollArea(QScrollArea):
    def __init__(self, radius=8, parent=None):
        super().__init__(parent)
        self.radius = radius

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_mask()

    def _update_mask(self):
        path = QPainterPath()
        rect = QRectF(self.rect())
        path.addRoundedRect(rect, self.radius, self.radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)