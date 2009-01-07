#############################################################################
#
# Navi-X Playlist browser
# by rodejo (rodejo16@gmail.com)
#############################################################################

#############################################################################
#
# CURLLoader:
# This class Retrieves the URL to a media item which the XBMC player 
# understands.
#############################################################################

from string import *
import sys, os.path
import urllib
import urllib2
import re, random, string
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import shutil
import zipfile
from libs2 import *
from settings import *
from CFileLoader import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

RootDir = os.getcwd()
if RootDir[-1]==';': RootDir=RootDir[0:-1]
if RootDir[-1]!='\\': RootDir=RootDir+'\\'
imageDir = RootDir + "\\images\\"
cacheDir = RootDir + "\\cache\\"
imageCacheDir = RootDir + "\\cache\\imageview\\"
scriptDir = "Q:\\scripts\\"
myDownloadsDir = RootDir + "My Downloads\\"
initDir = RootDir + "\\init\\"

class CURLLoader:
    ######################################################################
    # Description: This class is used to retrieve the direct URL of given
    #              URL which the XBMC player understands.
    #              
    # Parameters : URL=source URL
    # Return     : 0=successful, -1=fail
    ######################################################################
    def urlopen(self, URL):
        result = 0 #successful
    
        if URL[:4] == 'http':
            pos = URL.find("flyupload.com")
            if pos != -1:
                result = self.geturl_flyupload(URL)
            else:
                pos = URL.rfind('http://') #find last 'http://' in the URL
                loc_url = URL[pos:]
                    
                try:
                    oldtimeout=socket_getdefaulttimeout()
                    socket_setdefaulttimeout(url_open_timeout)

                    self.f = urllib.urlopen(loc_url)
                    self.loc_url=self.f.geturl()

#                    pos = self.loc_url.rfind('http://') #find last 'http' in the URL
#                    if pos != -1:
#                        self.loc_url = self.loc_url[pos:]                
                
                except IOError:
                    self.loc_url = "" #could not open URL
                    socket_setdefaulttimeout(oldtimeout)            
                    return -1 #fail

                socket_setdefaulttimeout(oldtimeout)
                
                #post processing for youtube files
                pos = URL.find('http://youtube.com') #find last 'http' in the URL
                if pos != -1:
                    result = self.geturl_youtube(self.loc_url)
        else:
            self.loc_url = URL
        
        return result

    ######################################################################
    # Description: This class is used to retrieve the URL of a FlyUpload
    #              webpage
    #              
    # Parameters : URL=source URL
    # Return     : 0=successful, -1=fail
    ######################################################################
    def geturl_youtube(self, URL):
        #retrieve the flv file URL
        #URL parameter is not used.
#        Trace("voor "+self.loc_url)

        id=''
        pos = self.loc_url.find('&video_id=') #find last 'http' in the URL
        if pos != -1:
            pos2 = self.loc_url.find('&',pos+1) #find last 'http' in the URL
            id = self.loc_url[pos+10:pos2] #only the video ID
        
        try:
            oldtimeout=socket_getdefaulttimeout()
            socket_setdefaulttimeout(url_open_timeout)

            #retrieve the timestamp based on the video ID
            self.f = urllib.urlopen("http://www.youtube.com/api2_rest?method=youtube.videos.get_video_token&video_id=" + id)
            data=self.f.read()
            
            index1 = data.find('<t>')
            index2 = data.find('</t>')
            if (index1 != -1) and (index2 != -1):
                t = data[index1+3:index2]
                #t contains the timestamp now. Create the URL of the video file (high quality).
                self.loc_url = "http://www.youtube.com/get_video.php?video_id=" + id + "&amp;t=" + t + "&amp;fmt=18"
            else:
                self.loc_url = ""
        
        except IOError:
            self.loc_url = "" #could not open URL
            return -1 #fail
        
        socket_setdefaulttimeout(oldtimeout)
       
#        Trace(self.loc_url)        
        
        if self.loc_url != "":
            return 0 #success
        else:
            return -1 #failure
    
        
    ######################################################################
    # Description: This class is used to retrieve the URL of a FlyUpload
    #              movie
    #              
    # Parameters : URL=URL to a FluyUpload webpage
    # Return     : 0=successful, -1=fail
    ######################################################################
    def geturl_flyupload(self, URL):
        loader = CFileLoader2()
        loader.load(URL, cacheDir + 'page.html', proxy="DISABLED")
        if loader.state != 0:
            return -1 #failure
        filename = loader.localfile
        
        try:
            f = open(filename, 'r')
            data = f.read()
            f.close()
        except IOError:
            return -1
        
        #defaults
        result = data.find("thankyou?")
        if result != -1:
            result2 = data.find("\"", result)
            if result2 != -1:
                self.loc_url = data[result+13:result2]
            else:
                return -1 #failure
        else:
            return -1 #failure

#        Trace(self.loc_url)

        return 0
        
        
