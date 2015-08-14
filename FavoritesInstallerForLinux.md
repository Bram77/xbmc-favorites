_Because Linux uses a different file structure then the XBOX the script has to be modified to work on Linux. Follow instructions carefully_

# Introduction #

This howto only applies to the XBMC for Linux version that are installed from the XBMC Ubuntu repositories! You need to be running Debian or Ubuntu to install XBMC this way.


# Installation instructions #

## Step 1 ##
**If you've already installed XBMC from the XBMC Ubuntu repositories you can skip this step**

  * Open Terminal and execute the following
```
sudo gedit /etc/apt/sources.list
```

  * A text file will be opened. Add the lines below to the bottom of this file and save it
```
## XBMC
deb http://ppa.launchpad.net/team-xbmc-svn/ubuntu hardy main
deb-src http://ppa.launchpad.net/team-xbmc-svn/ubuntu hardy main
```

  * Run the following in Terminal
```
sudo apt-get update
sudo apt-get install xbmc
```


## Step 2 ##

  * Create the programs directory for xbmc by executing the following line in Termial
```
mkdir ~/.xbmc/plugins/programs
```

  * Download the [XBMC-Favorites Installer for Linux](http://xbmc-favorites.googlecode.com/files/xbmc_favorites_installer_linux_v1.3a.zip) plugin to your desktop and execute the following lines from Terminal
```
sudo apt-get install unzip
unzip ~/Desktop/xbmc_favorites_installer_linux_v1.3a.zip -d ~/.xbmc/plugins/programs/
```

  * Run XBMC and add the plugin as discribed in the [plugin installation wiki](http://code.google.com/p/xbmc-favorites/wiki/Installation).



Now you're good to go. A lot of plugins won't work with Linux (yet). XBMC for Linux isn't even in Alpha stage. You'll have to try to find out which ones do and which ones don't. All skins will work (as far as I know)!