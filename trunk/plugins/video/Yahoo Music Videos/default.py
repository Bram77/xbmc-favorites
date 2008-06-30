"""
    Plugin for viewing music videos from Yahoo and partners
"""

# main imports
import sys
import os

# plugin constants
__plugin__ = "Yahoo Music Videos"
__author__ = "nuka1195/C-Quel"
__url__ = "http://code.google.com/p/xbmc-addons/"
__svn_url__ = "http://xbmc-addons.googlecode.com/svn/trunk/plugins/video/Yahoo%20Music%20Videos"
__credits__ = "Team XBMC"
__version__ = "1.2"

# base paths
BASE_PATH = os.getcwd().replace( ";", "" )


if ( __name__ == "__main__" ):
    if ( not sys.argv[ 2 ] ):
        from YahooAPI import xbmcplugin_categories as plugin
    elif ( "category='root_preset_videos'" in sys.argv[ 2 ] ):
        from YahooAPI import xbmcplugin_categories as plugin
    elif ( "category='play_video'" in sys.argv[ 2 ] ):
        from YahooAPI import xbmcplugin_player as plugin
    else:
        from YahooAPI import xbmcplugin_videos as plugin
    plugin.Main()
