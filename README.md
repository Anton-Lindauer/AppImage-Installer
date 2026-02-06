# AppImage-Installer

## A console-based tool to easily install AppImage files on Linux.

This project is **still in development**, but you can already do the following things: You can move the AppImage file to the right directory, make the file executable, launch it from the terminal and you can also create a desktop startmenu entry. For now in a command line interface, a GUI is in work.

Everything works now, but there is still more work to do, since the code is pretty messy.

## Requirements

You need Python version 3.13 or higher to use this program.

Pyside6 module is required. Check the official documentation or ask ChatGPT how to install it. It's recommended to use a virtual environment.

Should work on any **Linux** Distro, doesn't work on Windows.

## How to install and launch (NOT INCLUDING PYSIDE6!!!)
Download this directory as a .ZIP file, decompress it, open a terminal in the decompressed folder and type in this command:

```
python3 main.py
```

The program will guide you through the installation process. Please report any errors that may occoure.
## Other important notes
This tool is still work in progress and more functionality will be added soon.

The files are moved to ~/{username}/AppImages/.

If you want to contribute, make suggestions on how to make the program more performant or the code more organized - feature requests will be ignored until I have finished cleaning up the code.