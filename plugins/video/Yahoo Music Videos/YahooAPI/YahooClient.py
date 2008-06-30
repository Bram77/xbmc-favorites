"""
    Yahoo api client module
"""

# main imports
import sys
from urllib import urlencode
import urllib2
import xml.dom.minidom


class YahooClient:
    # base url
    BASE_SEARCH_URL = "http://search.yahooapis.com/VideoSearchService/V1/videoSearch?%s"
    BASE_YOUTUBE_VIDEO_URL = "http://www.youtube.com/get_video.php?video_id=%s&t=%s"
    BASE_YAHOO_VIDEO_PRE_URL = "http://mv.music.yahoo.com/system/admin/tools/getvideo?vid=%s"
    BASE_YOUTUBE_VIDEO_PRE_URL = "http://www.youtube.com/v/%s"

    # App Id
    APPID = "lbXMhBPV34HXtWTctXwFaeBQfT5gDGSV2OGgxqamZaOmEXWCImAN7AuXtsuUSmI-"

    def __init__( self, base_url=None ):
        self.base_url = base_url

    def get_videos( self, *args, **kwargs ):
        try:
            # json uses null instead of None, true instead of True and false instead of False (should be faster than replace()
            true = True
            false = False
            null = None
            # add json type to our parameters as it is basically a python dictionary
            kwargs[ "output" ] = "json"
            # add our app id
            kwargs[ "appid" ] = self.APPID
            # add our type
            kwargs[ "type" ] = "all"
            # urlencode our kwargs
            params = urlencode( kwargs )
            # add our sites
            params += "&site=yahoo.com&site=aol.com&site=youtube.com"#"&site=www.vh1classic.com"#
            # add our formats
            #params += "&format=avi&format=msmedia&format=quicktime&format=mpeg"
            # open url
            usock = urllib2.urlopen( self.base_url % ( params, ) )
            # read source
            jsonSource = usock.read()
            # close socket
            usock.close()
            # eval jsonSource to a native python dictionary
            return eval( jsonSource )
        except:
            # oops return an empty dictionary
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return {}

    def construct_youtube_video_url( self, url ):
        try:
            if ( "player.swf" in url ):
                url = self.BASE_YOUTUBE_VIDEO_PRE_URL % ( url.split( "video_id=" )[ 1 ], )
            # we need to request the url to be redirected to the swf player url to grab the session id
            request = urllib2.Request( url )
            # create an opener object to grab the info
            opener = urllib2.build_opener().open( request )
            # close opener
            opener.close()
            # we only need the url
            url = opener.geturl()
            # format the url and return a dictionary
            exec "part = dict(%s')" % ( url.split( "?" )[ 1 ].replace( "=", "='" ).replace( "&", "', " ), )
            # we found a valid session id, construct the video url and return it
            return self.BASE_YOUTUBE_VIDEO_URL % ( part[ "video_id" ], part[ "t" ], )
        except:
            # oops return an empty string
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return ""

    def construct_yahoo_video_url( self, url ):
        try:
            if ( "/*http://" in url ):
                vid = url.split( "vid=" )[ 1 ].split( "&" )[ 0 ]
                url = self.BASE_YAHOO_VIDEO_PRE_URL % ( vid, )
            # we need to request the url to be redirected to the swf player url to grab the session id
            request = urllib2.Request( url )
            # create an opener object to grab the info
            opener = urllib2.build_opener().open( request )
            # get redirect url
            xml_data = opener.read()
            # close opener
            opener.close()
            # get the url
            return_url = opener.geturl()
            # now we need to request the new url to grab the actual video url
            request = urllib2.Request( xml_data )
            # create an opener object to grab the info
            opener = urllib2.build_opener().open( request )
            # get info
            xml_data = opener.read()
            # close opener
            opener.close()
            # we only need the url
            doc = xml.dom.minidom.parseString( xml_data.replace( "&", "&amp;" ) )
            refs = doc.getElementsByTagName( "Ref" )
            if ( not refs ):
                refs = doc.getElementsByTagName( "ref" )
            if ( refs ):
                return_url = refs[ 0 ].getAttribute( "href" )
            doc.unlink()
            # we found a valid session id, construct the video url and return it
            return str( return_url )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return url


if ( __name__ == "__main__" ):
    client = YahooClient( YahooClient.BASE_SEARCH_URL )
    videos = client.get_videos( query="aguilera music", start=1, results=10, adult_ok=1 )
    print videos
