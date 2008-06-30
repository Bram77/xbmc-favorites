"""
    Plugin for streaming Apple Movie Trailers
"""

# main imports
import sys
import os

# plugin constants
__plugin__ = "Apple Movie Trailers II"
__author__ = "nuka1195"
__url__ = "http://code.google.com/p/xbmc-addons/"
__svn_url__ = "http://xbmc-addons.googlecode.com/svn/trunk/plugins/video/Apple%20Movie%20Trailers%20II"
__credits__ = "Team XBMC"
__version__ = "1.4"


if ( __name__ == "__main__" ):
    if ( not sys.argv[ 2 ] ):
        import resources.lib.xbmcplugin_trailers as plugin
        plugin.Main()
    elif ( sys.argv[ 2 ].startswith( "?Fetch_Showtimes" ) ):
        import resources.lib.xbmcplugin_showtimes as showtimes
        s = showtimes.GUI( "plugin-AMTII-showtimes.xml", xbmc.translatePath( os.path.join( os.getcwd().replace( ";", "" ), "resources" ) ), "default" )
        del s
    elif ( sys.argv[ 2 ].startswith( "?Download_Trailer" ) ):
        import resources.lib.xbmcplugin_download as download
        download.Main()
sys.modules.clear()