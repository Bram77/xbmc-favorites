"""
    Plugin for downloading scripts/plugins/skins from http://code.google.com/p/xbmc-favorites/
"""

# main imports
import sys

# plugin constants
__plugin__ = "XBMC-Favorites Installer"
__author__ = "nuka1195"
__url__ = "http://code.google.com/p/xbmc-favorites/"
__svn_url__ = "http://xbmc-addons.googlecode.com/svn/trunk/plugins/programs/XBMC-Favorites%20Installer"
__credits__ = "Team XBMC"
__version__ = "1.2"


if ( __name__ == "__main__" ):
    if ( "download_url=" in sys.argv[ 2 ] ):
        from installerAPI import xbmcplugin_downloader as plugin
    else:
        from installerAPI import xbmcplugin_list as plugin
    plugin.Main()
