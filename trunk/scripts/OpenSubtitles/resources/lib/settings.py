import sys
import os
import xbmc
import xbmcgui

from utilities import *

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__

class GUI( xbmcgui.WindowXMLDialog ):
    """ Settings module: used for changing settings """
    def __init__( self, *args, **kwargs ):
        pass

    def onInit( self ):
        self._get_settings()
        self._set_labels()
        self._set_functions()
        #self._setup_special()
        self._set_restart_required()
        self._set_controls_values()

    def _get_settings( self ):
        """ reads settings """
        self.settings = Settings().get_settings()

    def _set_labels( self ):
        xbmcgui.lock()
        try:
            self.getControl( 20 ).setLabel( _( 641 ) % __scriptname__ )
            self.getControl( 30 ).setLabel( "%s: %s" % ( _( 1006 ), __version__, ) )
            self.getControl( 250 ).setLabel( _( 250 ) )
            self.getControl( 251 ).setLabel( _( 251 ) )
            self.getControl( 252 ).setLabel( _( 252 ) )
            for x in range( 1, len( self.settings ) ):
                self.getControl( 200 + x ).setLabel( _( 200 + x ) )
        except: pass
        xbmcgui.unlock()

    def _set_functions( self ):
        self.functions = {}
        self.functions[ 250 ] = self._save_settings
        self.functions[ 251 ] = self._close_dialog
        self.functions[ 252 ] = self._update_script
        for x in range( 1, len( self.settings ) ):
            self.functions[ 200 + x ] = eval( "self._change_setting%d" % x )

##### Special defs, script dependent, remember to call them from _setup_special #################
    
    def _setup_special( self ):
        """ calls any special defs """
        self._setup_scrapers()
        self._setup_filename_format()
    
    def _set_restart_required( self ):
        """ copies self.settings and adds any settings that require a restart on change """
        self.settings_original = self.settings.copy()
        self.settings_restart = ( "osdb_server", "username", "password", )
        #self.settings_refresh = ( , )

###### End of Special defs #####################################################

    def _set_controls_values( self ):
        """ sets the value labels """
        xbmcgui.lock()
        try:
            self.getControl( 221 ).setLabel( self.settings[ "osdb_server" ] )
            self.getControl( 222 ).setLabel( self.settings[ "username" ] )
            self.getControl( 223 ).setLabel( '*'*len( self.settings[ "password" ] ) )
            self.getControl( 224 ).setSelected( self.settings[ "save_to_videofile_path" ] )
            self.getControl( 225 ).setLabel( self.settings[ "subtitles_path" ] )
        except: pass
        xbmcgui.unlock()

    def _change_setting1( self ):
        """ changes settings #1 """
        self.settings[ "osdb_server" ] = get_keyboard( self.settings[ "osdb_server" ], "OpenSubtitles server" )
        self._set_controls_values()

    def _change_setting2( self ):
        """ changes settings #2 """
        self.settings[ "username" ] = get_keyboard( self.settings[ "username" ], "OpenSubtitles username" )
        self._set_controls_values()

    def _change_setting3( self ):
        """ changes settings #3 """
        self.settings[ "password" ] = get_keyboard( self.settings[ "password" ], "OpenSubtitles password", True )
        self._set_controls_values()

    def _change_setting4( self ):
        """ changes settings #4 """
        self.settings[ "save_to_videofile_path" ] = not self.settings[ "save_to_videofile_path" ]
        self._set_controls_values()

    def _change_setting5( self ):
        """ changes settings #5 """
	if not self.settings[ "subtitles_path" ]:
		self.settings[ "subtitles_path" ] = get_browse_dialog( "files", _( self.controlId ), 3 )        	
	else:
        	self.settings[ "subtitles_path" ] = get_browse_dialog( self.settings[ "subtitles_path" ], _( self.controlId ), 3 )
        self._set_controls_values()

##### End of unique defs ######################################################
    
    def _save_settings( self ):
        """ saves settings """
        ok = Settings().save_settings( self.settings )
        if ( not ok ):
            ok = xbmcgui.Dialog().ok( __scriptname__, _( 230 ) )
            self._close_dialog()
        else:
            self._check_for_restart()

    def _check_for_restart( self ):
        """ checks for any changes that require a restart to take effect """
        restart = False
        refresh = False
        for setting in self.settings_restart:
            if ( self.settings_original[ setting ] != self.settings[ setting ] ):
                restart = True
                break
        #for setting in self.settings_refresh:
        #    if ( self.settings_original[ setting ] != self.settings[ setting ] ):
        #        refresh = True
        #        break
        self._close_dialog( True, restart, refresh )

    def _update_script( self ):
        """ checks for updates to the script """
        import update
        updt = update.Update()
        del updt
        
    def _close_dialog( self, changed=False, restart=False, refresh=False ):
        """ closes this dialog window """
        self.changed = changed
        self.restart = restart
        self.refresh = refresh
        self.close()

    def onClick( self, controlId ):
        #xbmc.sleep(5)
        self.functions[ controlId ]()

    def onFocus( self, controlId ):
        self.controlId = controlId

    def onAction( self, action ):
        if ( action.getButtonCode() in CANCEL_DIALOG ):
            self._close_dialog()
