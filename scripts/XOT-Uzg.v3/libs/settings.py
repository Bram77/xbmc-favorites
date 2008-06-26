import exceptions
import xml.dom.minidom
import sys, os, re
import database

#===============================================================================
# Make global object available
#===============================================================================
import config
import common
logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler

def CleanupXml(xmlDoc):
    #cleanup
    prettyXml = xmlDoc.toprettyxml()
    #remove not needed lines with only whitespaces
    prettyXml = re.sub("(?m)^\s+[\n\r]", "", prettyXml, )
    
    prettyXml = re.sub("[\n\r]+\t+([^<\t]+)[\n\r]+\t+", "\g<1>", prettyXml)
    return prettyXml

def LoadFavorites(channelName, icon):
    """
        Reads the favorites into items.
    """
    try:
        db = database.DatabaseHandler()
        items = db.LoadFavorites(channelName)
        for item in items:
            item.icon = icon
    except:
        logFile.error("Settings :: Error loading favorites", exc_info=True)
           
    return items


def AddToFavorites(item, channelName):
    """
        Adds an items to the favorites
    """
    try:
        db = database.DatabaseHandler()
        db.AddFavorite(item.name, item.url, channelName)
    except:
        logFile.error("Settings :: Error adding favorites", exc_info=True)
              

def RemoveFromFavorites(item, channelName):
    try:
        db = database.DatabaseHandler()
        db.DeleteFavorites(item.name, item.url)
    except:
        logFile.error("Settings :: Error removing from favorites", exc_info=True)
    return
