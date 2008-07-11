"""
    Plugin for downloading scripts/plugins/skins from http://code.google.com/p/xbmc-favorites/
"""

# main imports
import sys

# plugin constants
__plugin__ = "XBMC-Favorites Installer"
__author__ = "Bram77"
__url__ = "http://code.google.com/p/xbmc-favorites/"
__svn_url__ = "http://xbmc-favorites.googlecode.com/svn/trunk/plugins/programs/XBMC-Favorites%20Installer"
__credits__ = "Team XBMC"
__version__ = "1.3"


if ( __name__ == "__main__" ):
    if ( "download_url=" in sys.argv[ 2 ] ):
        from installerAPI import xbmcplugin_downloader as plugin
    else:
        from installerAPI import xbmcplugin_list as plugin
    plugin.Main()
