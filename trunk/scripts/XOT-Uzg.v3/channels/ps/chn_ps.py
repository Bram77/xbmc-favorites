
#===============================================================================
# Import the default modules
#===============================================================================
import xbmc, xbmcgui
import sys, re, os
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
register.channelRegister.append('chn_ps.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="pron")')

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
        
        self.icon = "psthumb.png"
        self.iconLarge = "pslarge.png"
        self.noImage = "psimage.png"
        self.channelName = "Pronshare.com"
        self.channelDescription = "A collection of adult videos from Stage6"
        self.moduleName = "chn_ps.py"
        self.maxXotVersion = "3.0.1"
        
        self.mainListUri = "http://pronshare.com"
        self.baseUrl = "http://pronshare.com"
        self.onUpDownUpdateEnabled = False
        
        self.requiresLogon = False
        
        self.episodeItemRegex = '<a href="(/Search\.aspx\?tag=\w+-\w+-\w+-\w+-\w+)">([^>]+)</a>' # used for the ParseMainList
        self.videoItemRegex = '<a href="(/watch\.aspx\?id=\w+-\w+-\w+-\w+-\w+)">\W+<img [^>]+src="([^"]+/)(\d+)t.jpg" alt="([^"]+)"'   # used for the CreateVideoItem 
        self.folderItemRegex = ''  # used for the CreateFolderItem
        self.mediaUrlRegex = '<param name="src" value="([^"]+)" />'    # used for the UpdateVideoItem
        
        #========================================================================== 
        # non standard items
        self.topDescription = ""
        
        return True
      
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def onActionFromContextMenu(self):
        """
        Using of the ContextMenu. It is called
        """
        
        if not self.contextMenuEnabled:
            return None
        
        _position = self.getCurrentListPosition()
        _item = self.listItems[_position]
        
        if not _item.type == "video":
            logFile.warning("Cannot show contextmenu for folder")
            return None
        
        # build menuitems
        _menuItems = ("Download Item","Play using Mplayer","Play using DVDPlayer")
        _contextMenu = contextmenu.GUI(config.contextMenuSkin, config.rootDir, config.skinFolder, parent=self.getFocus(), menuItems = _menuItems)
        _selectedItem = _contextMenu.selectedItem
        del _contextMenu
        
        # handle function from items
        if ( _selectedItem is not None ):    
            logFile.debug("Selection from menu was %s", _selectedItem)
            if _selectedItem == 1:
                self.listItems[_position] = self.DownloadEpisode(_item)
            elif _selectedItem == 2:
                self.PlayVideoItem(_item)
            elif _selectedItem == 3:
                self.PlayVideoItem(_item,"dvdplayer")    
        return None
      
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateEpisodeItem for %s', self.channelName)
        
        # dummy class
        item = common.clistItem(resultSet[1], self.baseUrl + resultSet[0])
        item.icon = self.folderIcon
        item.description = resultSet[1]
        
        item.complete = True
        return item
    
    #============================================================================== 
    def PreProcessFolderList(self, data):
        """
        Accepts an data from the ProcessFolderList Methode, BEFORE the items are
        processed. Allows setting of parameters (like title etc). No return value!
        """
        logFile.debug("PreProcessing")
        
        items = []
        #description
        matches = common.DoRegexFindAll('<div class="left-col">\W+<h3>([^<]+)</h3>', data)
        
        #initialise description
        if len(matches) > 0:
            self.progTitle = matches[0]
            if len(self.folderHistory) > 0:
                self.folderHistory[-1].description = self.progTitle
            logFile.debug("ProgramTitle = %s", self.progTitle)
        
#        # now remove everything above the sidebar HTML to prevent problems with new 
#        # links on the site
#        #
#        data = common.DoRegexFindAll('<div class="right-col">(([\n\r]|.)*)', data)
#        if len(data)>0:
#            if len(data[0])>0:
#                data = data[0][0]
        return (data, items)
        
    
    #==============================================================================
    def CreateFolderItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateFolderItem for %s', self.channelName)
        item = common.clistItem(resultSet[1], self.baseUrl + resultSet[0])
        item.description = "%s\n%s" % (self.folderHistory[-1].description, resultSet[1])
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
        #<a href="(/watch\.aspx\?id=\w+-\w+-\w+-\w+-\w+)">\W+<img [^>]+src="([^"]+/)(\d+)t.jpg" alt="([^"]+)"
        #                            0                                            1    2                3
        item = common.clistItem(resultSet[2], self.baseUrl + resultSet[0])
        
        item.description = resultSet[3]
        item.name = resultSet[3]
        
        if not self.pluginMode:
            if len(self.folderHistory) > 0:
                item.description = "%s\n%s" % (self.folderHistory[-1].description, resultSet[3])
        
        item.icon = self.icon
        item.thumbUrl = resultSet[1] + resultSet[2] + 't.jpg'
        item.thumb = self.CacheThumb(item.thumbUrl)
        item.type = 'video'
        item.url = self.baseUrl + resultSet[0]
        item.mediaurl = "http://video.stage6.com/%s/.divx" % (resultSet[2])
        #http://video.stage6.com/2141478/.divx
        # getting the URL is part of the PlayVideo
        item.complete = True
        return item
    
    #============================================================================== 
    #def UpdateVideoItem(self, item):
     #   """
      #      Updates an item
       # """
        #item.thumb = self.CacheThumb(item.thumbUrl)
        #return item
    
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
            
    #============================================================================== 
    def PlayVideoItem(self, item, player="dvdplayer"):
        """ NOT USER EDITABLE
        Accepts an item with or without MediaUrl and playback the item. If no 
        MediaUrl is present, one will be retrieved.
        """
        logFile.info("Starting Video Playback using the %s", player)
        try:
            logFile.info('opening '+ item.mediaurl)
            if player=="dvdplayer":
                logFile.info("Playing using DVDPlayer")
                xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(item.mediaurl)
            else:
                xbmc.Player().play(item.mediaurl)
        except:
            dialog = xbmcgui.Dialog()
            dialog.ok(config.appName,"Kan dit programma niet afspelen.")
            logFile.critical("Could not playback the url", exc_info=True)