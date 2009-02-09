"""
    Player module: plays the selected video
"""

# create the progress dialog (we do it here so there is minimal delay with nothing displayed)
import sys
import xbmcgui
import xbmc

g_msg = xbmc.getLocalizedString( 30909 )

pDialog = xbmcgui.DialogProgress()
def create_dialog():
    pDialog.create( sys.modules[ "__main__" ].__plugin__, g_msg )
create_dialog()

import threading
import xbmcplugin

from YoutubeAPI.YoutubeClient import YoutubeClient


class Main( xbmcgui.Window ):
    EXIT_SCRIPT = ( 247, 275, 61467, 216, 257, 61448, )

    def __init__( self ):
        self.setCoordinateResolution( 6 )
        self.get_dummy_timer()
        self._get_settings()
        self.play_random_video()
        self.addControl( xbmcgui.ControlLabel( 10, 280, 700, 20, "Middio Player", alignment=2 ) )
        self.doModal()

    def _get_settings( self ):
        player_core = ( xbmc.PLAYER_CORE_MPLAYER, xbmc.PLAYER_CORE_DVDPLAYER, )[ int( xbmcplugin.getSetting( "player_core" ) ) ]
        self.Player = XBMCPlayer( player_core, function=self.player_changed )

    def player_changed( self, event ):
        if ( event == 0 ):
            self.exit()
        elif ( event == 1 ):
            create_dialog()
            self.play_random_video()

    def play_random_video( self ):
        # Youtube client
        client = YoutubeClient()
        # fetch video information
        url, title, author, genre, rating, runtime, count, date, thumbnail_url, plot = client.get_random_middio_video( ( 0, 6, 18, )[ int( xbmcplugin.getSetting( "quality" ) ) ] )
        pDialog.close()
        if ( not pDialog.iscanceled() ):
            listitem = xbmcgui.ListItem( title, runtime, thumbnailImage=thumbnail_url )
            # set the key information
            listitem.setInfo( "video", { "Title": title, "Director": author, "Genre": genre, "Rating": rating, "Duration": runtime, "Count": count, "Date": date, "PlotOutline": plot, "Plot": plot } )
            # Play video with the proper core
            self.Player.play( url, listitem )

    def get_dummy_timer( self ):
        # needed for the XBMCPlayer's on* events to fire immediately
        self.Timer = threading.Timer( 60*60*60, self.get_dummy_timer,() )
        self.Timer.start()

    def exit( self ):
        if ( self.Timer ): self.Timer.cancel()
        self.close()

    def onControl(self, control):
        pass
            
    def onAction( self, action ):
        if ( action.getButtonCode() in self.EXIT_SCRIPT ):
            self.exit()


class XBMCPlayer( xbmc.Player ):
    """ Player Class: calls function when video changes or playback ends """
    def __init__( self, *args, **kwargs ):
        xbmc.Player.__init__( self )
        self.function = kwargs[ "function" ]

    def onPlayBackStopped( self ):
        self.function( 0 )
    
    def onPlayBackEnded( self ):
        self.function( 1 )
    
    def onPlayBackStarted( self ):
        self.function( 2 )

if ( __name__ == "__main__" ):
    ui = Main()
    ui.doModal()
    del ui
