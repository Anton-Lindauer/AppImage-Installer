import faulthandler
faulthandler.enable()

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGroupBox, QRadioButton, QPushButton, QStackedWidget, QLineEdit, QButtonGroup, QScrollArea, QTabWidget, QCheckBox, QHBoxLayout, QGridLayout, QDialog, QSizePolicy
from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QPixmap

import sys
import subprocess
import os
from pathlib import Path

from src.core.logic import Installer, Uninstaller, Logging, AppMetadata
from src.gui.components import MenuBarUtils, InstallFileSelector
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

        self.tab1Page1Handler = InstallFileSelector()

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
            self.selectedAppImagePath = self.selectedAppImage

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
        self.tabs.addTab(self.tab2, self.tr("Manage"))

        mainLayout.addWidget(self.tabs)



# All of the remaining code in this function is for the QMenuBar
        optionsBar = self.menuBar()

        fileMenu = optionsBar.addMenu(self.tr("File"))
        settingsMenu = optionsBar.addMenu(self.tr("Settings"))
        helpMenu = optionsBar.addMenu(self.tr("Help"))

        file1 = fileMenu.addAction(self.tr("Pick a file to install"))
        fileMenu.addSeparator()
        file2 = fileMenu.addAction(self.tr("Refresh list"))

        file1.triggered.connect(self.tab1Page1Validator)
        file2.triggered.connect(lambda: self.populateFileSelection() if self.tab1StackedWidget.currentIndex() == 0 and self.tabs.currentIndex() == 0 else None)
        file2.triggered.connect(lambda: self.tab1StackedWidget.setCurrentIndex(0) if self.tabs.currentIndex() == 0 else None)
        file2.triggered.connect(lambda: self.populateProgramSelection() if self.tab2StackedWidget.currentIndex() == 0 and self.tabs.currentIndex() == 1 else None)
        file2.triggered.connect(lambda: self.tab2StackedWidget.setCurrentIndex(0) if self.tabs.currentIndex() == 1 else None)

        
        setting1 = settingsMenu.addMenu(self.tr("Theme"))
        settingsMenu.addSeparator()
        setting2 = settingsMenu.addAction(self.tr("Configure"))

# Qt doesn't immediately close a menu inside a menu when hovering over a different element.
# Therefore you have to force Qt to do it
        setting2.hovered.connect(lambda: setting1.hide())

        setting2.triggered.connect(self.menubarUtils.openSettingsWindow)

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
        filedialogBtn.clicked.connect(lambda: self.tab1Page1Handler.openFileDialog(self))

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
        self.populateFileSelection()

        self.tab1Page1SubmitBtn = QPushButton(self.tr("Continue"))  
        self.tab1Page1SubmitBtn.clicked.connect(lambda: self.tab1Page1Handler.emitSelectedRadioBtn(self.groupPage1))

        mainLayout.addWidget(title)
        mainLayout.addWidget(filedialogBtn)
        mainLayout.addWidget(self.tab1Page1ContainerScrollArea)
        mainLayout.addWidget(self.tab1Page1SubmitBtn)
        mainLayout.addStretch()

        return mainWidget

# This is the dynamic part. By calling this function, the QRadioButtons in the QScrollArea get updated 
    def populateFileSelection(self):
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

# Disable the scrollbar handle when there aren't enough QRadioButtons to scroll
        if fileListLen <= 6:
            self.tab1Page1ContainerScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

# General method to delete all the content of a layout, currently used for the QScrollAreas on tab one and two page one
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
            self.tab1Page1Handler.openFileDialog(self)

# The worker that extracts the AppImages metadata
    def tab1Page1Worker(self, path):
        self.selectedAppImagePath = path

        self.tab1Page1SubmitBtn.setEnabled(False)

        self.metadataWorker = MetadataWorker(self.selectedAppImagePath, self.logger)

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
                           self.tr("A brief summary of the application."),
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
        self.page2SubmitBtn.clicked.connect(self.page2Validator)

        self.page2BackBtn = QPushButton(self.tr("Back"))
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
        self.page3SubmitBtn.clicked.connect(self.installProgram)

        self.page3BackBtn = QPushButton(self.tr("Back"))
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
        self.installWorker = InstallWorker(self.selectedAppImagePath, self.fileDest, self.userDir, self.programName,self.programDescr, self.programCategory, self.cmdName, self.logger, self.symLinkDir)

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

        try:
            self.tab1Page4OpenProgramBtn.clicked.disconnect()
        except TypeError:
            pass

