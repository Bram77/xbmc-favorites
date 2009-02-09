"""
    Player module: plays the selected video
"""

# TODO: remove this when dialog issue is resolved
import xbmc
"""
# set our title
g_title = unicode( xbmc.getInfoLabel( "ListItem.Title" ), "utf-8" )
# set our director
g_director = unicode( xbmc.getInfoLabel( "ListItem.Director" ), "utf-8" )
# set our genre
g_genre = unicode( xbmc.getInfoLabel( "ListItem.Genre" ), "utf-8" )
# set our rating
g_rating = 0.0
if ( xbmc.getInfoLabel( "ListItem.Rating" ) ):
    g_rating = float( xbmc.getInfoLabel( "ListItem.Rating" ) )
# set our date
g_date = xbmc.getInfoLabel( "ListItem.Date" )
# set our thumbnail
g_thumbnail = xbmc.getInfoImage( "ListItem.Thumb" )
# set our plotoutline
g_plotoutline = unicode( xbmc.getInfoLabel( "ListItem.Plot" ), "utf-8" )
"""

# create the progress dialog (we do it here so there is minimal delay with nothing displayed)
import sys
import xbmcgui
pDialog = xbmcgui.DialogProgress()
pDialog.create( sys.modules[ "__main__" ].__plugin__, xbmc.getLocalizedString( 30908 ) )

# main imports
import os
import urllib
import xbmcplugin

