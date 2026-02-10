from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGroupBox, QRadioButton, QPushButton, QFrame, QStackedWidget
from PySide6.QtCore import Qt
import sys
from main import showFiles

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

        container = QGroupBox()    # Box for the options for the user
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        container.setLayout(layout)

        fileList = showFiles()
        fileListLen = fileList.__len__

        for file in fileList:
            radioBtn = QRadioButton(file)
            layout.addWidget(radioBtn)
            itemPos = fileList.index(file)
            fileListLen = len(fileList)

            if not itemPos == fileListLen - 1:
                spacer = QWidget()
                spacer.setFixedHeight(2)
                layout.addWidget(spacer)

                line = QFrame()     # Dividers between the elements in the groupbox
                line.setFixedHeight(1)
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Sunken)
                line.setObjectName("line")
                layout.addWidget(line)

        submitButton = QPushButton("Continue")  # Button to continue with the selected options
        submitButton.setObjectName("submitBtn")
        submitButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))

        page1Layout.setContentsMargins(50, 50, 50, 50)

            # Add the elemts to the window
        page1Layout.addWidget(title)
        page1Layout.addWidget(container)
        page1Layout.addWidget(submitButton)

        page1Layout.addStretch()

        return widget
        
    def createPage2(self):
        widget = QWidget()
        page2Layout = QVBoxLayout(widget)

        title = QLabel("Select a file to install")   # Title of the current thing the user does
        title.setObjectName("title")
        title.setAlignment(Qt.AlignLeft)

        submitButton = QPushButton("Continue")  # Button to continue with the selected options
        submitButton.setObjectName("submitBtn")
        submitButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))

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

        programInfo = ["Enter a command to execute the file from the terminal: ",
                       "Enter the name of the program in the startmenu: ",
                       "Enter a description for the program: ",
                       "Enter the categories the program belongs to: "]
        
        for info in programInfo:
            entry = QLabel(info)
            layout.addWidget(entry)
            entry.setObjectName("entry")
            if programInfo.index(info) < 3:
                spacer = QWidget()
                spacer.setFixedHeight(2)
                layout.addWidget(spacer)
                line = QFrame()     # Dividers between the elements in the groupbox
                line.setFixedHeight(1)
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Sunken)
                line.setObjectName("line")
                layout.addWidget(line)

        page2Layout.addWidget(title)
        page2Layout.addWidget(container)
        page2Layout.addWidget(submitButton)

        page2Layout.addStretch()

        return widget
    
    def createPage3(self):
        widget = QWidget()
        page3Layout = QVBoxLayout(widget)

        submitButton = QPushButton("Install another program")  # Button to continue with the selected options
        submitButton.setObjectName("submitBtn")
        submitButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        page3Layout.addWidget(QLabel("Finished installing the program"))
        page3Layout.addWidget(submitButton)

        page3Layout.addStretch()
        return widget

if __name__ == "__main__":
    app = QApplication()

    window = MainWindow()
    window.show()

    with open("/home/silas/Programmieren/AppImage-Installer/style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    sys.exit(app.exec())