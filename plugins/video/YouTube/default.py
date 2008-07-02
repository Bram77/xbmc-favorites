"""
    Plugin for streaming content from youtube.com
"""

# main imports
import sys
import os
import xbmc

# plugin constants
__script__ = "YouTube"


ROOT_DIR = os.getcwd()[:-1]
RESOURCE_DIR = os.path.join(ROOT_DIR , "resources" )
sys.path.append( os.path.join( RESOURCE_DIR, "libs" ) )

import language
__language__ = language.Language().localized

if ( __name__ == "__main__" ):
    if ( not sys.argv[ 2 ] ):
    	import categories as plugin
    else:
	import videos as plugin	
    plugin.Main()