from YoutubeAPI.YoutubeClient import YoutubeClient


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    def __init__( self ):
        # parse video url
        self._parse_argv()
        # get user preferences
        self._get_settings()
        # download the video
        self._download_video()
        # play the video
        self._play_video()

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ).replace( "\\u0027", "'" ).replace( "\\u0022", '"' ).replace( "\\u0026", "&" ), )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "player_core" ] = ( xbmc.PLAYER_CORE_MPLAYER, xbmc.PLAYER_CORE_DVDPLAYER, )[ int( xbmcplugin.getSetting( "player_core" ) ) ]
        self.settings[ "download_path" ] = xbmcplugin.getSetting( "download_path" )
        self.settings[ "use_title" ] = ( xbmcplugin.getSetting( "use_title" ) == "true" )

    def _get_filesystem( self ):
        # get the flavor of XBMC
        filesystem = os.environ.get( "OS", "xbox" )
        # use win32 illegal characters for smb shares to be safe (eg run on linux, save to windows)
        if ( self.settings[ "download_path" ].startswith( "smb://" ) ):
            filesystem = "win32"
        return filesystem

    def _download_video( self ):
        try:
            # Youtube client
            client = YoutubeClient()
            # construct the video url with session id and get video details
            url, self.g_title, self.g_director, self.g_genre, self.g_rating, self.g_runtime, self.g_count, self.g_date, self.g_thumbnail, self.g_plotoutline, video_id = client.construct_video_url( self.args.video_url, ( 0, 6, 18, )[ int( xbmcplugin.getSetting( "quality" ) ) ] )
            # create our temp save path
            tmp_path = xbmc.translatePath( "Z:\\%s.flv" % ( video_id, ) )
            # get a valid filepath
            if ( self.settings[ "use_title" ] ):
                # add extension to video title
                title = self.g_title + ".flv"
            else:
                # we use the urls trailer name
                title = video_id + ".flv"
            # make the path legal for the users platform
            self.filepath = self._make_legal_filepath( title )
            # get the filesystem the trailer will be saved to
            filesystem = self._get_filesystem()
            # win32 requires encoding to work proper
            if ( self._get_filesystem() == "win32" ):
                filepath = self.filepath.encode( "utf-8" )
            else:
                filepath = self.filepath
            # only download if the trailer doesn't exist
            if ( not os.path.isfile( tmp_path ) ):
                # fetch the video
                urllib.urlretrieve( url, tmp_path, self._report_hook )
            ok = True
            # finalize
            if ( not os.path.isfile( filepath ) ):
                # copy to final location
                ok = self._finalize_download( tmp_path )
                # if the copy failed raise an error
                if ( not ok ): raise
        except:
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            # filepath is not always released immediately, we may need to try more than one attempt, sleeping between
            urllib.urlcleanup()
            remove_tries = 3
            while remove_tries and os.path.isfile( tmp_path ):
                try:
                    os.remove( tmp_path )
                except:
                    remove_tries -= 1
                    xbmc.sleep( 1000 )
            pDialog.close()
            self.filepath = ""

    def _report_hook( self, count, blocksize, totalsize ):
        percent = int( float( count * blocksize * 100) / totalsize )
        msg1 = xbmc.getLocalizedString( 30601  ) % ( os.path.split( self.filepath )[ 1 ], )
        msg2 = xbmc.getLocalizedString( 30602 ) % ( os.path.split( self.filepath )[ 0 ], )
        pDialog.update( percent, msg1, msg2 )
        if ( pDialog.iscanceled() ): raise

    def _make_legal_filepath( self, title ):
        # TODO: figure out how to determine download_path's filesystem, statvfs() not available on windows
        import re
        # different os's have different illegal characters
        illegal_characters = { "xbox": '\\/,*=|<>?;:\"+', "win32": '\\/*|<>?:\"', "Linux": "/", "OS X": "/:" }
        # get the flavor of XBMC
        environment = os.environ.get( "OS", "xbox" )
        # get the filesystem the trailer will be saved to
        filesystem = self._get_filesystem()
        # clean the filename
        filename = re.sub( '[%s]' % ( illegal_characters[ filesystem ], ), "_", title )
        # we need to set the length to 37 if filesystem is xbox and filepath isn't a smb share for the .conf file
        if ( filesystem == "xbox" and len( filename ) > 37 and not self.settings[ "download_path" ].startswith( "smb://" ) ):
            name, ext = os.path.splitext( filename )
            filename = name[ : 37 - len( ext ) ].strip() + ext
        # replace any charcaters whose ord > 127 for xbox filesystem
        if ( filesystem == "xbox" ):
            for char in filename:
                if ( ord( char ) > 127 ):
                    filename = filename.replace( char, "_" )
        # return a unicode object
        return unicode( xbmc.translatePath( os.path.join( self.settings[ "download_path" ], filename ) ), "utf-8", "replace" )

    def _finalize_download( self, tmp_path ):
        try:
            # copy the trailer
            msg1 = xbmc.getLocalizedString( 30603 ) % ( os.path.split( self.filepath )[ 1 ], )
            msg2 = xbmc.getLocalizedString( 30602 ) % ( os.path.split( self.filepath )[ 0 ], )
            pDialog.update( -1 )#, msg1, msg2 )
            # necessary for dialog to update
            xbmc.sleep( 50 )
            xbmc.executehttpapi( "FileCopy(%s,%s)" % ( tmp_path, self.filepath.encode( "utf-8" ), ) )
            """
            # create conf file for better MPlayer playback only when trailer saved on xbox and not progressive
            if ( not self.filepath.startswith( "smb://" ) and not url.endswith( "p.mov" ) and not os.path.isfile( self.filepath + ".conf" ) and os.environ.get( "OS", "xbox" ) == "xbox" ):
                f = open( self.filepath + ".conf" , "w" )
                f.write( "nocache=1" )
                f.close()
            """
            # copy the thumbnail
            ##thumbpath = os.path.splitext( self.filepath )[ 0 ] + ".tbn"
            ##msg1 = xbmc.getLocalizedString( 30603 ) % ( os.path.split( thumbpath )[ 1 ], )
            ##pDialog.update( -1, msg1, msg2 )
            # necessary for dialog to update
            ##xbmc.sleep( 50 )
            ##xbmc.executehttpapi( "FileCopy(%s,%s)" % ( self.g_thumbnail, thumbpath.encode( "utf-8" ), ) )
            # we succeeded
            return True
        except:
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return False

    def _play_video( self ):
        # close dialog
        pDialog.close()
        if ( self.filepath ):
            # create our playlist
            playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
            # clear any possible entries
            playlist.clear()
            # set the default icon
            icon = "DefaultVideo.png"
            # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
            listitem = xbmcgui.ListItem( self.g_title, iconImage=icon, thumbnailImage=self.g_thumbnail )
            # set the key information
            listitem.setInfo( "video", { "Title": self.g_title, "Genre": self.g_genre, "Director": self.g_director, "Rating": self.g_rating, "Plot": self.g_plotoutline, "Plotoutline": self.g_plotoutline, "Year": int( self.g_date[ -4 : ] ) } )
            # add item to our playlist
            playlist.add( self.filepath, listitem )
            # play item
            xbmc.Player( self.settings[ "player_core" ] ).play( playlist )
