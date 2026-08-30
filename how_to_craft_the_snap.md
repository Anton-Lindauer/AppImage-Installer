# How to craft the snap

- [How to craft the snap](#how-to-craft-the-snap)
  - [Setting up the build environment](#setting-up-the-build-environment)
  - [Downloading the repo](#downloading-the-repo)
  - [Building and installing the snap package](#building-and-installing-the-snap-package)

This is a guide on how to craft the snap package yourself. If you're not a developer, it is recommended to just download the app from snap instead of building it yourself.

## Setting up the build environment

**IMPORTANT:** Before you build the snap yourself, make sure that you have at least 20GB of free space on your hard drive.

Install <kbd>snapcraft</kbd> and <kbd>lxd</kbd> from the snap store

```bash
snap install snapcraft --classic
snap install lxd
```

Add your local account to the <kbd>lxd</kbd> group

```bash
sudo usermod -a -G lxd $USER
```

Now log out and back in to your account for the new group to become active.

```bash
groups $USER
```

<kbd>lxd</kbd> should be listed in the output.

Lastly initialize <kbd>lxd</kbd>

```bash
sudo lxd init --auto
```

## Downloading the repo

Download the repo to your home directory or whereever you like

```bash
git clone https://github.com/Anton-Lindauer/AppImage-Installer.git
```

Then go in the AppImage-Installer directory

```bash
cd AppImage-Installer
```

## Building and installing the snap package

Start the build process

```bash
snapcraft pack
```

Install the builded snap package

```bash
sudo snap install ./appimage-installer_1.2.0-alpha_amd64.snap --dangerous
```

Give the Snap acces to the required hidden directories

```bash
sudo snap connect appimage-installer:appimage-installer-desktop
sudo snap connect appimage-installer:appimage-installer-bin
sudo snap connect appimage-installer:appimage-installer-icons
```

Launch the snap

```bash
appimage-installer
```

Remove the snap if you don't want it anymore

```bash
sudo snap remove appimage-installer
```
