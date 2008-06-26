"""
    Plugin for downloading scripts/plugins/skins from http://code.google.com/p/xbmc-addons/
"""

# main imports
import sys

# plugin constants
__plugin__ = "XBMC-Addons Installer"
__author__ = "nuka1195"
__url__ = "http://code.google.com/p/xbmc-addons/"
__svn_url__ = "http://xbmc-addons.googlecode.com/svn/trunk/plugins/programs/XBMC-Addons%20Installer%20Plugin"
__credits__ = "Team XBMC"
__version__ = "1.0"


if ( __name__ == "__main__" ):
    if ( "download_url=" in sys.argv[ 2 ] ):
        from installerAPI import xbmcplugin_downloader as plugin
    else:
        from installerAPI import xbmcplugin_list as plugin
    plugin.Main()
