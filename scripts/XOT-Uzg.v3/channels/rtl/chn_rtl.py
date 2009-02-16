import sys, re, urllib, os.path, math, time,types
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
        self.mainListUri = "http://www.rtl.nl/(vm=/service/miMedia/rtl_gemist.xml/)/system/video/menu/videomenu.xml"
        self.baseUrl = "http://www.rtl.nl"
        self.icon = "rtlthumb.png"
        self.iconLarge = "rtllarge.png"
        self.noImage = "rtlimage.png"
        self.channelName = "RTL 4,5&7"
        self.channelDescription = "Uitzendingen van de zenders RTL 4,5,7 & 8."
        self.moduleName = "chn_rtl.py"
        self.maxXotVersion = "3.2.0"
        
        self.backgroundImage = "background-rtl.png"
        self.backgroundImage16x9 = "background-rtl-16x9.png"
        self.requiresLogon = False
        self.sortOrder = 5
        
        self.episodeItemRegex = '<li class="folder" rel="([^"]+)videomenu.xml">([^<]+)</li>'
        self.videoItemRegex = '<li class="video" (thumb="([^"]+)" ){0,1}(thumb_id="([^"]+)" )(ctime="([^"]+)" ){0,1}rel="([^"]*/)([^"]+)" (link="([^"]+)"){0,1}>([^<]+)</li>' 
        self.folderItemRegex = '<li class="folder" rel="([^"]*/)([^"]+)">([^<]+)</li>'
        self.mediaUrlRegex = "file:'([^']+_)(\d+)(K[^']+.wmv)'"
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play lowest bitrate stream", "CtMnPlayLow", itemTypes="video", completeStatus=True))            
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play highest bitrate stream", "CtMnPlayHigh", itemTypes="video", completeStatus=True))
        
        #============================================================================== 
        # non standard items
        self.PreProcessRegex = '<ul title="([^"]*)" rel="([^"]*)videomenu.xml"'
        self.progTitle = ""
        self.videoMenu = ""
        #self.parseWvx = True

        return True
    
    #==============================================================================
    def ParseMainList(self):
        # call the main list
        items = []
        if len(self.mainListItems) > 1:
            return self.mainListItems
        
        items = chn_class.Channel.ParseMainList(self)
        
        # get more items:
        url1 = "http://www.rtl.nl/service/gemist/home/"
        data1 = uriHandler.Open(url1, pb=True)         
        url2 = common.DoRegexFindAll('<script[^>]+src="([^"]+)"[^>]*></script><div id="navigatie_container">', data1)
        
        javaUrl = ""
        for url in url2:
            javaUrl = url
            pass
        
        if javaUrl != "":
            data = uriHandler.Open(javaUrl, pb=True)
            
            moreItems = common.DoRegexFindAll('\["([^"]+)","([^"]+)","[^"]+","[^"]+"\]', data)
            previousNumber = len(items)
            number = 0
            for item in moreItems:
                moreItem = common.clistItem(item[0], self.RtlFolderUri("/%s" % item[1], "videomenu.xml"))
                moreItem.icon = self.folderIcon
                moreItem.thumb = self.noImage
                if items.count(moreItem) == 0:
                    number = number + 1
                    items.append(moreItem)
        
        logFile.debug("Added %s more RTL Items to the already existing %s", number, previousNumber)
        
        rockNationItem = common.clistItem('Rock Nation','http://www.rtl.nl/system/video/menu/reality/rocknation/videomenu.xml', 'folder')
        rockNationItem.icon = self.folderIcon
        rockNationItem.thumb = self.noImage
        if items.count(rockNationItem) == 0:
            items.append(rockNationItem)
        
        # sort by name
        if self.episodeSort:
            items.sort(lambda x, y: cmp(x.name.lower(),y.name.lower()))
        
        return items
        
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
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
        #                       0      1               2                     3      4            5   6             7 
        #<li class="video" (thumb="([^"]+)" ){0,1}(ctime="\d+" ){0,1}rel="([^"]*/)([^"]+)" (link="([^"]+)"){0,1}>([^<]+)</li>
        
        #                           0      1              2      3       4        5                    6      7        8      9             10          
        #<li class="video" (thumb="([^"]+)" ){0,1}(thumb_id="([^"]+)" )(ctime="([^"]+)" ){0,1}rel="([^"]*/)([^"]+)" (link="([^"]+)"){0,1}>([^<]+)</li>
     
        item = common.clistItem(resultSet[10], self.RtlVideoUri(self.videoMenu, resultSet[6] + resultSet[7]))
        if len(self.folderHistory)>1:
            item.description = self.folderHistory[-1].description + item.name
        else:
            item.description = item.name
        item.icon = self.icon
        item.thumb = self.noImage
        item.thumbUrl = urlparse.urljoin(self.baseUrl, resultSet[1])
        item.type = 'video'
        item.mediaurl = []
        
        # as of 21-01-2009 this does not work anymore
