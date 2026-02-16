# AppImage-Installer

## A GUI or CLI tool to easily install AppImage files on Linux.

This project is **still in development**, but you can already do the following things: You can move the AppImage file to the right directory, make the file executable, launch it from the terminal and you can also create a desktop startmenu entry. You can choose between a GUI or a CLI to install your AppImages.

## Requirements

You need Python version 3.12 or higher to use the GUI or CLI version of this tool.

Pyside6 module is required for the GUI version. Check the official documentation or ask ChatGPT how to install it. It's recommended to use a virtual environment.

Should work on any **Linux** Distro, doesn't work on Windows.

## How to install and launch the CLI tool
Download this directory as a .ZIP file, decompress it, open a terminal in the decompressed folder and type in this command:

```
python3 mainCLI.py
```

The program will guide you through the installation process. Please report any errors that may occoure.

## How to install and launch the GUI tool
Download this directory as a .ZIP file, decompress it, install Pyside6 in a virtual environment in that directory and launch the GUI with this command:

```
python3 Pyside.py
```

The program will guide you through the installation process. Please report any errors that may occoure.

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

If you want to contribute, make suggestions on how to make the program more performant or the code more organized - feature requests will from now on be no longer ignored, since I finished the GUI.