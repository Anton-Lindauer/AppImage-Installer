# Execute this file to launch the GUI version

import sys
import os
from pathlib import Path

# KDE integration is necessary, because KDE also uses Qt and can mess with QSS stylesheets
desktopEnv = os.environ.get("XDG_CURRENT_DESKTOP")
if desktopEnv == "KDE":
    print("KDE Plasma integration will be used")
    os.environ["QT_PLUGIN_PATH"] = "/usr/lib/qt6/plugins"

selectedAppImage = None

if len(sys.argv) > 1:
    selectedAppImage = Path(sys.argv[1]).resolve()

from PySide6.QtWidgets import QApplication, QStyleFactory
from src.gui.mainWindow import MainWindow

def main():
    app = QApplication(sys.argv)
    
    if desktopEnv == "KDE":
        print(f"Available system themes: {QStyleFactory.keys()}")
        app.setStyle("Breeze")
        
    window = MainWindow(selectedAppImage)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()