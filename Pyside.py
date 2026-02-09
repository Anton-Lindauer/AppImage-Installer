from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGroupBox, QRadioButton, QPushButton, QFrame
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
                line = QFrame()     # Dividers between the elements in the groupbox
                line.setFixedHeight(1)
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Sunken)
                line.setObjectName("line")
                layout.addWidget(line)

        submitButton = QPushButton("Continue")  # Button to continue with the selected options
        submitButton.setObjectName("submitBtn")

        mainLayout.setContentsMargins(50, 50, 50, 50)

        # Add the elemts to the window
        mainLayout.addWidget(title)
        mainLayout.addWidget(container)
        mainLayout.addWidget(submitButton)

        mainLayout.addStretch()


if __name__ == "__main__":
    app = QApplication()

    window = MainWindow()
    window.show()

    with open("/home/silas/Programmieren/AppImage-Installer/style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    sys.exit(app.exec())