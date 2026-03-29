# Execute this file to launch the GUI version

import sys
from PySide6.QtWidgets import QApplication
from src.gui.mainWindow import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()