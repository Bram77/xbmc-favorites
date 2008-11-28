"""
    Plugin for streaming Apple Movie Trailers
"""

# main imports
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin

import time
import re
import urllib
import datetime
from xml.sax.saxutils import unescape

class _Parser:
    """
        Parses an xml document for videos
    """
    def __init__( self, xmlSource, settings ):
        self.success = True
        self.settings = settings
        # get our regions format
        try:
            self.date_format = xbmc.getRegion( "datelong" ).replace( "DDDD,", "" ).replace( "MMMM", "%B" ).replace( "D", "%d" ).replace( "YYYY", "%Y" ).strip()
        except:
            self.date_format = "%B %d, %Y"
        # get the list
        self.success = self._get_current_videos( xmlSource )

    def _get_current_videos( self, xmlSource ):
        try:
            mpaa_ratings = [ "G", "PG", "PG-13", "R", "NC-17" ]
            # encoding
            encoding = re.findall( "<\?xml version=\"[^\"]*\" encoding=\"([^\"]*)\"\?>", xmlSource )[ 0 ]
            # gather all video records <movieinfo>
            movies = re.findall( "<movieinfo[^>]*>(.*?)</movieinfo>", xmlSource )
            # enumerate thru the movie list and gather info
            for movie in movies:
                info = re.findall( "<info>(.*?)</info>", movie )
                cast = re.findall( "<cast>(.*?)</cast>", movie )
                genre = re.findall( "<genre>(.*?)</genre>", movie )
                poster = re.findall( "<poster>(.*?)</poster>", movie )
                preview = re.findall( "<preview>(.*?)</preview>", movie )
                # info
                title = unicode( unescape( re.findall( "<title>(.*?)</title>", info[ 0 ] )[ 0 ] ), encoding, "replace" )
                runtime = re.findall( "<runtime>(.*?)</runtime>", info[ 0 ] )[ 0 ]
                mpaa = re.findall( "<rating>(.*?)</rating>", info[ 0 ] )[ 0 ]
                rating_index = 0
                if ( self.settings[ "rating" ] < len( mpaa_ratings ) and mpaa in mpaa_ratings ):
                    rating_index = mpaa_ratings.index( mpaa )
                if ( rating_index > self.settings[ "rating" ] ):
                    continue
                studio = unicode( unescape( re.findall( "<studio>(.*?)</studio>", info[ 0 ] )[ 0 ] ), encoding, "replace" )
                postdate = ""
                tmp_postdate = re.findall( "<postdate>(.*?)</postdate>", info[ 0 ] )[ 0 ]
                if ( tmp_postdate ):
                    postdate = "%s-%s-%s" % ( tmp_postdate[ 8 : ], tmp_postdate[ 5 : 7 ], tmp_postdate[ : 4 ], )
                releasedate = re.findall( "<releasedate>(.*?)</releasedate>", info[ 0 ] )[ 0 ]
                if ( not releasedate ):
                    releasedate = ""
                copyright = unicode( unescape( re.findall( "<copyright>(.*?)</copyright>", info[ 0 ] )[ 0 ] ), encoding, "replace" )
                director = unicode( unescape( re.findall( "<director>(.*?)</director>", info[ 0 ] )[ 0 ] ), encoding, "replace" )
                plot = unicode( unescape( re.findall( "<description>(.*?)</description>", info[ 0 ] )[ 0 ] ), encoding, "replace" )
                # actors
                actors = []
                if ( cast ):
                    actor_list = re.findall( "<name>(.*?)</name>", cast[ 0 ] )
                    for actor in actor_list:
                        actors += [ unicode( unescape( actor ), encoding, "replace" ) ]
                # genres
                genres = []
                if ( genre ):
                    genres = re.findall( "<name>(.*?)</name>", genre[ 0 ] )
                genre = " / ".join( genres )
                # poster
                xlarge = re.findall( "<xlarge>(.*?)</xlarge>", poster[ 0 ] )
                location = re.findall( "<location>(.*?)</location>", poster[ 0 ] )
                if ( xlarge and self.settings[ "poster" ] ):
                    poster = xlarge[ 0 ]
                else:
                    poster = location[ 0 ]
                # trailer
                trailer = re.findall( "<large[^>]*>(.*?)</large>", preview[ 0 ] )[ 0 ]
                # size
                size = long( re.findall( "filesize=\"([0-9]*)", preview[ 0 ] )[ 0 ] )
                # add the item to our media list
                ok = self._add_video( { "title": title, "runtime": runtime, "mpaa": mpaa, "studio": studio, "postdate": postdate, "releasedate": releasedate, "copyright": copyright, "director": director, "plot": plot, "cast": actors, "genre": genre, "poster": poster, "trailer": trailer, "size": size }, 0 )
                # if user cancels, call raise to exit loop
                if ( not ok ): raise
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        return ok

    def _add_video( self, video, total ):
        try:
            # set the default icon
            icon = "DefaultVideo.png"
            # set an overlay if one is practical
            overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_HD, )[ "720p.mov" in video[ "trailer" ] or "1080p.mov" in video[ "trailer" ] ]
            # only need to add label and thumbnail, setInfo() and addSortMethod() takes care of label2
            listitem = xbmcgui.ListItem( video[ "title" ], iconImage=icon, thumbnailImage=video[ "poster" ] )
            # release date and year
            try:
                # format the date
                release_date = datetime.date( int( video[ "releasedate" ].split( "-" )[ 0 ] ), int( video[ "releasedate" ].split( "-" )[ 1 ] ), int( video[ "releasedate" ].split( "-" )[ 2 ] ) ).strftime( self.date_format )
                # we need just year also
                year = int( video[ "releasedate" ].split( "-" )[ 0 ] )
            except:
                release_date = ""
                year = 0
            # set the key information
            listitem.setInfo( "video", { "Title": video[ "title" ], "Overlay": overlay, "Size": video[ "size" ], "Year": year, "Plot": video[ "plot" ], "PlotOutline": video[ "plot" ], "MPAA": video[ "mpaa" ], "Genre": video[ "genre" ], "Studio": video[ "studio" ], "Director": video[ "director" ], "Duration": video[ "runtime" ], "Cast": video[ "cast" ], "Date": video[ "postdate" ] } )
            # set release date property
            listitem.setProperty( "releasedate", release_date )
            # TODO: remove this try/except block when branch is updated
            try:
                # set context menu items
                action1 = "XBMC.RunPlugin(%s?Fetch_Showtimes=True&title=%s)" % ( sys.argv[ 0 ], urllib.quote_plus( repr( video[ "title" ] ) ), )
                action2 = "XBMC.RunPlugin(%s?Download_Trailer=True)" % ( sys.argv[ 0 ], )
                listitem.addContextMenuItems( [ ( xbmc.getLocalizedString( 30900 ), action1, ), ( xbmc.getLocalizedString( 30910 ), action2, ) ] )
            except:
                pass
            # add the item to the media list
            ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=video[ "trailer" ], listitem=listitem, isFolder=False, totalItems=total )
            # return
            return ok
        except:
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return False


