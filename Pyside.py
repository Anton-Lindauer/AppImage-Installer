from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGroupBox, QRadioButton, QPushButton, QFrame, QStackedWidget, QLineEdit, QButtonGroup
from PySide6.QtCore import Qt
import sys
from main import showFiles
import os

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
    
        self.setWindowTitle("AppImage-Installer")   # Window name in the top bar

        central = QWidget()     # Widget for all the elements
        self.setCentralWidget(central)

        mainLayout = QVBoxLayout(central)   # Layout of the entiry window

        self.stackedWidget = QStackedWidget()

        self.page1 = self.createPage1()
        self.stackedWidget.addWidget(self.page1)

        self.page2 = self.createPage2()
        self.stackedWidget.addWidget(self.page2)

        self.page3 = self.createPage3()
        self.stackedWidget.addWidget(self.page3)

        mainLayout.addWidget(self.stackedWidget)

    def createPage1(self):

        widget = QWidget()
        page1Layout = QVBoxLayout(widget)

        title = QLabel("Select a file to install")   # Title of the current thing the user does
        title.setObjectName("title")
        title.setAlignment(Qt.AlignLeft)

        self.page1GropBox = QGroupBox()    # Box for the options for the user
        layout = QVBoxLayout(self.page1GropBox)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.page1GropBox.setLayout(layout)

        fileList = showFiles()
        fileListLen = len(fileList)

        self.groupPage1 = QButtonGroup(self)

        for file in fileList:   # Create a radiobutton for each file
            itemPos = fileList.index(file)
            radioBtn = QRadioButton(file)
            layout.addWidget(radioBtn)
            self.groupPage1.addButton(radioBtn)
            
            if not itemPos == fileListLen - 1:     # Only create a divider if the element isn't the last one
                spacer = QWidget()
                spacer.setFixedHeight(2)
                layout.addWidget(spacer)

                line = QFrame()     # Dividers between the elements in the groupbox
                line.setFixedHeight(1)
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Sunken)
                line.setObjectName("line")
                layout.addWidget(line)

        submitBtn = QPushButton("Continue")  # Button to continue with the selected options
        submitBtn.setObjectName("submitBtn")
        submitBtn.clicked.connect(self.findSeletedRadioBtn)

# Adding every main element to the main window
        page1Layout.addWidget(title)
        page1Layout.addWidget(self.page1GropBox)
        page1Layout.addWidget(submitBtn)

        page1Layout.addStretch()    # Increases the window size without increasing the elemet sizes

        return widget
    
    def findSeletedRadioBtn(self):  # Function to find out which file was selected by the user and the user can only continue with a file selected
            selected = self.groupPage1.checkedButton()
            if selected is not None:
                print(selected.text())  # Only for testing porpuses
                self.stackedWidget.setCurrentIndex(1)   # Continue with the next window
        
    def createPage2(self):  # Window two
        widget = QWidget()
        page2Layout = QVBoxLayout(widget)

        title = QLabel("Enter the program information")   # Title of the current thing the user does
        title.setObjectName("title")
        title.setAlignment(Qt.AlignLeft)

        submitBtn = QPushButton("Continue")  # Button to continue with the selected options
        submitBtn.setObjectName("submitBtn")
#        submitBtn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        submitBtn.clicked.connect(self.clearPages)

        backBtn = QPushButton("Back")  # Button to go back to the previously selected options
        backBtn.setObjectName("backBtn")
        backBtn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        container = QGroupBox()    # Box for the options for the user
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        container.setLayout(layout)

        line = QFrame()     # Dividers between the elements in the groupbox
        line.setFixedHeight(1)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("line")

        programInfo = ["Enter a command to execute the file from the terminal: ",   # All the things the user has to enter
                       "Enter the name of the program in the startmenu: ",
                       "Enter a description for the program: ",
                       "Enter the categories the program belongs to: "]
        
        for info in programInfo:    # Create all the element in the groupbox
            entry = QLabel(info)    # What the user is expected to enter 
            usrInput = QLineEdit()      # The input from the user (only for testing porpuses for now)
            layout.addWidget(entry)
            layout.addWidget(usrInput)
            entry.setObjectName("entry")
            if programInfo.index(info) < 3:     # Only create a divider if the element isn't the last one
                spacer = QWidget()  # For some reason you need this or the bottom divider is 2px thick, idk why
                spacer.setFixedHeight(2)
                layout.addWidget(spacer)
                line = QFrame()     # Dividers between the elements in the groupbox
                line.setFixedHeight(1)
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Sunken)
                line.setObjectName("line")
                layout.addWidget(line)

# Adding every main element to the main window
        page2Layout.addWidget(title)
        page2Layout.addWidget(container)
        page2Layout.addWidget(submitBtn)
        page2Layout.addWidget(backBtn)

        page2Layout.addStretch()    # Increases the window size without increasing the elemet sizes

        return widget
    
    def clearPages(self):   # Unselect the selected radiobutton
            self.groupPage1.setExclusive(False)     # Disable the one radiobutton has to be selected rule
            for button in self.groupPage1.buttons():
                button.setChecked(False)    # Set every radiobutton to not selected
            self.groupPage1.setExclusive(True)      # Enable the one radiobutton has to be selected rule 
            self.stackedWidget.setCurrentIndex(2)   # Switch to window 3
    
    def createPage3(self):
        widget = QWidget()
        page3Layout = QVBoxLayout(widget)

        title = QLabel("Finished installing the program")   # Tells the user that the installation was successfull
        title.setObjectName("title")

        submitBtn = QPushButton("Install another program")  # Button to install another program
        submitBtn.setObjectName("submitBtn")
        submitBtn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

# Adding every main element to the main window
        page3Layout.addWidget(title)
        page3Layout.addWidget(submitBtn)

        page3Layout.addStretch()
        return widget

if __name__ == "__main__":
    app = QApplication()

    window = MainWindow()
    window.show()

    programDir = os.path.dirname(os.path.abspath(__file__))     # Find the path for the stylesheet
    stylesheetPath = os.path.join(programDir, "style.qss")

    with open(stylesheetPath, "r") as f:  # Open a qss style sheet, for now only works on my machine
        _style = f.read()
        app.setStyleSheet(_style)

    sys.exit(app.exec())