import faulthandler
faulthandler.enable()

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGroupBox, QRadioButton, QPushButton, QStackedWidget, QLineEdit, QButtonGroup, QScrollArea, QTabWidget, QCheckBox, QHBoxLayout, QGridLayout, QDialog, QSizePolicy
from PySide6.QtCore import Qt, QSettings, QLocale
from PySide6.QtGui import QPixmap, QIcon

import sys
import subprocess
import os
from pathlib import Path

from src.core.logic import Logging
from src.gui.components import MenuBarUtils, InstallFileSelector, UpdateFileSelector
from src.gui.threads import MetadataThread, InstallThread, AppConfigsThread, UninstallThread, AppImageListThread, UpdateAppConfigThread

class MainWindow(QMainWindow):

    def __init__(self, selectedAppImage=None):
        super().__init__()

        self.selectedAppImage = selectedAppImage
    
        self.userDir = Path.home()
        self.appImagesDir = self.userDir / "AppImages"
        self.symLinkDir = self.userDir / ".local" / "bin"
        self.desktopEntriesDir = self.userDir / ".local" / "share" / "applications"

        self.menuBarUtils = MenuBarUtils()
        self.settings = QSettings("Anton-Lindauer", "AppImage-Installer")

        self.logger = Logging()

        self.tab1Page1FileSelector = InstallFileSelector()

        self.tab1Page1FileSelector.pickedFile.connect(self.tab1Page2Worker)

        self.configWindowFileSelector = UpdateFileSelector()

        self.configWindowFileSelector.newFile.connect(self.updateConfigWindowPath)

        self.desktopEnv = os.environ.get("XDG_CURRENT_DESKTOP")
        
        self.isKde = self.desktopEnv == "KDE"

# Used to display if the KDE integration is available
        kdeSupport = self.tr("Recommended") if self.isKde else self.tr("Not Supported")
        
        if not self.isKde:
            self.menuBarUtils.loadTheme(self.settings.value("theme", "sysTheme", str))
        else:
            self.menuBarUtils.loadTheme(self.settings.value("theme", "kdeTheme", str))
        
        self.setWindowTitle("AppImage-Installer")
        self.setMinimumSize(750, 710)

# QWidget for everything
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        mainLayout = QVBoxLayout(centralWidget)
        mainLayout.setContentsMargins(6, 6, 6, 6)
        mainLayout.setSpacing(0)

# Tab one
        self.tabWidget = QTabWidget()

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

        if self.selectedAppImage is not None:
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

        self.tabWidget.addTab(self.tab1, self.tr("Install"))
        self.tabWidget.addTab(self.tab2, self.tr("Manage"))

        mainLayout.addWidget(self.tabWidget)



# All of the remaining code in this function is for the QMenuBar
        mainMenuBar = self.menuBar()

        fileMenu = mainMenuBar.addMenu(self.tr("File"))
        settingsMenu = mainMenuBar.addMenu(self.tr("Settings"))
        helpMenu = mainMenuBar.addMenu(self.tr("Help"))

        pickFileAction = fileMenu.addAction(self.tr("Pick a file to install"))
        fileMenu.addSeparator()
        refreshListAction = fileMenu.addAction(self.tr("Refresh list"))

        pickFileAction.triggered.connect(self.tab1Page1Guard)
        refreshListAction.triggered.connect(lambda: self.filesWorker() if self.tab1StackedWidget.currentIndex() == 0 and self.tabWidget.currentIndex() == 0 else None)
        refreshListAction.triggered.connect(lambda: self.tab1StackedWidget.setCurrentIndex(0) if self.tabWidget.currentIndex() == 0 else None)
        refreshListAction.triggered.connect(lambda: self.tab2Page1Worker() if self.tab2StackedWidget.currentIndex() == 0 and self.tabWidget.currentIndex() == 1 else None)
        refreshListAction.triggered.connect(lambda: self.tab2StackedWidget.setCurrentIndex(0) if self.tabWidget.currentIndex() == 1 else None)

        
        themeMenu = settingsMenu.addMenu(self.tr("Theme"))
        settingsMenu.addSeparator()
        configureAction = settingsMenu.addAction(self.tr("Configure"))

# Qt doesn't immediately close a menu inside a menu when hovering over a different element.
# Therefore you have to force Qt to do it
        configureAction.hovered.connect(lambda: themeMenu.hide())

        configureAction.triggered.connect(self.menuBarUtils.openSettingsWindow)

        systemThemeAction = themeMenu.addAction(self.tr("System theme"))
        themeMenu.addSeparator()
        blueDarkThemeAction = themeMenu.addAction(self.tr("Modern Blue Dark"))
        themeMenu.addSeparator()
        darkThemeAction = themeMenu.addAction(self.tr("Modern Dark"))
        themeMenu.addSeparator()
        lightThemeAction = themeMenu.addAction(self.tr("Modern Light"))
        themeMenu.addSeparator()
        kdeThemeAction = themeMenu.addAction(self.tr("Use KDE theme ({Support})").format(Support=kdeSupport))

