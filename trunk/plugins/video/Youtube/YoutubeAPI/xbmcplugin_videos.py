"""
    Videos module: fetches a list of videos for a specific category
"""

# main imports
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin

from urllib import unquote_plus, quote_plus

from YoutubeAPI.YoutubeClient import YoutubeClient


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base paths
    BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( os.getcwd(), "thumbnails" )
    BASE_PRESETS_PATH = "/".join( [ "special://profile", "plugin_data", "video", os.path.basename( os.getcwd() ) ] )

    def __init__( self ):
        self._get_settings()
        self._get_strings()
        self._parse_argv()
        self._get_items()

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "username" ] = xbmcplugin.getSetting( "username" )
        self.settings[ "include_racy" ] = ( "exclude", "include", )[ xbmcplugin.getSetting( "include_racy" ) == "true" ]
        self.settings[ "perpage" ] = ( 10, 15, 20, 25, 30, 40, 50, 75, 100, )[ int( xbmcplugin.getSetting( "perpage" ) ) ]
        self.settings[ "feed_time" ] = ( "all_time", "today", "this_week", "this_month", )[ int( xbmcplugin.getSetting( "feed_time" ) ) ]
        self.settings[ "region_id" ] = ( "", "AU", "BR", "CA", "FR", "DE", "GB", "NL", "HK", "IE", "IT", "JP", "MX", "NZ", "PL", "RU", "KR", "ES", "TW", "US", )[ int( xbmcplugin.getSetting( "region_id" ) ) ]
        self.settings[ "saved_searches" ] = ( 10, 20, 30, 40, )[ int( xbmcplugin.getSetting( "saved_searches" ) ) ]
        self.settings[ "download_path" ] = xbmcplugin.getSetting( "download_path" )

    def _get_strings( self ):
        self.localized_string = {}
        self.localized_string[ 30900 ] = xbmc.getLocalizedString( 30900 )
        self.localized_string[ 30901 ] = xbmc.getLocalizedString( 30901 )
        self.localized_string[ 30902 ] = xbmc.getLocalizedString( 30902 )
        self.localized_string[ 30903 ] = xbmc.getLocalizedString( 30903 )
        self.localized_string[ 30905 ] = xbmc.getLocalizedString( 30905 )

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ).replace( "\\u0027", "'" ).replace( "\\u0022", '"' ).replace( "\\u0026", "&" ), )

    def _get_items( self ):
        # get the videos and/or subcategories and fill the media list
        exec "ok, total = self.%s()" % ( self.args.category, )
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok, updateListing=self.args.update_listing )#, cacheToDisc=not self.args.issearch )
        # if there were videos and this was a search ask to save result as a preset
        if ( ok and total and self.args.issearch ):
            self.save_as_preset()

    def save_as_preset( self ):
        # select correct query
        query = ( self.args.username, self.args.vq, )[ self.args.issearch - 1 ]
        # if user search and user was found then proceed, should never be an issue for video search
        if ( query ):
            # set the proper preset path
            preset_path = "/".join( [ self.BASE_PRESETS_PATH, ( "users", "videos", )[ self.args.issearch - 1 ] ] )
            # fetch saved presets
            try:
                # grab a file object
                fileobject = open( preset_path, "r" )
                # read the queries
                presets = eval( fileobject.read() )
                # close file object
                fileobject.close()
                # if this is an existing search, move it up
                for count, preset in enumerate( presets ):
                    if ( repr( query + " | " )[ : -1 ] in repr( preset ) ):
                        del presets[ count ]
                        break
                # limit to number of searches to save
                if ( len( presets ) >= self.settings[ "saved_searches" ] ):
                    presets = presets[ : self.settings[ "saved_searches" ] - 1 ]
            except:
                # no presets found
                presets = []
            # insert our new search
            presets = [ query + " | " + self.query_thumbnail ] + presets
            # save search query
            try:
                # grab a file object
                fileobject = open( preset_path, "w" )
                # write our current queries to file
                fileobject.write( repr( presets ) )
                # close file object
                fileobject.close()
            except:
                # oops print error message
                print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
                ok = xbmcgui.Dialog().ok( self.localized_string[ 30902 ], self.localized_string[ 30903 ], repr( sys.exc_info()[ 1 ] ) )

    def most_viewed( self ):
        return self.fetch_videos( YoutubeClient.BASE_STANDARD_URL, feed_time=self.settings[ "feed_time" ], region_id=self.settings[ "region_id" ] )

    def top_rated( self ):
        return self.fetch_videos( YoutubeClient.BASE_STANDARD_URL, feed_time=self.settings[ "feed_time" ], region_id=self.settings[ "region_id" ] )

    def recently_featured( self ):
        return self.fetch_videos( YoutubeClient.BASE_STANDARD_URL, region_id=self.settings[ "region_id" ] )

    def watch_on_mobile( self ):
        return self.fetch_videos( YoutubeClient.BASE_STANDARD_URL )

    def top_favorites( self ):
        return self.fetch_videos( YoutubeClient.BASE_STANDARD_URL, feed_time=self.settings[ "feed_time" ], region_id=self.settings[ "region_id" ] )

    def most_discussed( self ):
        return self.fetch_videos( YoutubeClient.BASE_STANDARD_URL, feed_time=self.settings[ "feed_time" ], region_id=self.settings[ "region_id" ] )

    def most_linked( self ):
        return self.fetch_videos( YoutubeClient.BASE_STANDARD_URL, feed_time=self.settings[ "feed_time" ], region_id=self.settings[ "region_id" ] )

    def most_responded( self ):
        return self.fetch_videos( YoutubeClient.BASE_STANDARD_URL, feed_time=self.settings[ "feed_time" ], region_id=self.settings[ "region_id" ] )

    def most_recent( self ):
        return self.fetch_videos( YoutubeClient.BASE_STANDARD_URL, region_id=self.settings[ "region_id" ] )

    def related( self ):
        return self.fetch_videos( YoutubeClient.BASE_RELATED_URL )

    def search_videos( self ):
        # get the query to search for from the user
        self.args.vq = self._get_keyboard( heading=xbmc.getLocalizedString( 30906 ) )
        # if blank or the user cancelled the keyboard, return
        if ( not self.args.vq ): return False, 0
        # we need to set the title to our query
        self.args.title = self.args.vq
        # we need to set the function to videos
        self.args.category = "videos"
        return self.fetch_videos( YoutubeClient.BASE_SEARCH_URL )

    def search_users( self ):
        # get the username to search for from the user
        self.args.username = self._get_keyboard( heading=xbmc.getLocalizedString( 30907 ) )
        # if blank or the user cancelled the keyboard, return
        if ( not self.args.username ): return False, 0
        # we need to set the title to our query
        self.args.title = self.args.username
        # we need to set the function to users
        self.args.category = "users"
        ok, total = self.fetch_videos( YoutubeClient.BASE_USERS_URL )
        # if exact match was found return results
        if ( total ): return ok, total
        # if no exact match found we search using regular search engine
        # we need to set the function to videos
        self.args.category = "videos"
        # set the search query to the username
        self.args.vq = self.args.username
        # empty username
        self.args.username = ""
        return self.fetch_videos( YoutubeClient.BASE_SEARCH_URL )

    def users__uploads( self ):
        # set author to user name
        self.args.username = self.settings[ "username" ]
        return self.fetch_videos( YoutubeClient.BASE_USERS_URL )

    def users__favorites( self ):
        # set author to user name
        self.args.username = self.settings[ "username" ]
        return self.fetch_videos( YoutubeClient.BASE_USERS_URL )

    def all_videos( self ):
        # we need to set the function to videos
        self.args.category = "videos"
        return self.fetch_videos( YoutubeClient.BASE_SEARCH_URL )

    def videos( self ):
        # we end up here for pages 2 and on
        return self.fetch_videos( YoutubeClient.BASE_SEARCH_URL )

    def users( self ):
        # we end up here for pages 2 and on
        return self.fetch_videos( YoutubeClient.BASE_USERS_URL )

    def fetch_videos( self, url, feed_time="", region_id="" ):
        # Youtube client
        client = YoutubeClient( url )
        # starting video
        start_index = ( self.args.page - 1 ) * self.settings[ "perpage" ] + 1
        # fetch the videos
        exec 'feeds = client.%s( format=5, orderby=self.args.orderby, related=self.args.related, region_id=region_id, time=feed_time, racy=self.settings[ "include_racy" ], start__index=start_index, max__results=self.settings[ "perpage" ], vq=self.args.vq, author=self.args.username )' % ( self.args.category, )
        # calculate total pages
        pages = self._get_total_pages( int( feeds[ "feed" ][ "openSearch$totalResults" ][ "$t" ] ) )
        # if this was a search and there is a spelling correction get the correction
        spell_vq = ""
        if ( url == YoutubeClient.BASE_SEARCH_URL and self.args.page == 1 ):
            spell_vq = self._get_spellcorrection( feeds["feed"][ "link" ], feeds[ "encoding" ] )
        # if there are results
        if ( pages or spell_vq ):
            return self._fill_media_list( True, feeds[ "feed" ].get( "entry", [] ), self.args.page, pages, self.settings[ "perpage" ], int( feeds[ "feed" ][ "openSearch$totalResults" ][ "$t" ] ), feeds["encoding"], spell_vq )
        #else return failed
        return False, 0

    def _get_spellcorrection( self, links, encoding ):
        # we need to unquote the spelling correction url
        # initialize the result
        vq = ""
        # enumerate through the links to find a spelling correction url
        for link in links:
            # if we find one, we only need the corrected search phrase
            if ( "spellcorrection" in link[ "rel" ] ):
                # set url using this hack to clean the result (exec is a hack for unescaping \u#### characters)
                exec 'url = u"%s"' % ( unicode( link[ "href" ], encoding ), )
                # find the start of the corrected search phrase
                vq_start = url.find( "vq=" ) + 3
                # find the end of the corrected search phrase
                vq_end = url.find( "&", vq_start )
                # unquote the corrected search phrase
                vq = unquote_plus( url[ vq_start : vq_end ] )
                # no need to continue
                break
        return vq

    def _get_total_pages( self, total ):
        # calculate the total number of pages
        pages = int( total / self.settings[ "perpage" ] ) + ( total % self.settings[ "perpage" ] > 0 )
        return pages

    def _fill_media_list( self, ok, videos, page, pages=1, perpage=1, total=1, encoding="utf-8", spell_vq="" ):
        try:
            # calculate total items including previous, next and spelling folders
            total_items = len( videos ) + ( page < pages ) + ( page > 1 ) + ( spell_vq != "" and len( videos ) )
            # if ok (always is for now) fill directory
            if ( ok ):
                # if this was a search and there is a correction
                if ( spell_vq ):
                    # set the correct query
                    username = ( "", spell_vq, )[ self.args.issearch == 2 ]
                    vq = ( "", spell_vq, )[ self.args.issearch == 1 ]
                    # create the callback url
                    url = '%s?title=%s&category=%s&page=%d&vq=%s&username=%s&orderby=%s&related=%s&issearch=%d&update_listing=%d' % ( sys.argv[ 0 ], repr( self.args.title ), repr( "videos" ), 1, repr( vq ), repr( username ), repr( self.args.orderby ), repr( self.args.related ), self.args.issearch, True, )
                    # TODO: get rid of self.BASE_PLUGIN_THUMBNAIL_PATH
                    # we set the thumb so XBMC does not try and cache the next pictures
                    thumbnail = os.path.join( self.BASE_PLUGIN_THUMBNAIL_PATH, "spell_page.png" )
                    # set the default icon
                    icon = "DefaultFolderBig.png"
                    # only need to add label and icon, setInfo() and addSortMethod() takes care of label2
                    listitem=xbmcgui.ListItem( label="%s: %s" % ( xbmc.getLocalizedString( 30911 ), spell_vq, ), iconImage=icon, thumbnailImage=thumbnail )
                    # add the folder item to our media list
                    ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=total_items + ( len( videos ) == 0 ) )
                # if there is more than one page and we are not on the last page, we add our next page folder
                if ( page < pages ):
                    # calculate the starting video
                    startno = page * perpage + 1
                    # calculate the ending video
                    endno = startno + perpage - 1
                    # if there are fewer videos than per_page set endno to total
                    if ( endno > total ):
                        endno = total
                    # create the callback url
                    url = '%s?title=%s&category=%s&page=%d&vq=%s&username=%s&orderby=%s&issearch=0&related=%s&update_listing=%d' % ( sys.argv[ 0 ], repr( self.args.title ), repr( self.args.category ), page + 1, repr( self.args.vq ), repr( self.args.username ), repr( self.args.orderby ), repr( self.args.related ), True, )
                    # TODO: get rid of self.BASE_PLUGIN_THUMBNAIL_PATH
                    # we set the thumb so XBMC does not try and cache the next pictures
                    thumbnail = os.path.join( self.BASE_PLUGIN_THUMBNAIL_PATH, "next.png" )
                    # set the default icon
                    icon = "DefaultFolderBig.png"
                    # only need to add label and icon, setInfo() and addSortMethod() takes care of label2
                    listitem=xbmcgui.ListItem( label="%s (%d-%d)" % ( xbmc.getLocalizedString( 3 ), startno, endno, ), iconImage=icon, thumbnailImage=thumbnail )
                    # add the folder item to our media list
                    ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=total_items )
                # if we are on page 2 or more, we add our previous page folder
                if ( page > 1 ):
                    # calculate the starting video
                    startno = ( page - 2 ) * perpage + 1
                    # calculate the ending video
                    endno = startno + perpage - 1
                    # create the callback url
                    url = '%s?title=%s&category=%s&page=%d&vq=%s&username=%s&orderby=%s&related=%s&issearch=0&update_listing=%d' % ( sys.argv[ 0 ], repr( self.args.title ), repr( self.args.category ), page - 1, repr( self.args.vq ), repr( self.args.username ), repr( self.args.orderby ), repr( self.args.related ), True, )
                    # TODO: get rid of self.BASE_PLUGIN_THUMBNAIL_PATH
                    # we set the thumb so XBMC does not try and cache the previous pictures
                    thumbnail = os.path.join( self.BASE_PLUGIN_THUMBNAIL_PATH, "previous.png" )
                    # set the default icon
                    icon = "DefaultFolderBig.png"
                    # only need to add label and icon, setInfo() and addSortMethod() takes care of label2
                    listitem=xbmcgui.ListItem( label="%s (%d-%d)" % ( xbmc.getLocalizedString( 3 ), startno, endno, ), iconImage=icon, thumbnailImage=thumbnail )
                    # add the folder item to our media list
                    ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=total_items )
                # set our thumbnail for queries
                self.query_thumbnail = videos[ 0 ][ "media$group" ][ "media$thumbnail" ][ -1 ][ "url" ]
                # enumerate through the list of pictures and add the item to the media list
                for video in videos:
                    # only add videos with an embeddable video
                    if ( video[ "media$group" ].has_key( "media$content" ) ):
                        # create the title, we use video title and author (exec is a hack for unescaping \u#### characters)
                        exec 'title = u"%s"' % ( unicode( video[ "title" ][ "$t" ].replace( '"', '\\"' ), encoding, "replace" ), )
                        # set the director with author (exec is a hack for unescaping \u#### characters)
                        exec 'director = u"%s"' % ( unicode( video[ "author" ][ 0 ][ "name" ][ "$t" ].replace( '"', '\\"' ), encoding, "replace" ), )
                        # thumbnail url
                        thumbnail_url = video[ "media$group" ][ "media$thumbnail" ][ -1 ][ "url" ]
                        # plot
                        plot = xbmc.getLocalizedString( 30904 )
                        if ( "media$description" in video[ "media$group" ] ):
                            # we need to replace \n and \r as it messes up our exec hack (exec is a hack for unescaping \u#### characters)
                            exec 'plot = u"%s"' % ( unicode( video[ "media$group" ][ "media$description" ][ "$t" ].replace( '"', '\\"' ).replace( "\n", "\\n" ).replace( "\r", "\\r" ), encoding, "replace" ), )
                        # format runtime as 00:00
                        runtime = int( video[ "media$group" ][ "yt$duration" ][ "seconds" ] )
                        # video runtime
                        if ( runtime ):
                            runtime = "%02d:%02d" % ( int( runtime / 60 ), runtime % 60, )
                        else:
                            runtime = ""
                        # viewer rating
                        try:
                            rating = float( video[ "gd$rating" ][ "average" ] )
                        except:
                            rating = 0.0
                        # times viewed
                        try:
                            count = int( video[ "yt$statistics" ][ "viewCount" ] )
                        except:
                            count = 0
                        # genre
                        genre = video[ "media$group" ][ "media$category" ][ 0 ][ "$t" ]
                        # updated date
                        date = "%s-%s-%s" % ( video[ "updated" ][ "$t" ][ 8 : 10 ], video[ "updated" ][ "$t" ][ 5 : 7 ], video[ "updated" ][ "$t" ][ : 4 ], )
                        # video url
                        exec 'video_url = u"%s"' % ( unicode( video[ "media$group" ][ "media$player" ][ 0 ][ "url" ], encoding ), )
                        # construct our url
                        url = "%s?category='play_video'&video_url=%s&releated=%s&update_listing=%d" % ( sys.argv[ 0 ], repr( quote_plus( video_url ) ), repr( video[ "id" ][ "$t" ].split( "/" )[ -1 ] ), False, )
                        # set the default icon
                        icon = "DefaultVideo.png"
                        # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
                        listitem=xbmcgui.ListItem( label=title, iconImage=icon, thumbnailImage=thumbnail_url )
                        # add the different infolabels we want to sort by
                        listitem.setInfo( type="Video", infoLabels={ "Title": title, "Director": director, "Duration": runtime, "Plot": plot, "Rating": rating, "Genre": genre, "Count": count, "Date": date } )
                        # set context menu items
                        action = "XBMC.ActivateWindow(%d,%s?title=%s&category='related'&page=1&vq=''&username=''&orderby='relevance'&related=%s&issearch=False&update_listing=False)" % ( xbmcgui.getCurrentWindowId(), sys.argv[ 0 ], repr( xbmc.getLocalizedString( 30968 ) ), repr( video[ "id" ][ "$t" ].split( "/" )[ -1 ] ), )
                        cm = [ ( xbmc.getLocalizedString( 30500 ), action, ) ]
                        # if download path set, add download item
                        if ( self.settings[ "download_path" ] != "" ):
                            action2 = "XBMC.RunPlugin(%s?category='download_video'&video_url=%s)" % ( sys.argv[ 0 ], repr( quote_plus( video_url ) ), )
                            cm += [ ( xbmc.getLocalizedString( 30501 ), action2, ) ]
                        try:
                            listitem.addContextMenuItems( cm )
                        except:
                            pass
                        # add the video to the media list
                        ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=False, totalItems=total_items )
                        # if user cancels, call raise to exit loop
                        if ( not ok ): raise
                if ( spell_vq ):
                    self.args.username = ( "", spell_vq, )[ self.args.issearch == 2 ]
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        # if successful and user did not cancel, add all the required sort methods
        if ( ok ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_PROGRAM_COUNT )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
            # set content
            xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="movies" )
            try:
                # set our plugin category
                xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=self.args.title )
            except:
                pass
        return ok, total_items

    def _get_keyboard( self, default="", heading="", hidden=False ):
        """ shows a keyboard and returns a value """
        keyboard = xbmc.Keyboard( default, heading, hidden )
        keyboard.doModal()
        if ( keyboard.isConfirmed() ):
            return unicode( keyboard.getText(), "utf-8" )
        return default
