# Execute this file to launch the GUI version
import faulthandler
faulthandler.enable()

import sys
import os
from pathlib import Path

# KDE integration is necessary, because KDE also uses Qt and can mess with QSS stylesheets
# Has to be initialized before ANYTHING else
# In the snap this isn't wanted, the snap provides thoose styles with the kde-neon-6 extension
desktopEnv = os.environ.get("XDG_CURRENT_DESKTOP")

if desktopEnv == "KDE" and "SNAP" not in os.environ:

# KDE integration for Arch based distros
    if Path("/usr/lib/qt6/plugins").exists():
        os.environ["QT_PLUGIN_PATH"] = "/usr/lib/qt6/plugins"

# KDE integratioon for Debian based distros
    if Path("/usr/lib/x86_64-linux-gnu/qt6/plugins").exists():
        os.environ["QT_PLUGIN_PATH"] = "/usr/lib/x86_64-linux-gnu/qt6/plugins"

# Accept a file path from the right click menu in the file manager
selectedAppImage = None

if len(sys.argv) > 1:
    selectedAppImage = Path(sys.argv[1]).resolve()

from PySide6.QtCore import QTranslator, QSettings, QLocale
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QStyleFactory
from src.gui.main_window import MainWindow

def getSysLanguage() -> str:
# There are two ways to figure out the system language
# Firstly by reading out environment variables, which is also the most reliable way
    for envVar in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(envVar)

        if value and value not in ("C", "POSIX"):
            shortValue = value.split(".")[0].split(":")[0]

            if shortValue:
                print("V1")
                return shortValue[:2].lower()

# Secondly via QLocal 
    sysLanguage = QLocale.system().name()

    if sysLanguage and sysLanguage not in ("C", "POSIX"):
        print("V2")
        return sysLanguage[:2].lower()

# The fallback if reading out the system language failed
    return "en"


def loadTranslator(app):
    settings = QSettings("Anton-Lindauer", "AppImage-Installer")

    sysLanguage = getSysLanguage()

    if not settings.contains("language"):
        settings.setValue("language", sysLanguage)

    language = settings.value("language", sysLanguage, type=str)

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
            snapDir / "meta/gui/appimage-installer_icon.svg",
            snapDir / "snap/gui/appimage-installer_icon.svg",
            snapDir / "assets/appimage-installer_icon.svg",
        ]
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
            
# Find the icon path if the app is run unpackaged with python from source
    projectDir = Path(__file__).resolve().parent
    localCandidates = [
        projectDir / "snap/gui/appimage-installer_icon.svg",
        projectDir / "assets/appimage-installer_icon.svg",
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
        print(appIconPath)

    print(f"Keys: {QStyleFactory.keys()}")
    
# Loading "Breeze" loads the KDE Plasma theme, even if it has a different name in the KDE settings theme selection
# Only load it if "Breeze" is available AND KDE is the desktop environment,
# because "Breeze" can show up as "available" on none KDE systems and break parts of the UI
    availableStyles = QStyleFactory.keys()
    if "Breeze" in availableStyles and desktopEnv == "KDE":
        app.setStyle("Breeze")
        print("Set Breeze")

    loadTranslator(app)
        
    window = MainWindow(selectedAppImage)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()