# Reloading tab 1 page 2 because it uses a different layout for QSS and KDE themes
        systemThemeAction.triggered.connect(lambda: self.menuBarUtils.loadTheme("sysTheme"))
        systemThemeAction.triggered.connect(lambda: self.reloadTab1() if self.isKde else None)
        blueDarkThemeAction.triggered.connect(lambda: self.menuBarUtils.loadTheme("modernBlueDarkTheme"))
        blueDarkThemeAction.triggered.connect(lambda: self.reloadTab1() if self.isKde else None)
        darkThemeAction.triggered.connect(lambda: self.menuBarUtils.loadTheme("modernDarkTheme"))
        darkThemeAction.triggered.connect(lambda: self.reloadTab1() if self.isKde else None)
        lightThemeAction.triggered.connect(lambda: self.menuBarUtils.loadTheme("modernLightTheme"))
        lightThemeAction.triggered.connect(lambda: self.reloadTab1() if self.isKde else None)
        kdeThemeAction.triggered.connect(lambda: self.menuBarUtils.loadTheme("kdeTheme"))
        kdeThemeAction.triggered.connect(lambda: self.reloadTab1() if self.isKde else None)

        githubRepoAction = helpMenu.addAction("Github Repo")
        githubRepoAction.triggered.connect(self.menuBarUtils.openRepo)

# Hides the box around the box with the menues; Has to be declared for every menu
        for menu in (fileMenu, settingsMenu, themeMenu, helpMenu):
            menu.setWindowFlags(
                menu.windowFlags()
                | Qt.FramelessWindowHint
                | Qt.NoDropShadowWindowHint
                | Qt.Popup
            )
            menu.setAttribute(Qt.WA_TranslucentBackground)


            
