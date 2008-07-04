"""
svn repo installer plugin

Nuka1195
"""

# main imports
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin

import urllib
from sgmllib import SGMLParser
import re


class Parser( SGMLParser ):
    """ Parser Class: grabs all tag versions and urls """
    def reset( self ):
        self.tags = []
        self.dict = { "status": "fail"}
        self.tag_found = None
        self.url_found = True
        SGMLParser.reset( self )

    def start_a( self, attrs ):
        for key, value in attrs:
            if ( key == "href" ): self.tag_found = value
    
    def handle_data( self, text ):
        if ( self.tag_found == text.replace( " ", "%20" ) ):
            self.tags.append( self.tag_found )
            self.tag_found = False
        if ( self.url_found ):
            self.dict[ "items" ] = { "url": text.split( ":" )[ 1 ].strip(), "assets": self.tags }
            self.dict[ "status" ] = "ok"
            self.url_found = False
            
    def unknown_starttag( self, tag, attrs ):
        if ( tag == "h2" ):
            self.url_found = True


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base path
    BASE_CACHE_PATH = os.path.join( "P:\\Thumbnails", "Pictures" )

    def __init__( self ):
        # get the repository info
        self._get_repo_info()
        # parse sys.argv for our current url
        self._parse_argv()
        # get the list
        ok = self._show_categories()
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        if ( sys.argv[ 2 ] ):
            exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ).replace( "\\u0027", "'" ).replace( "\\u0022", '"' ).replace( "\\u0026", "&" ), )
        else:
            self.args = _Info( category=self.REPO_ROOT )

    def _get_repo_info( self ):
        # path to info file
        repopath = xbmc.translatePath( os.path.join( os.getcwd().replace( ";", "" ), "resources", "repositories", xbmcplugin.getSetting( "repository" ), "repo.xml" ) )
        try:
            # grab a file object
            fileobject = open( repopath, "r" )
            # read the info
            info = fileobject.read()
            # close the file object
            fileobject.close()
            # repo's base url
            self.REPO_URL = re.findall( '<url>([^<]+)</url>', info )[ 0 ]
            # root of repository
            self.REPO_ROOT = re.findall( '<root>([^<]*)</root>', info )[ 0 ]
            # structure of repo
            self.REPO_STRUCTURES = re.findall( '<structure name="([^"]+)" offset="([^"]+)" install="([^"]*)"', info )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )

    def _show_categories( self ):
        ok = False
        # fetch the html source
        items = self._get_items()
        # if successful
        if ( items and items[ "status" ] == "ok" ):
            # if there are assets, we have categories
            ok = self._fill_list( items[ "items" ] )
        return ok

    def _fill_list( self, items ):
        try:
            ok = False
            # enumerate through the list of categories and add the item to the media list
            for item in items[ "assets" ]:
                isFolder = True
                for name, offset, install in self.REPO_STRUCTURES:
                    if ( items[ "url" ].split( "/" )[ int( offset ) ] == name ):
                        isFolder = False
                        break
                if ( isFolder ):
                    heading = "category"
                    thumbnail = ""
                else:
                    heading = "download_url"
                    thumbnail = self._get_thumbnail( "%s%s/%sdefault.tbn" % ( self.REPO_URL, items[ "url" ], item, ) )
                url = '%s?%s="%s/%s"&install="%s"' % ( sys.argv[ 0 ], heading, items[ "url" ], item, install )
                # set the default icon
                icon = "DefaultFolder.png"
                # create our listitem, fixing title
                listitem = xbmcgui.ListItem( item[ : -1 ].replace( "%20", " " ).title(), iconImage=icon, thumbnailImage=thumbnail )
                # set the title
                listitem.setInfo( type="Video", infoLabels={ "Title": item[ : -1 ].replace( "%20", " " ).title() } )
                # add the item to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=isFolder, totalItems=len( items[ "assets" ] ) )
                # if user cancels, call raise to exit loop
                if ( not ok ): raise
        except:
            # user cancelled dialog or an error occurred
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        if ( ok ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
        return ok

    def _get_items( self ):
        try:
            # open url
            usock = urllib.urlopen( self.REPO_URL + self.args.category )
            # read source
            htmlSource = usock.read()
            # close socket
            usock.close()
            # parse source and return a dictionary
            return self._parse_html_source( htmlSource )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return {}

    def _parse_html_source( self, htmlsource ):
        # initialize the parser
        parser = Parser()
        # pass the htmlSource
        parser.feed( htmlsource )
        # close parser
        parser.close()
        # return results
        return parser.dict

    def _get_thumbnail( self, thumbnail_url ):
        # make the proper cache filename and path so duplicate caching is unnecessary
        if ( not thumbnail_url.startswith( "http://" ) ): return thumbnail_url
        try:
            filename = xbmc.getCacheThumbName( thumbnail_url )
            filepath = xbmc.translatePath( os.path.join( self.BASE_CACHE_PATH, filename[ 0 ], filename ) )
            # if the cached thumbnail does not exist fetch the thumbnail
            if ( not os.path.isfile( filepath ) ):
                # fetch thumbnail and save to filepath
                info = urllib.urlretrieve( thumbnail_url, filepath )
                # cleanup any remaining urllib cache
                urllib.urlcleanup()
            return filepath
        except:
            # return empty string if retrieval failed
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return ""        
