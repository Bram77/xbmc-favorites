import sys
import os
import xbmcgui
import xbmc

__scriptname__ = "OpenSubtitles"
__author__ = "Leo"
__url__ = ""
__svn_url__ = ""
__credits__ = "Leo"
__version__ = "1.0"

BASE_RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
import language
__language__ = language.Language().localized

if ( __name__ == "__main__" ):

	import gui
	window = "main"
	filename = ""

#	if len(sys.argv) > 1:
#		filename = sys.argv[1]		
	ui = gui.GUI( "script-%s-%s.xml" % ( __scriptname__.replace( " ", "_" ), window, ), os.getcwd(), "Default")
#	ui.set_filepath( filename )	
	ui.set_filepath( "" )
	ui.doModal()
	del ui
