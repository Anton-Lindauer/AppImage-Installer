# Installation guide

## For every distro

Download this repo to your home directory
```
git clone https://github.com/Anton-Lindauer/AppImage-Installer.git
```

Then go in the AppImage-Installer directory
```
cd AppImage-Installer
```

**CLI:**

If you only want the CLI version, then enter this command to launch it
```
python3 src/cli/mainCLI.py
```

**GUI:**

If you want the GUI version, follow these steps

Create a virtual environment
```
python3 -m venv .venv
```

Activate the virtual environment in bash
```
source .venv/bin/activate
```

Or if you use fish
```
source .venv/bin/activate.fish
```

Install all requirements
```
pip install -r requirements.txt
```

Launch the GUI version via the terminal or click the run button in VS Code if you have done everything in VS Code
```
python3 main.py
```

The program will guide you through the installation process. Please report any errors that may occure, unless it's a problem with your AppImage file, I can't fix your brocken file

## For every distro with KDE Plasma

KDE Plasma also uses the Qt framework and can mess with QSS stylesheets. That's why I recommend you use the default theme of your KDE Plasma system

### For Debian based distros

```
sudo apt install qt6ct

sudo apt install qt6-wayland qwayland-qt6
```

### For Arch based distros

```
sudo pacman -S qt6ct

sudo pacman -S qt6-wayland plasma-integration
```

### For other distros

I don't know which packagemanager your distro uses, but you need to install qt6ct and qt6-wayland qwayland-qt6 or qt6-wayland plasma-integration or however it's called in your packagemanager

### IF IT DOESN'T WORK

KDE Plasma also uses the Qt framework and therefore you have to make sure that the system Pyside6 and in the .venv installed Pyside6 are the exact same version. If they are different, change the .venv version to the system version

Check your system version, by pasting this in a new terminal outside of your .venv and your venv version by pasting this in a terminal inside your activated .venv
```
pip list | grep PySide6
```

Remove the wrong version and install the system version in your activated .venv
```
pip uninstall PySide6

pip install PySide6==6.X.X
```