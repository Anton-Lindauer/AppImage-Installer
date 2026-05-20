# Execute this file to launch the GUI version

import sys
import os
from pathlib import Path

# KDE integration is necessary, because KDE also uses Qt and can mess with QSS stylesheets
desktopEnv = os.environ.get("XDG_CURRENT_DESKTOP")
if desktopEnv == "KDE":
    print("KDE Plasma integration will be used")
    os.environ["QT_PLUGIN_PATH"] = "/usr/lib/qt6/plugins"

# Accept a file path from the right click menu in the file manager
selectedAppImage = None

if len(sys.argv) > 1:
    selectedAppImage = Path(sys.argv[1]).resolve()

from PySide6.QtCore import QTranslator, QSettings, QLocale
from PySide6.QtWidgets import QApplication, QStyleFactory
from src.gui.mainWindow import MainWindow

def loadTranslator(app):
    settings = QSettings("Anton-Lindauer", "AppImage-Installer")
    
    language = settings.value("language", QLocale.system().name()[:2], type=str)

# English is the default language and doesn't have a separate .qm file
    if language == "en":
        return None

    translator = QTranslator(app)
    translations_path = Path(__file__).parent / "translations" / f"{language}.qm"

    if translator.load(str(translations_path)):
        app.installTranslator(translator)
        print(f"Loaded language: {language}")
        return translator
    else:
        print(f"Couldn't load: {language}, Fallback to English")
        return None

def main():
    app = QApplication(sys.argv)
    
    if desktopEnv == "KDE":
        print(f"Available system themes: {QStyleFactory.keys()}")
        app.setStyle("Breeze")

# Temporarily disabled, because the translations aren't complete
#    loadTranslator(app)
        
    window = MainWindow(selectedAppImage)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()