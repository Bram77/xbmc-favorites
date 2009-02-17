#===============================================================================
# Import the default modules
#===============================================================================
from beautifulsoup import ResultSet
from cgi import log
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

register.channelRegister.append('chn_freecaster.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="freecaster")')

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
        self.guid = "52230AF6-FBA9-11DD-87D4-15B656D89593"
        self.icon = "freecastericon.png"
        self.iconLarge = "freecasterlarge.png"
        self.noImage = "freecasterimage.png"
        self.channelName = "Freecaster.tv"
        self.maxXotVersion = "3.2.0"
        self.channelDescription = "Freecaster.tv movies"
        self.moduleName = "chn_freecaster.py"
        self.mainListUri = "http://www.freecaster.com/"
        self.baseUrl = "http://www.freecaster.com"
        self.onUpDownUpdateEnabled = True
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
                
        self.requiresLogon = False
        
        self.folderItemRegex = ''
        self.videoItemRegex = "<img src='([^']+)' alt='[^']+' [^>]+>[^\n]+<a class='clip_link' href='([^']+)'\W*>([^<]+)[^-]+- (\d{1,2}[^<]+)"   # used for the CreateVideoItem 
        self.mediaUrlRegex = '<param\W+name="URL"\W+value="([^"]+)"'
        self.pageNavigationRegex = '<pagenav>([^<])<pagenav><pagenavurl>([^<]+)</pagenavurl>' 
        self.pageNavigationRegexIndex = 0 
        return True
      
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def CtMnPlayMplayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, "mplayer")
    
    def CtMnPlayDVDPlayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item,"dvdplayer")    
    
    #==============================================================================
    def ParseMainList(self):
        """ 
        accepts an url and returns an list with items of type CListItem
        Items have a name and url. 
        """
        items = []
                        
        """
            * Air Race      http://www.freecaster.com/helpers/videolist_helper.php?apID=1000041&i=0&q=&sortby=&sort=DESC&event_id=
            * BMX           http://www.freecaster.com/helpers/videolist_helper.php?apID=1000002&i=0&q=&sortby=&sort=DESC&event_id=
            * Beach Volley  http://www.freecaster.com/helpers/videolist_helper.php?apID=1000194&i=0&q=&sortby=&sort=DESC&event_id=
            * Breakdance    http://www.freecaster.com/helpers/videolist_helper.php?apID=1000030&i=0&q=&sortby=&sort=DESC&event_id=
                            http://www.freecaster.com/helpers/videolist_helper.php?apID=1000030&i=0&q=&sortby=top&sort=DESC&event_id=
            * Dance         http://www.freecaster.com/helpers/videolist_helper.php?apID=1000046&i=0&q=&sortby=&sort=DESC&event_id=
            * Freeski       http://www.freecaster.com/helpers/videolist_helper.php?apID=1000023&i=0&q=&sortby=&sort=DESC&event_id=
            * Kitesurf      http://www.freecaster.com/helpers/videolist_helper.php?apID=1000005&i=0&q=&sortby=&sort=DESC&event_id=
            * MX/FMX        http://www.freecaster.com/helpers/videolist_helper.php?apID=1000003&i=0&q=&sortby=&sort=DESC&event_id=
            * Mountain Bike http://www.freecaster.com/helpers/videolist_helper.php?apID=1000006&i=0&q=&sortby=&sort=DESC&event_id=
            * Outdoor       http://www.freecaster.com/helpers/videolist_helper.php?apID=1000007&i=0&q=&sortby=&sort=DESC&event_id=
            * Rally         http://www.freecaster.com/helpers/videolist_helper.php?apID=1000179&i=0&q=&sortby=&sort=DESC&event_id=
            * Skateboard    http://www.freecaster.com/helpers/videolist_helper.php?apID=1000008&i=0&q=&sortby=&sort=DESC&event_id=
            * Snowboard     http://www.freecaster.com/helpers/videolist_helper.php?apID=1000009&i=0&q=&sortby=&sort=DESC&event_id=
            * Surf          http://www.freecaster.com/helpers/videolist_helper.php?apID=1000010&i=0&q=&sortby=&sort=DESC&event_id=
            * Wakeboard     http://www.freecaster.com/helpers/videolist_helper.php?apID=1000011&i=0&q=&sortby=&sort=DESC&event_id=
            * Windsurf       http://www.freecaster.com/helpers/videolist_helper.php?apID=1000024&i=0&q=&sortby=&sort=DESC&event_id=
        """
        
        urls = []
        urls.append(('Air Race', '1000041'))
        urls.append(('BMX','1000002'))
        urls.append(('Beach Volley','1000194'))
        urls.append(('Breakdance','1000030'))
        urls.append(('Dance','1000046'))
        urls.append(('Freeski','1000023'))
        urls.append(('Kitesurf','1000005'))
        urls.append(('MX/FMX','1000003'))
        urls.append(('Mountain Bike','1000006'))
        urls.append(('Outdoor','1000007'))
        urls.append(('Rally','1000179'))
        urls.append(('Skateboard','1000008'))
        urls.append(('Snowboard','1000009'))
        urls.append(('Surf','1000010'))
        urls.append(('Wakeboard','1000011'))
        urls.append(('Windsurf','1000024'))
       
        for url in urls:
            item = self.CreateEpisodeItem(url)
            items.append(item)
        
        return items
    
    #==============================================================================
    def PreProcessFolderList(self, data):
        """
        Accepts an data from the ProcessFolderList Methode, BEFORE the items are
        processed. Allows setting of parameters (like title etc). No return value!
        """
        
        pages = []
        
        numberOfItems = common.DoRegexFindAll("class='clipslist' name='(\d+)'>[^/]+'/([^_]+)_\d+'[^>]*>", data)
        logFile.debug(numberOfItems)
        
        if len(numberOfItems) > 0:
            pageId = numberOfItems[0][1]
            numberOfItems = numberOfItems[0][0]
            
        
        # 20 items per page, so we need to calculate
        numberOfPages = int(float(numberOfItems)/20+0.5)
        logFile.debug('Number of items: %s\nNumber of page: %s', numberOfItems, numberOfPages)
        
        pageData = ''
        for i in range(1, numberOfPages + 1):
            pageUrl = "http://www.freecaster.com/helpers/videolist_helper.php?apID=%s&i=%s&q=&sortby=date&sort=DESC&event_id=" % (pageId,i)
            pageData = "%s<pagenav>%s<pagenav><pagenavurl>%s</pagenavurl>" % (pageData, i, pageUrl)
        data = "%s%s" % (pageData, data)
         
        return (data, pages)        
    
    
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        item = common.clistItem(resultSet[0], "http://www.freecaster.com/helpers/videolist_helper.php?apID=%s&i=0&q=&sortby=date&sort=DESC&event_id=" % resultSet[1])
        item.icon = self.icon
        item.complete = True
        return item
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateVideoItem for %s', self.channelName)
        
        item = common.clistItem(resultSet[2],"%s%s" % (self.baseUrl, resultSet[1]))
        item.description = item.name
        item.thumbUrl = resultSet[0]
        item.icon = self.icon
        item.date = resultSet[3]
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
        
        # get the thumb
        item.thumb = self.CacheThumb(item.thumbUrl)
        
        # get additional info
        data = uriHandler.Open(item.url, pb=False)
        guid = common.DoRegexFindAll("fo.addVariable\('id'\W*,\W*'([^']+)'\)", data)
        
        url = ''
        if len(guid) > 0:
            url = 'http://gateway.freecaster.com/VP/%s' % (guid[0],) 
        
        if url == '':
            logFile.error("Cannot find GUID in url: %s", item.url)
            return item
        
        data = uriHandler.Open(url, pb=False)
        urls = common.DoRegexFindAll('<stream[^>]+>([^>]+)</stream_[^>]+>', data)
        
        if len(urls) > 0:
            item.mediaurl = urls[0]
            item.complete = True
        
        logFile.debug("UpdateVideoItem complete: mediaUrl = %s", item.mediaurl)
        
        return item    