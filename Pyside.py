from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGroupBox, QRadioButton
from PySide6.QtCore import Qt
import sys

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
    
        self.setWindowTitle("AppImage-Installer")

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        container = QGroupBox()
        layout = QVBoxLayout(container)

        title = QLabel("one")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(title)
        layout.addWidget(QLabel("TEST"))

        main_layout.addWidget(container)


if __name__ == "__main__":
    app = QApplication()

    window = MainWindow()
    window.show()

    with open("/home/silas/Programmieren/AppImage-Installer/style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    sys.exit(app.exec())