"""
    Videos module: fetches a list of playable streams (assets) or categories (channels)
"""

# main imports
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin

import urllib


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base urls     &outputLocale=en-us
    BASE_URL = "http://%s/API/platform/jsondispatch.adp/IContainerDescribe?clientcap=WINAMP_OSClient_1.0&freeAssetsOnly=true&timeout=10000&RefId=%s"
    #BASE_SEARCH_URL = "http://%s/API/platform/jsondispatch.adp/IMetadataBrowse?clientcap=WINAMP_OSClient_1.0&freeAssetsOnly=true&domain=video&pmmsAssetsOnly=true&SearchDirective=fulltext%20contains%20\"" + escape(document.getElementById("search_query").value) + "\""
    BASE_URL_LOCALE = ( "videoapi.aol.com", "videoapi.aol.co.uk", "videoapi.aol.de", )
    BASE_WMV_STREAMING_URL = "http://wms.stream.aol.com%s_%s.wmv"

    def __init__( self ):
        self._parse_argv()
        #print "CHANNEL:", self.args.channel
        ok = self.get_items()
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

    def _parse_argv( self ):
        self._get_settings()
        # call _Info() with our formatted argv to create the self.args object
        if ( sys.argv[ 2 ] ):
            exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ).replace( "\\u0027", "'" ).replace( "\\u0022", '"' ).replace( "\\u0026", "&" ), )
        else:
            self.args = _Info( channel="video:channel:top" )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "country" ] = int( xbmcplugin.getSetting( "country" ) )
        self.settings[ "quality" ] = int( xbmcplugin.getSetting( "quality" ) )
        self.settings[ "include_wmv" ] = xbmcplugin.getSetting( "include_wmv" ) == "true"
        self.settings[ "mode" ] = int( xbmcplugin.getSetting( "mode" ) )

    def get_items( self ):
        ok = False
        # fetch the json source
        items = self.get_channel_source()
        # if successful
        if ( items and items[ "status" ][ "comment" ] == "Success" ):
            # if there are subchannel entries, we have categories
            if ( len( items[ "channel" ][ 0 ][ "subchannel" ] ) ):
                ok = self._fill_media_list_channels( items[ "channel" ][ 0 ][ "subchannel" ] )
            # no subchannels, must be videos
            else:
                ok = self._fill_media_list_assets( items[ "channel" ][ 0 ][ "asset" ] )
        return ok

    def get_channel_source( self ):
        try:
            # json uses null instead of None, true instead of True and false instead of False (should be faster than replace()
            true = True
            false = False
            null = None
            # open url
            usock = urllib.urlopen( self.BASE_URL % ( self.BASE_URL_LOCALE[ self.settings[ "country" ] ], self.args.channel, ) )
            # read source
            jsonSource = usock.read()
            # close socket
            usock.close()
            # eval jsonSource to a native python dictionary, correcting and stripping
            return eval( jsonSource.strip() )
        except:
            # oops return an empty dictionary
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return {}

    def _fill_media_list_channels( self, channels ):
        try:
            ok = False
            # enumerate through the list of categories and add the item to the media list
            for channel in channels:
                url = "%s?title=%s&channel=%s" % ( sys.argv[ 0 ], repr( channel[ "name" ] ), repr( channel[ "containerId" ] ), )
                # check for a valid custom thumbnail for the current category
                icon = "DefaultFolder.png"
                # only need to add label and icon
                listitem=xbmcgui.ListItem( channel[ "name" ], iconImage=icon )
                # add the item to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=len( channels ) )
                # if user cancels, call raise to exit loop
                if ( not ok ): raise
        except:
            # user cancelled dialog or an error occurred
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        return ok

    def _fill_media_list_assets( self, assets ):
        try:
            content = ""
            ok = False
            # enumerate through the list of categories and add the item to the media list
            for asset in assets:
                # construct the video url
                video_url, video_bitrate = self._get_video_url( asset[ "location" ] )
                # if there are no valid urls skip this video
                if ( not video_url ): continue
                # multiply video_bitrate by 1024 to get actual streaming bitrate
                video_bitrate *= 1024
                try:
                    # check for a valid custom thumbnail for the current video
                    thumbnail = asset[ "thumbnail" ][ -1 ][ "mediaThumb" ]
                except:
                    thumbnail = ""
                # set the default icon
                icon = "DefaultVideo.png"
                # only need to add label and thumbnail, setInfo() and addSortMethod() takes care of label2
                listitem = xbmcgui.ListItem( unicode( asset[ "titleName" ], "utf-8" ), iconImage=icon, thumbnailImage=thumbnail )
                # plot
                plot = unicode( asset.get( "titleDescription", "No description supplied" ), "utf-8" )
                plot = plot.replace( "<b>", "[B]" ).replace( "</b>", "[/B]" )
                # mpaa rating
                mpaa_rating = unicode( asset.get( "ratingText", "" ), "utf-8" )
                # studio
                try:
                    studio = unicode( asset[ "providedBy" ], "utf-8" )
                except:
                    try:
                        studio = unicode( asset[ "titleSource" ], "utf-8" )
                    except:
                        studio = unicode( asset[ "groupName" ], "utf-8" )
                # set our content type
                if ( not content ):
                    tmp_content = asset.get( "subject", "" ).lower()
                    if ( tmp_content == "music" ):
                        content = "musicvideos"
                    elif ( tmp_content == "movies" ):
                        content = "movies"
                    elif ( tmp_content == "television" ):
                        content = "tvshows"
                # runtime
                t = asset.get( "duration", 0 )
                runtime = "0"
                if ( t ):
                    hours = t / 60 / 60
                    minutes = ( t - ( hours * 60 * 60 ) ) / 60
                    seconds = ( t - ( hours * 60 * 60 ) ) % 60
                    runtime = "%02d:%02d:%02d" % ( hours, minutes, seconds, )
                # genre
                genre = u" ~ ".join( asset[ "genre" ] )
                genre = genre.replace( "MUSIC:" , "" ).replace( "TV:" , "" ).replace( "MOVIES:" , "" ).replace( "and", " / ").replace( "~", " / " ).strip()
                # year
                try:
                    year = int( asset[ "releaseYear" ].split( "(" )[ -1 ][ : 4 ] )
                except:
                    year = 0
                # cast
                cast = []
                cast_list = asset.get( "titleParticipant", [] )
                if ( cast_list ):
                    for name in cast_list:
                        if ( unicode( name[ "name" ], "utf-8" ) not in cast ):
                            cast += [ unicode( name[ "name" ], "utf-8" ) ]
                if ( self.settings[ "mode" ] > 0 and os.path.splitext( video_url )[ 1 ] != ".wmv" ):
                    video_url = "%s?download_url=%s" % ( sys.argv[ 0 ], repr( video_url ), )
                # set the key information
                listitem.setInfo( "video", { "Title": unicode( asset[ "titleName" ], "utf-8" ), "Size": video_bitrate, "Plot": plot, "PlotOutline": plot, "MPAA": mpaa_rating, "Genre": genre, "Studio": studio, "Duration": runtime, "Year": year, "Cast": cast } )
                # add the item to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=video_url, listitem=listitem, isFolder=False, totalItems=len( assets ) )
                # if user cancels, call raise to exit loop
                if ( not ok ): raise
        except:
            # user cancelled dialog or an error occurred
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        if ( ok ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_SIZE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_STUDIO )
            # set content
            if ( not content ): content = "movies"
            xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content=content )
        return ok

    def _get_bitrate( self, text ):
        # if it's already a number return the int()
        if ( text.isdigit() ): return int( text )
        number = ""
        # enumerate through the text, adding only digits
        for char in text:
            if ( char.isdigit() ):
                number += char
        # if it is not blank return the int()
        if ( number ): return int( number )
        # else we return 0
        return 0

    def _get_video_url( self, videos ):
        # include only the video type we want to add to the list, in the order of preference
        vtypes = [ "WmvURL", "flashNBURL", "flashLBURL", "flashMBURL", "flashHBURL", "h264MBURL", "h264BBURL" ]#, "h264_480pURL", "h264_720pURL", "h264_1080pURL" ]
        video_url = ""
        video_quality = -1
        video_bitrate = 0
        for video in videos:
            #try:
            #    if ( video[ "isDRMWrapped" ] ): continue
            #except:
            #    pass
            # we need to construct most wmv video urls
            if ( video[ "type" ] == "WmvURL" ):
                if ( self.settings[ "include_wmv" ] ):
                    try:
                        parts = video[ "url" ][ 0 ].split( ";sbr:" )
                        bitrate = self._get_bitrate( parts[ 1 ].split( "," )[ 0 ] )
                        url = self.BASE_WMV_STREAMING_URL % ( parts[ 0 ], bitrate, )
                    except:
                        try:
                            # there are no bitrate choices in the url
                            url = video[ "url" ][ 0 ]
                            bitrate = 0
                        except:
                            url = ""
            else:
                try:
                    # this is .mov or .flv video file
                    url = video[ "url" ][ 0 ]
                    bitrate = self._get_bitrate( url.split( "_" )[ -2 ] )
                except:
                    url = ""
            try:
                if ( url ):
                    # now check to see if the video quality is better than our current and is the preferred quality, if so use it
                    new_quality = vtypes.index( video[ "type" ] )
                    if ( new_quality > video_quality and bitrate >= video_bitrate ):
                        # is it the preferred quality
                        if ( ( self.settings[ "quality" ] == 0 and bitrate < 700 ) or ( self.settings[ "quality" ] == 1 and bitrate < 1500 ) or self.settings[ "quality" ] == 2 ):
                            video_quality = new_quality
                            video_url = url
                            video_bitrate = bitrate
            except:
                pass
        return video_url, video_bitrate
