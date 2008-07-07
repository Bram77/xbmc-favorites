"""
    Videos module: fetches a list of playable streams (assets) or categories (channels)
"""

# main imports
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import re

import MpTVConnector

SERVER_HOST = '10.1.1.243'
SERVER_PORT = 9596


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:

    # base paths
    BASE_PATH = os.getcwd().replace( ";", "" )

    def __init__( self ):
        self._handle = int(sys.argv[ 1 ])
        self._path = sys.argv[ 0 ]

        # init the connection
        self._conn = MpTVConnector.MpTVConnector()
        self._conn.connect(SERVER_HOST, SERVER_PORT)


        if sys.argv[ 2 ]:
            chanUrl = sys.argv[ 2 ]
            if chanUrl.startswith("?G"):
                # this is a group
                ok = self.get_channel(chanUrl[ 3: ])
            elif chanUrl.startswith("?C"):
                ok = self.choose_channel(chanUrl[ 3: ])
            elif chanUrl.startswith("?K"):
                ok = self.stop_timeshift()
            else:
                print "Unknown path : ", chanUrl

        else:
            ok = self.get_groups()
        
        
        if ok:
            listitem = xbmcgui.ListItem("~~Stop timeshifting", iconImage = "DefaultFolder.png")
            ok = xbmcplugin.addDirectoryItem( handle=int( self._handle ), url="%s?K" % (self._path), listitem=listitem, isFolder=True)
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=self._handle, succeeded=ok )

    def get_groups ( self ):
        try:
            groups = self._conn.getGroups()
            icon = "DefaultFolder.png"

            for group in groups:
                listitem = xbmcgui.ListItem(group, iconImage = icon)
                url = '%s?G?%s' % (self._path, group)
                
                ok = xbmcplugin.addDirectoryItem( handle=int( self._handle ), url=url, listitem=listitem, isFolder=True, totalItems=len(groups) )
                if ( not ok ): raise
            
        except:
            print sys.exc_info()[ 1 ]
            ok = False
        
        return ok


    def get_channel ( self, group ):
        try:
            channels = self._conn.getChannels(group)
            icon = "DefaultFolder.png"

            for channel in channels:
                listitem = xbmcgui.ListItem(channel[1], iconImage = icon)
                url = '%s?C?%s' % (self._path, channel[0])
                
                ok = xbmcplugin.addDirectoryItem( handle=int( self._handle ), url=url, listitem=listitem, isFolder=True, totalItems=len(channels) )
                if ( not ok ): raise
            
        except:
            print sys.exc_info()[ 1 ]
            ok = False
        
        return ok

    def choose_channel ( self, chanId ):
        # we start the time shift, and mplayer it?
        ok = True
        try:
            result = self._conn.startTimeshift(chanId)
            
            # results is rtsp://MACHINE/stream, we want to replace machine with IP
            result = re.sub("rtsp://([^\/]+)/", "rtsp://" + SERVER_HOST + "/", result)

            if result.startswith("[ERROR]"):
                # handle the error
                xbmcgui.Dialog().ok("Error", "Error timeshifting channel\n" + result)
            else:
                listitem = xbmcgui.ListItem(result, iconImage = "DefaultFolder.png")
                url = result
                
                ok = xbmcplugin.addDirectoryItem( handle=int( self._handle ), url=url, listitem=listitem, isFolder=False, totalItems=2 )
                xbmc.Player().play(result)
        except:
            ok = False

        return ok
    
    def stop_timeshift (self ):
        try:
            result = self._conn.stopTimeshift()
        except:
            return False


        return False





# vim: set sw=4 ts=4 sts=4:
