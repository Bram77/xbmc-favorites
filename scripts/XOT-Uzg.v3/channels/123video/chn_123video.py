import xbmc, xbmcgui
import sys, re, urllib, os.path, math
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
register.channelRegister.append('chn_123video.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder)')

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
        
        self.mainListUri = "http://www.123video.nl"
        self.baseUrl = "http://www.123video.nl/"
        self.icon = "123icon.png"
        self.iconLarge = "123large.png"
        self.noImage = "123image.png"
        self.channelName = "123Video.nl"
        self.channelDescription = "Videos van www.123video.nl"
        self.moduleName = "chn_123video.py"
        self.maxXotVersion = "3.1.0"
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Update Item", "CtMnUpdateItem", itemTypes="video", completeStatus=None))            
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
        
        #self.backgroundImage = ""
        #self.backgroundImage16x9 = ""
        self.requiresLogon = False
        #self.sortOrder = 5
        
        self.episodeItemRegex = '<option value="(\d+)">([^<]+)</option>'
        self.videoItemRegex = '<a onFocus="this.blur\(\);" href="/playvideos.asp\?MovieID=(\d+)[^"]+" title="([^"]+)" [^>]+><img src="([^"]+)" width="\d+" /></a>[^:]+:[^:]+:[^:]+[^"]+"[^"]+">([^<]+)' 
        self.folderItemRegex = ''# Pages are now seperate items '&nbsp;&nbsp;<a href="(/video.asp\?Page=\d+)[^"]+(&CatID=\d+)&[^"]+" title="Ga naar pagina (\d+)'
                
        """ 
            The ProcessPageNavigation method will parse the current data using the pageNavigationRegex. It will
            create a pageItem using the CreatePageItem method. If no CreatePageItem method is in the channel,
            a default one will be created with the number present in the resultset location specified in the 
            pageNavigationRegexIndex and the url from the combined resultset. If that url does not contain http://
            the self.baseUrl will be added. 
        """
        self.pageNavigationRegex = '<a href="(/video.asp\?Page=)(\d+)([^"]+)" title="Ga naar pagina'  
        self.pageNavigationRegexIndex = 1 
       
        
        #============================================================================== 
        # non standard items
        self.ipVideoServer = "85.17.191.65"
        #http://85.17.191.44/263/263621.flv
        return True
    
    #==============================================================================
    def ParseMainList(self):
        #get base items and add some other categories
        items = chn_class.Channel.ParseMainList(self)        
        #remove xxx category
        items.pop() 
        
        recent = common.clistItem("Meest recente video's", "%s/video.asp?So=0" % self.mainListUri)
        recent.icon = self.folderIcon
        items.insert(0, recent)
        
        best = common.clistItem("Best beoordeelde video's", "%s/video.asp?So=2" % self.mainListUri)
        best.icon = self.folderIcon
        items.insert(0, best)
        
        watched = common.clistItem("Meest bekeken video's", "%s/video.asp?So=1" % self.mainListUri)
        watched.icon = self.folderIcon
        items.insert(0, watched)
        
        spoken = common.clistItem("Meest besproken video's", "%s/video.asp?So=2" % self.mainListUri)
        spoken.icon = self.folderIcon
        items.insert(0, spoken)
                
#    <a onfocus="this.blur();" href="/video.asp?So=0" title="Meest recente video's" onmouseover="fOver(this);return true;">Meest recente video's</a> |
#    <a onfocus="this.blur();" href="/video.asp?So=2" title="Best beoordeelde video's" onmouseover="fOver(this);return true;">Best beoordeelde video's</a> |
#    <a onfocus="this.blur();" href="/video.asp?So=1" title="Meest bekeken video's" onmouseover="fOver(this);return true;">Meest bekeken video's</a> |
#    <a onfocus="this.blur();" href="/video.asp?So=3" title="Meest besproken video's" onmouseover="fOver(this);return true;">Meest besproken video's</a>
        
        return items
    
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #logFile.info('starting CreateEpisodeItem for %s', self.channelName)
        item = common.clistItem(resultSet[1], "http://www.123video.nl/video.asp?CatID=%s" % resultSet[0])
        item.icon = self.folderIcon
        return item
    
    #==============================================================================
    def PreProcessFolderList(self, data):
        """
        Accepts an data from the ProcessFolderList Methode, BEFORE the items are
        processed. Allows setting of parameters (like title etc). No return value!
        """
        logFile.info("Performing Pre-Processing")
        
        items = []
        # first part of the data to prevent double pages
        data = common.DoRegexFindAll('<div class="resultBox">([\w\W]+)', data)[0]
                
        logFile.debug("Pre-Processing finished")
        return (data, items)
    
    #==============================================================================
    def CreateFolderItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateFolderItem for %s', self.channelName)
        item = common.clistItem("Pagina %02i" % int(resultSet[2]), "%s%s%s" % (self.mainListUri, resultSet[0], resultSet[1]))
        item.description = item.name
        item.icon = self.folderIcon
        item.type = 'folder'
        item.thumb = self.noImage
        item.complete = True
        return item
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #logFile.debug('starting FormatVideoItem for %s', self.channelName)
        
        item = common.clistItem(resultSet[1].title(), "http://www.123video.nl/playvideo.asp?MovieID=%s" % resultSet[0])
        item.icon = self.icon
        item.type = 'video'
        item.date = resultSet[3].lstrip()
        item.description = item.name
        if len(resultSet[0]) == 6:        
            item.mediaurl = "http://%s/%s/%s.flv" % (self.ipVideoServer, resultSet[0][0:3], resultSet[0])
        elif len(resultSet[0]) == 5:
            item.mediaurl = "http://%s/%s/%s.flv" % (self.ipVideoServer, resultSet[0][0:2], resultSet[0])
        elif len(resultSet[0]) == 4:
            item.mediaurl = "http://%s/%s/%s.flv" % (self.ipVideoServer, resultSet[0][0:1], resultSet[0])
        else:
            item.mediaurl = ""
        
        #logFile.debug("len=%s (%s), %s", len(resultSet[0]) ,resultSet[0], item.mediaurl)               
                
        #Do this on mouseover
        #item.thumb = self.CacheThumb(resultSet[2])
        item.thumbUrl = resultSet[2]
        item.complete = False
        
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. Usually retrieves the MediaURL 
        and the Thumb! It should return a completed item. 
        """
        logFile.info('starting UpdateVideoItem for %s (%s)', item.name, self.channelName)
        
        item.thumb = self.CacheThumb(item.thumbUrl)
        item.complete = True
        return item
    
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def CtMnUpdateItem(self, selectedIndex):
        logFile.debug('Updating item (Called from ContextMenu)')
        self.onUpDown(ignoreDisabled = True)
    
    def CtMnDownloadItem(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.listItems[selectedIndex] = self.DownloadEpisode(item)

    def CtMnPlayMplayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, "mplayer")
    
    def CtMnPlayDVDPlayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item,"dvdplayer")    
    
    #============================================================================== 
    def DownloadEpisode(self, item):
        #check if data is already present and if video or folder
        if item.type == 'folder':
            logFile.warning("Cannot download a folder")
        elif item.type == 'video':
            if item.complete == False:
                logFile.info("Fetching MediaUrl for VideoItem")
                item = self.UpdateVideoItem(item)
            destFilename = item.name + ".flv"
            if item.mediaurl=="":
                logFile.error("Cannot determine mediaurl")
                return item
            logFile.info("Going to download %s", destFilename)
            downLoader = uriHandler.Download(item.mediaurl, destFilename)
            item.downloaded = True
            return item
        else:
            logFile.warning('Error determining folder/video type of selected item');