"""
    Plugin for streaming AOL Videos
"""

# main imports
import sys

# plugin constants
__plugin__ = "AOL Videos"
__author__ = "nuka1195/dataratt"
__url__ = "http://code.google.com/p/xbmc-addons/"
__svn_url__ = "http://xbmc-addons.googlecode.com/svn/trunk/plugins/video/AOL%20Videos"
__credits__ = "Team XBMC"
__version__ = "1.1.2"


if ( __name__ == "__main__" ):
    if ( "download_url=" in sys.argv[ 2 ] ):
        from AolAPI import xbmcplugin_player as plugin
    else:
        from AolAPI import xbmcplugin_list as plugin
    plugin.Main()
