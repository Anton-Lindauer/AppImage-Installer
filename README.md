# AppImage-Installer

## A GUI tool to easily install AppImage files on Linux

This project is **still in development**, but you can already do the following things: You can move the AppImage file to the right directory, make the file executable, make a symlink (to launch it from the terminal) and you can also create a desktop startmenu entry. You can choose between a GUI or a CLI to install your AppImages. The AppImages files are expected to be in your downloads directory.

And if you don't want a AppImage program anymore, you can also uninstall the program now (only in the GUI version).

The CLI version is no longer maintained and can only install AppImages and not uninstall them.

## Requirements

You need Python version 3.12 or higher to use the GUI or CLI version of this tool.

Pyside6 module is required for the GUI version.

Should work on any **Linux** Distro, doesn't work on Windows.

## How to install and launch the CLI or GUI version

[Installation guide can be found here.](HowToInstall.md)

## Have a look at the GUI version

**Note:** The pictures are not 100% up to date and small visual changes are not worth the effort to update them.

### Selecting a file to install

![image alt](https://github.com/Anton-Lindauer/AppImage-Installer/blob/46315701a187ff9cb3c29cbf78db58fbf1f3189a/pictures%20for%20README%20file/Installer%20Page%201.png)
Pick a file from your Downloads directory with the radiobuttons or from somewhere else.

### Entering program info

![image alt](https://github.com/Anton-Lindauer/AppImage-Installer/blob/c62f0112bedb32829aca441519ca4207fe638803/pictures%20for%20README%20file/Installer%20Page%202.png)
Example of installing Ultimaker Cura. AppImage-Installer extracts the metadata from the AppImage file and will fill out everything accourdingly.

Allthough the GUI doesn't tell you, you have to fill out every field on this page to continue. You can select multiple categories.

### Uninstalling AppImage programs

![image alt](https://github.com/Anton-Lindauer/AppImage-Installer/blob/3c2d934e4599e7d495e181149be2eb9587fd7ad3/pictures%20for%20README%20file/Uninstaller%20Page%201.png)
**Note:** Only complete AppImage installation that follow this tools install principles will show up here.

### Uninstallation terminal

![image alt](https://github.com/Anton-Lindauer/AppImage-Installer/blob/c62f0112bedb32829aca441519ca4207fe638803/pictures%20for%20README%20file/Uninstaller%20Page%202.png)
The installer tab has a similar terminal after page 2. When pressing start uninstallation/installation, the process will actually start.

## Other important notes

Removing a AppImage file with this program will permanently delete it.

If you suddenly find a directory called "AppDir" or another new directory in the directory of the installer scripts, you can most likely safely delete them. Sometimes such directories are created by the AppImages durin the app icon extraction process.

A light mode and other themes, as well as KDE Plasma theme integration are also included.

This tool is still work in progress and more functionality will be added soon.

Error log are stored in ~/{username}/.local/share/AppImage-Installer/logs

The AppImage files are moved to ~/{username}/AppImages/.

The symlinks are created in ~/{username}/.local/bin/

The startmenu entries are created in ~/{username}/.local/applications/

Logs are stored in ~/{username}/.local/share/AppImage-Installer/logs

If you want to contribute, make suggestions on how to make the code better or the themes look better - feature requests will from now on be no longer ignored, since I finished the core GUI. Just make sure to check the known issues section before opening a new issue.

## Known issues

The divider lines in the boxes don't look the same because of how Qt renders them, there isn't really a fix for this.

The ComboBox in the configure menu has a box around the drop down menu on Linux Mint. This is because of some Qt or Cinnamon default behavior when creating that element. I haven't found a fix yet and I'm not even sure if this is fixable.

There is a random line under the text of a tab when using the KDE Plasma integration, I couldn't find a fix yet.
