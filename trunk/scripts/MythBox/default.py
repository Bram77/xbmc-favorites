#
#  MythBox for XBMC
#
#  Copyright (C) 2009 analogue@yahoo.com 
#  http://mythbox.googlecode.com
#
#  Copyright (C) 2005 Tom Warkentin <tom@ixionstudios.com>
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

import os
import sys

def addLibsToPythonPath():
    """Add 3rd party libs in $SCRIPT_HOME/lib to PYTHONPATH"""
    if 'win32' in sys.platform:
        platform = 'win32'
    elif 'linux' in sys.platform:
        import platform
        arch = platform.architecture()[0]
        if arch == '32bit':
            platform = 'linux'
        elif arch == '64bit':
            platform = 'linux64'
        else:
            print("ERROR: Can't determine linux arch: platform.architecture() returned '%s'. Defaulting to 32bit linux" % arch)
            platform = 'linux'
    elif 'darwin' in sys.platform:
        platform = 'osx'
    else:
        raise Exception('Platform %s not supported' % sys.platform)
    print('platform = %s' % platform)
    
    libs = [] 
    libs.append(os.getcwd() + os.sep + 'resources' + os.sep + 'src')
    for lib in [
        'pysmb', 
        'pyxcoder', 
        'decorator',
        'pyfiglet', 
        'MySQLdb', 
        'MySQLdb' + os.sep + platform]:
        libdir = os.getcwd() + os.sep + 'resources' + os.sep + 'lib' + os.sep + lib
        libs.append(libdir)
        
    for path in libs:    
        sys.path.append(path)
        print('syspath += %s' % path)

try:
    addLibsToPythonPath()
except Exception, ex:
    import xbmcgui
    xbmcgui.Dialog().ok('Error: %s', str(ex))

import codecs
import logging
import logging.config
import string
import traceback
import util
import xbmcgui

#
# Script constants
#
__scriptname__ = "MythBox for XBMC"
__author__ = "analogue@yahoo.com"
__url__ = "http://code.google.com/p/mythbox/"
__svn_url__ = "http://mythbox.googlecode.com/svn/trunk"
__credits__ = "bunch of ppl"
__version__ = " Alpha SVN 682"
__svn_revision__ = 0

#
# Init logger before all else...
#
log = None
try:
    loggerIniFile = os.getcwd() + os.sep + 'mythbox_log.ini'
    xbmc.log('loggerIniFile = %s' % loggerIniFile)
    logging.config.fileConfig(loggerIniFile)
    log = logging.getLogger('mythtv.ui')
    log.debug('Mythbox Logger Initialized')
    
    #    import pyfiglet
    #    figlet = pyfiglet.Figlet(zipfile=os.getcwd() + os.sep + 'resources' + os.sep + 'lib' + os.sep + 'pyfiglet' + os.sep + 'fonts.zip')
    #    #figlet = pyfiglet.Figlet(zipfile='fonts.zip')
    #    s = figlet.renderText("\nhello world!")
    #    log.debug(s)
except Exception, ex:
    xbmc.log('Exception trying to initialize logger: %s' % ex)    
    print traceback.print_exc()
    xbmcgui.Dialog().ok('Trying to initialize logger', str(ex))
    
myprogress = xbmcgui.DialogProgress()
myprogress.create("MythBox %s"%__version__)
myprogress.update(0,"Loading MythBox","Please wait...","Importing mythtv.py")

# how many updateProgress calls are there?
progressValue = 0
progressCount = 9

# Enter default start page in your settings using Page ID
#   Page ID, Description,       Action,          Control ID
pages = [[0, "Main",           "self.refresh()", "refresh"],
         [1, "LiveTV",         "livetv.showWindow(self.loadingWin, None, self.conn, self.db, self.settings, self.translator)",                "main_live_tv"],
         [2, "Recorded Shows", "recordings.showWindow(self.loadingWin, self.conn, self.db, self.settings, self.translator, self.thumbCache)", "main_recorded_shows"],
         [3, "TV Guide",       "tvguide.showWindow(self.loadingWin, self.conn, self.db, self.settings, self.translator)",                     "main_tv_guide"],
         [4, "Schedules",      "schedules.showWindow(self.loadingWin, self.conn, self.db, self.settings, self.translator)",                   "main_schedules"],
         [5, "Upcoming Shows", "upcoming.showWindow(self.loadingWin, self.conn, self.db, self.settings, self.translator)",                    "main_upcoming_shows"],
         [6, "Settings",       "uisettings.showWindow(self.loadingWin, self.settings, self.translator, self.platform)",                       "main_settings"]]
 
