"""
Update module

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
    def __init__( self ):
        self.dialog = xbmcgui.DialogProgress()
        # get the repository info
        self._get_repo_info()
        # parse sys.argv for our current url
        self._parse_argv()
        # create the script/plugin/skin title
        self.title = self.args.download_url.split( "/" )[ -2 ].replace( "%20", " " )
        # get the list
        self._download_item()

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
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ).replace( "\\u0027", "'" ).replace( "\\u0022", '"' ).replace( "\\u0026", "&" ), )

    def _download_item( self ):
        try:
            if ( xbmcgui.Dialog().yesno( self.title, xbmc.getLocalizedString( 30000 ), "", "", xbmc.getLocalizedString( 30020 ), xbmc.getLocalizedString( 30021 ) ) ):
                self.dialog.create( self.title, xbmc.getLocalizedString( 30002 ), xbmc.getLocalizedString( 30003 ) )
                script_files = []
                folders = [ self.args.download_url ]
                while folders:
                    try:
                        htmlsource = self._get_html_source( self.REPO_URL + folders[ 0 ] )
                        if ( not htmlsource ): raise
                        items = self._parse_html_source( htmlsource )
                        if ( not items or items[ "status" ] == "fail" ): raise
                        files, dirs = self._parse_items( items )
                        for file in files:
                            script_files.append( "%s/%s" % ( items[ "items" ][ "url" ], file, ) )
                        for folder in dirs:
                            folders.append( folders[ 0 ] + folder )
                        folders = folders[ 1 : ]
                    except:
                        folders = []
                self._get_files( script_files )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            self.dialog.close()
            xbmcgui.Dialog().ok( self.title, xbmc.getLocalizedString( 30030 ) )
        
    def _get_files( self, script_files ):
        """ fetch the files """
        try:
            finished_path = ""
            for cnt, url in enumerate( script_files ):
                items = os.path.split( url )
                # TODO: Change this to U: for other than xbox
                drive = ( "Q:\\%s" % self.args.install, "Q:\\%s" % self.args.install, )[ os.environ.get( "OS", "xbox" ) == "xbox" ]
                path = drive + items[ 0 ][ 7 : ].replace( "%20", " " ).replace( "/", "\\" )
                # use this if we categorize scripts
                #if ( path.startswith( "Q:\\scripts" ) ):
                #    path = path.split( "\\" )
                #    path = path[ : 2 ] + path[ 3 : ]
                #    path = "\\".join( path )
                if ( not finished_path ): finished_path = xbmc.translatePath( path )
                file = items[ 1 ].replace( "%20", " " )
                pct = int( ( float( cnt ) / len( script_files ) ) * 100 )
                self.dialog.update( pct, "%s %s" % ( xbmc.getLocalizedString( 30005 ), url, ), "%s %s" % ( xbmc.getLocalizedString( 30006 ), xbmc.translatePath( path ), ), "%s %s" % ( xbmc.getLocalizedString( 30007 ), file, ) )
                if ( self.dialog.iscanceled() ): raise
                if ( not os.path.isdir( path ) ): os.makedirs( path )
                url = self.REPO_URL + url
                fpath = xbmc.translatePath( os.path.join( path, file ) )
                urllib.urlretrieve( url.replace( " ", "%20" ), fpath )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            raise
        else:
            self.dialog.close()
            xbmcgui.Dialog().ok( self.title, xbmc.getLocalizedString( 30008 ), finished_path )
            
    def _get_html_source( self, url ):
        try:
            sock = urllib.urlopen( url )
            htmlsource = sock.read()
            sock.close()
            return htmlsource
        except:
            return ""

    def _parse_html_source( self, htmlsource ):
        """ parse html source for tagged version and url """
        try:
            parser = Parser()
            parser.feed( htmlsource )
            parser.close()
            return parser.dict
        except:
            return {}
            
    def _parse_items( self, items ):
        """ separates files and folders """
        folders = []
        files = []
        for item in items[ "items" ][ "assets" ]:
            if ( item.endswith( "/" ) ):
                folders.append( item )
            else:
                files.append( item )
        return files, folders
