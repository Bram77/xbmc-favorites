"""
    Plugin for streaming live TV to XBMC from TVServer
"""

# main imports
import sys

# plugin constants
__plugin__ = "TVServer Live TV"
__author__ = "evildude aka prashantv"
__url__ = "http://code.google.com/p/xbmc-addons/"
__svn_url__ = ""
__credits__ = "Prashant V"
__version__ = "1.0.0"


if ( __name__ == "__main__" ):
    from MpLiveTv import xbmcplugin_list as plugin
    plugin.Main()
