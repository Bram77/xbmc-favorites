"""
    Videos module: fetches a list of videos for a specific category
"""

# main imports
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin

from YahooAPI.YahooClient import YahooClient


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base paths
    BASE_PRESETS_PATH = os.path.join( "P:\\plugin_data", "video", os.path.basename( os.getcwd().replace( ";", "" ) ), "presets" )

    def __init__( self ):
        self._get_settings()
        self._parse_argv()
        self.get_items()

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ).replace( "\\u0027", "'" ).replace( "\\u0022", '"' ).replace( "\\u0026", "&" ), )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "per_page" ] = ( 10, 15, 20, 25, 30, 40, 50, 75, 100, )[ int( xbmcplugin.getSetting( "per_page" ) ) ]
        self.settings[ "total_pages" ] = ( 5, 10, 15, 20, 25, 30, 40, 50, )[ int( xbmcplugin.getSetting( "total_pages" ) ) ]
        self.settings[ "adult_ok" ] = xbmcplugin.getSetting( "adult_ok" ) == "true"
        #self.settings[ "mode" ] = int( xbmcplugin.getSetting( "mode" ) )
        #self.settings[ "download_path" ] = xbmcplugin.getSetting( "download_path" )

    def get_items( self ):
        # is this a search
        issearch = self.args.category == "search_videos"
        # get the videos and/or subcategories and fill the media list
        exec "ok, total = self.%s()" % ( self.args.category, )
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )
        # if there were videos and this was a search ask to save result as a preset
        if ( ok and total and issearch ):
            self.save_as_preset( self.args.query )

    def save_as_preset( self, query ):
        # ask if we want to save this as a preset
        if ( xbmcgui.Dialog().yesno( "Save as preset", "Would you like to save this query as a preset?" ) ):
            # get the preset name from the user
            preset = self._get_keyboard( default=query, heading="Preset name" )
            # if not blank and the user did not cancel the keyboard save preset
            if ( preset ):
                try:
                    f = open( xbmc.translatePath( os.path.join( self.BASE_PRESETS_PATH, preset ) ), "w" )
                    f.write( query )
                    f.close()
                except:
                    ok = xbmcgui.Dialog().ok( "Save preset failed!", "Saving preset file failed with error:", str( sys.exc_info()[ 1 ] ) )

    def search_videos( self ):
        # get the query to search for from the user
        self.args.query = self._get_keyboard( heading="Search keywords" )
        # if blank or the user cancelled the keyboard return
        if ( not self.args.query ): return False, 0
        # we need to set the function to preset_videos
        self.args.category = "preset_videos"
        # fetch videos
        return self.fetch_videos( YahooClient.BASE_SEARCH_URL )

    def all_videos( self ):
        # fetch videos
        return self.fetch_videos( YahooClient.BASE_SEARCH_URL )

    def preset_videos( self ):
        # fetch videos
        return self.fetch_videos( YahooClient.BASE_SEARCH_URL )

    def fetch_videos( self, url ):
        try:
            # Yahoo client
            client = YahooClient( url )
            start_index = ( self.args.page - 1 ) * self.settings[ "per_page" ] + 1
            exec "videos = client.get_videos( query=%s, start=start_index, results=%d, adult_ok=%d )" % ( repr( self.args.query + " music" ), self.settings[ "per_page" ], self.settings[ "adult_ok" ], )
            pages = self._get_total_pages( int( videos[ "ResultSet" ][ "totalResultsAvailable" ] ) )
            return self._fill_media_list( videos[ "ResultSet" ][ "Result" ], self.args.page, pages, self.settings[ "per_page" ], int( videos[ "ResultSet" ][ "totalResultsAvailable" ] ) )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return False, 0

    def _get_total_pages( self, total ):
        # calculate the total number of pages
        pages = int( total / self.settings[ "per_page" ] ) + ( total % self.settings[ "per_page" ] > 0 )
        if ( pages > self.settings[ "total_pages" ] ): pages = self.settings[ "total_pages" ]
        return pages

    def _fill_media_list( self, videos, page, pages=1, perpage=1, total=1 ):
        try:
            ok = True
            # calculate total items including dummy folders
            total_items = len( videos )
            # if there is more than one page and we're on page one, we create dummy folders for the other videos
            if ( page == 1 and pages > 1 ):
                # add our pages to the total items
                total_items += pages - 1
                # enumerate the pages
                for pageno in range( 2, pages + 1 ):
                    # calculate the starting video
                    startno = ( pageno - 1 ) * perpage + 1
                    # calculate the ending video
                    endno = pageno * perpage
                    # if there are fewer videos than per_page set endno to total
                    if ( endno > total ):
                        endno = total
                    # create the callback url
                    url = "%s?title=%s&category=%s&page=%d&query=%s" % ( sys.argv[ 0 ], repr( self.args.title ), repr( self.args.category ), pageno, repr( self.args.query ), )
                    # set the default icon
                    icon = "DefaultFolder.png"
                    # only need to add label and icon, setInfo() and addSortMethod() takes care of label2
                    listitem=xbmcgui.ListItem( label="%s (%d-%d)" % ( xbmc.getLocalizedString( 3 ), startno, endno, ), iconImage=icon )
                    # add the folder item to our media list
                    ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=total_items )
            # enumerate through the list of videos and add the item to the media list
            for video in videos:
                # only add videos with an embeddable video
                # TODO: Filter formats ?
                if ( video[ "FileFormat" ] ):
                    # create the title, we use video title and author
                    title = video[ "Title" ].replace( "\\/", "/" )
                    if ( title.startswith( "'" ) and title.endswith( "'" ) ):
                        title = title[ 1 : -1 ]
                    # thumbnail url
                    thumbnail_url = video[ "Thumbnail" ][ "Url" ].replace( "\\/", "/" )
                    # plot
                    plot = "no summary was furnished by user"
                    if ( video[ "Summary" ] ):
                        plot = video[ "Summary" ]
                    # format runtime as 00:00
                    try:
                        runtime = int( video[ "Duration" ] )
                    except:
                        runtime = ""
                    # video runtime
                    if ( runtime ):
                        runtime = "%02d:%02d" % ( int( runtime / 60 ), runtime % 60 )
                    # we use studio as the site specifier
                    if ( "yahoo" in video[ "ClickUrl" ] ): studio = "Yahoo"
                    elif ( ".aol." in video[ "ClickUrl" ] ): studio = "AOL"
                    elif ( "youtube" in video[ "ClickUrl" ] ): studio = "Youtube"
                    #elif ( "google" in video[ "ClickUrl" ] ): studio = "Google"
                    else: studio = "Other"
                    # construct our url
                    url = "%s?title=%s&url=%s&category='play_video'" % ( sys.argv[ 0 ], repr( title ), repr( video[ "ClickUrl" ].replace( "\\/", "/" ).replace( "&", "-*-*-" ) ), )
                    # set the default icon
                    icon = "DefaultVideo.png"
                    # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
                    listitem=xbmcgui.ListItem( label=title, iconImage=icon, thumbnailImage=thumbnail_url )
                    # add the different infolabels we want to sort by
                    listitem.setInfo( type="Video", infoLabels={ "Title": title, "Duration": runtime, "Plot": plot, "PlotOutline": plot, "Studio": studio } )
                    # add the video to the media list
                    ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=False, totalItems=total_items )
                    # if user cancels, call raise to exit loop
                    if ( not ok ): raise
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        # if successful and user did not cancel, add all the required sort methods
        if ( ok ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_STUDIO )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
        return ok, total_items

    def _get_keyboard( self, default="", heading="", hidden=False ):
        """ shows a keyboard and returns a value """
        keyboard = xbmc.Keyboard( default, heading, hidden )
        keyboard.doModal()
        if ( keyboard.isConfirmed() ):
            return keyboard.getText()
        return default
