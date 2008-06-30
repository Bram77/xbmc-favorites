"""
    Player module: plays the selected video
"""

# TODO: remove this when dialog issue is resolved
import xbmc
# set our title
g_title = unicode( xbmc.getInfoLabel( "ListItem.Title" ), "utf-8" )
# set our studio (only works if the user is using the video library)
g_studio = unicode( xbmc.getInfoLabel( "ListItem.Studio" ), "utf-8" )
# set our genre (only works if the user is using the video library)
#g_genre = unicode( xbmc.getInfoLabel( "ListItem.Genre" ), "utf-8" )
# set our rating (only works if the user is using the video library)
#g_mpaa_rating = unicode( xbmc.getInfoLabel( "ListItem.MPAA" ), "utf-8" )
# set our thumbnail
g_thumbnail = xbmc.getInfoImage( "ListItem.Thumb" )
# set our plotoutline
g_plotoutline = unicode( xbmc.getInfoLabel( "ListItem.Plot" ), "utf-8" )

# create the progress dialog (we do it here so there is minimal delay with nothing displayed)
import xbmcgui
pDialog = xbmcgui.DialogProgress()
pDialog.create( "Yahoo Music Videos Plugin", "Getting session ID..." )

# main imports
import sys
import os
import traceback
import urllib

import xbmcplugin

from YahooAPI.YahooClient import YahooClient


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    def __init__( self ):
        # get the settings
        self._get_settings()
        # parse sys.argv
        self._parse_argv()
        # get our url
        filepath = self.construct_url()
        if ( self.settings[ "mode" ] > 0 and not filepath.startswith( "mms://" ) ):
            filepath = self._download_video( filepath )
        self._play_video( filepath )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "mode" ] = int( xbmcplugin.getSetting( "mode" ) )
        self.settings[ "download_path" ] = xbmcplugin.getSetting( "download_path" )

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ).replace( "\\u0027", "'" ).replace( "\\u0022", '"' ).replace( "\\u0026", "&" ), )
        self.args.url = self.args.url.replace( "-*-*-", "&" )

    def _download_video( self, url ):
        try:
            pDialog.update( -1, "Downloading video..." )
            # check for a valid extension, if none use .avi
            ext = os.path.splitext( url )[ 1 ]
            if ( len( ext ) != 4 ):
                ext = ".avi"
            if ( self.settings[ "mode" ] == 1 ):
                filepath = "Z:\\YahooVideo%s" % ( ext, )
            else:
                # replace forward and back slashes, split at colon and replace leading and trailing apostrophes
                title = g_title.replace( "/", "" ).replace( "\\", "" ).split( ":", 1 )
                # strip extra spaces
                title[ 0 ] = title[ 0 ].strip()
                title[ -1 ] = title[ -1 ].strip()
                # eliminate leading apostrophe
                if ( title[ -1 ].startswith( "'" ) ):
                    title[ -1 ] = title[ -1 ][ 1 : ]
                # join back together
                title = u"-".join( title )
                # get a valid filepath
                filepath = self._make_legal_filepath( os.path.join( self.settings[ "download_path" ], title + ext ) )
                ext = os.path.splitext( filepath )[ 1 ]
                name = os.path.splitext( filepath )[ 0 ]
                # eliminate leading and trailing apostrophes
                if ( name.endswith( "'" ) ):
                    name = name[ : -1 ]
                filepath = name + ext
            if ( not os.path.isfile( filepath ) or self.settings[ "mode" ] == 1 ):
                # fetch the video
                urllib.urlretrieve( url, filepath, self._report_hook )
        except:
            urllib.urlcleanup()
            remove_tries = 3
            while remove_tries and os.path.isfile( filepath ):
                try:
                    os.remove( filepath )
                except:
                    remove_tries -= 1
                    xbmc.sleep( 1000 )
            filepath = ""
            pDialog.close()
        return filepath

    def _report_hook( self, count, blocksize, totalsize ):
        percent = int( float( count * blocksize * 100) / totalsize )
        pDialog.update( percent )
        if ( pDialog.iscanceled() ): raise

    def _make_legal_filepath( self, path, compatible=False, extension=True, conf=True, save_end=False ):
        environment = os.environ.get( "OS", "xbox" )
        if ( environment == "win32" or environment == "xbox" ):
            path = path.replace( "\\", "/" )
        drive = os.path.splitdrive( path )[ 0 ]
        parts = os.path.splitdrive( path )[ 1 ].split( "/" )
        if ( not drive and parts[ 0 ].endswith( ":" ) and len( parts[ 0 ] ) == 2 and compatible ):
            drive = parts[ 0 ]
            parts[ 0 ] = ""
        if ( environment == "xbox" or environment == "win32" or compatible ):
            illegal_characters = """,*=|<>?;:"+"""
            length = ( 42 - ( conf * 5 ) )
            for count, part in enumerate( parts ):
                tmp_name = ""
                for char in part:
                    # if char's ord() value is > 127 or an illegal character remove it
                    if ( char in illegal_characters or ord( char ) > 127 ): char = ""
                    tmp_name += char
                if ( environment == "xbox" or compatible ):
                    if ( len( tmp_name ) > length ):
                        if ( count == len( parts ) - 1 and extension == True ):
                            filename = os.path.splitext( tmp_name )[ 0 ]
                            ext = os.path.splitext( tmp_name )[ 1 ]
                            if ( save_end ):
                                tmp_name = filename[ : 35 - len( ext ) ] + filename[ -2 : ]
                            else:
                                tmp_name = filename[ : 37 - len( ext ) ]
                            tmp_name = "%s%s" % ( tmp_name.strip(), ext )
                        else:
                            tmp_name = tmp_name[ : 42 ].strip()
                parts[ count ] = tmp_name
        filepath = drive + "/".join( parts )
        if ( environment == "win32" ):
            return filepath.encode( "utf-8" )
        else:
            return filepath

    def _play_video( self, filepath ):
        if ( filepath ):
            # create our playlist
            playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
            # clear any possible entries
            playlist.clear()
            # set the default icon
            icon = "DefaultVideo.png"
            # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
            listitem = xbmcgui.ListItem( g_title, iconImage=icon, thumbnailImage=g_thumbnail )
            # set the key information
            listitem.setInfo( "video", { "Title": g_title, "Genre": "Music Videos", "Studio": g_studio, "Plotoutline": g_plotoutline } )
            # add item to our playlist
            playlist.add( filepath, listitem )
            # close dialog
            pDialog.close()
            # play item
            xbmc.Player().play( playlist )

    def construct_url( self ):
        # Yahoo client
        client = YahooClient()
        if ( "yahoo" in self.args.url ):
            url = client.construct_yahoo_video_url( self.args.url )
        elif ( "youtube" in self.args.url ):
            url = client.construct_youtube_video_url( self.args.url )
        else:
            url = self.args.url
        return url
