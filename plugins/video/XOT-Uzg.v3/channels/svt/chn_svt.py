from uriopener import UriHandler
import uriopener
import xbmc, xbmcgui
import sys, re, urllib, os.path, math, urlparse, types
#===============================================================================
# Make global object available
#===============================================================================
import common
import config
import controls
import contextmenu
import chn_class

logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler
#===============================================================================
# register the channels
#===============================================================================
if (sys.modules.has_key('progwindow')):
    register = sys.modules['progwindow']
elif (sys.modules.has_key('plugin')):
    register = sys.modules['plugin']
#register.channelButtonRegister.append(105)
register.channelRegister.append('chn_svt.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder)')

#===============================================================================
# main Channel Class
#===============================================================================
class Channel(chn_class.Channel):
    #===============================================================================
    # define class variables
    #===============================================================================
    def InitialiseVariables(self):
        """
        Used for the initialisation of user defined parameters. All should be 
        present, but can be adjusted
        """
        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self)
        
        self.guid = "06DB83A2-42F4-11DD-AAC1-CEFD55D89593"
        self.mainListUri = "http://svt.se/svt/road/Classic/shared/mediacenter/navigation.jsp?d=37591&frameset=true"
        self.baseUrl = "http://svt.se/svt/road/Classic/shared/mediacenter/"
        self.icon = "svticon.png"
        self.iconLarge = "svtlarge.png"
        self.noImage = "svtimage.png"
        self.channelName = "Sveriges Television"
        self.channelDescription = u'Sända från SVT'
        self.moduleName = "chn_svt.py"
        self.maxXotVersion = "3.2.0"
        
        #self.backgroundImage = ""
        #self.backgroundImage16x9 = ""
        self.requiresLogon = False
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
        
        
        self.episodeItemRegex = '<div class="enddep"><a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>\W*</div>'
        self.videoItemRegex = '(<td class="image"><img src="([^"]+)" [^>]+>\W*</td>\W*<td [^>]+>)*<div class="video"><a [^>]+ href="([^"]+)" [^>]+>([^<]+)</a>'
        self.folderItemRegex = '<div class="enddep"><a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>\W*</div>'
        self.mediaUrlRegex = '<item>\W*<file>\W*([^>]*)\W*</file>\W*<bandwidth>(\d+)</bandwidth>'
        
        """ 
            The ProcessPageNavigation method will parse the current data using the pageNavigationRegex. It will
            create a pageItem using the CreatePageItem method. If no CreatePageItem method is in the channel,
            a default one will be created with the number present in the resultset location specified in the 
            pageNavigationRegexIndex and the url from the combined resultset. If that url does not contain http://
            the self.baseUrl will be added. 
        """
        # remove the &amp; from the url
        self.pageNavigationRegex = "<a class='pView pnNumbers'  href='([^?]+\?lpage=)(\d+)([^']+)"  
        self.pageNavigationRegexIndex = 1

        #========================================================================== 
        # non standard items
        self.categoryName = ""
        
        return True
    
    #============================================================================== 
    def PreProcessFolderList(self, data):
        """
        Accepts an data from the ProcessFolderList Methode, BEFORE the items are
        processed. Allows setting of parameters (like title etc). No return value!
        """
        logFile.info("Performing Pre-Processing")
        _items = []
        
        regex = '<div id="crumbsWrap">[\W\w]+<div id="links'
        results = common.DoRegexFindAll(regex, data)
        headerData = ""
        for result in results:
            headerData = result
        
        regex = '\);">([^<]+)</a>[^/<]+'
        results = common.DoRegexFindAll(regex, headerData)
        
        self.categoryName = ""
        for result in results:
            self.categoryName = "%s%s\n" % (self.categoryName, result)
        
        return (data, _items)
    
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #logFile.info('starting CreateEpisodeItem for %s', self.channelName)
        #<div class="enddep"><a\W+href="([^"]+)"[^>]+>([^<]+)</a></div>
        #                                 0               1                                
        item = common.clistItem(resultSet[1], common.StripAmp(urlparse.urljoin(self.baseUrl, resultSet[0])))
        item.description = "%s%s" % (self.categoryName, item.name)
        item.icon = self.icon
        logFile.debug("%s (%s)", item.name, item.url)
        return item
    
    #==============================================================================
    def CreateFolderItem(self, resultSet):
        # <div class="enddep"><a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>\W*</div>
        #                                      0            1
        # <td class="image"><a[^>]+><img[^>]+src="([^"]+)"[^>]+></a></td>\W+<td[^>]+><div[^>]+><div class="enddep"><a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>\W*</div>
        #                         
        #                   0                                                                            1            2
        item = common.clistItem(resultSet[1], common.StripAmp(urlparse.urljoin(self.baseUrl, resultSet[0])))
        item.description = "%s%s" % (self.categoryName, item.name)
        item.thumb = self.noImage
        item.type = "folder"
        item.complete = True
        item.icon = self.folderIcon
        return item
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting FormatVideoItem for %s', self.channelName)
        
        #(<td class="image"><img src="([^"]+)" [^>]+>\W*</td>\W*<td [^>]+>)*<div class="video"><a [^>]+ href="([^"]+)" [^>]+>([^<]+)</a>
        #      0                        1                                                                        2              3
        name = common.ConvertHTMLEntities(resultSet[3])
        item = common.clistItem(name, common.StripAmp(urlparse.urljoin(self.baseUrl, resultSet[2])))
        
        item.description = "%s%s" % (self.categoryName, item.name)
        item.icon = self.icon
        
        if resultSet[1] != "":
            item.thumbUrl = common.StripAmp(urlparse.urljoin(self.baseUrl, resultSet[1]))
            logFile.debug("Setting thumburl=%s", item.thumbUrl)
        
        item.thumb = self.noImage
        
        item.type = 'video'
        item.complete = False
        
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. 
        """
        logFile.debug('starting UpdateVideoItem for %s (%s)', item.name, self.channelName)
        
        item.thumb = self.CacheThumb(item.thumbUrl)
        
        # retrieve the mediaurl
        data = uriHandler.Open(item.url, pb=False)
        
        # them for RAM
        asxRegex = '<a href="([^"]+asx)">'
        asxResults = common.DoRegexFindAll(asxRegex, data)
        if len(asxResults) > 0:
            item.mediaurl = "%s%s" % ("http://www.svt.se", asxResults[0]) 
        
        else:
            # first check for ASX
            ramRegex = '<a href="([^"]+ram)">'
            ramResults = common.DoRegexFindAll(ramRegex, data)
            if len(ramResults) > 0:
                item.mediaurl = "%s%s" % ("http://www.svt.se", ramResults[0]) 
                        
            else:
                # then for FLV
                flvRegex = 'so.addVariable\("pathflv"\W*,\W*"([^"]+)"\W*\)'
                flvResults = common.DoRegexFindAll(flvRegex, data)
                if len(flvResults) > 0:
                    item.mediaurl = flvResults[0]
        
        item.complete = True
        logFile.debug("Found mediaurl: %s", item.mediaurl)
        return item


    #============================================================================== 
    def PlayVideoItem(self, item, player="defaultplayer"):
        """ NOT USER EDITABLE
        Accepts an item with or without MediaUrl and playback the item. If no 
        MediaUrl is present, one will be retrieved.
        """
        item.mediaurl = self.ReplaceMediaUrl(item.mediaurl)
        logFile.info("Starting Video Playback of %s using the %s", item.mediaurl, player)
        chn_class.Channel.PlayVideoItem(self, item, player=player)
         
    #==============================================================================
    def ReplaceMediaUrl(self, mediaurl):
        """
            retrieves the real Mediaurl
        """
        # if it is a list, it was already processed. 
        if type(mediaurl) is types.ListType or type(mediaurl) is types.TupleType:
            return mediaurl
        
        elif mediaurl.find(".asx") > 0:
            logFile.debug("Parsing ASX")
            data = uriHandler.Open(mediaurl)
            results = common.DoRegexFindAll('<REF HREF\W*=\W*"([^"]+)"\W*/>', data)
            if len(results) > 0:
                mediaurl = results[0]
            
        elif mediaurl.find(".ram") > 0:
            logFile.debug("Parsing RAM")
            mediaurl = uriHandler.Open(mediaurl)
            mediaurl = mediaurl.split('\n')

        return mediaurl 
        
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def CtMnDownloadItem(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.listItems[selectedIndex] = self.DownloadEpisode(item)

    def CtMnPlayMplayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, "mplayer")
    
    def CtMnPlayDVDPlayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, "dvdplayer")    
    
    #============================================================================== 
    def DownloadEpisode(self, item):
        #check if data is already present and if video or folder
        if item.type == 'folder':
            logFile.warning("Cannot download a folder")
        
        elif item.type == 'video':
            if item.complete == False:
                logFile.info("Fetching MediaUrl for VideoItem")
                item = self.UpdateVideoItem(item)
            
            if item.mediaurl=="":
                logFile.error("Cannot determine mediaurl")
                return item
            
            if not item.mediaurl.find("flv") > 0:
                dialog = xbmcgui.Dialog()
                dialog.ok(config.appName, "Only FLV items can be downloaded.")
                return item
            
            destFilename = item.name + ".flv"
            
            logFile.info("Going to download %s", destFilename)
            downLoader = uriHandler.Download(item.mediaurl, destFilename)
            item.downloaded = True
            return item
        else:
            logFile.warning('Error determining folder/video type of selected item')