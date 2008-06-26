"""
    Plugin for downloading personal favorite scripts/plugins/skins from http://www.kraak-forum.nl/remote/XBMC/addons_installer/
"""

# main imports
import sys

# plugin constants
__plugin__ = "XBMC-Favorites Installer Plugin"
__author__ = "Bram77"
__url__ = "http://www.kraak-forum.nl/remote/XBMC/addons_installer/"
__svn_url__ = "http://www.kraak-forum.nl/remote/XBMC/addons_installer/XBMC-Favorites%20Installer%20Plugin"
__credits__ = "Bram van Oploo"
__version__ = "0.1"


if ( __name__ == "__main__" ):
    if ( "download_url=" in sys.argv[ 2 ] ):
        from installerAPI import xbmcplugin_downloader as plugin
    else:
        from installerAPI import xbmcplugin_list as plugin
    plugin.Main()
