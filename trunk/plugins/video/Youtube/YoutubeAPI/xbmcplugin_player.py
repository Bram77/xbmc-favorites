"""
    Player module: plays the selected video
"""

# TODO: remove this when dialog issue is resolved
import xbmc
"""
# set our title
g_title = unicode( xbmc.getInfoLabel( "ListItem.Title" ), "utf-8" )
# set our director
g_director = unicode( xbmc.getInfoLabel( "ListItem.Director" ), "utf-8" )
# set our genre
g_genre = unicode( xbmc.getInfoLabel( "ListItem.Genre" ), "utf-8" )
# set our rating
g_rating = 0.0
if ( xbmc.getInfoLabel( "ListItem.Rating" ) ):
    g_rating = float( xbmc.getInfoLabel( "ListItem.Rating" ) )
# set our date
g_date = xbmc.getInfoLabel( "ListItem.Date" )
# set our thumbnail
g_thumbnail = xbmc.getInfoImage( "ListItem.Thumb" )
# set our plotoutline
g_plotoutline = unicode( xbmc.getInfoLabel( "ListItem.Plot" ), "utf-8" )
"""
# create the progress dialog (we do it here so there is minimal delay with nothing displayed)
import sys
import xbmcgui
pDialog = xbmcgui.DialogProgress()
pDialog.create( sys.modules[ "__main__" ].__plugin__, xbmc.getLocalizedString( 30908 ) )

# main imports
import os
import xbmcplugin

from YoutubeAPI.YoutubeClient import YoutubeClient


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    def __init__( self ):
        self._parse_argv()
        self._get_settings()
        self._play_video()

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ).replace( "\\u0027", "'" ).replace( "\\u0022", '"' ).replace( "\\u0026", "&" ), )

    def _get_settings( self ):
        self.player_core = ( xbmc.PLAYER_CORE_MPLAYER, xbmc.PLAYER_CORE_DVDPLAYER, )[ int( xbmcplugin.getSetting( "player_core" ) ) ]

    def _play_video( self ):
        # Youtube client
        client = YoutubeClient()
        # construct the video url with session id and get video details
        url, g_title, g_director, g_genre, g_rating, g_runtime, g_count, g_date, g_thumbnail, g_plotoutline, video_id = client.construct_video_url( self.args.video_url, ( 0, 6, 18, )[ int( xbmcplugin.getSetting( "quality" ) ) ] )
        # close the dialog
        pDialog.close()
        if ( not pDialog.iscanceled() ):
            # get cached thumbnail, no need to redownload
            g_thumbnail = xbmc.getCacheThumbName( sys.argv[ 0 ] + sys.argv[ 2 ] )
            g_thumbnail = os.path.join( xbmc.translatePath( "p:\\Thumbnails" ), "Video", g_thumbnail[ 0 ], g_thumbnail )
            # construct our listitem
            listitem = xbmcgui.ListItem( g_title, thumbnailImage=g_thumbnail )
            # set the key information
            listitem.setInfo( "video", { "Title": g_title, "Plotoutline": g_plotoutline, "Plot": g_plotoutline, "Director": g_director, "Genre": g_genre, "Rating": g_rating, "Date": g_date } )
            # set special property
            listitem.setProperty( "isVideo", "1" )
            listitem.setProperty( "RecommendLink", sys.argv[ 0 ] + sys.argv[ 2 ] )
            # Play video with the proper core
            xbmc.Player( self.player_core ).play( url, listitem )
