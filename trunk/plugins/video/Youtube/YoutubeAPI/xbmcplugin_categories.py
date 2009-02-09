"""
    Category module: list of categories to use as folders
"""

# main imports
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base paths
    BASE_SKIN_THUMBNAIL_PATH = "/".join( [ "special://xbmc", "skin", xbmc.getSkinDir(), "media", sys.modules[ "__main__" ].__plugin__ ] )
    BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( os.getcwd(), "thumbnails" )
    BASE_PRESETS_PATH = "/".join( [ "special://profile", "plugin_data", "video", os.path.basename( os.getcwd().replace( ";", "" ) ) ] )

    def __init__( self ):
        # create the settings folder for presets
        self.make_presets_folders()
        # parse sys.argv
        self._parse_argv()
        # set username
        self.username = xbmcplugin.getSetting( "username" )
        if ( not sys.argv[ 2 ] ):
            self.get_categories()
        else:
            self.get_categories( False )

    def make_presets_folders( self ):
        if ( not os.path.isdir( xbmc.translatePath( self.BASE_PRESETS_PATH ) ) ):
            os.makedirs( xbmc.translatePath( self.BASE_PRESETS_PATH ) )

    def _parse_argv( self ):
        if ( not sys.argv[ 2 ] ):
            self.args = _Info( title="" )
        else:
            # call _Info() with our formatted argv to create the self.args object
            exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ).replace( "\\u0027", "'" ).replace( "\\u0022", '"' ).replace( "\\u0026", "&" ), )

    def get_categories( self, root=True ):
        try:
            # default categories
            if ( root ):
                categories = (
                                        #( xbmc.getLocalizedString( 30950 ), "all_videos", "", "", True, "updated", 0, "", False, "", ),
                                        ( xbmc.getLocalizedString( 30951 ), "most_viewed", "", "", True, "viewCount", 0, "", False, 0, ),
                                        ( xbmc.getLocalizedString( 30952 ), "presets_videos", "", "", True, "updated", 0, "", False, 0, ),
                                        ( xbmc.getLocalizedString( 30953 ), "presets_users", "", "", True, "updated", 0, "", False, 0, ),
                                        ( xbmc.getLocalizedString( 30954 ), "recently_featured", "", "", True, "updated", 0, "", False, 0, ),
                                        ( xbmc.getLocalizedString( 30957 ), "top_rated", "", "", True, "rating", 0, "", False, 0, ),
                                        #( xbmc.getLocalizedString( 30958 ), "watch_on_mobile", "", "", True, "updated", 0, "", False, "", ),
                                        #( xbmc.getLocalizedString( 30959 ), "play_random_videos", "", "", False, "relevance", 0, "", False, "", ),
                                        ( xbmc.getLocalizedString( 30960 ), "play_video_by_id", "", "", False, "relevance", 0, "", False, 0, ),
                                        ( xbmc.getLocalizedString( 30961 ), "users__uploads", "", "", True, "updated", 0, "", True, 0, ),
                                        ( xbmc.getLocalizedString( 30962 ), "users__favorites", "", "", True, "updated", 0, "", True, 0, ),
                                        ( xbmc.getLocalizedString( 30963 ), "top_favorites", "", "", True, "relevance", 0, "", False, 0, ),
                                        ( xbmc.getLocalizedString( 30964 ), "most_discussed", "", "", True, "relevance", 0, "", False, 0, ),
                                        ( xbmc.getLocalizedString( 30965 ), "most_linked", "", "", True, "relevance", 0, "", False, 0, ),
                                        ( xbmc.getLocalizedString( 30966 ), "most_responded", "", "", True, "relevance", 0, "", False, 0, ),
                                        ( xbmc.getLocalizedString( 30967 ), "most_recent", "", "", True, "relevance", 0, "", False, 0, ),
                                    )
            # search preset category
            elif ( "category='presets_videos'" in sys.argv[ 2 ] ):
                categories = self.get_presets()
            # user preset category
            elif ( "category='presets_users'" in sys.argv[ 2 ] ):
                categories = self.get_presets( True )
            # fill media list
            ok = self._fill_media_list( categories )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        # set cache to disc
        cacheToDisc = ( ok and not ( "category='presets_videos'" in sys.argv[ 2 ] or "category='presets_users'" in sys.argv[ 2 ] ) )
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok, cacheToDisc=cacheToDisc )

    def get_presets( self, ptype=False ):
        # we add time to the url, so it is always unique
        import time
        # set the proper preset path
        preset_path = "/".join( [ self.BASE_PRESETS_PATH, ( "videos", "users", )[ ptype ] ] )
        # initialize our category tuple
        categories = ()
        # add our new search item
        if ( ptype ):
            categories += ( ( xbmc.getLocalizedString( 30955 ), "search_users", "", "", True, "updated", 1, "", False, time.time(), ), )
        else:
            categories += ( ( xbmc.getLocalizedString( 30956 ), "search_videos", "", "", True, "updated", 2, "", False, time.time(), ), )
        # fetch saved presets
        try:
            # grab a file object
            fileobject = open( preset_path, "r" )
            # read the queries
            presets = eval( fileobject.read() )
            # close file object
            fileobject.close()
            # sort items
            presets.sort()
        except:
            # no presets found
            presets = []
        # enumerate through the presets list and read the query
        for query in presets:
            try:
                # set video query and user query to empty
                vq = username = u""
                # set thumbnail
                thumbnail = query.split( " | " )[ 1 ].encode( "utf-8" )
                # if this is the user presets set username else set video query
                if ( ptype ):
                    username = query.split( " | " )[ 0 ].encode( "utf-8" )
                else:
                    vq = query.split( " | " )[ 0 ].encode( "utf-8" )
                # add preset to our dictionary
                categories += ( ( query.split( " | " )[ 0 ].encode( "utf-8" ), "videos", vq, username, True, "updated", 0, thumbnail, False, 0, ), )
            except:
                # oops print error message
                print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
        return categories

    def _fill_media_list( self, categories ):
        try:
            ok = True
            # enumerate through the tuple of categories and add the item to the media list
            for ( ltitle, method, vq, username, isfolder, orderby, issearch, thumbnail, user_required, time, ) in categories:
                # if a username is required for category and none supplied, skip category
                if ( user_required and self.username == "" ): continue
                # set the callback url
                url = '%s?title=%s&category=%s&page=1&vq=%s&username=%s&orderby=%s&related=""&issearch=%d&update_listing=%d&time=%d' % ( sys.argv[ 0 ], repr( ltitle ), repr( method ), repr( vq ), repr( username ), repr( orderby ), issearch, False, time, )
                # check for a valid custom thumbnail for the current category
                thumbnail = thumbnail or self._get_thumbnail( method )
                # set the default icon
                icon = "DefaultFolderBig.png"
                # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
                listitem=xbmcgui.ListItem( ltitle, iconImage=icon, thumbnailImage=thumbnail )
                # add the item to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=isfolder, totalItems=len( categories ) )
                # if user cancels, call raise to exit loop
                if ( not ok ): raise
            # we do not want to sort queries list
            if ( "category='presets_videos'" in sys.argv[ 2 ] or "category='presets_users'" in sys.argv[ 2 ] ):
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
                try:
                    # set our plugin category
                    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=self.args.title )
                    # set our fanart from user setting
                    #if ( self.settings[ "fanart_image" ] ):
                    #    xbmcplugin.setPluginFanart( handle=int( sys.argv[ 1 ] ), image=self.settings[ "fanart_image" ], color1=self.settings[ "fanart_color1" ], color2=self.settings[ "fanart_color2" ], color3=self.settings[ "fanart_color3" ] )
                except:
                    pass
        except:
            # user cancelled dialog or an error occurred
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        return ok

    def _get_thumbnail( self, title ):
        # create the full thumbnail path for skins directory
        thumbnail = "/".join( [ self.BASE_SKIN_THUMBNAIL_PATH, title.replace( " ", "-" ).lower() + ".png" ] )
        # use a plugin custom thumbnail if a custom skin thumbnail does not exists
        if ( not os.path.isfile( thumbnail ) ):
            # create the full thumbnail path for plugin directory
            thumbnail = os.path.join( self.BASE_PLUGIN_THUMBNAIL_PATH, title.replace( " ", "-" ).lower() + ".png" )
            # use a default thumbnail if a custom thumbnail does not exists
            if ( not os.path.isfile( thumbnail ) ):
                thumbnail = "DefaultFolderBig.png"
        return thumbnail
