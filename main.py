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
from PySide6.QtGui import QIcon
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

def getAppIconPath() -> str | None:
# Find the icon path if the app is running as snap
    if "SNAP" in os.environ:
        snapDir = Path(os.environ["SNAP"])
        candidates = [
            snapDir / "meta/gui/AppImage-Installer_Icon.svg",
            snapDir / "snap/gui/AppImage-Installer_Icon.svg",
            snapDir / "assets/AppImage-Installer_Icon.svg",
        ]
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
            
# Find the icon path if the app is run unpackaged with python from source
    projectDir = Path(__file__).resolve().parent
    localCandidates = [
        projectDir / "snap/gui/AppImage-Installer_Icon.svg",
        projectDir / "assets/AppImage-Installer_Icon.svg",
    ]
    for candidate in localCandidates:
        if candidate.is_file():
            return str(candidate)

    return None

def main():
    app = QApplication(sys.argv)

    app.setDesktopFileName("appimage-installer")

    appIconPath = getAppIconPath()
    if appIconPath:
        app.setWindowIcon(QIcon(appIconPath))
    
# Loading "Breeze" loads the KDE Plasma theme, even if it has a different name in the KDE settings theme selection
    if desktopEnv == "KDE":
        app.setStyle("Breeze")

    loadTranslator(app)
        
    window = MainWindow(selectedAppImage)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()