import xbmc, xbmcgui
import sys, re, urllib, os.path, math
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
#register.channelButtonRegister.append(105)
register.channelRegister.append('chn_rtl.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder)')

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
        
        self.guid = "15D92364-42F4-11DD-AF9B-7BFF55D89593"
        #self.mainListUri = "http://www.rtl.nl//system/video/menu/videomenu.xml"
        self.mainListUri = "http://www.rtl.nl/(vm=/service/miMedia/rtl_gemist.xml/)/system/video/menu/videomenu.xml"
        self.baseUrl = "http://www.rtl.nl"
        self.icon = "rtlthumb.png"
        self.iconLarge = "rtllarge.png"
        self.noImage = "rtlimage.png"
        self.channelName = "RTL 4,5&7"
        self.channelDescription = "Uitzendingen van de zenders RTL 4,5,7 & 8."
        self.moduleName = "chn_rtl.py"
        self.maxXotVersion = "3.1.0"
        
        self.backgroundImage = "background-rtl.png"
        self.backgroundImage16x9 = "background-rtl-16x9.png"
        self.requiresLogon = False
        self.sortOrder = 5
        
        self.episodeItemRegex = '<li class="folder" rel="([^"]+)videomenu.xml">([^<]+)</li>'
        self.videoItemRegex = '<li class="video" (thumb="([^"]+)" ){0,1}(ctime="\d+" ){0,1}rel="([^"]*/)([^"]+)" (link="([^"]+)"){0,1}>([^<]+)</li>' 
        self.folderItemRegex = '<li class="folder" rel="([^"]*/)([^"]+)">([^<]+)</li>'
        #self.mediaUrlRegex = '<item target="web">[^<]*<file>([^>]*)</file>\W*<description>[^>]*>\W*<bandwidth>(\d+)</bandwidth>'
        self.mediaUrlRegex = '<item>\W*<file>\W*([^>]*)\W*</file>\W*<bandwidth>(\d+)</bandwidth>'
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play lowest bitrate stream", "CtMnPlayLow", itemTypes="video", completeStatus=True))            
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play highest bitrate stream", "CtMnPlayHigh", itemTypes="video", completeStatus=True))
        
        #============================================================================== 
        # non standard items
        self.PreProcessRegex = '<ul title="([^"]*)" rel="([^"]*)videomenu.xml"'
        self.progTitle = ""
        self.videoMenu = ""

        return True
    
    #==============================================================================
    def ParseMainList(self):
        # call the main list
        items = chn_class.Channel.ParseMainList(self)
        
        # then add GTST
        gtstItem = common.clistItem('Goede Tijden, Slechte Tijden (Oud)', 'http://www.rtl.nl/(vm=/service/miMedia/rtl_gemist.xml/)/system/video/menu/soaps/gtst/videomenu.xml', 'folder')
        gtstItem.icon = self.folderIcon
        gtstItem.thumb = self.noImage
        items.append(gtstItem)
        
        gtstItem = common.clistItem('Goede Tijden, Slechte Tijden', 'http://www.rtl.nl/(vm=/service/miMedia/rtl_gemist.xml/)/system/video/menu/soaps/gtst/home/videomenu.xml', 'folder')
        gtstItem.icon = self.folderIcon
        gtstItem.thumb = self.noImage
        items.append(gtstItem)
        
        # sort by name
        if self.episodeSort:
            items.sort(lambda x, y: cmp(x.name.lower(),y.name.lower()))
        
        return items
        
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #logFile.info('starting CreateEpisodeItem for %s', self.channelName)
        item = common.clistItem(resultSet[1], "http://www.rtl.nl/(vm="+ resultSet[0] + ")/system/video/menu" + resultSet[0] + "videomenu.xml")
        item.icon = self.folderIcon
        return item
    
    #==============================================================================
    def PreProcessFolderList(self, data):
        """
        Accepts an data from the ProcessFolderList Methode, BEFORE the items are
        processed. Allows setting of parameters (like title etc). No return value!
        """
        _items = []
        
        if len(self.folderHistory)==1:
            # The first folder to be processed
            matches = common.DoRegexFindAll('<ul title="([^"]*)" rel="([^"]*)videomenu.xml"', data)
            self.progTitle = matches[0][0]
            self.videoMenu = matches[0][1]
            
        return (data, _items)
    
    #==============================================================================
    def CreateFolderItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateFolderItem for %s', self.channelName)
        item = common.clistItem(resultSet[2], self.RtlFolderUri(resultSet[0],resultSet[1]))
        if len(self.folderHistory)==1:
            item.description = "%s \n%s \n" %(self.progTitle ,item.name)
        else:
            item.description = "%s \n%s \n" %(self.folderHistory[-1].description ,item.name)
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
        logFile.debug('starting FormatVideoItem for %s', self.channelName)
        #logFile.debug(resultSet)
        item = common.clistItem(resultSet[7], self.RtlVideoUri(self.videoMenu, resultSet[3] + resultSet[4]))
        if len(self.folderHistory)>1:
            item.description = self.folderHistory[-1].description + item.name
        else:
            item.description = item.name
        item.icon = self.icon
        item.thumb = self.noImage
        item.thumbUrl = urlparse.urljoin(self.baseUrl, resultSet[1])
        item.type = 'video'
        item.complete = False
        
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. 
        """
        logFile.debug('starting UpdateVideoItem for %s (%s)',item.name, self.channelName)
        
        data = uriHandler.Open(item.url, pb=False)

        matches = common.DoRegexFindAll(self.mediaUrlRegex, data)
        logFile.debug("Possible Matches: %s",matches)

        # sort mediaurl -> get highest quality
        matches.sort(lambda x, y: int(y[1])-int(x[1]))

        mediaUrls = []
        for match in matches:
            mediaUrls.append(match[0])
        
        logFile.debug("Sorted Matches: %s", mediaUrls)                
        item.mediaurl = mediaUrls

        logFile.info('finishing UpdateVideoItem. Media url = %s', item.mediaurl)
        
        item.thumb = self.CacheThumb(item.thumbUrl)
        item.complete = True
        return item
    
    #============================================================================== 
    def CtMnPlayLow(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, lowBitrate=True)

    def CtMnPlayHigh(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, lowBitrate=False)

    #============================================================================== 
    def PlayVideoItem(self, item, lowBitrate=False, player=""):
        # overriding the default playvideoitem to allow selection of low and high bitrate
        if len(item.mediaurl) > 1:
            # create dummy item for playback
            dummy = common.clistItem(item.name, item.url, item.type)
            dummy.complete = True
            
            #select the right url
            if not lowBitrate:
                dummy.mediaurl = item.mediaurl[0]
                logFile.debug("Starting playback of the high bitrate mediaUrl (%s)", dummy.mediaurl)
            else:
                dummy.mediaurl = item.mediaurl[-1]
                logFile.debug("Starting playback of the low bitrate mediaUrl (%s)", dummy.mediaurl)
            
            # play it
            chn_class.Channel.PlayVideoItem(self, dummy, player)            
        else:
            logFile.debug("Starting playback of the only available mediaUrl (%s)", item.mediaurl)
            chn_class.Channel.PlayVideoItem(self, item, player)
            

    #===============================================================================
    def RtlFolderUri(self, folder, filename):
        return 'http://www.rtl.nl/(vm'+ folder + ')/system/video/menu' + folder + filename

    #===============================================================================    
    def RtlVideoUri(self, videoMenu, videoURL):
        return 'http://www.rtl.nl/(vm'+ videoMenu + ')' + videoURL
    
    