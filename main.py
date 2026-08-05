# Execute this file to launch the GUI version
import faulthandler
faulthandler.enable()

import sys
import os
from pathlib import Path

# KDE integration is necessary, because KDE also uses Qt and can mess with QSS stylesheets
desktopEnv = os.environ.get("XDG_CURRENT_DESKTOP")
if desktopEnv == "KDE":
    os.environ["QT_PLUGIN_PATH"] = "/usr/lib/qt6/plugins"

# Accept a file path from the right click menu in the file manager
selectedAppImage = None

if len(sys.argv) > 1:
    selectedAppImage = Path(sys.argv[1]).resolve()

from PySide6.QtCore import QTranslator, QSettings, QLocale
from PySide6.QtWidgets import QApplication
from src.gui.mainWindow import MainWindow

def loadTranslator(app):
    settings = QSettings("Anton-Lindauer", "AppImage-Installer")

# Write the used language to the settings if there is no entry allready
    if not settings.contains("language"):
        settings.setValue("language", QLocale.system().name()[:2])
    
    language = settings.value("language", QLocale.system().name()[:2], type=str)

# English is the default language and doesn't have a separate .qm file
    if language == "en":
        return None

    translator = QTranslator(app)
    translationsPath = Path(__file__).parent / "translations" / f"{language}.qm"

    if translator.load(str(translationsPath)):
        app.installTranslator(translator)
        return translator
    else:
        print(f"Couldn't load: {language}, Fallback to English")
        return None

def main():
    app = QApplication(sys.argv)
    
# Loading "Breeze" loads the KDE Plasma theme, even if it has a different name in the KDE settings theme selection
    if desktopEnv == "KDE":
        app.setStyle("Breeze")

    loadTranslator(app)
        
    window = MainWindow(selectedAppImage)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()