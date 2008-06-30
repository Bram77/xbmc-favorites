"""
    Player module: plays the selected video
"""

import sys

# TODO: we may need to store these in the addContextMenuItem() call, when using a mouse, if the user
# moves, before this module can be imported the selection can change.
# TODO: remove this when dialog issue is resolved
import xbmc
# set our title
g_title = unicode( xbmc.getInfoLabel( "ListItem.Title" ), "utf-8" )
# set our studio (only works if the user is using the video library)
g_studio = unicode( xbmc.getInfoLabel( "ListItem.Studio" ), "utf-8" )
# set our studio (only works if the user is using the video library)
g_director = unicode( xbmc.getInfoLabel( "ListItem.Director" ), "utf-8" )
# set our genre (only works if the user is using the video library)
g_genre = unicode( xbmc.getInfoLabel( "ListItem.Genre" ), "utf-8" )
# set our rating (only works if the user is using the video library)
g_mpaa_rating = unicode( xbmc.getInfoLabel( "ListItem.MPAA" ), "utf-8" )
# set our thumbnail
g_thumbnail = xbmc.getInfoImage( "ListItem.Thumb" )
# set our plotoutline
g_plotoutline = unicode( xbmc.getInfoLabel( "ListItem.Plot" ), "utf-8" )
# set movie url
g_movie_url = xbmc.getInfoLabel( "ListItem.FilenameAndPath" )

# create the progress dialog (we do it here so there is minimal delay with nothing displayed)
import xbmcgui
pDialog = xbmcgui.DialogProgress()
pDialog.create( sys.modules[ "__main__" ].__plugin__ )

import os
import xbmcplugin
import urllib


class Main:
    def __init__( self ):
        # get user preferences
        self._get_settings()
        # download the video
        self._download_video()
        # play the video
        self._play_video()

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "download_mode" ] = int( xbmcplugin.getSetting( "download_mode" ) )
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
            # create our temp save path
            tmp_path = xbmc.translatePath( "Z:\\%s" % ( os.path.basename( g_movie_url ), ) )
            # if download_mode is temp or a smb share, then download to cache folder
            if ( self.settings[ "download_mode" ] == 0 ):
                self.filepath = unicode( tmp_path, "utf-8", "replace" )
            else:
                # get a valid filepath
                if ( self.settings[ "use_title" ] ):
                    # add trailer extension to trailer title
                    title = g_title + os.path.splitext( g_movie_url )[ 1 ]
                else:
                    # we use the urls trailer name
                    title = os.path.basename( g_movie_url )
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
            if ( not os.path.isfile( filepath ) ):
                # fetch the video
                urllib.urlretrieve( g_movie_url, tmp_path, self._report_hook )
                # create the conf file for xbox and copy to final location
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
        msg1 = xbmc.getLocalizedString( 30500 + self.settings[ "download_mode" ]  ) % ( os.path.split( self.filepath )[ 1 ], )
        msg2 = ( "", xbmc.getLocalizedString( 30502 ) % ( os.path.split( self.filepath )[ 0 ], ), )[ self.settings[ "download_mode" ] ]
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
            msg1 = xbmc.getLocalizedString( 30503 ) % ( os.path.split( self.filepath )[ 1 ], )
            msg2 = xbmc.getLocalizedString( 30502 ) % ( os.path.split( self.filepath )[ 0 ], )
            pDialog.update( -1, msg1, msg2 )
            # necessary for dialog to update
            xbmc.sleep( 50 )
            xbmc.executehttpapi( "FileCopy(%s,%s)" % ( tmp_path, self.filepath.encode( "utf-8" ), ) )
            # create conf file for better MPlayer playback only when trailer saved on xbox and not progressive
            if ( not self.filepath.startswith( "smb://" ) and not g_movie_url.endswith( "p.mov" ) and not os.path.isfile( self.filepath + ".conf" ) and os.environ.get( "OS", "xbox" ) == "xbox" ):
                f = open( self.filepath + ".conf" , "w" )
                f.write( "nocache=1" )
                f.close()
            # copy the thumbnail
            thumbpath = os.path.splitext( self.filepath )[ 0 ] + ".tbn"
            msg1 = xbmc.getLocalizedString( 30503 ) % ( os.path.split( thumbpath )[ 1 ], )
            pDialog.update( -1, msg1, msg2 )
            # necessary for dialog to update
            xbmc.sleep( 50 )
            xbmc.executehttpapi( "FileCopy(%s,%s)" % ( g_thumbnail, thumbpath.encode( "utf-8" ), ) )
            # we succeeded
            return True
        except:
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return False

    def _play_video( self ):
        if ( self.filepath ):
            # set DVDPLAYER as the player for progressive videos
            core_player = ( xbmc.PLAYER_CORE_MPLAYER, xbmc.PLAYER_CORE_DVDPLAYER, )[ g_movie_url.endswith( "p.mov" ) ]
            # create our playlist
            playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
            # clear any possible entries
            playlist.clear()
            # set the default icon
            icon = "DefaultVideo.png"
            # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
            listitem = xbmcgui.ListItem( g_title, iconImage=icon, thumbnailImage=g_thumbnail )
            # set the key information
            listitem.setInfo( "video", { "Title": g_title, "Genre": g_genre, "Studio": g_studio, "Director": g_director, "MPAA": g_mpaa_rating, "Plotoutline": g_plotoutline } )
            # add item to our playlist
            playlist.add( self.filepath, listitem )
            # close dialog
            pDialog.close()
            # play item
            xbmc.Player( core_player ).play( playlist )