# Currently broken; idk why but a clicked signal is send twice when calling the connect funktion
        self.tab1Page4OpenProgramBtn.setText(self.tr("Open {name}").format(name=self.programInfoList[1].text()))
        #self.tab1Page4OpenProgramBtn.clicked.connect(self.openProgram(self.cmdName))

        self.tab1StackedWidget.setCurrentIndex(3)

        self.terminalUpdateMsg.setText("")

        self.page3SubmitBtn.setEnabled(True)
        self.page3BackBtn.setEnabled(True)

        self.populateProgramSelection()


    def createTab1Page4(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        self.tab1Page4Title = QLabel(self.tr("Finished installing"))
        self.tab1Page4Title.setObjectName("title")

        submitBtn = QPushButton(self.tr("Install another program"))
# Reload the filelist, if the user wants to install more AppImages
        submitBtn.clicked.connect(self.populateFileSelection)
        submitBtn.clicked.connect(lambda: self.tab1Page1SubmitBtn.setEnabled(True)) 
        submitBtn.clicked.connect(lambda: self.tab1StackedWidget.setCurrentIndex(0))

        self.tab1Page4OpenProgramBtn = QPushButton(self.tr("Open"))

        mainLayout.addWidget(self.tab1Page4Title)
        mainLayout.addWidget(submitBtn)
        mainLayout.addWidget(self.tab1Page4OpenProgramBtn)
        mainLayout.addStretch()
        
        return mainWidget
    
    def openProgram(self, program):
        subprocess.Popen(
        [program],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True)

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

        title = QLabel(self.tr("App selection"))
        title.setObjectName("title")

# QScrollArea with a container for all the QRadioButtons with adjustable size to fit up to five QRadioButtons and then enable scrolling
        self.tab2Page1ContainerScrollArea = QScrollArea()
        self.tab2Page1ContainerScrollArea.setWidgetResizable(True)
        self.tab2Page1ContainerScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

# Container in the QScrollArea
        container = QWidget() 
        self.tab2Page1ContainerScrollArea.setWidget(container)

        self.tab2Page1ContainerLayout = QVBoxLayout(container)   
        self.tab2Page1ContainerLayout.setContentsMargins(10, 10, 10, 10,)
        self.tab2Page1ContainerLayout.setSpacing(6)

        self.populateProgramSelection()

        mainLayout.addWidget(title)
        mainLayout.addWidget(self.tab2Page1ContainerScrollArea)
        mainLayout.addStretch()

        return mainWidget
    
    def populateProgramSelection(self):
        self.clearLayout(self.tab2Page1ContainerLayout)

        self.appsMetadata = Uninstaller.getInstalledMetadata(self.startMenuFilePath)

        appsConfigList = AppMetadata.getAppsMetadata(self.startMenuFilePath)

        numOfApps = len(self.appsMetadata)

# Group for all QRadioButtons to later find out which one is checked
        if hasattr(self, "groupTab2Page1"):
            self.groupTab2Page1.deleteLater()
        self.groupTab2Page1 = QButtonGroup(self) 

# Create a tile for each file
        if numOfApps > 0:
             for app in self.appsMetadata:

                tile = QGroupBox()
                tile.setObjectName("appTile")

                tileLayout = QHBoxLayout(tile)
                tileLayout.setContentsMargins(10, 10, 10, 10)
                tileLayout.setSpacing(6)

                iconPath = app.iconPath

                iconLabel = QLabel()
                iconLabel.setObjectName("iconLabel")
                pixmap = QPixmap(iconPath)
                iconLabel.setPixmap(pixmap.scaled(22, 22, aspectMode=Qt.AspectRatioMode.KeepAspectRatio))

                nameLabel = QLabel(app.name)
                nameLabel.setFixedWidth(200)
                nameLabel.setObjectName("nameLabel")

                launchBtn = QPushButton(self.tr("Launch"))
                launchBtn.setObjectName("appBtn")
                launchBtn.clicked.connect(lambda checked=False, app=app: self.openProgram(app.path))

                configureBtn = QPushButton(self.tr("Configure"))
                configureBtn.setObjectName("appBtn")
                configureBtn.clicked.connect(lambda checked=False, app=app: self.appConfigWindow(appsConfigList, app.name))

                deleteBtn = QPushButton(self.tr("Delete"))
                deleteBtn.setObjectName("appBtn")
                deleteBtn.clicked.connect(lambda checked=False, app=app: self.tab2Page1Worker(app.name))

                tileLayout.addWidget(iconLabel)
                tileLayout.addWidget(nameLabel)
                tileLayout.addStretch()
                tileLayout.addWidget(launchBtn)
                tileLayout.addWidget(configureBtn)
                tileLayout.addWidget(deleteBtn)

                self.tab2Page1ContainerLayout.addWidget(tile)

        else:
            tab2Page1NoFileMsg = QLabel(self.tr("No AppImage installation has been found"))
            tab2Page1NoFileMsg.setObjectName("message")
            self.tab2Page1ContainerLayout.addWidget(tab2Page1NoFileMsg)

# Set the size of the QScrollArea to the size of the QRadioButtons in the QScrollArea to fix Qt's stupid default behaviour
        self.tab2Page1ContainerScrollArea.setFixedHeight(min(numOfApps, 6) * 70)

    def tab2Page1Worker(self, name):
        self.tab2StackedWidget.setCurrentIndex(1)
        for app in self.appsMetadata:
            if app.name == name:
                self.selectedAppPath = app.path
                self.desktopFilePath = app.desktopPath
                self.selectedAppName = app.name

    def appConfigWindow(self, appsConfigs, name):
        for app in appsConfigs:
            if app.name == name:

                configWindow = QDialog()
                configWindow.setWindowTitle(self.tr("Configure {appName}").format(appName=name))

                configWindowLayout = QVBoxLayout(configWindow)

                appNameLabel = QLabel(name)
                appNameLabel.setObjectName("title")

                appDescriptionLabel = QLabel(app.description)

                filePathLabel = QLabel(app.filePath)

                fileSizeLabel = QLabel(str(app.fileSize))

                configWindowLayout.addWidget(appNameLabel)
                configWindowLayout.addWidget(appDescriptionLabel)
                configWindowLayout.addWidget(filePathLabel)
                configWindowLayout.addWidget(fileSizeLabel)

                configWindow.exec()

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
        self.tab2Page2SubmitBtn.clicked.connect(self.uninstallProgram)

        self.tab2Page2BackBtn = QPushButton(self.tr("Back"))
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

        symLinkFilePath = Uninstaller.getSymlinkPath(self.selectedAppPath, self.symLinkDir)

        self.tab2TerminalUpdateMsg.setText(self.tr("Uninstallation in process..."))
        self.tab2TerminalUpdateMsg.show()


        Uninstaller.rmvInstalledFiles(symLinkFilePath)
        self.logger.addGeneralEntry(f"Permanently removed {symLinkFilePath}")
        self.terminalUpdate(self.tr("Removed symlink"))

        Uninstaller.rmvInstalledFiles(self.desktopFilePath)
        self.logger.addGeneralEntry(f"Permanently removed {self.desktopFilePath}")
        self.terminalUpdate(self.tr("Removed startmenu entry"))

        Uninstaller.rmvInstalledFiles(self.selectedAppPath)
        self.logger.addGeneralEntry(f"Permanently removed {self.selectedAppPath}")
        self.terminalUpdate(self.tr("Removed AppImage file"))

        self.terminalUpdate(self.tr("Uninstallation finished"))

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
        self.tab2Page3Title.setText(self.tr("Finished uninstalling {name}").format(name=self.selectedAppName))
        self.tab2StackedWidget.setCurrentIndex(2)

        self.tab2TerminalUpdateMsg.setText("")
        self.tab2Page2SubmitBtn.setEnabled(True)
        self.tab2Page2BackBtn.setEnabled(True)
    

    def createTab2Page3(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        self.tab2Page3Title = QLabel(self.tr("Uninstallation finished"))
        self.tab2Page3Title.setObjectName("title")

# Reload all pages if the user wants to install another program
        submitBtn = QPushButton(self.tr("Remove another AppImage program"))
        submitBtn.clicked.connect(self.populateProgramSelection)     
        submitBtn.clicked.connect(lambda: self.tab2StackedWidget.setCurrentIndex(0))

        mainLayout.addWidget(self.tab2Page3Title)
        mainLayout.addWidget(submitBtn)
        mainLayout.addStretch()
        
        return mainWidget



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