############################################### Tab 1 - Page 1 ###############################################
# All of the following functions belong to the install tab / tab one
# This is the static part of the page, it's only generated once, when the app launches
    def createTab1Page1(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        pageTitle = QLabel(self.tr("AppImage selection"))
        pageTitle.setObjectName("title")

# Let the user pick an AppImage from anywhere
        openFileDialogBtn = QPushButton(self.tr("Pick a file to install"))
        openFileDialogBtn.clicked.connect(lambda: self.tab1Page1FileSelector.openFileDialog(self))

# QScrollArea with a container for all the QRadioButtons with adjustable size to fit up to five QRadioButtons and then enable scrolling
        self.tab1Page1ContainerScrollArea = QScrollArea()
        self.tab1Page1ContainerScrollArea.setWidgetResizable(True)
        self.tab1Page1ContainerScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

# Container in the QScrollArea
        radioBtnContainer = QWidget()
        self.tab1Page1ContainerScrollArea.setWidget(radioBtnContainer)

        self.tab1Page1ContainerLayout = QVBoxLayout(radioBtnContainer)   
        self.tab1Page1ContainerLayout.setContentsMargins(0, 0, 0, 0,)
        self.tab1Page1ContainerLayout.setSpacing(0)

# The radiobutton selection has to be a seperate funktion to be able to update it, without updating the entire UI
        self.filesWorker()

        self.tab1Page1ContinueBtn = QPushButton(self.tr("Continue"))  
        self.tab1Page1ContinueBtn.clicked.connect(lambda: self.tab1Page1FileSelector.emitSelectedRadioBtn(self.tab1Page1RadioBtnGroup))

        mainLayout.addWidget(pageTitle)
        mainLayout.addWidget(openFileDialogBtn)
        mainLayout.addWidget(self.tab1Page1ContainerScrollArea)
        mainLayout.addWidget(self.tab1Page1ContinueBtn)
        mainLayout.addStretch()

        return mainWidget

# This is the dynamic part. By calling this function, the QRadioButtons in the QScrollArea get updated 
    def populateFileSelection(self, appImagesPaths):
        self.clearLayout(self.tab1Page1ContainerLayout)

        if hasattr(self, "tab1Page1RadioBtnGroup"):
            self.tab1Page1RadioBtnGroup.deleteLater()
        self.tab1Page1RadioBtnGroup = QButtonGroup(self)

# All paths of AppImage files in the Downloads directory
        self.appImageFilePaths = appImagesPaths 
        appImageFileCount = len(self.appImageFilePaths)

# Create a QRadioButton for each file
        if appImageFileCount > 0:
             for filePath in self.appImageFilePaths:
                radioBtn = QRadioButton(filePath)
                self.tab1Page1ContainerLayout.addWidget(radioBtn)
                self.tab1Page1RadioBtnGroup.addButton(radioBtn)

        else:
            noFilesFoundLabel = QLabel(self.tr("No .AppImage file has been found in your Downloads directory"))
            noFilesFoundLabel.setObjectName("message")
            self.tab1Page1ContainerLayout.addWidget(noFilesFoundLabel)

# Set the size of the QScrollArea to the size of the QRadioButtons in the QScrollArea to fix Qt's stupid default behaviour
        self.tab1Page1ContainerScrollArea.setFixedHeight(min(max(appImageFileCount, 1), 6) * 39)

# Disable the scrollbar handle when there aren't enough QRadioButtons to scroll
        if appImageFileCount <= 6:
            self.tab1Page1ContainerScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

# Only accept a file from the menubar selector if the user is on the first page
    def tab1Page1Guard(self):
        if self.tab1StackedWidget.currentIndex() == 0:
            self.tab1Page1FileSelector.openFileDialog(self)

    def filesWorker(self):
        self.filesThread = AppImageListThread(self.logger, self.userDir)

        self.filesThread.finished.connect(self.populateFileSelection)
        self.filesThread.error.connect(self.workerError)

        self.filesThread.start()



############################################### Tab 1 - Page 2 ###############################################
# This is the static part of the page, it's only generated once, when the app launches
    def createTab1Page2(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        pageTitle = QLabel(self.tr("Program information"))
        pageTitle.setObjectName("title")

# Box for the options for the user; Contains other boxes with the descriptions and QlineEdits
        programInfoGroupBox = QGroupBox()
        
# Set the layout in the container
# Has to be dynamic, because the layout is different for QSS and KDE themes
        self.tab1Page2ContainerLayout = QVBoxLayout(programInfoGroupBox)

        self.configureTab1Page2Layout()

# All the things the user has to enter
        self.programInfoLabels = [self.tr("Terminal Command"),
                                  self.tr("Display Name"),
                                  self.tr("Short Description"),
                                  self.tr("Categories")]
        
# More information on what to enter for the user
        fieldHelpTexts = [self.tr("The command used to launch the application from the terminal."),
                          self.tr("The name that will appear in the start menu and application list."),
                          self.tr("A brief summary of the application."),
                          self.tr("Determines the placement in the start menu.")]
        
# All main categories from freedesktop.org
        self.categoryList = ["AudioVideo", "Audio", "Video", 
                             "Development", "Education", "HealthFitness", 
                             "Game", "Graphics", "Network",
                             "Office", "Science", "Settings", 
                             "System", "Utility"]
        
        self.programInfoInputs = []
        
# Create all the element in the groupbox
        for index, fieldLabelText in enumerate(self.programInfoLabels):  
# Boxes with the descriptions and the QLineEdits
            fieldTile = QWidget()
            fieldTile.setObjectName("page2InnerBox")

            fieldTileLayout = QVBoxLayout(fieldTile)
            fieldTileLayout.setContentsMargins(0, 0, 0, 0)
            fieldTileLayout.setSpacing(6)

# Special properties for the first and last boxes; Used in QSS for rounded corners
            if index == 0:
                fieldTile.setProperty("isFirst", "true")
            elif index == 3:
                fieldTile.setProperty("isLast", "true")
            
# What the user is expected to enter 
            fieldNameLabel = QLabel(fieldLabelText)
            fieldNameLabel.setObjectName("entry")

# More detailed description for the user
            fieldHelpLabel = QLabel(fieldHelpTexts[index])
            fieldHelpLabel.setObjectName("infoDescription")
            fieldHelpLabel.setWordWrap(True)

            fieldTileLayout.addWidget(fieldNameLabel)
            fieldTileLayout.addWidget(fieldHelpLabel)

# Add QRadioButtons only to the last box, QLineEdits for all other boxes
            if index == len(self.programInfoLabels) - 1:
                categoryGrid = QWidget()
                categoryGridLayout = QGridLayout(categoryGrid)
                categoryGridLayout.setContentsMargins(0, 0, 0, 6)
                categoryGridLayout.setSpacing(6)

                self.tab1Page2CategoryRadioBtns = QButtonGroup()
                self.tab1Page2CategoryRadioBtns.setExclusive(False)

# Create a QRadioButton for all 14 categories
                for i, categoryName in enumerate(self.categoryList):
                    radioBtn = QRadioButton(categoryName)
                    radioBtn.setObjectName("categorySel")
                    radioBtn.setAutoExclusive(False)
                    self.tab1Page2CategoryRadioBtns.addButton(radioBtn)

                    row = i // 3
                    column = i % 3

                    categoryGridLayout.addWidget(radioBtn, row, column)

                fieldTileLayout.addWidget(categoryGrid)

# Add QLineEdit input fields for box one to three
            else:
                inputField = QLineEdit()
                self.programInfoInputs.append(inputField)
                fieldTileLayout.addWidget(inputField)
                

            self.tab1Page2ContainerLayout.addWidget(fieldTile)

        self.tab1Page2ContinueBtn = QPushButton(self.tr("Continue"))
        self.tab1Page2ContinueBtn.clicked.connect(self.page2Validator)

        self.tab1Page2BackBtn = QPushButton(self.tr("Back"))
        self.tab1Page2BackBtn.clicked.connect(lambda: self.tab1StackedWidget.setCurrentIndex(0))
        self.tab1Page2BackBtn.clicked.connect(lambda: self.tab1Page1ContinueBtn.setEnabled(True))

        mainLayout.addWidget(pageTitle)
        mainLayout.addWidget(programInfoGroupBox)
        mainLayout.addWidget(self.tab1Page2ContinueBtn)
        mainLayout.addWidget(self.tab1Page2BackBtn)
        mainLayout.addStretch()  

        return mainWidget

# Only continue when all QLineEdits contain text and one or more QRadioButton is selected
    def page2Validator(self):
        if all(edit.text().strip() for edit in self.programInfoInputs) and self.tab1Page2CategoryRadioBtns.checkedButton() is not None:
            self.tab1StackedWidget.setCurrentIndex(2)

# Custom layouts for KDE and QSS themes
    def configureTab1Page2Layout(self):
        if self.isKde and self.settings.value("theme", "sysTheme", str) == "kdeTheme":
            self.tab1Page2ContainerLayout.setContentsMargins(10, 10, 10, 10)
            self.tab1Page2ContainerLayout.setSpacing(6)
        else:
            self.tab1Page2ContainerLayout.setContentsMargins(0, 0, 0, 0)
            self.tab1Page2ContainerLayout.setSpacing(0)

# The worker that extracts the AppImages metadata
    def tab1Page2Worker(self, appImagePath):
        self.selectedAppImagePath = appImagePath

        self.tab1Page1ContinueBtn.setEnabled(False)

        self.metadataThread = MetadataThread(self.logger, self.selectedAppImagePath)

        self.metadataThread.finished.connect(self.metadataLoader)
        self.metadataThread.error.connect(self.workerError)

        self.metadataThread.start()

# Loads the AppImages metadata in the QLineEdits and QRadiobuttons on page two
    def metadataLoader(self, metadata):
        self.tab1StackedWidget.setCurrentIndex(1)

        self.programInfoInputs[0].setText(metadata["exec"].lower())
        self.programInfoInputs[1].setText(metadata["name"])
        self.programInfoInputs[2].setText(metadata["comment"])
        
# Activate the QRadioButtons when they are in the AppImages category string
        categories = metadata["categories"].split(";")

        for button in self.tab1Page2CategoryRadioBtns.buttons():
            button.setChecked(button.text() in categories)



############################################### Tab 1 - Page 3 ###############################################
# This is the static part of the page, it's only generated once, when the app launches
    def createTab1Page3(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        pageTitle = QLabel(self.tr("Installation process"))
        pageTitle.setObjectName("title")

# QGroupBox thats used as a terminal for the status updates, that the user receives
        terminalGroupBox = QGroupBox()    
        terminalLayout = QVBoxLayout(terminalGroupBox)
        terminalLayout.setContentsMargins(6, 6, 6, 6)
        terminalLayout.setSpacing(0)

        terminalGroupBox.setMinimumHeight(200)
        terminalGroupBox.setObjectName("page3Container")

# Updates that are displayed in the GUIs terminal like UI element
        self.tab1Page3TerminalUpdateMsg = QLabel()     
        self.tab1Page3TerminalUpdateMsg.setObjectName("terminalText")

        terminalLayout.addWidget(self.tab1Page3TerminalUpdateMsg)
        terminalLayout.addStretch()

        self.tab1Page3StartInstallBtn = QPushButton(self.tr("Start installation"))
        self.tab1Page3StartInstallBtn.clicked.connect(self.installWorker)

        self.tab1Page3BackBtn = QPushButton(self.tr("Back"))
        self.tab1Page3BackBtn.clicked.connect(lambda: self.tab1StackedWidget.setCurrentIndex(1))

        mainLayout.addWidget(pageTitle)
        mainLayout.addWidget(terminalGroupBox)
        mainLayout.addWidget(self.tab1Page3StartInstallBtn)
        mainLayout.addWidget(self.tab1Page3BackBtn)
        mainLayout.addStretch()

        return mainWidget
    
    def installWorker(self):
# Disable the buttons on page 3 
        self.tab1Page3StartInstallBtn.setEnabled(False)
        self.tab1Page3BackBtn.setEnabled(False)

        self.tab1Page3TerminalUpdateMsg.setText(self.tr("Installation in process..."))
        self.tab1Page3TerminalUpdateMsg.show()

# Get program data from the QLineEdits
        self.cmdName = self.programInfoInputs[0].text()
        self.programName = self.programInfoInputs[1].text()
        self.programDescription = self.programInfoInputs[2].text()

# Get all selected categories
        self.programCategory = ""
        categoryRadioBtns = self.tab1Page2CategoryRadioBtns.buttons()

        selectedCategories = [rb.text() for rb in categoryRadioBtns if rb.isChecked()]

        if selectedCategories:
            self.programCategory = ";".join(selectedCategories)

# Temporary way of deleting old logs
        if self.settings.value("autoDelete", True, type=bool):
            self.logger.rmvOldLogs()

# Function that installs the program
        self.installThread = InstallThread(self.logger, self.selectedAppImagePath, self.appImagesDir, self.userDir, self.programName,self.programDescription, self.programCategory, self.cmdName, self.symLinkDir)

# Process status updates from the installation function
        self.installThread.progressUpdate.connect(self.installWorkerProgress)
        self.installThread.finished.connect(self.installWorkerFinished)
        self.installThread.error.connect(self.workerError)

        self.installThread.start()

    def installWorkerProgress(self, message):
        currentProgress = self.tab1Page3TerminalUpdateMsg.text()

# Update the terminal if a new progress update arrived
        if currentProgress: 
            newProgress = currentProgress + "\n" + message
        else:
            newProgress = message

        self.tab1Page3TerminalUpdateMsg.setText(newProgress)

        QApplication.processEvents()

    def installWorkerFinished(self):
        self.tab1Page4PageTitle.setText(self.tr("Finished installing {name}").format(name=self.programInfoInputs[1].text()))

        try:
            self.tab1Page4OpenProgramBtn.clicked.disconnect()
        except TypeError:
            pass

        self.tab1Page4OpenProgramBtn.setText(self.tr("Open {name}").format(name=self.programInfoInputs[1].text()))
        self.tab1Page4OpenProgramBtn.clicked.connect(lambda: self.openProgram(self.cmdName))

        self.tab1StackedWidget.setCurrentIndex(3)

        self.tab1Page3TerminalUpdateMsg.setText("")

        self.tab1Page3StartInstallBtn.setEnabled(True)
        self.tab1Page3BackBtn.setEnabled(True)

        print("before")

        self.tab2Page1Worker()

        print("after")


    def createTab1Page4(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        self.tab1Page4PageTitle = QLabel(self.tr("Finished installing"))
        self.tab1Page4PageTitle.setObjectName("title")

        installAnotherBtn = QPushButton(self.tr("Install another program"))
# Reload the filelist, if the user wants to install more AppImages
        installAnotherBtn.clicked.connect(self.filesWorker)
        installAnotherBtn.clicked.connect(lambda: self.tab1Page1ContinueBtn.setEnabled(True)) 
        installAnotherBtn.clicked.connect(lambda: self.tab1StackedWidget.setCurrentIndex(0))

        self.tab1Page4OpenProgramBtn = QPushButton(self.tr("Open"))

        mainLayout.addWidget(self.tab1Page4PageTitle)
        mainLayout.addWidget(installAnotherBtn)
        mainLayout.addWidget(self.tab1Page4OpenProgramBtn)
        mainLayout.addStretch()
        
        return mainWidget
    
    def openProgram(self, command):
        subprocess.Popen(
        [command],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True)

# Only reloads parts of pages with different layouts for QSS and KDE themes
    def reloadTab1(self):
        currentIndex = self.tab1StackedWidget.currentIndex()

        self.configureTab1Page2Layout()

        self.tab1StackedWidget.setCurrentIndex(currentIndex)

        self.populateProgramSelection(self.appConfigs)



############################################### Tab 1 - Page 1 ###############################################
# All of the following functions belong to the manage tab / tab two
# This is the static part of the page, it's only generated once, when the app launches
    def createTab2Page1(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        pageTitle = QLabel(self.tr("App selection"))
        pageTitle.setObjectName("title")

# QScrollArea with a container for all the QRadioButtons with adjustable size to fit up to five QRadioButtons and then enable scrolling
        self.tab2Page1ContainerScrollArea = QScrollArea()
        self.tab2Page1ContainerScrollArea.setWidgetResizable(True)
        self.tab2Page1ContainerScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

# Container in the QScrollArea
        appTileContainer = QWidget() 
        self.tab2Page1ContainerScrollArea.setWidget(appTileContainer)

        self.tab2Page1ContainerLayout = QVBoxLayout(appTileContainer)   
        self.tab2Page1ContainerLayout.setContentsMargins(10, 10, 10, 10,)
        self.tab2Page1ContainerLayout.setSpacing(6)

        self.tab2Page1Worker()

        mainLayout.addWidget(pageTitle)
        mainLayout.addWidget(self.tab2Page1ContainerScrollArea)
        mainLayout.addStretch()

        return mainWidget
    
# The dynamicly generated part, the list of installed AppImage programs
    def populateProgramSelection(self, appConfigs):
        self.clearLayout(self.tab2Page1ContainerLayout)

        self.appConfigs = appConfigs
        print("appConfigList")
        installedAppCount = len(self.appConfigs)

# Create a tile for each file
        if installedAppCount > 0:
             for installedApp in self.appConfigs:

                appTile = QGroupBox()
                appTile.setObjectName("appTile")

                appTileLayout = QHBoxLayout(appTile)
                appTileLayout.setContentsMargins(10, 10, 10, 10)
                appTileLayout.setSpacing(6)

                iconPath = installedApp.iconFile

                appIconLabel = QLabel()
                appIconLabel.setObjectName("iconLabel")
                appIconPixmap = QPixmap(iconPath)
                appIconLabel.setPixmap(appIconPixmap.scaled(22, 22, aspectMode=Qt.AspectRatioMode.KeepAspectRatio))

                appNameLabel = QLabel(installedApp.name)
                appNameLabel.setFixedWidth(200)
                appNameLabel.setObjectName("nameLabel")

                launchAppBtn = QPushButton(self.tr("Launch"))
                if self.isKde:
                    launchAppBtn.setIcon(QIcon.fromTheme("media-playback-start"))
                launchAppBtn.setObjectName("launchAppBtn")
                launchAppBtn.clicked.connect(lambda checked=False, app=installedApp: self.openProgram(app.filePath))

                configureAppBtn = QPushButton(self.tr("Configure"))
                if self.isKde:
                    configureAppBtn.setIcon(QIcon.fromTheme("configure"))
                configureAppBtn.setObjectName("configureAppBtn")
                configureAppBtn.clicked.connect(lambda checked=False, app=installedApp: self.appConfigWindow(self.appConfigs, app.name))

                deleteAppBtn = QPushButton(self.tr("Delete"))
                if self.isKde:
                    deleteAppBtn.setIcon(QIcon.fromTheme("edit-delete"))
                deleteAppBtn.setObjectName("deleteAppBtn")
                deleteAppBtn.clicked.connect(lambda checked=False, app=installedApp: self.prepUninstallData(app.name))

                appTileLayout.addWidget(appIconLabel)
                appTileLayout.addWidget(appNameLabel)
                appTileLayout.addStretch()
                appTileLayout.addWidget(launchAppBtn)
                appTileLayout.addWidget(configureAppBtn)
                appTileLayout.addWidget(deleteAppBtn)

                self.tab2Page1ContainerLayout.addWidget(appTile)

        else:
            noAppsFoundLabel = QLabel(self.tr("No AppImage installation has been found"))
            noAppsFoundLabel.setObjectName("message")
            self.tab2Page1ContainerLayout.addWidget(noAppsFoundLabel)

# Set the size of the QScrollArea to the size of the QRadioButtons in the QScrollArea to fix Qt's stupid default behaviour
        self.tab2Page1ContainerScrollArea.setFixedHeight(min(installedAppCount, 6) * 70)

    def tab2Page1Worker(self):
# Hotfix for this QThread not beeing ended properly for some unknown reason
        if hasattr(self, "appConfigsThread") and self.appConfigsThread.isRunning():
            self.appConfigsThread.quit()
            self.appConfigsThread.wait()

        self.appConfigsThread = AppConfigsThread(self.logger, self.desktopEntriesDir)

        print("tab2Page1Worker")

        self.appConfigsThread.finished.connect(self.populateProgramSelection)
        self.appConfigsThread.error.connect(self.workerError)      

        self.appConfigsThread.start()

    def prepUninstallData(self, name):
        self.tab2StackedWidget.setCurrentIndex(1)
        for app in self.appConfigs:
            if app.name == name:
                self.selectedAppPath = app.filePath
                self.desktopFilePath = app.desktopFile
                self.selectedAppName = app.name

    def appConfigWindow(self, appsConfigs, name):
        self.appConfigDialog = QDialog()
        self.appConfigDialog.setFixedSize(650, 400)

        appConfigLayout = QVBoxLayout(self.appConfigDialog)

        configGroupBox = QGroupBox()

        configBoxLayout = QVBoxLayout(configGroupBox)
        configBoxLayout.setContentsMargins(10, 10, 10, 10)

        for appConfig in appsConfigs:
            if appConfig.name == name:
                desktopFile = appConfig.desktopFile
                categories = appConfig.startMenuCategories

                self.appConfigDialog.setWindowTitle(self.tr("Configure {appName}").format(appName=name))

                appNameLabel = QLabel(self.tr("App name"))

                self.appNameInput = QLineEdit()
                self.appNameInput.setText(name)
                self.appNameInput.setObjectName("appConfigInput")

                appDescriptionLabel = QLabel(self.tr("App description"))
                
                self.appDescriptionInput = QLineEdit()
                self.appDescriptionInput.setText(appConfig.description)
                self.appDescriptionInput.setObjectName("appConfigInput")

                launchConfigLabel = QLabel(self.tr("Custom launch configuration"))

                self.launchConfigInput = QLineEdit()
                self.launchConfigInput.setObjectName("appConfigInput")
                self.launchConfigInput.setText(" ".join(appConfig.launchFlagString))

                filePathLayout = QHBoxLayout()

                pathLabel = QLabel(self.tr("Path"))

                self.filePathLabel = QLabel(appConfig.filePath)

                filePathLayout.addWidget(pathLabel)
                filePathLayout.addStretch()
                filePathLayout.addWidget(self.filePathLabel)

                fileSizeLayout = QHBoxLayout()

                sizeLabel = QLabel(self.tr("File size"))

# Returns the AppImage file size in KiB, MiB, etc. rounded to one decimal place
                fileSize = QLocale.system().formattedDataSize(
                    appConfig.fileSize, precision=1,
                    format=QLocale.DataSizeFormat.DataSizeIecFormat
                )

                fileSizeLabel = QLabel(fileSize)

                fileSizeLayout.addWidget(sizeLabel)
                fileSizeLayout.addStretch()
                fileSizeLayout.addWidget(fileSizeLabel)

                updateFileLayout = QHBoxLayout()

                self.updateFileInput = QLineEdit()
                self.updateFileInput.setObjectName("appConfigInput")
                self.updateFileInput.setPlaceholderText(self.tr("DifferentFileVersion.AppImage"))

                updateFileBtn = QPushButton(self.tr("Install a new version of this AppImage"))
                updateFileBtn.clicked.connect(lambda: self.configWindowFileSelector.openFileDialog(self))
                updateFileBtn.setObjectName("configWindowBtn")

                updateFileLayout.addWidget(self.updateFileInput)
                updateFileLayout.addWidget(updateFileBtn)

                self.refreshIconCheckBox = QCheckBox(self.tr("Refresh icon when updating"))

                btnLayout = QHBoxLayout()

                self.saveChangesBtn = QPushButton(self.tr("Update installation"))
                self.saveChangesBtn.setObjectName("configWindowBtn")
                self.saveChangesBtn.clicked.connect(lambda: self.configWindowWorker(desktopFile, categories, appConfig.iconFile))

                self.discardChangesBtn = QPushButton(self.tr("Discard"))
                self.discardChangesBtn.setObjectName("configWindowBtn")
                self.discardChangesBtn.clicked.connect(lambda: self.appConfigDialog.close())

                configBoxLayout.addWidget(self.saveChangesBtn)
                configBoxLayout.addWidget(appNameLabel)
                configBoxLayout.addWidget(self.appNameInput)
                configBoxLayout.addWidget(appDescriptionLabel)
                configBoxLayout.addWidget(self.appDescriptionInput)
                configBoxLayout.addWidget(launchConfigLabel)
                configBoxLayout.addWidget(self.launchConfigInput)
                configBoxLayout.addLayout(filePathLayout)
                configBoxLayout.addLayout(fileSizeLayout)
                configBoxLayout.addLayout(updateFileLayout)
                configBoxLayout.addWidget(self.refreshIconCheckBox)
                
                appConfigLayout.addWidget(configGroupBox)

# Workaround to get the save button auto selected instead of the QLineEdit
                self.saveChangesBtn.setFocus()
                configBoxLayout.removeWidget(self.saveChangesBtn)
                btnLayout.addWidget(self.saveChangesBtn)
                btnLayout.addWidget(self.discardChangesBtn)
                appConfigLayout.addLayout(btnLayout)
                appConfigLayout.addStretch()

                self.appConfigDialog.exec()

    def configWindowWorker(self, desktopFile, categories, iconPath):
        self.saveChangesBtn.setEnabled(False)
        self.discardChangesBtn.setEnabled(False)

        newAppName = self.appNameInput.text()
        newAppDescription = self.appDescriptionInput.text()
        newLaunchConfig = self.launchConfigInput.text()
        newAppImageFile = self.updateFileInput.text()
        oldDesktopFile = desktopFile
        oldAppImage = self.filePathLabel.text()
        startMenuCategories = categories

        if not self.refreshIconCheckBox.isChecked():
            icon = iconPath
        else:
            icon = False

        self.updateConfigThread = UpdateAppConfigThread(self.logger, newAppName, newAppDescription, newLaunchConfig, newAppImageFile, oldDesktopFile, oldAppImage, self.symLinkDir, self.appImagesDir, self.userDir, startMenuCategories, self.desktopEntriesDir, icon)

        self.updateConfigThread.error.connect(self.workerError)
        self.updateConfigThread.finished.connect(self.finishedConfigUpdate)

        self.updateConfigThread.start()

    def finishedConfigUpdate(self):
        self.tab2Page1Worker()

        self.appConfigDialog.close()


    def updateConfigWindowPath(self, newPath):
        self.updateFileInput.setText(newPath)

# Ensures that the QDialog stays in the foreground after closing the QFileDialog
        self.appConfigDialog.raise_()
        self.appConfigDialog.activateWindow()



############################################### Tab 2 - Page 2 ###############################################
# This is the static part of the page, it's only generated once, when the app launches
    def createTab2Page2(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        pageTitle = QLabel(self.tr("Uninstallation process"))
        pageTitle.setObjectName("title")

# QGroupBox thats used as a terminal for the status updates, that the user receives
        terminalGroupBox = QGroupBox()    
        terminalLayout = QVBoxLayout(terminalGroupBox)
        terminalLayout.setContentsMargins(6, 6, 6, 6)
        terminalLayout.setSpacing(0)

        terminalGroupBox.setMinimumHeight(200)
        terminalGroupBox.setObjectName("page3Container")

# Updates that are displayed in the GUIs terminal like UI element
        self.tab2Page2TerminalUpdateMsg = QLabel()     
        self.tab2Page2TerminalUpdateMsg.setObjectName("terminalText")

        terminalLayout.addWidget(self.tab2Page2TerminalUpdateMsg)
        terminalLayout.addStretch()

        self.tab2Page2StartUninstallBtn = QPushButton(self.tr("Start uninstallation"))
        self.tab2Page2StartUninstallBtn.clicked.connect(self.tab2Page2Worker)

        self.tab2Page2BackBtn = QPushButton(self.tr("Back"))
        self.tab2Page2BackBtn.clicked.connect(lambda: self.tab2StackedWidget.setCurrentIndex(0))

        mainLayout.addWidget(pageTitle)
        mainLayout.addWidget(terminalGroupBox)
        mainLayout.addWidget(self.tab2Page2StartUninstallBtn)
        mainLayout.addWidget(self.tab2Page2BackBtn)
        mainLayout.addStretch()

        return mainWidget
    
    def tab2Page2Worker(self):
        self.tab2Page2StartUninstallBtn.setEnabled(False)
        self.tab2Page2BackBtn.setEnabled(False)

        self.tab2Page2TerminalUpdateMsg.setText(self.tr("Uninstallation in process..."))
        self.tab2Page2TerminalUpdateMsg.show()

        self.uninstallThread = UninstallThread(self.logger, self.selectedAppPath, self.symLinkDir, self.desktopFilePath)

        self.uninstallThread.progressUpdate.connect(self.uninstallWorkerProgress)
        self.uninstallThread.finished.connect(self.uninstallWorkerFinished)
        self.uninstallThread.error.connect(self.workerError)

        self.uninstallThread.start()

    def uninstallWorkerProgress(self, msg):
        currentProgress = self.tab2Page2TerminalUpdateMsg.text()

# Update the terminal if a new progress update arrived
        if currentProgress: 
            newProgress = currentProgress + "\n" + msg
        else:
            newProgress = msg

        self.tab2Page2TerminalUpdateMsg.setText(newProgress)
        self.tab2Page2TerminalUpdateMsg.show()

    def uninstallWorkerFinished(self):
        self.tab2Page3PageTitle.setText(self.tr("Finished uninstalling {name}").format(name=self.selectedAppName))
        self.tab2StackedWidget.setCurrentIndex(2)

        self.tab2Page2TerminalUpdateMsg.setText("")
        self.tab2Page2StartUninstallBtn.setEnabled(True)
        self.tab2Page2BackBtn.setEnabled(True)
    


############################################### Tab 2 - Page 3 ###############################################
# This is the static part of the page, it's only generated once, when the app launches
    def createTab2Page3(self):
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setContentsMargins(20, 10, 20, 0)
        mainLayout.setSpacing(6)

        self.tab2Page3PageTitle = QLabel(self.tr("Uninstallation finished"))
        self.tab2Page3PageTitle.setObjectName("title")

# Reload all pages if the user wants to install another program
        removeAnotherBtn = QPushButton(self.tr("Remove another AppImage program"))
        removeAnotherBtn.clicked.connect(self.tab2Page1Worker)     
        removeAnotherBtn.clicked.connect(lambda: self.tab2StackedWidget.setCurrentIndex(0))

        mainLayout.addWidget(self.tab2Page3PageTitle)
        mainLayout.addWidget(removeAnotherBtn)
        mainLayout.addStretch()
        
        return mainWidget



############################################### General methods ###############################################
# General method to delete all the content of a layout, currently used for the QScrollAreas on tab one and two page one
    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()


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