def cancel():
    """Cancel clicked on progress bar"""
    raise Exception("MythBox Canceled")

def updateProgress(txt):
    """Update Progress Bar"""
    global progressValue, myprogress, progressCount, pages
    try:
        myprogress.update(progressValue, "Loading MythBox", "Please Wait...", txt)
    except:
        myprogress.update(progressValue)
        
    if myprogress.iscanceled():
        cancel()
    progressValue += int(100 / (progressCount + (len(pages) - 1)))
    
try:
    updateProgress("Importing mythtv ...")
    import mythtv
    
    updateProgress("Importing system libraries ...")
    import os, sre, time
    from datetime import datetime
    
    updateProgress("Importing ui ...")
    import ui
    from ui import Dialog
    
    updateProgress("Importing screens ...")
    # preload windows 
    for mod in pages:
        if int(mod[0]) == 0:
            continue
        evalMe = 'import ' + mod[2].split('.')[0]
        log.debug('Evaluating: ' + evalMe)
        exec(evalMe)
        updateProgress("Importing %s ..." % mod[1] )
except Exception, ex:
    log.exception('Initializing stage 2')
    myprogress.close()
    del myprogress
    xbmcgui.Dialog().ok('Initializing stage 2', str(ex))

# =============================================================================

# TODO: Remove after home.py verified to work
class Window(ui.BaseWindow):

    def __init__(self, *args, **kwargs):
        """
        @keyword conn: Connection
        @keyword db: MythDatabase
        @keyword settings: MythSettings
        @keyword translator: Translator
        @keyword thumbCache: ThumbnailCache
        @keyword platform: Platform 
        """
        ui.BaseWindow.__init__(self, *args, **kwargs)
        self.platform = kwargs['platform']
        self.loadingWin = xbmcgui.DialogProgress()
        
    def showIconImg(self, img, path=""):
        c = self.controls['popup_icon'].control
        self.removeControl(c)
        del c

        x = int(self.getvalue(self.getoption("popup_channel_x")))
        y = int(self.getvalue(self.getoption("popup_channel_y")))
        w = int(self.getvalue(self.getoption("popup_channel_w")))
        h = int(self.getvalue(self.getoption("popup_channel_h")))

        myW = w * 1.172
        myH = h * 0.95
        log.debug("New Width: %s New Height: %s" %(myW, myH))
        y -= (( myW - w ) / 2)
        texture = img
        tx = util.findMediaFile(texture)
        if tx == None:
            tx = path + texture

        c = xbmcgui.ControlImage(x, y, myW, myH, tx)
        self.addControl(c)
        self.controls['popup_icon'].control = c
        
    def openStartPage(self):
        if startPage != 0:
            myprogress.close()
            if startPage < len(pages):
                self.loadPage(startPage)
            else:
                log.debug ("%s is not a valid Start Page ID" % startPage)

    def loadAction (self, action):
        for p in pages:
            if p[3] == action:
                self.loadPage(p[0])
                return 1
        return 0

    def loadPage(self, page, progressDialog=None):
        global pages
        try:
            log.debug("Loading %s" % pages[page])
            if int(page) > 0:
                self.loadingWin.create(
                    str(pages[page][1]),
                    "Loading %s" % str(pages[page][1]),
                    "Please Wait...",
                    "")    
           
            exec("%s" % pages[page][2])
            if int(page) > 0:
                self.refresh()
        except:
            log.exception("Failed to Load %s" % str(pages[page][1]))
            self.loadingWin.close()
 
    def onControlHook( self, control ):
        id = self.getcontrolid( control )
        log.debug("Window.onControlHook(id = %s)"%id)
        actionConsumed = self.loadAction( id )
        return actionConsumed

    ## used so we can make sure they have a proper connection before continuing

    def checkConnections( self ):
        log.debug('check connections...')
        
        #
        # TODO: Figure out some way to re-acquire conns on failure
        #
        if self.conn is None:
            log.error("Connection to mythtv server is null")
            xbmcgui.Dialog().ok(
                self.translator.get( 27 ), 
                "MythTV Server Connection Failed.",
                "XBMCMythTV is Unable to Continue" )
            return False
            
        if self.db is None:
            log.error("Connection to mysql db server is null")
            xbmcgui.Dialog().ok(
                self.translator.get( 27 ), 
                "MySQL Server Connection Failed.",
                "XBMCMythTV is Unable to Continue" )
            return False

    def refresh( self ):
        log.debug("Window.refresh()")
        try:
            self.checkConnections()
            tuners = self.conn.getTuners()
            maxVisibleCards = 3
            cnt = 0
            for tuner in tuners:
                if cnt < maxVisibleCards:
                    tunerStatus = self.conn.getTunerStatus(str(tuner.tunerID))
                    self.controls['encoder_status' + str(cnt)].control.reset()
                    self.controls['encoder_status' + str(cnt)].control.addLabel(tunerStatus)
                    cnt += 1

            space = self.conn.getFreeSpace()
            self.controls['space_free'].control.setLabel(space[0])
            self.controls['space_total'].control.setLabel(space[1])
            self.controls['space_used'].control.setLabel(space[2])

            loads = self.conn.getLoad()
            self.controls['load_avg_1min'].control.setLabel(str(loads[0]))
            self.controls['load_avg_5min'].control.setLabel(str(loads[1]))
            self.controls['load_avg_15min'].control.setLabel(str(loads[2]))
            
            self.controls['mythfilldatabase'].control.reset()
            self.controls['mythfilldatabase'].control.addLabel(self.conn.getMythFillStatus())

            pendingRecordings = [] # TODO: uncomment - self.conn.getPendingRecordings()
            ctl = self.controls['schedule'].control
            ctl.reset()
            try:
                ctl.setPageControlVisible(False)
            except:
                pass
            
            now = datetime.now().strftime("%Y%m%d%H%M%S")
            totRecs = 0
            for s in pendingRecordings:
                if s.endtime() >= now:
                    totRecs += 1 
                    ctl.addItem( "%s - Encoder %s - %s - %s-%s" % (
                        time.strftime("%a %d/%m %I:%M%p",time.localtime(float(s.recstarttime()))),
                        s.cardid(),
                        s.channame(),
                        s.title(), 
                        s.subtitle()))
                
            self.controls['schedule_lbl'].control.setLabel(self.translator.get(84) % totRecs)
            self.controls['guidedata'].control.reset()
            self.controls['guidedata'].control.addLabel(self.conn.getGuideData())
        except:
            log.exception("refresh")