class Main:
    # base url
    BASE_CURRENT_URL = "http://www.apple.com/trailers/home/xml/current%s.xml"

    # base paths
    BASE_DATA_PATH = xbmc.translatePath( os.path.join( "P:\\plugin_data", "video", sys.modules[ "__main__" ].__plugin__ ) )
    BASE_CURRENT_SOURCE_PATH = xbmc.translatePath( os.path.join( "P:\\plugin_data", "video", sys.modules[ "__main__" ].__plugin__, "current%s.xml" ) )

    def __init__( self ):
        # get users preference
        self._get_settings()
        # fetch videos
        ok = self.get_videos()
        # if successful and user did not cancel, set our sort orders, content, plugin category and fanart
        if ( ok ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_SIZE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_MPAA_RATING )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_STUDIO )
            # set content
            xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="movies" )
            try:
                # set our plugin category
                xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=self.PluginCategory )
                # set our fanart from user setting
                if ( self.settings[ "fanart_image" ] ):
                    xbmcplugin.setPluginFanart( handle=int( sys.argv[ 1 ] ), image=self.settings[ "fanart_image" ], color1=self.settings[ "fanart_color1" ], color2=self.settings[ "fanart_color2" ], color3=self.settings[ "fanart_color3" ] )
            except:
                pass
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

    def _get_settings( self ):
        self.settings = {}
        # TODO: enable 1080p in settings
        self.PluginCategory = ( xbmc.getLocalizedString( 30700 ), xbmc.getLocalizedString( 30701 ), xbmc.getLocalizedString( 30702 ), xbmc.getLocalizedString( 30703 ), )[ int( xbmcplugin.getSetting( "quality" ) ) ]
        self.settings[ "quality" ] = ( "", "_480p", "_720p", "_1080p", )[ int( xbmcplugin.getSetting( "quality" ) ) ]
        self.settings[ "poster" ] = ( xbmcplugin.getSetting( "poster" ) == "true" )
        self.settings[ "rating" ] = int( xbmcplugin.getSetting( "rating" ) )
        self.settings[ "fanart_image" ] = xbmcplugin.getSetting( "fanart_image" )
        self.settings[ "fanart_color1" ] = xbmcplugin.getSetting( "fanart_color1" )
        self.settings[ "fanart_color2" ] = xbmcplugin.getSetting( "fanart_color2" )
        self.settings[ "fanart_color3" ] = xbmcplugin.getSetting( "fanart_color3" )

    def get_videos( self ):
        ok = False
        # fetch xml source
        xmlSource = self.get_xml_source()
        if ( xmlSource ):
            ok = self.parse_xml_source( xmlSource )
        return ok

    def get_xml_source( self ):
        try:
            ok = True
            # set proper source
            base_path = self.BASE_CURRENT_SOURCE_PATH % ( self.settings[ "quality" ], )
            base_url = self.BASE_CURRENT_URL % ( self.settings[ "quality" ], )
            # get the source files date if it exists
            try: date = os.path.getmtime( base_path )
            except: date = 0
            # we only refresh if it's been more than a day, 24hr * 60min * 60sec
            refresh = ( ( time.time() - ( 24 * 60 * 60 ) ) >= date )
            # only fetch source if it's been more than a day
            if ( refresh ):
                # open url
                usock = urllib.urlopen( base_url )
            else:
                # open path
                usock = open( base_path, "r" )
            # read source
            xmlSource = usock.read()
            # close socket
            usock.close()
            # save the xmlSource for future parsing
            if ( refresh ):
                ok = self.save_xml_source( xmlSource )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        if ( ok ):
            return xmlSource
        else:
            return ""

    def save_xml_source( self, xmlSource ):
        try:
            # set proper source
            base_path = self.BASE_CURRENT_SOURCE_PATH % ( self.settings[ "quality" ], )
            # if the path to the source file does not exist create it
            if ( not os.path.isdir( self.BASE_DATA_PATH ) ):
                os.makedirs( self.BASE_DATA_PATH )
            # open source path for writing
            file_object = open( base_path, "w" )
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

    def parse_xml_source( self, xmlSource ):
        # Parse xmlSource for videos
        parser = _Parser( xmlSource, self.settings )
        return parser.success
