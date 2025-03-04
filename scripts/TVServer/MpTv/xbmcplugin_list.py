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
import urllib

import MpTVConnector


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:

    # base paths
    BASE_PATH = os.getcwd().replace( ";", "" )

    def __init__( self ):
        self._handle = int(sys.argv[ 1 ])
        self._path = sys.argv[ 0 ]

        self._get_settings()

        server_host = str(self.settings["mptvserver"])
        server_port = int(self.settings["mptvport"])

        # init the connection
        self._conn = MpTVConnector.MpTVConnector()
        self._conn.connect(server_host, server_port)


        showshift = False
        if sys.argv[ 2 ]:
            chanUrl = sys.argv[ 2 ]
            if chanUrl.startswith("?G"):
                # this is a group
                ok = self.get_channel(chanUrl[ 3: ])
                showshift = True
            elif chanUrl.startswith("?C"):
                ok = self.choose_channel(chanUrl[ 3: ])
                showshift = True
            elif chanUrl.startswith("?K"):
                ok = self.stop_timeshift()
                showshift = True
            elif chanUrl.startswith("?S"):
                ok = self.choose_show(showUrl[ 3: ])
            elif chanUrl.startswith("?D"):
                ok = self.delete_show(chanUrl[ 3: ])
            elif chanUrl.startswith("?R"):
                xbmc.executebuiltin("Container.Refresh")
                ok = True
            elif chanUrl.startswith("?PS"):
                # play shows
                ok = self.get_shows()
            elif chanUrl.startswith("?PL"):
                # play live TV
                ok = self.get_groups()
                showshift = True
            else:
                print "Unknown path : ", chanUrl

        else:
            ok = self.main_menu()


        if ok:
            if showshift:
                curShift = self._conn.isTimeshifting();
                if curShift[0] == "True":
                    curProgram = curShift[3] + " - " + curShift[4] + " [" + curShift[5] + "]"
                    listitem = xbmcgui.ListItem("Current Timeshift: " + curProgram, iconImage = "DefaultFolder.png")

                    # give the item a stop timeshift context menu
                    listitem.addContextMenuItems([("Stop Timeshifting", "XBMC.RunPlugin(%s?K)" % (sys.argv[0]))])
                    ok = xbmcplugin.addDirectoryItem(handle = int(self._handle), url=curShift[1], listitem=listitem, isFolder = False)

        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=self._handle, succeeded=ok, cacheToDisc=False )


    def _get_settings( self ):
        self.settings = {}
        self.settings["mptvserver" ] = xbmcplugin.getSetting("mptvserver")
        self.settings["mptvport"   ] = xbmcplugin.getSetting("mptvport"  )
        self.settings["mpsharename"] = xbmcplugin.getSetting("mpsharename")
        self.settings["extsort"] = ( xbmcplugin.getSetting("extsort") == "true" )

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


    def main_menu ( self ):
        try:
            listitem = xbmcgui.ListItem("Live TV", iconImage = "DefaultFolder.png")
            ok = xbmcplugin.addDirectoryItem( handle=int( self._handle ), url="%s?PL" % (self._path), listitem=listitem, isFolder=True)
            listitem = xbmcgui.ListItem("Recorded Shows", iconImage = "DefaultFolder.png")
            ok = xbmcplugin.addDirectoryItem( handle=int( self._handle ), url="%s?PS" % (self._path), listitem=listitem, isFolder=True)
        except:
            print sys.exc_info()[ 1 ]
            ok = False
        return ok


    def get_channel ( self, group ):
        try:
            channels = self._conn.getChannels(group)
            icon = "DefaultFolder.png"

            for channel in channels:
                channelStr = channel[1]
                if channel[2] != "":
                    channelStr += " - " + channel[2]
                if channel[3] != "":
                    channelStr += " [" + channel[3] + "]"
                listitem = xbmcgui.ListItem(channelStr, iconImage = icon)
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
            xbmc.Player().stop()
	    if self._conn.isTimeshifting()[0] == "True":
                self_.conn.stopTimeshift()
            print "Timeshifting channel : " + chanId
            result = self._conn.startTimeshift(chanId)
            
            # results is rtsp://MACHINE/stream, we want to replace machine with IP
            # result = re.sub("rtsp://([^\/]+)/", "rtsp://" + SERVER_HOST + "/", result)
            # disabled - server now resolves for us.

            if result.startswith("[ERROR]"):
                # handle the error
                xbmcgui.Dialog().ok("Error", "Error timeshifting channel\n" + result)
            else:
                xbmc.Player().play(result)
            
	    xbmcplugin.endOfDirectory( succeeded=False )

        except:
            ok = False

        return ok
    
    def stop_timeshift (self ):
        try:
            result = self._conn.stopTimeshift()
            xbmc.executebuiltin("Container.Refresh")
        except:
            return False


        return False


    def get_shows ( self ):

        extended_sort = False
        ok = True

        try:
            shows = self._conn.getShows()
            icon = "DefaultFolder.png"

            server_host = str(self.settings["mptvserver"])
            sharepath = str(self.settings["mpsharename"])
            hostIp = str(server_host)
            extended_sort = self.settings["extsort"]

            baseurl = xbmc.translatePath("smb://" + hostIp + "/" + sharepath + "/")

            # check for show list where the only entry is blank
            # and if so, empty the list
            if len(shows) == 1:
		    if len(shows[0][0]) == 0:
		        shows=()
            for show in shows:
                recID = show[0]
                title = show[1]
                # limit the length of descr as it's used in the URL
                descr = show[2][0:1023]
                genre = show[3]
                seen  = show[4]
                start = show[5]
                end   = show[6]
                fname = show[7]
                chan  = show[8]

                # later versions provide more info
                if len(show)>=10:
                    runtime = str(int(show[9]) / 60)
                    streamURL = show[10]
                else:
                    runtime = ""
                    streamURL = ""

                # clean up descr for adding to title, as it may have embedded newlines
                descrShort=descr.replace('\n',' ')[0:128]

                # construct the smb:// URL from the
                # original filename and the configured
                # sharename
                # TODO: make this a configurable format
                # like the XBMCMythTV scripts do

                basename = str(fname).rsplit('\\',1)[1]

                # we use the filename (less the extension) as the title
                showStr = basename.rsplit('.',1)[0] + ' - ' + descrShort

                smbName = baseurl + basename

                # use the RTSP URL if given
                # TODO: bypass all the SMB stuff above when using this
                # TODO: get this working - the stream never plays!
                #if streamURL != "":
                #    smbName=streamURL

                # MP doesn't give us a channel name,
                # so we fudge it from the filename
                chan=basename.split(' - ',3)[1]

                size = os.path.getsize(smbName)
                studio = chan

                listitem = xbmcgui.ListItem(showStr, iconImage = icon)

                # get date "31:01:2008" from start "1/31/2008 3:25:01 PM"
                startdate=start.split(" ")[0].split("/")
                if len(startdate[0]) == 1:
                    startdate[0] = "0" + startdate[0]
                date = startdate[1]+":"+startdate[0]+":"+startdate[2]

                # add "Delete <name of show>" to context menu
                # get "Delete" string from locale index 117
                if len(title) > 26:
                    deleteLabel = xbmc.getLocalizedString(117) + " " + title[0:23] + "..."
                else:
                    deleteLabel = xbmc.getLocalizedString(117) + " " + title

                listitem.addContextMenuItems([
                    (deleteLabel,	"XBMC.RunPlugin(%s?D&%s&%s)"%(sys.argv[0],recID,title))
                ])

                # we'll need "url" this when we start calling choose_show()
                # but for now we go straight to the player by using the smb name
                # TODO: encode only the recID, and have choose_show() get the info itself
                #url = '%s?S?%s&%s&%s&%s' % (self._path, urllib.quote(smbName),urllib.quote(title),urllib.quote(genre),urllib.quote(descr))
                #ok = xbmcplugin.addDirectoryItem( handle=int( self._handle ), url=url, listitem=listitem, isFolder=False, totalItems=len(shows) )

                listitem.setInfo( type="Video", infoLabels={
                    "Title": title,
                    "Tvshowtitle": title,
                    "Genre": genre,
                    "Plot": descr,
                    #"Plotoutline": descr,
                    "Size": size,
                    "Studio": studio,
                    "Date": date,
                    "Year": int(startdate[2]),
                    "Playcount": int(seen),
                    "Count": 1,
                } )
                if runtime != "":
                    listitem.setInfo(  type="Video", infoLabels={ "Duration": runtime } )
                ok = xbmcplugin.addDirectoryItem( handle=int( self._handle ), url=smbName, listitem=listitem, isFolder=False, totalItems=len(shows) )
                if ( not ok ): raise

        except:
            print sys.exc_info()[ 1 ]
            ok = False

        if ( ok and extended_sort ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_TITLE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_SIZE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_STUDIO )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_PROGRAM_COUNT )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_EPISODE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_FILE )

        return ok

    def delete_show ( self, args ):
	# we get the file ID and title and request its deletion
	# Note: still in beta

        ok = True
        try:
            args=args.split("&",2)
            recID=urllib.unquote(args[0])
            title=urllib.unquote(args[1])
            print "delete_show: " + title + " (" + recID + ")"
            if xbmcgui.Dialog().yesno("Delete", "Delete "+title+"?"):
                result = self._conn.deleteShow(recID)

                if result.startswith("[ERROR]"):
                    # handle the error, or maybe we can just "raise"
                    xbmcgui.Dialog().ok("Error", "Error deleting " + title + "\n" + result)
		    ok = False
                else:
		    # we probably need to refresh the list, somehow
		    # or remove the listitem, or navigate back
		    xbmc.executebuiltin("Container.Refresh")
		    ok = True

        except:
            print "delete failed"
            xbmcgui.Dialog().ok("Error", "An error ocurred deleting the selected show")
            ok = False
            raise

	return ok

    def choose_show ( self, args ):
        # NOTE: ***** not used yet *****
        # we get the filename and add to the playlist

        ok = True
        try:
            args=args.split("&",4)
            smbName=urllib.unquote(args[0])
            print "choose_show: Playing show: " + smbName
            title=urllib.unquote(args[1])
            genre=urllib.unquote(args[2])
            descr=urllib.unquote(args[3])

            print "playing " + smbName

            thumbnail = xbmc.getInfoImage( "ListItem.Thumb" )

            filesize = os.path.getsize(smbName)

            playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
            # clear any possible entries
            playlist.clear()
            # set the default icon
            icon = "DefaultVideo.png"
            # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
            listitem = xbmcgui.ListItem( title, iconImage=icon, thumbnailImage=thumbnail )
            # set the key information
            listitem.setInfo( "video", {
			"Title": title,
			"Tvshowtitle": title,
			"Genre": genre,
			"Plotoutline": descr,
			"Size": filesize,
			} )
            # add item to our playlist
            playlist.add( smbName, listitem )
            player = xbmc.Player()
            player.play( playlist )
        except:
            print "playing failed"
            xbmcgui.Dialog().ok("Error", "An error ocurred playing the selected show")
            ok = False
            raise

        # set some sort methods
        if ( ok ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_TITLE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_SIZE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_STUDIO )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_PROGRAM_COUNT )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_EPISODE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_FILE )

        # saw this in the MythTV plug-in
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

        return ok


    def stop_playing (self ):
        # not used yet
        try:
            result = self._conn.stopPlaying()
        except:
            return False


        return False
