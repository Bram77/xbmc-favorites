"""
    Category module: list of categories to use as folders
"""

# main imports
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin

from FlickrAPI.FlickrClient import FlickrClient


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base paths
    BASE_SKIN_THUMBNAIL_PATH = "/".join( [ "special://xbmc", xbmc.getSkinDir(), "media", sys.modules[ "__main__" ].__plugin__ ] )
    BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( os.getcwd(), "thumbnails" )
    BASE_PRESETS_PATH = "/".join( [ "special://profile", "plugin_data", "pictures", os.path.basename( os.getcwd() ) ] )

    def __init__( self ):
        # create the settings folder for presets
        self.make_presets_folders()
        # parse sys.argv
        self._parse_argv()
        # get user
        ok = self._get_user()
        # set the main default categories
        if ( ok ):
            ok = self._get_root_categories( sys.argv[ 2 ] == "" )
        # set cache to disc
        cacheToDisc = ( ok and not ( "category='presets_photos'" in sys.argv[ 2 ] or "category='presets_groups'" in sys.argv[ 2 ] ) )
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok, cacheToDisc=cacheToDisc )

    def make_presets_folders( self ):
        if ( not os.path.isdir( xbmc.translatePath( self.BASE_PRESETS_PATH ) ) ):
            os.makedirs( xbmc.translatePath( self.BASE_PRESETS_PATH ) )

    def _parse_argv( self ):
        if ( not sys.argv[ 2 ] ):
            self.args = _Info( title="" )
        else:
            # call _Info() with our formatted argv to create the self.args object
            exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ).replace( "\\u0027", "'" ).replace( "\\u0022", '"' ).replace( "\\u0026", "&" ), )

    def _get_user( self ):
        try:
            self.user_id = ""
            self.user_nsid = ""
            # get the users id
            userid = xbmcplugin.getSetting( "user_id" )
            # if user did not edit settings, return
            if ( userid == "" ): return True
            # flickr client
            client = FlickrClient( True )
            # find the user Id of the person
            if ( "@" in userid ):
                user = client.flickr_people_findByEmail( find_email=userid )
            else:
                user = client.flickr_people_findByUsername( username=userid )
            # if user id is valid and no error occurred return True
            ok = user[ "stat" ] != "fail"
            # if successful, set our user id and nsid
            if ( ok ):
                self.user_id = user[ "user" ][ "id" ]
                self.user_nsid = user[ "user" ][ "nsid" ]
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        # if an error or an invalid id was entered, notify the user
        if ( not ok ):
            xbmcgui.Dialog().ok( xbmc.getLocalizedString( 30900 ), xbmc.getLocalizedString( 30901 ), xbmc.getLocalizedString( 30902 ) )
        return ok

    def _get_root_categories( self, root=True ):
        try:
            # default categories
            if ( root ):
                categories = (
                                    ( xbmc.getLocalizedString( 30950 ), "flickr_photosets_getList", True, "", "", 0, "", 0, ),
                                    ( xbmc.getLocalizedString( 30951 ), "flickr_photos_getRecent", False, "", "", 0, "", 0, ),
                                    ( xbmc.getLocalizedString( 30952 ), "flickr_people_getPublicPhotos", True, "", "", 0, "", 0, ),
                                    ( xbmc.getLocalizedString( 30953 ), "flickr_interestingness_getList", False, "", "", 0, "", 0, ),
                                    ( xbmc.getLocalizedString( 30954 ), "flickr_favorites_getPublicList", True, "", "", 0, "", 0, ),
                                    ( xbmc.getLocalizedString( 30955 ), "flickr_photos_getContactsPublicPhotos", True, "", "", 0, "", 0, ),
                                    ( xbmc.getLocalizedString( 30956 ), "flickr_people_getPublicGroups", True, "", "", 0, "", 0, ),
                                    ( xbmc.getLocalizedString( 30959 ), "presets_groups", False, "", "", 0, "", 0, ),
                                    ( xbmc.getLocalizedString( 30960 ), "presets_photos", False, "", "", 0, "", 0, ),
                                    )
            # photo preset category
            elif ( "category='presets_photos'" in sys.argv[ 2 ] ):
                categories = self.get_presets()
            # group preset category
            elif ( "category='presets_groups'" in sys.argv[ 2 ] ):
                categories = self.get_presets( True )
            # fill media list
            ok = self._fill_media_list( categories )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        return ok

    def get_presets( self, ptype=False ):
        # we add time to the url, so it is always unique
        import time
        # set category
        category = ( "photos", "groups", )[ ptype ]
        # set the proper preset path
        preset_path = "/".join( [ self.BASE_PRESETS_PATH, category ] )
        # initialize our category tuple
        categories = ()
        # add our new search item
        if ( ptype ):
            categories += ( ( xbmc.getLocalizedString( 30957 ), "flickr_groups_search", False, "", "", 1, "", time.time(), ), )
        else:
            categories += ( ( xbmc.getLocalizedString( 30958 ), "flickr_photos_search", False, "", "", 2, "", time.time(), ), )
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
                # set photo query and group query to empty
                pq = gq = u""
                # set thumbnail
                thumbnail = query.split( " | " )[ 1 ].encode( "utf-8" )
                # if this is the group presets set group query else set photo query
                if ( ptype ):
                    gq = query.split( " | " )[ 0 ].encode( "utf-8" )
                else:
                    pq = query.split( " | " )[ 0 ].encode( "utf-8" )
                # add preset to our dictionary
                categories += ( ( query.split( " | " )[ 0 ].encode( "utf-8" ), categories[ 0 ][ 1 ], False, pq, gq, 0, thumbnail, 0, ), )
            except:
                # oops print error message
                print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
        return categories

    def _fill_media_list( self, categories ):
        try:
            ok = True
            # enumerate through the list of categories and add the item to the media list
            for ( ltitle, method, userid_required, pq, gq, issearch, thumbnail, time, ) in categories:
                # if a user id is required for category and none supplied, skip category
                if ( userid_required and self.user_id == "" ): continue
                # set the callback url with all parameters
                url = '%s?title=%s&category=%s&userid=%s&usernsid=%s&photosetid=""&photoid=""&groupid=""&primary=""&secret=""&server=""&photos=0&page=1&prevpage=0&pq=%s&gq=%s&issearch=%d&update_listing=%d&time=%d' % ( sys.argv[ 0 ], repr( ltitle ), repr( method ), repr( self.user_id ), repr( self.user_nsid ), repr( pq ), repr( gq ), issearch, False, time, )
                # check for a valid custom thumbnail for the current method
                thumbnail = thumbnail or self._get_thumbnail( method )
                # set the default icon
                icon = "defaultfolderBig.png"
                # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
                listitem=xbmcgui.ListItem( ltitle, iconImage=icon, thumbnailImage=thumbnail )
                # set special properties
                listitem.setProperty( "IsFolder", "true" )
                listitem.setProperty( "IsPictureFolder", "true" )
                # add the item to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=len( categories ) )
                # if user cancels, call raise to exit loop
                if ( not ok ): raise
            # we do not want to sort queries list
            if ( "category='presets_photos'" in sys.argv[ 2 ] or "category='presets_groups'" in sys.argv[ 2 ] ):
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
                try:
                    # set our plugin category
                    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=self.args.title )
                    # set our fanart from user setting
                    if ( self.settings[ "fanart_image" ] ):
                        xbmcplugin.setPluginFanart( handle=int( sys.argv[ 1 ] ), image=self.settings[ "fanart_image" ], color1=self.settings[ "fanart_color1" ], color2=self.settings[ "fanart_color2" ], color3=self.settings[ "fanart_color3" ] )
                except:
                    pass
        except:
            # user cancelled dialog or an error occurred
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        return ok

    def _get_thumbnail( self, method ):
        # create the full thumbnail path for skins directory
        thumbnail = "/".join( [ self.BASE_SKIN_THUMBNAIL_PATH, method + ".png" ] )
        # use a plugin custom thumbnail if a custom skin thumbnail does not exists
        if ( not os.path.isfile( thumbnail ) ):
            # create the full thumbnail path for plugin directory
            thumbnail = os.path.join( self.BASE_PLUGIN_THUMBNAIL_PATH, method + ".png" )
            # use a default thumbnail if a custom thumbnail does not exists
            if ( not os.path.isfile( thumbnail ) ):
                thumbnail = "DefaultFolderBig.png"
        return thumbnail
