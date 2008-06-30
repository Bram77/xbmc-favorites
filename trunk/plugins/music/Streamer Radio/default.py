"""
    Plugin for streaming music content from the internet
"""

# main imports
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin

import time
import xml.dom.minidom
import urllib


# plugin constants
__plugin__ = "Streamer Radio"
__author__ = "nuka1195/blittan"
__url__ = "http://code.google.com/p/xbmc-addons/"
__svn_url__ = "http://xbmc-addons.googlecode.com/svn/trunk/plugins/music/Streamer%20Radio"
__credits__ = "Team XBMC"
__version__ = "1.1"


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class _Parser:
    """
        Parses an xml document for category links
    """
    def __init__( self, xml_path, levels ):
        # initialize our content lists
        self.categories = []
        self.stations = []
        # get the list
        self._get_items( xml_path, levels )

    def _get_items( self, xml_path, levels ):
        try:
            # load and parse xmlSource
            doc = xml.dom.minidom.parse( xml_path )
            # make sure this is valid <Screamer> xml source
            root = doc.documentElement
            if ( root is None or root.tagName != "Screamer" ): raise
            # get the proper node for the level we're at
            node = self._first_child( root, levels=levels )
            # check to see if this is a folder list or a station list
            isFolder = self._is_folder( node )
            # if it is a station list get the list of stations,otherwise get the subcategories
            if ( isFolder ):
                self.categories = self._get_categories( node, levels )
            else:
                self.stations = self._get_stations( node )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
        # clean-up document object
        try: doc.unlink()
        except: pass

    def _get_categories( self, node, levels ):
        categories = []
        while ( node is not None ):
            if ( node.nodeType == node.ELEMENT_NODE and node.hasAttributes() ):
                title = node.getAttribute( "title" )
                new_level = levels + [ title ]
                # add category to our categories list
                categories += [ _Info( levels=new_level, title=title, isFolder=True ) ]
            node = node.nextSibling
        return categories

    def _get_stations( self, node ):
        stations = []
        while ( node is not None ):
            if ( node.nodeType == node.ELEMENT_NODE and node.hasAttributes() ):
                title = node.getAttribute( "title" )
                source = self._first_child( node, "Source", [ None ] )
                while ( source is not None ):
                    if ( source.nodeType == source.TEXT_NODE ):
                        url = source.nodeValue
                        if ( url.startswith( "mms://" ) or url.endswith( ".asx" ) ):
                            # add station to our categories list
                            stations += [ _Info( title=title, url=url, isFolder=False ) ]
                            break
                    source = source.nextSibling
            node = node.nextSibling
        return stations

    def _is_folder( self, node, tagName="Group" ):
        while ( node is not None ):
            if ( node.nodeType == node.ELEMENT_NODE and node.tagName == tagName ):
                return True
            node = node.nextSibling
        return False

    def _first_child( self, node, tagName="Group", levels=[] ):
        for level in levels:
            node = node.firstChild
            while ( node is not None ):
                if ( node.nodeType == node.ELEMENT_NODE and node.tagName == tagName and node.hasAttributes ):
                    title = node.getAttribute( "title" )
                    if ( title == level or level is None ):
                        break
                node = node.nextSibling
        return node.firstChild


class Main:
    # base urls
    BASE_URL = "http://www.screamer-radio.com/update.php"

    # base paths
    BASE_PATH = os.getcwd().replace( ";", "" )
    BASE_DATA_PATH = os.path.join( "T:\\plugin_data", __plugin__ )
    BASE_SOURCE_PATH = os.path.join( BASE_DATA_PATH, "screamer.xml" )
    BASE_SKIN_THUMBNAIL_PATH = os.path.join( "Q:\\skin", xbmc.getSkinDir(), "media", __plugin__ )
    BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( BASE_PATH, "thumbnails" )

    def __init__( self ):
        self._parse_argv()
        ok = self.get_items()
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        if ( sys.argv[ 2 ] ):
            exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ).replace( "\\u0027", "'" ).replace( "\\u0022", '"' ).replace( "\\u0026", "&" ), )
        else:
            self.args = _Info( levels=[] )

    def get_items( self ):
        # TODO: change this to True when finished
        ok = self.get_xml_source()
        if ( ok ):
            categories, stations = self.parse_xml_source( self.BASE_SOURCE_PATH, self.args.levels )
            if ( categories ):
                ok = self._fill_media_list_categories( categories )
            else:
                ok = self._fill_media_list_stations( stations )
        return ok

    def get_xml_source( self ):
        try:
            # TODO: check date of file and download new if older than a day.
            ok = True
            # get the source files date if it exists
            try: date = os.path.getmtime( self.BASE_SOURCE_PATH )
            except: date = 0
            # we only refresh if it's been more than a day, 24hr * 60min * 60sec
            refresh = ( ( time.time() - ( 24 * 60 * 60 ) ) >= date )
            # only fetch source if it's been more than a day
            if ( refresh ):
                # open url
                usock = urllib.urlopen( self.BASE_URL )
                # read source
                xmlSource = usock.read()
                # close socket
                usock.close()
                # save the xmlSource for future parsing
                ok = self.save_xml_source( xmlSource )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        return ok

    def save_xml_source( self, xmlSource ):
        try:
            # if the path to the source file does not exist create it
            if ( not os.path.isdir( self.BASE_DATA_PATH ) ):
                os.makedirs( self.BASE_DATA_PATH )
            # open source path for writing
            file_object = open( self.BASE_SOURCE_PATH , "w" )
            # write xmlSource
            file_object.write( xmlSource )
            # close file object
            file_object.close()
            # return successful
            return True
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return False

    def parse_xml_source( self, xmlSource="", levels=[] ):
        # Parse xmlSource for categories
        parser = _Parser( xmlSource, levels )
        return parser.categories, parser.stations

    def _fill_media_list_categories( self, categories ):
        try:
            ok = True
            # enumerate through the list of categories and add the item to the media list
            for category in categories:
                url = "%s?title=%s&levels=%s&isFolder=%d" % ( sys.argv[ 0 ], repr( category.title ), repr( category.levels ), category.isFolder )
                # check for a valid custom thumbnail for the current category
                thumbnail = self._get_thumbnail( category.title )
                # set the default icon
                icon = "DefaultFolder.png"
                # only need to add label and thumbnail, setInfo() and addSortMethod() takes care of label2
                listitem=xbmcgui.ListItem( category.title, iconImage=icon, thumbnailImage=thumbnail )
                # add the item to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=len( categories ) )
                # if user cancels, call raise to exit loop
                if ( not ok ): raise
        except:
            # user cancelled dialog or an error occurred
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        return ok

    def _fill_media_list_stations( self, stations ):
        try:
            ok = True
            # enumerate through the list of categories and add the item to the media list
            for station in stations:
                # check for a valid custom thumbnail for the current category
                #thumbnail = self._get_thumbnail( station.title )
                icon = "defaultAudio.png"
                # only need to add label and icon, setInfo() and addSortMethod() takes care of label2
                listitem=xbmcgui.ListItem( station.title, iconImage=icon )
                # add the item to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=station.url, listitem=listitem, isFolder=False, totalItems=len( stations ) )
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


if ( __name__ == "__main__" ):
    Main()
