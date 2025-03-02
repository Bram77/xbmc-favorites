#############################################################################
#
# Navi-X Playlist browser
# by rodejo (rodejo16@gmail.com)
#############################################################################

#############################################################################
#
# CBackgroundLoader:
# This class loads playlists properties in a separate background task.
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
import threading
from settings import *
from CFileLoader import *
from libs2 import *

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

######################################################################
# Description: Background loader thread
######################################################################
class CBackgroundLoader(threading.Thread):
    def __init__(self, *args, **kwargs):
        if (kwargs.has_key('window')): 
            self.MainWindow = kwargs['window']
        else:
            self.MainWindow = 0
       
        threading.Thread.__init__(self)    

        self.setDaemon(True) #make a deamon thread   
       
        self.killed = False
       
        self.event = threading.Event()
        
        self.counter=0
        
    def run(self):
        while self.killed == False:
            #self.event.wait()
            #self.event.clear()
            time.sleep(0.2) #delay 1 second
#            self.counter = self.counter + 1
#            self.MainWindow.setInfoText(str(self.counter)) #loading text
            self.UpdateThumb()
            #Update the thumb image  
            
    def kill(self):
        self.killed = True
#        self.event.set() #notify the thread
    
#    def notify(self):
#        self.event.set()
               
    ######################################################################
    # Description: Displays the logo or media item thumb on left side of
    #              the screen.
    # Parameters : -
    # Return     : -
    ######################################################################
    def UpdateThumb(self):  
#        if self.MainWindow.state_busy != 0:
#            return
 
        playlist = self.MainWindow.pl_focus
        index = self.MainWindow.list.getSelectedPosition()
        index2 = -1 #this value never will be reached
        thumb_update = False
                              
        while (self.MainWindow.state_busy == 0) and (index != index2):
        #while (index != index2):
            index = self.MainWindow.list.getSelectedPosition()
            if playlist.size() > 0:
                m = self.MainWindow.pl_focus.list[index].thumb
                      
                if (m == 'default') or (m == ""): #no thumb image
                    m = self.MainWindow.pl_focus.logo #use the logo instead
                    if m != self.MainWindow.userthumb:
                        self.MainWindow.user_thumb.setVisible(0)
            
                if m != self.MainWindow.userthumb:
                    #diffent thumb image
                    if (m == 'default') or (m == ""): #no image
                        self.MainWindow.thumb_visible = False
                    elif m != 'previous': #URL to image located elsewhere
                        ext = getFileExtension(m)

                        loader = CFileLoader() #file loader
                        loader.load(m, cacheDir + "thumb." + ext, timeout=2, proxy="ENABLED", content_type='image')
                        if loader.state == 0: #success
                            #next line is fix, makes sure thumb is update.
                            self.MainWindow.thumb_visible = True
                            thumb_update = True
                        else:
                            self.MainWindow.thumb_visible = False
                    self.MainWindow.userthumb = m
            else:
                self.MainWindow.thumb_visible = False
                
            index2 = self.MainWindow.list.getSelectedPosition()

        if self.MainWindow.thumb_visible == True:
#            self.MainWindow.user_logo.setVisible(0)
            if thumb_update == True:
                self.MainWindow.user_thumb.setVisible(0)
                self.MainWindow.user_thumb.setImage("")
                self.MainWindow.user_thumb.setImage(loader.localfile)

            self.MainWindow.user_thumb.setVisible(1)
        else:
            self.MainWindow.user_thumb.setVisible(0)
            
  
        
