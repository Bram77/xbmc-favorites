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
    BASE_SKIN_THUMBNAIL_PATH = os.path.join( "Q:\\skin", xbmc.getSkinDir(), "media", sys.modules[ "__main__" ].__plugin__ )
    BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( sys.modules[ "__main__" ].BASE_PATH, "thumbnails" )
    BASE_PRESETS_PATH = os.path.join( "P:\\plugin_data", "video", os.path.basename( os.getcwd().replace( ";", "" ) ), "presets" )

    def __init__( self ):
        self.make_presets_folder()
        if ( not sys.argv[ 2 ] ):
            self.get_categories()
        else:
            self.get_categories( False )

    def make_presets_folder( self ):
        if ( not os.path.isdir( xbmc.translatePath( self.BASE_PRESETS_PATH ) ) ):
            os.makedirs( xbmc.translatePath( self.BASE_PRESETS_PATH ) )

    def get_categories( self, root=True ):
        try:
            # initialize category list
            categories = []
            # default categories. 
            #TODO: consider localizing these
            if ( root ):
                category_dict = {
                                            "All Videos": ( "all_videos", "", True ),
                                            "Search Videos": ( "search_videos", "", True ),
                                            "Presets": ( "root_preset_videos", "", True ),
                                        }
            else:
                category_dict = self.get_presets()
            # enumerate through the category list and add the item to our categories list with id
            for key, value in category_dict.items():
                # add item to our _Info() object list
                categories += [ _Info( title=key, category=value[ 0 ], query=value[ 1 ], isFolder=value[ 2 ] ) ]
            # fill media list
            ok = self._fill_media_list( categories )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

    def get_presets( self ):
        category_dict = {}
        presets = os.listdir( self.BASE_PRESETS_PATH )
        for preset in presets:
            try:
                f = open( os.path.join( self.BASE_PRESETS_PATH, preset ), "r" )
                query = f.read()
                f.close()
                category_dict[ preset ] = ( "preset_videos", query, True, )
            except:
                pass
        return category_dict

    def _fill_media_list( self, categories ):
        try:
            ok = True
            # enumerate through the list of categories and add the item to the media list
            for category in categories:
                # set the callback url
                url = "%s?title=%s&category=%s&page=1&query=%s" % ( sys.argv[ 0 ], repr( category.title ), repr( category.category ), repr( category.query ), )
                # check for a valid custom thumbnail for the current category
                thumbnail = self._get_thumbnail( category.title )
                # set the default icon
                icon = "DefaultFolder.png"
                # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
                listitem=xbmcgui.ListItem( category.title, iconImage=icon, thumbnailImage=thumbnail )
                # add the item to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=category.isFolder, totalItems=len( categories ) )
                # if user cancels, call raise to exit loop
                if ( not ok ): raise
        except:
            # user cancelled dialog or an error occurred
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        return ok

    def _get_thumbnail( self, title ):
        # create the full thumbnail path for skins directory
        thumbnail = xbmc.translatePath( os.path.join( self.BASE_SKIN_THUMBNAIL_PATH, title.replace( " ", "-" ).lower() + ".tbn" ) )
        # use a plugin custom thumbnail if a custom skin thumbnail does not exists
        if ( not os.path.isfile( thumbnail ) ):
            # create the full thumbnail path for plugin directory
            thumbnail = xbmc.translatePath( os.path.join( self.BASE_PLUGIN_THUMBNAIL_PATH, title.replace( " ", "-" ).lower() + ".tbn" ) )
            # use a default thumbnail if a custom thumbnail does not exists
            if ( not os.path.isfile( thumbnail ) ):
                thumbnail = ""
        return thumbnail