#***************************************************************************#
#   End Window Class                                                        #
#***************************************************************************#

try:
    log.info("\n\t\tInitializing...\n\n")
    updateProgress("Initializing...")
    util.initialize()
    log.info(">> MythBox Version: %s <<" % __version__)
    
    updateProgress("Creating Main Window")

    import mythtv
    import mythdb
    import mythtv
    import util
    
    updateProgress("Checking Settings")
    
    # TODO: Springify later...
    # Injected dependencies that get passed all over the place
    
    # 1
    platform = util.getPlatform()
    log.debug(platform)
    # 2
    translator = util.NativeTranslator(platform.getScriptDir())
    # 3
    settings = mythtv.MythSettings(platform, translator, 'settings.xml')

    settingsOK = False
    
    try:
        import uisettings
        settings.verify()
        settingsOK = True
    except mythtv.SettingsException:
        settingsWindow = uisettings.showWindow(myprogress, settings, translator, platform)
        try:
            settings.verify()
            settingsOK = True
        except mythtv.SettingsException:
            settingsOK = False
    
    if settingsOK:    
        # everything below requires valid myth session & mysql db settings
        
        # 4
        db = mythdb.MythDatabase(settings, translator)
        # 5
        conn = mythtv.Connection(settings, db, translator, platform)
        # 6
        thumbCache = ui.ThumbnailCache(platform.getScriptDataDir() + os.sep + 'thumbs', conn)
        
        win = Window(
            conn=conn, 
            db=db, 
            settings=settings, 
            translator=translator,
            thumbCache=thumbCache,
            platform=platform)
    
        startPage = 0
        
        updateProgress("Loading Skin")
        win.loadskin("home.xml")
        
        updateProgress("Checking MythTV Connection")
        if win.checkConnections() == False:
            startPage = 6
            
        updateProgress("Done")
        if startPage != 6:
            win.refresh()
        
        win.openStartPage()
    
        # refesh AFTER settings have been checked to make sure connection OK
        if startPage == 6:
            win.refresh()
        
        myprogress.close()
        win.doModal()  # Blocks until home window closed
        del win
except Exception, ex:
    log.exception('Initializing stage 3')
    myprogress.close()
    xbmcgui.Dialog().ok( 'Initializing stage 3', str(ex))
