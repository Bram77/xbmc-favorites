import sys
import os
import xbmc
import xbmcgui

DEBUG_MODE = 5

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__

# comapatble versions
SETTINGS_VERSIONS = ( "1.0", )
# base paths
BASE_DATA_PATH = os.path.join( "T:/script_data", __scriptname__ )
BASE_SETTINGS_PATH = os.path.join( "P:/script_data", __scriptname__ )
BASE_RESOURCE_PATH = sys.modules[ "__main__" ].BASE_RESOURCE_PATH
# special action codes
SELECT_ITEM = ( 11, 256, 61453, )
EXIT_SCRIPT = ( 247, 275, 61467, 216, 257, 61448, )
CANCEL_DIALOG = EXIT_SCRIPT + ( 216, 257, 61448, )
GET_EXCEPTION = ( 216, 260, 61448, )
SELECT_BUTTON = ( 229, 259, 261, 61453, )
MOVEMENT_UP = ( 166, 270, 61478, )
MOVEMENT_DOWN = ( 167, 271, 61480, )
# Log status codes
LOG_INFO, LOG_ERROR, LOG_NOTICE, LOG_DEBUG = range( 1, 5 )

def _create_base_paths():
    """ creates the base folders """
    if ( not os.path.isdir( BASE_DATA_PATH ) ):
        os.makedirs( BASE_DATA_PATH )
    if ( not os.path.isdir( BASE_SETTINGS_PATH ) ):
        os.makedirs( BASE_SETTINGS_PATH )
_create_base_paths()

def get_keyboard( default="", heading="", hidden=False ):
    """ shows a keyboard and returns a value """
    keyboard = xbmc.Keyboard( default, heading, hidden )
    keyboard.doModal()
    if ( keyboard.isConfirmed() ):
        return keyboard.getText()
    return default

def get_numeric_dialog( default="", heading="", type=3 ):
    """ shows a numeric dialog and returns a value
        - 0 : ShowAndGetNumber		(default format: #)
        - 1 : ShowAndGetDate		(default format: DD/MM/YYYY)
        - 2 : ShowAndGetTime		(default format: HH:MM)
        - 3 : ShowAndGetIPAddress	(default format: #.#.#.#)
    """
    dialog = xbmcgui.Dialog()
    value = dialog.numeric( type, heading, default )
    return value

def get_browse_dialog( default="", heading="", type=1, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value = dialog.browse( type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value

def LOG( status, format, *args ):
    if ( DEBUG_MODE >= status ):
        xbmc.output( "%s: %s\n" % ( ( "INFO", "ERROR", "NOTICE", "DEBUG", )[ status - 1 ], format % args, ) )

def show_settings():
    """ shows a settings window """
    import settings
    s = settings.GUI( "script-%s-settings.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(), "Default" )
    s.doModal()
    del s

class Settings:
    """ Settings class """
    def get_settings( self ):
        """ read settings from a settings.txt file in BASE_SETTINGS_PATH """
	try:
            #if os.file.exists( os.path.join( BASE_SETTINGS_PATH, "settings.txt" ) ):
		#print "Error! File not found: " + os.path.join( BASE_SETTINGS_PATH, "settings.txt" )
            	#raise
            settings_file = open( os.path.join( BASE_SETTINGS_PATH, "settings.txt" ), "r" )
            settings_temp = settings_file.read()
            settings = eval( settings_temp )
            settings_file.close()
            if ( settings[ "version" ] not in SETTINGS_VERSIONS ):
                raise
        except:
            settings = self._use_defaults()
        return settings

    def _use_defaults( self, show_dialog=False ):
        """ setup default values if none obtained """
        LOG( LOG_NOTICE, "%s (ver: %s) used default settings", __scriptname__, __version__ )
        settings = {
            "version": __version__,
            "osdb_server": "http://www.opensubtitles.org/xml-rpc",
            "username": "",
            "password": "",
            "save_to_videofile_path": False,
            "subtitles_path": "F:\\subtitles",
            }
        ok = self.save_settings( settings )
        return settings

    def save_settings( self, settings ):
        """ save settings to a settings.txt file in BASE_SETTINGS_PATH """
        try:
            settings_file = open( os.path.join( BASE_SETTINGS_PATH, "settings.txt" ), "w" )
            settings_temp = repr( settings )
            settings_file.write( settings_temp )
            settings_file.close()
            return True
        except:
            LOG( LOG_ERROR, "%s (ver: %s) Settings::save_settings [%s]", __scriptname__, __version__, sys.exc_info()[ 1 ], )
            return False
