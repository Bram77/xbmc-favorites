"""
    Player module: plays the selected video
"""

def _get_keyboard( default="", heading="", hidden=False ):
    """ shows a keyboard and returns a value """
    keyboard = xbmc.Keyboard( default, heading, hidden )
    keyboard.doModal()
    if ( keyboard.isConfirmed() ):
        return keyboard.getText()
    return default

# get the video id (we do it here so there is minimal delay with nothing displayed)
import xbmc
video_id = _get_keyboard( heading=xbmc.getLocalizedString( 30910 ) )#"W2cMJE35WKE"

if ( video_id ):
    # create the progress dialog (we do it here so there is minimal delay with nothing displayed)
    import sys
    import xbmcgui
    pDialog = xbmcgui.DialogProgress()
    pDialog.create( sys.modules[ "__main__" ].__plugin__, xbmc.getLocalizedString( 30908 ) )

    import xbmcplugin

    from YoutubeAPI.YoutubeClient import YoutubeClient


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    def __init__( self ):
        if ( video_id ):
            self._parse_argv()
            self._get_settings()
            self.play_video( video_id )

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ).replace( "\\u0027", "'" ).replace( "\\u0022", '"' ).replace( "\\u0026", "&" ), )

    def _get_settings( self ):
        self.player_core = ( xbmc.PLAYER_CORE_MPLAYER, xbmc.PLAYER_CORE_DVDPLAYER, )[ int( xbmcplugin.getSetting( "player_core" ) ) ]

    def play_video( self, video_id ):
        # Youtube client
        client = YoutubeClient()
        # construct the video url with session id
        video_url = client.BASE_ID_URL % ( video_id, )
        # fetch video information
        url, title, author, genre, rating, runtime, count, date, thumbnail_url, plot, video_id = client.construct_video_url( video_url, ( 0, 6, 18, )[ int( xbmcplugin.getSetting( "quality" ) ) ] )
        pDialog.close()
        if ( not pDialog.iscanceled() ):
            listitem = xbmcgui.ListItem( title, runtime, thumbnailImage=thumbnail_url )
            # set the key information
            listitem.setInfo( "video", { "Title": title, "Director": author, "Genre": genre, "Rating": rating, "Duration": runtime, "Count": count, "Date": date, "PlotOutline": plot, "Plot": plot } )
            # Play video with the proper core
            xbmc.Player( self.player_core ).play( url, listitem )
