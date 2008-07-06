#===============================================================================
# Import the default modules
#===============================================================================
from cgi import log
from common import clistItem
from uriopener import UriHandler
import xbmc, xbmcgui 
import sys, os
import string
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
register.channelRegister.append('chn_dumpert.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="dumpert")')

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
        
        self.guid = "80726A74-42F3-11DD-BBA6-A1F055D89593"
        self.icon = "dumperticon.png"
        self.iconLarge = "dumperticonlarge.png"
        self.noImage = "dumpertimage.png"
        self.backgroundImage = ""  # if not specified, the one defined in the skin is used
        self.backgroundImage16x9 = ""  # if not specified, the one defined in the skin is used
        self.channelName = "Dumpert.nl"
        self.channelDescription = "Fimpjes van Dumpert.nl"
        self.moduleName = "chn_dumpert.py"
        self.maxXotVersion = "3.1.0"
        self.sortOrder = 255 #max 255 channels
        self.buttonID = 0
        self.onUpDownUpdateEnabled = True
        
        self.mainListUri = "http://www.dumpert.nl/filmpjes/%s/"
        self.baseUrl = "http://www.dumpert.nl/mediabase/flv/%s_YTDL_1.flv.flv"
        self.playerUrl = ""
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
        
        self.requiresLogon = False
        
        self.asxAsfRegex = '<[^\s]*REF href[^"]+"([^"]+)"' # default regex for parsing ASX/ASF files
        self.episodeSort = True
        self.videoItemRegex = '<a class="item" href="([^"]+)"[^=]+="([^"]+)" alt="([^"]+)[^:]+<div class="date">([^<]+)'
        self.folderItemRegex = ''  # used for the CreateFolderItem
        
        # Changed on 2008-04-23 self.mediaUrlRegex = "'(http://www.dumpert.nl/mediabase/flv/[^']+)'"    # used for the UpdateVideoItem
        self.mediaUrlRegex = ("addVariable\('file','(http://[^']+)'\);","var flashurl = '([^']+)'")    # used for the UpdateVideoItem
        
        return True
    
    #==============================================================================
    def ParseMainList(self):
        """ 
        accepts an url and returns an list with items of type CListItem
        Items have a name and url. This is used for the filling of the progwindow
        """
        items = []
        
        for page in range(0,10):
            item = common.clistItem("Pagina %s" % (page), self.mainListUri % (page))
            item.icon = self.icon;
            items.append(item)                    
        
        item = common.clistItem("Zoeken", "searchSite")
        item.icon = self.icon;
        items.append(item)            
            
        return items
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #                         0              1             2                             3
        #<a class="item" href="([^"]+)"[^=]+="([^"]+)" alt="([^"]+)[^:]+<div class="date">([^<]+)
        logFile.debug('starting CreateVideoItem for %s', self.channelName)
        
        item = common.clistItem(resultSet[2],resultSet[0], type='video')
        item.icon = self.icon;
        item.description = resultSet[2]
        #item.mediaurl = self.baseUrl % (resultSet[1])
        item.thumb = self.noImage 
        item.thumbUrl = resultSet[1]   
        item.date = resultSet[3]                            
        item.complete = False
        item.downloadable = True
        return item
    
    #==============================================================================
    def UpdateVideoItem(self, item):        
        """
        Updates the item
        """
        item.thumb = self.CacheThumb(item.thumbUrl)
        
        data = uriHandler.Open(item.url, pb=False)
        
        for regex in self.mediaUrlRegex:
            results = common.DoRegexFindAll(regex, data)
            for result in results:
                if result != "":
                    item.mediaurl = result
                    break
        
        if item.mediaurl == "":
            item.complete = False
        else:
            item.complete = True
            
        logFile.debug("VideoItem updated (mediaUrl=%s)", item.mediaurl)
        return item
    
    #==============================================================================
    def SearchSite(self):
        """
        Creates an list of items by searching the site
        """
        items = []
        
        keyboard = xbmc.Keyboard('')
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            needle = keyboard.getText()
            if len(needle)>0:
                #convert to HTML
                needle = string.replace(needle, " ", "%20")
                searchUrl = "http://www.dumpert.nl/search/V/%s/ " % (needle)
                return self.ProcessFolderList(searchUrl)
                
        return items
    
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
        self.PlayVideoItem(item,"dvdplayer")    
    
    #============================================================================== 
    def DownloadEpisode(self, item):
        #check if data is already present and if video or folder
        if item.type == 'folder':
            logFile.warning("Cannot download a folder")
        elif item.type == 'video':
            _destFilename = item.name + ".flv"
            if item.mediaurl=="":
                logFile.error("Cannot determine mediaurl")
                return item
            logFile.info("Going to download %s", _destFilename)
            _downLoader = uriHandler.Download(item.mediaurl, _destFilename)
            item.downloaded = True
            return item
        else:
            logFile.warning('Error determining folder/video type of selected item');
   
    
