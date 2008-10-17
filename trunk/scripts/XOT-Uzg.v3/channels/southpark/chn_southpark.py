#===============================================================================
# Import the default modules
#===============================================================================
import xbmc, xbmcgui
import re, sys, os
import urlparse
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
#register.channelButtonRegister.append(108)

register.channelRegister.append('chn_southpark.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="southpark")')

#===============================================================================
# main Channel Class
#===============================================================================
class Channel(chn_class.Channel):
    """
    main class from which all channels inherit
    """
    
    #===============================================================================
    def InitialiseVariables(self):
        """
        Used for the initialisation of user defined parameters. All should be 
        present, but can be adjusted
        """
        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self)
        self.guid = "3ac3d6d0-5b2a-11dd-ae16-0800200c9a66"
        self.icon = "southparkicon.png"
        self.iconLarge = "southparklarge.png"
        self.noImage = "southparkimage.png"
        self.channelName = "Southpark"
        self.maxXotVersion = "3.2.0"
        self.channelDescription = "Southpark Epsides."
        self.moduleName = "chn_southpark.py"
        self.mainListUri = "http://www.southparkstudios.com/"
        self.baseUrl = "http://www.southparkstudios.com/"
        self.onUpDownUpdateEnabled = True
        
        self.contextMenuItems = []
#        self.contextMenuItems.append(contextmenu.ContextMenuItem("Update Item", "CtMnUpdateItem", itemTypes="video", completeStatus=None))            
#        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
                
        self.requiresLogon = False
        
        self.episodeItemRegex = '<li><a href="(/guide/season/[^"]+)">(\d+)</a></li>' # used for the ParseMainList
        self.videoItemRegex = '<div class="image">\W+<a href="([^"]+)"><img src="([^"]+)" alt="[^"]+" /></a>\W+</div>\W[^:]+<span class="epnumber">Episode: \d(\d+)</span>\W+<span[^>]+>([^<]+)</span>\W+<span class="epdate">([^<]+)</span>\W+<span class="epdesc">([^/]+)</span>\W+</a>\W+<div class="more">\W+<a href="/episodes/(\d+)/"'   # used for the CreateVideoItem 
#        self.folderItemRegex = '<a href="\.([^"]*/)(cat/)(\d+)"( style="color:\s*white;"\s*)*>([^>]+)</a><br'  # used for the CreateFolderItem
        self.mediaUrlRegex = '<param name="src" value="([^"]+)" />'    # used for the UpdateVideoItem
        return True
      
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
#    def CtMnUpdateItem(self, selectedIndex):
#        logFile.debug('Updating item (Called from ContextMenu)')
#        self.onUpDown(ignoreDisabled = True)
#    
#    def CtMnDownloadItem(self, selectedIndex):
#        item = self.listItems[selectedIndex]
#        self.listItems[selectedIndex] = self.DownloadEpisode(item)

    def CtMnPlayMplayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, "mplayer")
    
    def CtMnPlayDVDPlayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item,"dvdplayer")    
    
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateEpisodeItem for %s', self.channelName)
        
        # <li><a href="(/guide/season/[^"]+)">(\d+)</a></li>
        item = common.clistItem("Season %02d" % int(resultSet[1]), urlparse.urljoin(self.baseUrl, resultSet[0]))
        item.icon = self.icon
        item.complete = True
        return item
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateVideoItem for %s', self.channelName)
        #logFile.debug(resultSet)
        
        #                                  0 = href           1 = image                                               
        #<div class="image">\W+<a href="([^"]+)"><img src="([^"]+)" alt="[^"]+" /></a>\W+</div>\W[^:]+<span class="epnumber">
        #            2 = number                         3 = title                              4 = date                      5 = desc
        #Episode: \d(\d+)</span>\W+<span[^>]+>([^<]+)</span>\W+<span class="epdate">([^<]+)</span>\W+<span class="epdesc">([^/]+)</span>
        #                                             6 = episode id
        #\W+</a>\W+<div class="more">\W+<a href="/episodes/(\d+)/"item = common.clistItem("%s %s" % (resultSet[2], resultSet[3]), urlparse.urljoin(self.baseUrl, resultSet[0]))
        
        infoUrl = "http://media.mtvnservices.com/video/feed.jhtml?type=network&uri=mgid%3Acms%3Acontent%3Asouthparkstudios.com%3A" + resultSet[6] 
        item = common.clistItem("%s %s" % (resultSet[2], resultSet[3]), infoUrl)
        
        item.thumb = self.noImage
        item.thumbUrl = resultSet[1]
        item.date = resultSet[4]
        item.icon = self.icon
        item.description = resultSet[5]                                
        item.type = 'video'
        item.complete = False
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. Usually retrieves the MediaURL 
        and the Thumb! It should return a completed item. 
        """
        logFile.info('starting UpdateVideoItem for %s (%s)', item.name, self.channelName)
        
        # download the thumb
        item.thumb = self.CacheThumb(item.thumbUrl)        
        
        # load the url and get the info for the media urls:
        data = uriHandler.Open(item.url, pb=False)
        acts = common.DoRegexFindAll('<media:content url="([^=]+=\d+&amp;hiLoPref=hi)"[^>]+>', data)
        
        #retrieve the first real url
        rtmpUrls = []
        if len(acts)>0:
            rtmpData = uriHandler.Open(common.StripAmp(acts[0]), pb=False)
            
            #<src>rtmp://cp40493.edgefcs.net/ondemand/comedystor/_!/com/sp/acts/Season01/E_0102/compressed/flv/0102_3_DI_640x480_500kbps.flv</src>
            #rtmp://cp40493.edgefcs.net/ondemand?slist=comedystor/_!/com/sp/acts/Season01/E_0106/compressed/flv/0106_4_DI_640x480_700kbps 
            parts = common.DoRegexFindAll('<src>([^<]+ondemand)/([^<]+flv/\d+_)\d+(_[^<]+)[.]flv</src>', rtmpData)
            
            rtmpUrlParts = []
            for part in parts:
                rtmpUrlParts = part
            
            actNr = 1
            for act in acts:
                rtmpUrl = "%s?slist=%s%s%s" % (rtmpUrlParts[0], rtmpUrlParts[1], actNr ,rtmpUrlParts[2])
                rtmpUrls.append(rtmpUrl)
                actNr = actNr + 1
                logFile.debug('Appending: %s', rtmpUrl)
            item.mediaurl = rtmpUrls
        else:
            logFile.critical("Error retrieving rtmp stream from %s", item.url)
            
        if item.mediaurl != "":
            logFile.debug("Media url was found: %s", item.mediaurl)
            item.complete = True
        else:
            logFile.debug("Media url was not found.")
        return item    