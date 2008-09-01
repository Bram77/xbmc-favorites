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
#register.channelButtonRegister.append(110)
register.channelRegister.append('chn_sbs6.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder)')

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
        
        self.guid = "11A6D5FC-42F4-11DD-AD55-12FF55D89593"
        self.mainListUri = "http://www.pczapper.tv/pzc5/lfui/index.php?t=p&m=28304&pm=0"
        self.icon = "sbs6icon.png"
        self.iconLarge = "sbs6large.png"
        self.noImage = "sbs6image.png"
        self.backgroundImage = "background-sbs6.png"
        self.backgroundImage16x9 = "background-sbs6-16x9.png"
        self.channelName = "SBS6 (PZ)"
        self.maxXotVersion = "3.1.0"
        self.channelDescription = "Online uitzendingen van SBS6 via PCZapper.nl."
        self.sortOrder = 7
        self.moduleName = "chn_sbs6.py"
        self.baseUrl = "http://www.pczapper.tv/pzc5/lfui/index.php"
        self.playerUrl = "http://www.pczapper.tv/pzc5/lfui/?e=1&v="
        self.onUpDownUpdateEnabled = False
        
        self.passWord = ""
        self.userName = ""
        self.requiresLogon = False
        
        self.episodeItemRegex = '<div class="thumb">\W+<a href="([^"]+)">\W+<img[^>]+alt="([^"]+)"/>'
        #self.episodeItemRegex = '<div id="pcz_menublock_header">\s+<a href="([^"]+)">([^<]+)</a>'
        self.videoItemRegex = '<table class="pcz_videolist_item" cellpadding="1" cellspacing="0">[^\.]+<img src="([^"]*)" class="pcz_videolist_img">[^:]+<a href="javascript:pcz_playvideo\((\d+), 0\)" style="font-weight:bold">([^<]*)</a>'
        self.folderItemRegex = ''  # used for the CreateFolderItem
        self.mediaUrlRegex = "pcz_video_url='http://[^?]+player.php\?url=([^\']+)"    # used for the UpdateVideoItem
        #self.mediaUrlRegex = 'http://www.pczapper.tv/pzc5/lfui/mediamanager_client/player.php\?url=([^\']+)'    # used for the UpdateVideoItem
        
        #========================================================================== 
        # non standard items
        self.programTitle = ""
        
        return True
 
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateEpisodeItem for %s', self.channelName)
        item = common.clistItem(resultSet[1], self.baseUrl + resultSet[0])
        item.icon = self.icon
        item.complete = False
        return item

    #==============================================================================
    def PreProcessFolderList(self, data):
        """
        Accepts an data from the ProcessFolderList Methode, BEFORE the items are
        processed. Allows setting of parameters (like title etc). No return value!
        """
        _items = []
        
        #load all additional pages and add the html to the data variable
        #self.programTitle = common.DoRegexFindAll('- ([^<]+)</title>', data)[-1]
        self.programTitle = common.DoRegexFindAll('title="[^"]+">([^<]+)</a>\W+</td>', data)[-1]
        #title="Admirals TV">Admirals TV</a>                    </td>
        _totalPages = 1
        
        # determine second page
        _pageExtUrl = common.DoRegexFindAll('<a href="([^"]+p=\d+&pm=\d+)">\d+</a>', data)
        
        # check if more
        if _pageExtUrl != []:
            # load second page as "pageExt"
            _nPagesExt = len(_pageExtUrl)
            logFile.info('Extra pages %s',_nPagesExt)
            _totalPages += int(_nPagesExt)

        # determine percentage per page:
        _percentagePerPage = int(math.floor(100/int(_totalPages)))
        _percentage = 0
        
        # now add all data to the data variable
        
        if _pageExtUrl != []:
        # do first page (already loaded)
            _parsePB = xbmcgui.DialogProgress()
            _parsePB.create('Opening Additional Pages', 'Opening additional pages', self.initialUri)
            _page = 1
            for _pageUrl in _pageExtUrl:
                _page += 1
                data = data + uriHandler.Open(self.baseUrl+_pageUrl, pb=False)
                _percentage += _percentagePerPage
                _parsePB.update(_percentage, "Loading page %s" %(_page))
                if _parsePB.iscanceled():
                    break
            _parsePB.close()
        
        return (data, _items)
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #logFile.info('starting CreateVideoItem for %s', self.channelName)
        item = common.clistItem(resultSet[2], self.playerUrl + resultSet[1])
        item.type = 'video'
        item.icon = self.icon
        
        # they all have the same Thumb, so we can do this here. Usually this
        # isn't wise here.
        item.thumb = self.CacheThumb(resultSet[0])
        item.description = "%s\n%s" % (self.programTitle, item.name)
                
        item.complete = False
        return item
        
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. Usually retrieves the MediaURL 
        and the Thumb!
        """
        # no MediaURL retrieving is done, because that is done in Playvideo (we don't need to open
        # any urls here. Info is already present, except the url).
        logFile.info('starting UpdateVideoItem for %s (%s)\nUrl:%s', item.name, self.channelName, item.url)
        
        data = uriHandler.Open(item.url)
        
        #get mediaurl
        videoUrl = common.DoRegexFindAll(self.mediaUrlRegex, data)
        item.mediaurl = common.ConvertURLEntities(videoUrl[-1])
        
        if item.mediaurl.find('.flv')<0:
            #parse ASX/ASF for older XBMC verions
            item.mediaurl = self.ParseAsxAsf(item.mediaurl)
            logFile.info("Real media url = %s", item.mediaurl)
        else:
            # if it is an FLV, it is downloadable
            item.downloadable = True
            
        item.complete = True
        
        # finish and return
        logFile.info('finishing ParseVideo for %s. MediaUrl=%s', item.url, item.mediaurl)
        return item
    