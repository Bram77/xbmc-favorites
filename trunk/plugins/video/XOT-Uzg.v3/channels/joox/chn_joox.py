#===============================================================================
# Import the default modules
#===============================================================================
import xbmc, xbmcgui
import re, sys, os

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
register.channelRegister.append('chn_joox.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="joox")')

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
        
        self.guid = "320E8790-42F4-11DD-9B2E-660356D89593"
        self.icon = "jooxthumb.png"
        self.iconLarge = "jooxlarge.png"
        self.noImage = "jooximage.png"
        self.channelName = "Joox.Net"
        self.channelDescription = "Archive containing a large number of online Divx clips from Stage6."
        self.moduleName = "chn_joox.py"
        self.maxXotVersion = "3.0.0"
        
        self.mainListUri = "http://www.joox.net"
        self.baseUrl = "http://www.joox.net"
        self.onUpDownUpdateEnabled = False
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Update Item", "CtMnUpdateItem", itemTypes="video", completeStatus=None))            
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
                
        self.requiresLogon = False
        
        self.episodeItemRegex = '<a href="\.([^"]+)">([^>]+)</a><br />' # used for the ParseMainList
        self.videoItemRegex = '<a href="\.([^"]*/)(id/)(\d+)"( style="color:\s*white;"\s*)*>([^>]+)</a><br'   # used for the CreateVideoItem 
        self.folderItemRegex = '<a href="\.([^"]*/)(cat/)(\d+)"( style="color:\s*white;"\s*)*>([^>]+)</a><br'  # used for the CreateFolderItem
        # decrepated. Using url based on ID now
        #self.mediaUrlRegex = '<param name="src" value="([^"]+)" />'    # used for the UpdateVideoItem
        
        #========================================================================== 
        # non standard items
        self.topDescription = ""
        
        return True
      
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
    # Custom Methodes, in chronological order   
    #==============================================================================
    def ParseMainList(self):
        # first retrieve normal items
        items = chn_class.Channel.ParseMainList(self)
        
        # create newly added movies  item
        item = common.clistItem("Newly Added Movies",self.baseUrl)
        item.icon = self.folderIcon
        items.append(item)
        
        # sort by name
        if self.episodeSort:
            items.sort(lambda x, y: cmp(x.name.lower(),y.name.lower()))
        
        return items
      
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #logFile.debug('starting CreateEpisodeItem for %s', self.channelName)
        
        # dummy class
        _item = common.clistItem(resultSet[1], self.baseUrl + resultSet[0])
        _item.icon = self.folderIcon

        _item.complete = True
        return _item
    
    #==============================================================================
    def PreProcessFolderList(self, data):
        """
        Accepts an data from the ProcessFolderList Methode, BEFORE the items are
        processed. Allows setting of parameters (like title etc). No return value!
        """
        
        _items = []
        
        _items = []
        #description
        _matches = common.DoRegexFindAll('/ <a href="\.([^"]+)">([^<]+)</a>', data)
        
        # Because of the Newly Added Movies item, we must check if we are at the main 
        # page or not. The mainpage does not have the / <a href and thus no matches
        if len(_matches) > 0:
            # we are not on the mainpage anymore
            
            #description
            _matches = common.DoRegexFindAll('/ <a href="\.([^"]+)">([^<]+)</a>', data)
            
            if self.folderHistory[-1].description == "Please wait while loading data":
                self.previousDescription = _matches[0][1]
            else:
                self.previousDescription = self.folderHistory[-1].description
            
            # now remove everything above the sidebar HTML to prevent problems with new 
            # links on the site
            data = common.DoRegexFindAll('<div id="body-sidebar">(([\n\r]|.)*)', data)
            if len(data)>0:
                if len(data[0])>0:
                    data = data[0][0]
        else:
            # we remain on the mainpage for newly added movies.
            self.previousDescription = "Newly Added Movies"
            data = common.DoRegexFindAll('<div class="xboxcontent">([\w\W]*)<div class="clear"', data)
            if len(data)>0:
                data = data[0]

        return (data, _items)
        
    
    #==============================================================================
    def CreateFolderItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #logFile.debug('starting CreateFolderItem for %s', self.channelName)
        item = common.clistItem(resultSet[4], self.baseUrl + resultSet[0]+resultSet[1]+resultSet[2])
        item.description = "%s\n%s" % (self.previousDescription, item.name)
        item.icon = self.folderIcon
        item.thumb = self.noImage
        item.type = 'folder'
        
        item.complete = True
        return item
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #logFile.debug('starting CreateVideoItem for %s', self.channelName)
        item = common.clistItem(resultSet[4], self.baseUrl + resultSet[0]+resultSet[1]+resultSet[2])
        item.description = "%s\n%s" % (self.previousDescription, item.name)
        item.icon = self.icon
        item.thumb = self.noImage
        item.type = 'video'
        item.mediaurl = "http://video.stage6.com/%s/.divx" % (resultSet[2])
        
        item.downloadable = True
        
        # getting the URL is part of the PlayVideo
        item.complete = True
        return item
    
    #============================================================================== 
    def DownloadEpisode(self, item):
        #check if data is already present and if video or folder
        if item.type == 'folder':
            logFile.warning("Cannot download a folder")
        elif item.type == 'video':
            if item.complete == False:
                logFile.info("Fetching MediaUrl for VideoItem")
                item = self.UpdateVideoItem(item)
            _destFilename = item.name + ".divx"
            if item.mediaurl=="":
                logFile.error("Cannot determine mediaurl")
                return item
            logFile.info("Going to download %s", _destFilename)
            _downLoader = uriHandler.Download(item.mediaurl, _destFilename)
            item.downloaded = True
            return item
        else:
            logFile.warning('Error determining folder/video type of selected item');