#        if resultSet[9] != '':
#            item.mediaurl = []
#            item.mediaurl.append(urlparse.urljoin(self.baseUrl, resultSet[9]))
#            item.mediaurl.append(item.mediaurl[0].replace("max.wvx","min.wvx"))
#        else:
#            logFile.error('CreateVideo: No mediaUrl was found.')

        if resultSet[5] != '':
            logFile.debug('ctime=%s (%s)', resultSet[5], time.ctime(int(resultSet[5])))
            item.date = time.strftime('%d-%m-%Y',time.localtime(int(resultSet[5])))
            
        item.complete = False
        
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. 
        """
        logFile.debug('starting UpdateVideoItem for %s (%s)',item.name, self.channelName)
        
        if len(item.mediaurl) == 0:    
            data = uriHandler.Open(item.url, pb=False)
            matches = common.DoRegexFindAll(self.mediaUrlRegex, data)
            logFile.debug("Possible Matches for mediaUrl: %s",matches)
    
            if len(matches) > 0:        
                # sort mediaurl -> get highest quality
                matches.sort(lambda x, y: int(y[1])-int(x[1]))
    
                mediaUrls = []
                for match in matches:
                    mediaUrls.append("%s%s%s" % match)
            
                logFile.debug("Sorted Matches: %s", mediaUrls)                
                item.mediaurl = mediaUrls
            else:
                logFile.error("Cannot find media URL")
        
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
        
        #if len(item.mediaurl) > 1:
        if type(item.mediaurl) is types.ListType or type(item.mediaurl) is types.TupleType:
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
            
            # parse it
            #if self.parseWvx:
            #    dummy = self.ParseWvx(dummy)
                
            # play it
            chn_class.Channel.PlayVideoItem(self, dummy, player)            
        else:
            logFile.debug("Starting playback of the only available mediaUrl (%s)", item.mediaurl)
            #if self.parseWvx:
            #    dummy = self.ParseWvx(dummy)
            
            chn_class.Channel.PlayVideoItem(self, item, player)
            

    #===============================================================================
    def RtlFolderUri(self, folder, filename):
        return 'http://www.rtl.nl/(vm='+ folder + ')/system/video/menu' + folder + filename

    #===============================================================================    
    def RtlVideoUri(self, videoMenu, videoURL):
        return 'http://www.rtl.nl/(vm'+ videoMenu + ')' + videoURL
    
#    #===============================================================================    
#    def ParseWvx(self, item):
#        #Parse the playlist
#        logFile.debug('Starting parsing of WXV')
#        data = uriHandler.Open(item.mediaurl, pb=False)
#        urls = common.DoRegexFindAll('<REF HREF="([^"]+)"\W*/>', data)
#        # create a new empty holder for urls.....
#        newUrls = []
#        for url in urls:
#            logFile.debug('Appending %s as mediaUrl', url)
#            newUrls.append(url)
#            # ...but only assign them to the mediaurl property if there where results
#            item.mediaurl = newUrls
#        return item
    