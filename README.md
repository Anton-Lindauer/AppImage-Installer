# AppImage-Installer

## A console-based tool to easily install AppImage files on Linux.

This project is **still in development**, but you can already do the following things: You can move the AppImage file to the right directory, make the file executable, launch it from the terminal and you can also create a desktop startmenu entry. For now in a command line interface, a GUI is in work.

Everything works now, but there is still more work to do, since the code is pretty messy.

## Requirements

You need Python version 3.12 or higher to use the CLI version of this tool.

Pyside6 module is required for the unfinished GUI. Check the official documentation or ask ChatGPT how to install it. It's recommended to use a virtual environment.

Should work on any **Linux** Distro, doesn't work on Windows.

## How to install and launch the CLI tool
Download this directory as a .ZIP file, decompress it, open a terminal in the decompressed folder and type in this command:

```
python3 mainCLI.py
```

The program will guide you through the installation process. Please report any errors that may occoure.

## About the GUI
The GUI design is almost finished, but the logic doesn't fully work yet. You can choose a file in the GUI, but everything else still has to be done in the terminal. If you want to test the unfinished GUI, you will need Pyside6 (venv recommended) and execute the Pyside.py file or for now just have a look at the screenshots.

### Selecting a file to install
![image alt](https://github.com/Anton-Lindauer/AppImage-Installer/blob/f14feb2ef58f4b6dcdb579f0e8fe16d1b458bedb/pictures%20for%20README%20file/Page1.png)

### Entering program info
![image alt](https://github.com/Anton-Lindauer/AppImage-Installer/blob/f14feb2ef58f4b6dcdb579f0e8fe16d1b458bedb/pictures%20for%20README%20file/Page2.png)

### Finished installation screen
![image alt](https://github.com/Anton-Lindauer/AppImage-Installer/blob/f14feb2ef58f4b6dcdb579f0e8fe16d1b458bedb/pictures%20for%20README%20file/Page3.png)

## Other important notes
main.py will from now on be used by the GUI, if you want the terminal version of this tool, you have to execute the mainCLI.py file.

This tool is still work in progress and more functionality will be added soon.

The files are moved to ~/{username}/AppImages/.

If you want to contribute, make suggestions on how to make the program more performant or the code more organized - feature requests will be ignored until I have finished the GUI.