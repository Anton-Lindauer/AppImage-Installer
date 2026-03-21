# AppImage-Installer

## A GUI or CLI tool to easily install AppImage files on Linux.

This project is **still in development**, but you can already do the following things: You can move the AppImage file to the right directory, make the file executable, launch it from the terminal and you can also create a desktop startmenu entry. You can choose between a GUI or a CLI to install your AppImages. The AppImages files are expected to be in your downloads directory.

## Requirements

You need Python version 3.12 or higher to use the GUI or CLI version of this tool.

Pyside6 module is required for the GUI version.

Should work on any **Linux** Distro, doesn't work on Windows.

## How to install and launch the CLI or GUI version
Download this repo to your home directory:
```
git clone https://github.com/Anton-Lindauer/AppImage-Installer.git
```

Then go in the AppImage-Installer directory:
```
cd AppImage-Installer
```

**CLI:**

If you only want the CLI version, then enter this command to launch it:
```
python3 mainCLI.py
```

**GUI:**

If you want the GUI version, follow these steps

Create a virtual environment:
```
python3 -m venv .venv
```

Activate the virtual environment (activation needs to be done each time you want to launch the GUI version):
```
source .venv/bin/activate
```

Install all requirements:
```
pip install -r requirements.txt
```

Launch the GUI version:
```
python3 Pyside.py
```

The program will guide you through the installation process. Please report any errors that may occure.

## Have a look at the GUI version

**Note:** The pictures are not 100% up to date and small visual changes are not worth the effort to update them.

### Selecting a file to install
![image alt](https://github.com/Anton-Lindauer/AppImage-Installer/blob/2bc87f13cd6052a6deaa93b7b3f674f80bc25afa/pictures%20for%20README%20file/page1.png)

### Entering program info
![image alt](https://github.com/Anton-Lindauer/AppImage-Installer/blob/2bc87f13cd6052a6deaa93b7b3f674f80bc25afa/pictures%20for%20README%20file/page2.png)
Example of installing Ultimaker Cura.

### Installation process status page
![image alt](https://github.com/Anton-Lindauer/AppImage-Installer/blob/2bc87f13cd6052a6deaa93b7b3f674f80bc25afa/pictures%20for%20README%20file/page3.png)
This may take a while, especially the creation of a startmenu entry takes a while. 

If you encounter a error message, check the terminal you used to launch the program from for more details.

### Finished installation screen
![image alt](https://github.com/Anton-Lindauer/AppImage-Installer/blob/2bc87f13cd6052a6deaa93b7b3f674f80bc25afa/pictures%20for%20README%20file/page4.png)

## Other important notes
If you suddenly find a directory called "AppDir" or another new directory in the directory of the installer scripts, you can most likely safely delete them. Sometimes such directories are created by the AppImages durin the app icon extraction process. 

main.py will from now on be used by the GUI, if you want the terminal version of this tool, you have to execute the mainCLI.py file.

A light mode is also supported, the program uses your system themen when launched.

The GUI design is inspired by linux mint with orchis dark/light compact themes, it's not a 1:1 replica, because Qt hates doing what it should do and there is no mint menu with a similar layout.

This tool is still work in progress and more functionality will be added soon.

The AppImage files are moved to ~/{username}/AppImages/.

The symlinks are created in ~/{username}/.local/bin/

The startmenu entries are created in ~/{username}/.local/applications/

If you want to contribute, make suggestions on how to make the program more performant or the code more organized - feature requests will from now on be no longer ignored, since I finished the core GUI. Just make sure to check the known issues section before opening a new issue.

## Known issues
The divider lines in the boxes don't look the same because of how Qt renders them, there isn't really a fix for this.

The program only adapts to your system theme when launched, since there isn't a easy way to read the theme out and change it while the program is running. If you want to change it, you have to press on the buttons on the first page or relaunch the program.

The handle of the scroll areas won't get bigger when hovered over it, because QSS doesn't care about a new width when accessing the hover selector.