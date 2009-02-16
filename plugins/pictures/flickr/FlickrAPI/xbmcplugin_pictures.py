"""
    Pictures module: fetches a list of pictures for a specific category
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
    # base urls
    BASE_THUMBNAIL_URL = u"http://farm%s.static.flickr.com/%s/%s_%s_m.jpg" 
    BASE_ORIGINAL_PIC_URL = u"http://farm%s.static.flickr.com/%s/%s_%s_o.%s"

    # base paths
    BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( os.getcwd(), "thumbnails" )
    BASE_AUTH_FILE_PATH = "/".join( [ "special://profile", "plugin_data", "pictures", os.path.basename( os.getcwd() ), "authfile.txt" ] )
    BASE_PRESETS_PATH = "/".join( [ "special://profile", "plugin_data", "pictures", os.path.basename( os.getcwd() ) ] )

    # flickr client
    client = FlickrClient( True, True )

    def __init__( self ):
        self._get_settings()
        self._get_authkey()
        self._parse_argv()
        self._get_items()

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "privacy_filter" ] = ( 1, 2, 3, 4, 5, )[ int( xbmcplugin.getSetting( "privacy_filter" ) ) ]
        self.settings[ "safe_search" ] = ( 1, 2, 3, )[ int( xbmcplugin.getSetting( "safe_search" ) ) ]
        self.settings[ "perpage" ] = ( 10, 15, 20, 25, 30, 40, 50, 75, 100, )[ int( xbmcplugin.getSetting( "perpage" ) ) ]
        self.settings[ "full_details" ] = xbmcplugin.getSetting( "full_details" ) == "true"
        self.settings[ "advanced_photos_query" ] = False#xbmcplugin.getSetting( "advanced_photos_query" ) == "true"
        """
        self.settings[ "photos_query_userid" ] = xbmcplugin.getSetting( "photos_query_userid" )
        self.settings[ "photos_query_tags" ] = xbmcplugin.getSetting( "photos_query_tags" )
        self.settings[ "photos_query_tag_mode" ] = ( "Any", "All", )[ int( xbmcplugin.getSetting( "photos_query_tag_mode" ) ) ]
        self.settings[ "photos_query_text" ] = xbmcplugin.getSetting( "photos_query_text" )
        self.settings[ "photos_query_content" ] = ( 1, 2, 3, 4, 5, 6, 7, )[ int( xbmcplugin.getSetting( "photos_query_content" ) ) ]
        self.settings[ "photos_query_machine_tags" ] = xbmcplugin.getSetting( "photos_query_machine_tags" )
        self.settings[ "photos_query_machine_tag_mode" ] = ( "Any", "All", )[ int( xbmcplugin.getSetting( "photos_query_machine_tag_mode" ) ) ]
        self.settings[ "photos_query_groupid" ] = xbmcplugin.getSetting( "photos_query_groupid" )
        """
        self.settings[ "saved_searches" ] = ( 10, 20, 30, 40, )[ int( xbmcplugin.getSetting( "saved_searches" ) ) ]

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )

    def _get_authkey( self ):
        self.authkey = ""
        # we only need to authenticate one time (TODO: verify this)
        if ( os.path.isfile( self.BASE_AUTH_FILE_PATH ) ):
            # grab a file object
            fileobject = open( self.BASE_AUTH_FILE_PATH, "r" )
            # read the query
            self.authkey = fileobject.read().strip()
            # close # file object
            fileobject.close()

    def _get_items( self ):
        try:
            # get the pictures or subcategories
            exec "items = self.%s()" % ( self.args.category, )
            # fill the media list
            if ( items is None ): raise
            ok, total = self._fill_media_list( items )
            # if there were photos and this was a search ask to save result as a preset
            if ( ok and total and self.args.issearch ):
                self.save_as_preset()
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok, updateListing=self.args.update_listing )#, cacheToDisc=not self.args.issearch )

    def _get_url( self, **kwargs ):
        # we add all the parameters for consitancy
        url = u'%s?' % sys.argv[ 0 ]
        url += u'userid=%s' % repr( kwargs[ "userid" ] )
        url += u'&usernsid=%s' % repr( kwargs[ "usernsid" ] )
        url += u'&photosetid=%s' % repr( kwargs[ "photosetid" ] )
        url += u'&photoid=%s' % repr( kwargs[ "photoid" ] )
        url += u'&groupid=%s' % repr( kwargs[ "groupid" ] )
        url += u'&title=%s' % repr( kwargs[ "title" ] )
        url += u'&category=%s' % repr( kwargs[ "category" ] )
        url += u'&primary=%s' % repr( kwargs[ "primary" ] )
        url += u'&secret=%s' % repr( kwargs[ "secret" ] )
        url += u'&server=%s' % repr( kwargs[ "server" ] )
        url += u'&photos=%d' % kwargs[ "photos" ]
        url += u'&page=%d' % kwargs[ "page" ]
        url += u'&prevpage=%d' % kwargs[ "prevpage" ]
        url += u'&pq=%s' % repr( self.args.pq )
        url += u'&gq=%s' % repr( self.args.gq )
        url += u'&issearch=%d' % self.args.issearch
        url += u'&update_listing=%d' % kwargs[ "update_listing" ]
        return url

    def flickr_photosets_getList( self ):
        items = []
        photosets = self.client.flickr_photosets_getList( user_id=self.args.usernsid, auth_token=self.authkey )
        if ( photosets[ "stat" ] == "ok" ):
            for photoset in photosets[ "photosets" ][ "photoset" ]:
                # if full details leave thumbnail blank, so a thumb will be created(sloooooooow)
                #if ( self.settings[ "full_details" ] ):
                #thumbnail = ""
                #else:
                thumbnail = "DefaultFolderBig.png"
                # set the default icon
                icon = "DefaultFolderBig.png"
                # hack to correct \u0000 characters, TODO: find why unicode() isn't working
                exec 'title=u"%s (%s)"' % ( photoset[ "title" ][ "_content" ].replace( '"', '\\"' ), photoset[ "photos" ], )
                exec 'description=u"%s"' % ( photoset[ "description" ][ "_content" ].replace( '"', '\\"' ), )
                # create the callback url
                url = self._get_url( title=title, userid=self.args.userid, usernsid=self.args.usernsid, photosetid=photoset[ "id" ], photoid="", groupid="", category="flickr_photosets_getPhotos", primary=photoset[ "primary" ], secret=photoset[ "secret" ], server=photoset[ "server" ], photos=int( photoset[ "photos" ] ), page=1, prevpage=0, update_listing=False )
                items += [ _Info( title=title, url=url, author="", description=description, icon=icon, thumbnail_url=thumbnail, isFolder=True ) ]
        return items

    def flickr_photos_getContactsPublicPhotos( self ):
        items = []
        if ( self.authkey ):
            contacts = self.client.flickr_photos_getContactsPhotos( user_id=self.args.usernsid, auth_token=self.authkey, count=100, single_photo=1, include_self=0 )
        else:
            contacts = self.client.flickr_photos_getContactsPublicPhotos( user_id=self.args.usernsid, auth_token=self.authkey, count=100, single_photo=1, include_self=0 )
        if ( contacts[ "stat" ] == "ok" ):
            for contact in contacts[ "photos" ][ "photo" ]:
                thumbnail_url = self.BASE_THUMBNAIL_URL % ( contact[ "farm" ], contact[ "server" ], contact[ "id" ], contact[ "secret" ], )
                # set the default icon
                icon = "DefaultFolderBig.png"
                # hack to correct \u0000 characters, TODO: find why unicode() isn't working
                exec 'title=u"%s"' % ( contact[ "username" ].replace( '"', '\\"' ), )
                exec 'description=u"%s"' % ( contact[ "title" ].replace( '"', '\\"' ), )
                # create the callback url
                url = self._get_url( title=self.args.title, userid=contact[ "owner" ], usernsid=contact[ "owner" ], photosetid="", photoid=contact[ "id" ], groupid="", category="flickr_people_getPublicPhotos", primary="", secret=contact[ "secret" ], server=contact[ "server" ], photos=0, page=1, prevpage=0, update_listing=False )
                items += [ _Info( title=title, author=title, description=description, url=url, icon=icon, thumbnail_url=thumbnail_url, isFolder=True ) ]
        return items

    def flickr_people_getPublicGroups( self ):
        items = []
        groups = self.client.flickr_people_getPublicGroups( user_id=self.args.usernsid, auth_token=self.authkey )
        if ( groups[ "stat" ] == "ok" ):
            for group in groups[ "groups" ][ "group" ]:
                # doesn't return much
                #info = self.client.flickr_groups_getInfo( group_id=group[ "nsid" ] )
                # if full details leave thumbnail blank, so a thumb will be created(sloooooooow)
                #if ( self.settings[ "full_details" ] ):
                #    thumbnail = ""
                #else:
                thumbnail = "DefaultFolderBig.png"
                # set the default icon
                icon = "DefaultFolderBig.png"
                # hack to correct \u0000 characters, TODO: find why unicode() isn't working
                exec 'title=u"%s"' % ( group[ "name" ].replace( '"', '\\"' ), )
                # create the callback url
                url = self._get_url( title=title, userid=self.args.userid, usernsid=self.args.usernsid, photosetid="", photoid="", groupid=group[ "nsid" ], category="flickr_groups_pools_getPhotos", primary="", secret="", server="", photos=0, page=1, prevpage=0, update_listing=False )
                items += [ _Info( title=title, author=title, description="", url=url, icon=icon, thumbnail_url=thumbnail, isFolder=True ) ]
        return items

    def flickr_photos_search( self ):
        if ( self.settings[ "advanced_photos_query" ] ):
            user_id = self.settings[ "photos_query_userid" ]
            if ( user_id ):
                # find the user Id of the person
                if ( "@" in user_id ):
                    info = self.client.flickr_people_findByEmail( find_email=user_id )
                else:
                    info = self.client.flickr_people_findByUsername( username=user_id )
                if ( info[ "stat" ] != "fail" ):
                    user_id = info[ "user" ][ "id" ]
            tags = self.settings[ "photos_query_tags" ]
            tag_mode = ( "", self.settings[ "photos_query_tag_mode" ] )[ tags != "" ]
            self.args.pq = self.settings[ "photos_query_text" ]
            content_type = self.settings[ "photos_query_content" ]
            machine_tags = self.settings[ "photos_query_machine_tags" ]
            machine_tag_mode = ( "", self.settings[ "photos_query_machine_tag_mode" ] )[ machine_tags != "" ]
            group_id = self.settings[ "photos_query_groupid" ]
        else:
            # empty advanced search variables for simple search
            user_id = ""
            tags = ""
            tag_mode = ""
            content_type = ""
            machine_tags = ""
            machine_tag_mode = ""
            group_id = ""
            # get the user input
            if ( self.args.pq == "" ):
                self.args.pq = self._get_keyboard( heading=xbmc.getLocalizedString( 30903 ) )
        # if keyboard was cancelled or no query entered return None (cancel)
        if ( self.args.pq == "" and not self.settings[ "advanced_photos_query" ] ): return None
        # we need to set the title to our query
        self.args.title = self.args.pq
        # perform the query
        items_dict = self.client.flickr_photos_search( text=self.args.pq, auth_token=self.authkey, per_page=self.settings[ "perpage" ], page=self.args.page, user_id=user_id, tags=tags, tag_mode=tag_mode, content_type=content_type, machine_tags=machine_tags, machine_tag_mode=machine_tag_mode, group_id=group_id, extras=u"date_upload,date_taken,owner_name,original_format" )
        return self._set_pictures( items_dict[ "stat" ] == "ok", items_dict[ "photos" ][ "photo" ], self.args.page, items_dict[ "photos" ][ "pages" ], items_dict[ "photos" ][ "perpage" ], items_dict[ "photos" ][ "total" ] )

    def flickr_groups_search( self ):
        #if ( self.settings[ "advanced_groups_query" ] ):
        #    text = xbmcplugin.getSetting( "groups_query_text" )
        #else:
        # get the user input
        if ( self.args.gq == "" ):
            self.args.gq = self._get_keyboard( heading=xbmc.getLocalizedString( 30904 ) )
        # if keyboard was cancelled or no query entered return None (cancel)
        if ( self.args.gq == "" ): return None
        items = []
        # perform the query
        groups = self.client.flickr_groups_search( text=self.args.gq, auth_token=self.authkey, per_page=self.settings[ "perpage" ], page=self.args.page )
        if ( groups[ "stat" ] == "ok" ):
            # get our previous and/or next page item
            items = self._get_pages( xbmc.getLocalizedString( 30905 ), groups[ "groups" ][ "page" ], groups[ "groups" ][ "pages" ], groups[ "groups" ][ "perpage" ], groups[ "groups" ][ "total" ] )

            self.query_thumbnail = "DefaultFolderBig.png"
            
            # enumerate through and add the group to our _Info object
            for group in groups[ "groups" ][ "group" ]:
                # doesn't return much
                #info = self.client.flickr_groups_getInfo( group_id=group[ "nsid" ] )
                # if full details leave thumbnail blank, so a thumb will be created(sloooooooow)
                #if ( self.settings[ "full_details" ] ):
                #    thumbnail = ""
                #else:
                thumbnail = "DefaultFolderBig.png"
                # set the default icon
                icon = "DefaultFolderBig.png"
                # hack to correct \u0000 characters, TODO: find why unicode() isn't working
                exec 'title=u"%s"' % ( group[ "name" ].replace( '"', '\\"' ), )
                # create the callback url
                url = self._get_url( title=title, userid=self.args.userid, usernsid=self.args.usernsid, photosetid="", photoid="", groupid=group[ "nsid" ], category="flickr_groups_pools_getPhotos", primary="", secret="", server="", photos=0, page=1, prevpage=0, update_listing=False )
                items += [ _Info( title=title, author=title, description="", url=url, icon=icon, thumbnail_url=thumbnail, isFolder=True ) ]
        return items

    def flickr_favorites_getPublicList( self ):
        if ( self.authkey ):
            items_dict = self.client.flickr_favorites_getList( user_id=self.args.userid, auth_token=self.authkey, per_page=self.settings[ "perpage" ], page=self.args.page, extras=u"date_upload,date_taken,owner_name,original_format" )
        else:
            items_dict = self.client.flickr_favorites_getPublicList( user_id=self.args.userid, auth_token=self.authkey, per_page=self.settings[ "perpage" ], page=self.args.page, extras=u"date_upload,date_taken,owner_name,original_format" )
        return self._set_pictures( items_dict[ "stat" ] == "ok", items_dict[ "photos" ][ "photo" ], self.args.page, items_dict[ "photos" ][ "pages" ], items_dict[ "photos" ][ "perpage" ], items_dict[ "photos" ][ "total" ] )

    def flickr_groups_pools_getPhotos( self ):
        items_dict = self.client.flickr_groups_pools_getPhotos( group_id=self.args.groupid, auth_token=self.authkey, per_page=self.settings[ "perpage" ], page=self.args.page, extras="date_upload,date_taken,owner_name,original_format" )
        return self._set_pictures( items_dict[ "stat" ] == "ok", items_dict[ "photos" ][ "photo" ], self.args.page, items_dict[ "photos" ][ "pages" ], items_dict[ "photos" ][ "perpage" ], items_dict[ "photos" ][ "total" ] )

    def flickr_interestingness_getList( self ):
        # TODO: get and use a date
        items_dict = self.client.flickr_interestingness_getList( auth_token=self.authkey, per_page=self.settings[ "perpage" ], page=self.args.page, extras=u"date_upload,date_taken,owner_name,original_format" )
        return self._set_pictures( items_dict[ "stat" ] == "ok", items_dict[ "photos" ][ "photo" ], self.args.page, items_dict[ "photos" ][ "pages" ], items_dict[ "photos" ][ "perpage" ], items_dict[ "photos" ][ "total" ] )

    def flickr_people_getPublicPhotos( self ):
        items_dict = self.client.flickr_people_getPublicPhotos( user_id=self.args.userid, auth_token=self.authkey, safe_search=self.settings[ "safe_search" ], per_page=self.settings[ "perpage" ], page=self.args.page, extras=u"date_upload,date_taken,owner_name,original_format" )
        return self._set_pictures( items_dict[ "stat" ] == "ok", items_dict[ "photos" ][ "photo" ], self.args.page, items_dict[ "photos" ][ "pages" ], items_dict[ "photos" ][ "perpage" ], items_dict[ "photos" ][ "total" ] )

    def flickr_photos_getRecent( self ):
        items_dict = self.client.flickr_photos_getRecent( user_id=self.args.userid, auth_token=self.authkey, per_page=self.settings[ "perpage" ], page=self.args.page, extras=u"date_upload,date_taken,owner_name,original_format" )
        return self._set_pictures( items_dict[ "stat" ] == "ok", items_dict[ "photos" ][ "photo" ], self.args.page, items_dict[ "photos" ][ "pages" ], items_dict[ "photos" ][ "perpage" ], items_dict[ "photos" ][ "total" ] )

    def flickr_photosets_getPhotos( self ):
        items_dict = self.client.flickr_photosets_getPhotos( photoset_id=self.args.photosetid, auth_token=self.authkey, privacy_filter=self.settings[ "privacy_filter" ], per_page=self.settings[ "perpage" ], page=self.args.page, extras=u"date_upload,date_taken,owner_name,original_format" )
        return self._set_pictures( items_dict[ "stat" ] == "ok", items_dict[ "photoset" ][ "photo" ], self.args.page, items_dict[ "photoset" ][ "pages" ], items_dict[ "photoset" ][ "per_page" ], items_dict[ "photoset" ][ "total" ] )

    def flickr_photos_getInfo( self ): # TODO: add secret
        items_dict = self.client.flickr_photos_getInfo( photo_id=self.args.photoid, auth_token=self.authkey )
        return self._set_pictures( items_dict[ "stat" ] == "ok", items_dict[ "photos" ][ "photo" ], self.args.page, items_dict[ "photos" ][ "pages" ], items_dict[ "photos" ][ "perpage" ], items_dict[ "photos" ][ "total" ] )

    def _set_pictures( self, ok, items_dict, page, pages, perpage, total ):
        try:
            items = []
            if ( ok ):
                # get our previous and/or next page items
                items = self._get_pages( xbmc.getLocalizedString( 30906 ), page, pages, perpage, total )
                # set our thumbnail for queries
                self.query_thumbnail = self.BASE_THUMBNAIL_URL % ( items_dict[ 0 ][ "farm" ], items_dict[ 0 ][ "server" ], items_dict[ 0 ][ "id" ], items_dict[ 0 ][ "secret" ], )
                # enumerate through the list of pictures and add the item to the media list
                for item in items_dict:
                    description = ""
                    if ( self.settings[ "full_details" ] ):
                        info = self.client.flickr_photos_getInfo( auth_token=self.authkey, photo_id=item[ "id" ], secret=item[ "secret" ] )
                        exec 'description=u"%s"' % ( info[ "photo" ][ "description" ][ "_content" ].replace( '"', '\\"' ).replace( '\n', '\\n' ).replace( '\r', '\\r' ), )
                    # create the thumbnail url and if no original format available, we set our url for something to view when clicked
                    url = thumbnail_url = self.BASE_THUMBNAIL_URL % ( item[ "farm" ], item[ "server" ], item[ "id" ], item[ "secret" ], )
                    # set the default icon
                    icon = "DefaultPicture.png"
                    # if this is a pro account and original format is available create a url to it
                    if ( "originalformat" in item ):
                        url = self.BASE_ORIGINAL_PIC_URL % ( item[ "farm" ], item[ "server" ], item[ "id" ], item[ "originalsecret" ], item[ "originalformat" ], )
                    # hack to correct \u0000 characters, TODO: find why unicode() isn't working
                    exec 'title=u"%s"' % ( ( item[ "title" ], item[ "ownername" ], )[ item[ "title" ] == "" ].replace( '"', '\\"' ), )
                    exec 'author=u"%s"' % ( item[ "ownername" ].replace( '"', '\\"' ), )
                    # add item to our _Info() object list
                    items += [ _Info( title=title, author=author, description=description, datetaken=item[ "datetaken" ], url=url, icon=icon, thumbnail_url=thumbnail_url, isFolder=False ) ]
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
        return items

    def _get_pages( self, title, page, pages, perpage, total ):
        page = int( page )
        pages = int( pages )
        perpage = int( perpage )
        total = int( total )
        items = []
        # if there is more than one page and we are not on the last page, we add our next page folder
        if ( int( page ) < int( pages ) ):
            # calculate the starting index
            start_index = page * perpage + 1
            # calculate the ending picture
            end_index = start_index + perpage - 1
            # if there are fewer pictures than per_page set end_index to total
            if ( end_index > total ):
                end_index = total
            # create the callback url
            url = self._get_url( title=self.args.title, userid=self.args.userid, usernsid=self.args.usernsid, photosetid=self.args.photosetid, photoid=self.args.photoid, groupid=self.args.groupid, category=self.args.category, primary=self.args.primary, secret=self.args.secret, server=self.args.server, photos=self.args.photos, page=page + 1, prevpage=page, pq=self.args.pq, gq=self.args.gq, issearch=0, update_listing=True )
            # TODO: set this without path, so the skin controls it
            # we set the thumb so XBMC does not try and cache the next pictures
            thumbnail_url = os.path.join( self.BASE_PLUGIN_THUMBNAIL_PATH, "next.png" )
            # set the default icon
            icon = "DefaultFolderBig.png"
            # add the folder item to our _Info() object list
            items += [ _Info( title="%s (%d-%d)" % ( title, start_index, end_index, ), url=url, icon=icon, thumbnail_url=thumbnail_url, isFolder=True ) ]
        # if we are on page 2 or more, we add our previous page folder
        if ( page > 1 ):
            # calculate the starting picture
            start_index = ( page - 2 ) * perpage + 1
            # calculate the ending picture
            end_index = start_index + perpage - 1
            # create the callback url
            url = self._get_url( title=self.args.title, userid=self.args.userid, usernsid=self.args.usernsid, photosetid=self.args.photosetid, photoid=self.args.photoid, groupid=self.args.groupid, category=self.args.category, primary=self.args.primary, secret=self.args.secret, server=self.args.server, photos=self.args.photos, page=page - 1, prevpage=page, pq=self.args.pq, gq=self.args.gq, issearch=0, update_listing=True )
            # TODO: set this without path, so the skin controls it
            # we set the thumb so XBMC does not try and cache the previous pictures
            thumbnail_url = os.path.join( self.BASE_PLUGIN_THUMBNAIL_PATH, "previous.png" )
            # set the default icon
            icon = "DefaultFolderBig.png"
            # add the folder item to our _Info() object list
            items += [ _Info( title=u"%s (%d-%d)" % ( title, start_index, end_index, ), url=url, icon=icon, thumbnail_url=thumbnail_url, isFolder=True ) ]
        return items

    def _fill_media_list( self, items ):
        try:
            ok = True
            # enumerate through the list of items and add the item to the media list
            for item in items:
                # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
                listitem=xbmcgui.ListItem( label=item.title, iconImage=item.icon, thumbnailImage=item.thumbnail_url )
                # TODO: add info and sort methods
                # add the different infolabels we want to sort by
                listitem.setInfo( type="Pictures", infoLabels={ "Title": item.title } )#, "Genre": self.args.title, "Duration": video.duration, "Date": video.date } )
                # we add additional properties and infolabels for pictures
                if ( not item.isFolder ):
                    listitem.setInfo( type="Pictures", infoLabels={ "Date": "%s-%s-%s" % ( item.datetaken[ 8 : 10 ], item.datetaken[ 5 : 7 ], item.datetaken[  : 4 ], ), } )#"Size": item[ "photo_size" ], "exif:exiftime": item[ "photo_datetime" ], "exif:resolution": "%d,%d" % ( item[ "photo_width" ], item[ "photo_height" ], ) } )
                    # skins display these with ListItem.Property(User)...
                    listitem.setProperty( "User", item.author )
                    listitem.setProperty( "Description", item.description )
                    listitem.setProperty( "DateTaken", item.datetaken )
                # add the item to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=item.url, listitem=listitem, isFolder=item.isFolder, totalItems=len( items ) )
                # if user cancels, call raise to exit loop
                if ( not ok ): raise
        except:
            # user cancelled dialog or an error occurred
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        # if successful and user did not cancel, add all the required sort methods
        if ( ok ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
            try:
                # set our plugin category
                xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=self.args.title )
            except:
                pass
        return ok, len( items )

    def _get_keyboard( self, default="", heading="", hidden=False ):
        """ shows a keyboard and returns a value """
        keyboard = xbmc.Keyboard( default, heading, hidden )
        keyboard.doModal()
        if ( keyboard.isConfirmed() ):
            return unicode( keyboard.getText(), "utf-8" )
        return default

    def save_as_preset( self ):
        # select correct query
        query = ( self.args.gq, self.args.pq, )[ self.args.issearch - 1 ]
        # set the proper preset path
        preset_path = "/".join( [ self.BASE_PRESETS_PATH, ( "groups", "photos", )[ self.args.issearch - 1 ] ] )
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

