#
#  MythBox for XBMC - http://mythbox.googlecode.com
#  Copyright (C) 2009 analogue@yahoo.com
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

import logging
import mythtv
import os
import shutil
import skin
import string
import traceback
import util
import xbmc
import xbmcgui

from util import timed

log = logging.getLogger('mythtv.ui')
mlog = logging.getLogger('mythtv.method')

ACTION_MOVE_LEFT                    = 1
ACTION_MOVE_RIGHT                   = 2
ACTION_MOVE_UP                      = 3
ACTION_MOVE_DOWN                    = 4
ACTION_PAGE_UP                      = 5
ACTION_PAGE_DOWN                    = 6
ACTION_SELECT_ITEM                  = 7
ACTION_HIGHLIGHT_ITEM               = 8
ACTION_PARENT_DIR                   = 9
ACTION_PREVIOUS_MENU                = 10
ACTION_SHOW_INFO                    = 11
ACTION_PAUSE                        = 12
ACTION_STOP                         = 13
ACTION_NEXT_ITEM                    = 14
ACTION_PREV_ITEM                    = 15
ACTION_SCROLL_UP                    = 111
ACTION_SCROLL_DOWN                  = 112
ACTION_CONTEXT_MENU                 = 117

# from xbmc/guilib/common/xbfont.h
ALIGN_LEFT                          = 0
ALIGN_RIGHT                         = 1
ALIGN_CENTER_X                      = 2
ALIGN_CENTER_Y                      = 4
ALIGN_TRUNCATED                     = 8

picBase = os.getcwd() + os.sep + 'images' + os.sep

# channel icons should be placed in images\channel and named after channel id
picType = "_square.png"  # change to reflect you image type
#picType = ".png"

def checkSettings(settings):
    mlog.debug("checkSettings() called" )

    try:
        settings.load()
        settings.verify()
    except mythtv.SettingsException:
        raise Exception, 'FIXME: translate string 86' 

def showPopup(title, text):
    xbmc.executebuiltin('XBMC.Notification(%s, %s)' %(title, text))

# =============================================================================        
class BaseWindow(skin.XBMC_SKIN):

    def __init__(self, *args, **kwargs):
        """Requires kwargs conn, db, settings, translator, thumbCache"""
        skin.XBMC_SKIN.__init__(self, *args, **kwargs)
        if 'conn' in kwargs:
            self.conn = kwargs['conn']
        if 'db' in kwargs:
            self.db = kwargs['db']
        self.settings = kwargs['settings']
        self.translator = kwargs['translator']
        
        # Thumb cache optional for now...
        try:
            self.thumbCache = kwargs['thumbCache']
        except KeyError:
            self.thumbCache = None
                
        self.actionConsumed = 0
        self.lock = 0
        
    def onAction( self, action ):
        log.debug("BaseWindow.onAction( action = %s )"%action )

        try:
            # Lock out concurrent events - XBMC fires events in separate
            # threads.  Without the lock, two threads can be modifying window
            # objects at the same time corrupting data structures.
            if self.lock == 0:
                try:
                    self.lock += 1

                    # call subclass defined hook
                    actionConsumed = self.onActionHook( action )

                    # check if action was not consumed
                    if actionConsumed == 0:
                        # process help request - if subclass hook overrides
                        # this behavior then it should have consumed the event
                        if action in (ACTION_SHOW_INFO, ACTION_CONTEXT_MENU):
                            id = self.getcontrolid( self.getFocus() )
                            if len( id ) > 0:
                                help = self.controls[id].getoption( 'help' )
                            else:
                                help = ""

                            if len( help ) > 0:
                                Dialog().ok(self.translator.get(26), help)
                                actionConsumed = 1

                    # check if event was consumed
                    if actionConsumed == 0:
                        # check if parent dir selected
                        if action == ACTION_PARENT_DIR:
                            self.close()
                        else:
                            skin.XBMC_SKIN.onAction( self, action )

                    self.onActionPostHook( action )

                    self.lock -= 1
                except:
                    self.lock -= 1
                    raise
        except mythtv.ProtocolException, ex:
            Dialog().ok(self.translator.get(27), self.translator.get(109)%str(ex)) 
        except Exception, ex:
            traceback.print_exc()
            Dialog().ok( self.translator.get(27), str(ex))

    def onActionHook( self, action ):
        """
        Method that is called by BaseWindow class.  This method is intended to
        be overridden by subclasses to perform custom logic.
        
        Return values:

        0   Event was not consumed by the hook.  Event will be handled
            internally. (default)
        1   Event was consumed by hook.  No further processing will be done.

        BaseWindow catches exceptions and displays dialog.  Therefore this
        type of logic does not need to replicated in this hook.
        """
        return 0
        
    def onActionPostHook( self, action ):
        """
        Method that is called after internal processing is done on an action.
        This is meant to be overridden if additional logic needs to be
        performed after the internal processing is complete.
        """
        pass

    def onControl( self, control ):
        log.debug("onControl( control= %s )"%control )

        try:
            if self.lock == 0:
                try:
                    self.lock += 1
                    rc = self.onControlHook(control)
                    self.lock -= 1
                except:
                    self.lock -= 1
                    raise
        except mythtv.ProtocolException, ex:
            Dialog().ok(
                self.translator.get(27),
                self.translator.get(109) % str(ex))
        except Exception, ex:
            traceback.print_exc(ex)
            Dialog().ok(self.translator.get(27), str(ex))

    def onControlHook( self, control ):
        """
        Method that is called by BaseWindow class.  This method is intended to
        be overridden by subclasses to perform custom logic.
        
        Return values:

        0   Event was not consumed by the hook.  Event will be handled
            internally.
        1   Event was consumed by hook.  No further processing will be done.
            (default)

        BaseWindow catches exceptions and displays dialog.  Therefore this
        type of logic does not need to replicated in this hook.
        """
        return 1

# =============================================================================
class BaseWindowDialog(skin.XBMC_SKIN_DIALOG):

    #
    # Needed a new class for a DialogWindow as required for OSD
    #        

    def __init__( self, translator):
        skin.XBMC_SKIN_DIALOG.__init__( self )
        self.translator = translator
        self.actionConsumed = 0
        self.lock = 0

    def onAction( self, action ):
        log.debug("BaseWindowDialog.onAction( action= %s )"%action )

        try:
            # Lock out concurrent events - XBMC fires events in separate
            # threads.  Without the lock, two threads can be modifying window
            # objects at the same time corrupting data structures.
            if self.lock == 0:
                try:
                    self.lock += 1

                    # call subclass defined hook
                    actionConsumed = self.onActionHook( action )

                    # check if action was not consumed
                    if actionConsumed == 0:
                        # process help request - if subclass hook overrides
                        # this behavior then it should have consumed the event
                        if action in (ACTION_SHOW_INFO, ACTION_CONTEXT_MENU):
                            id = self.getcontrolid( self.getFocus() )
                            if len( id ) > 0:
                                help = self.controls[id].getoption( 'help' )
                            else:
                                help = ""

                            if len( help ) > 0:
                                Dialog().ok(
                                    self.translator.get( 26 ),
                                    help )
                                actionConsumed = 1

                    # check if event was consumed
                    if actionConsumed == 0:
                        # check if parent dir selected
                        if action == ACTION_PARENT_DIR:
                            self.close()
                        else:
                            skin.XBMC_SKIN_DIALOG.onAction( self, action )

                    self.onActionPostHook( action )

                    self.lock -= 1
                except:
                    self.lock -= 1
                    raise
        except mythtv.ProtocolException, ex:
            Dialog().ok(
                self.translator.get( 27 ),
                self.translator.get( 109 )%str( ex ) )
        except Exception, ex:
            traceback.print_exc()
            Dialog().ok( self.translator.get( 27 ), str( ex ) )

    def onActionHook( self, action ):
        """
        Method that is called by BaseWindowDialog class.  This method is intended to
        be overridden by subclasses to perform custom logic.
        
        Return values:

        0   Event was not consumed by the hook.  Event will be handled
            internally. (default)
        1   Event was consumed by hook.  No further processing will be done.

        BaseWindowDialog catches exceptions and displays dialog.  Therefore this
        type of logic does not need to replicated in this hook.
        """
        return 0
        
    def onActionPostHook( self, action ):
        """
        Method that is called after internal processing is done on an action.
        This is meant to be overridden if additional logic needs to be
        performed after the internal processing is complete.
        """
        pass

    def onControl( self, control ):
        log.debug("BaseWindowDialog.onControl( control= %s )"%control )

        try:
            if self.lock == 0:
                try:
                    self.lock += 1
                    rc = self.onControlHook( control )
                    self.lock -= 1
                except:
                    self.lock -= 1
                    raise
        except mythtv.ProtocolException, ex:
            Dialog().ok(
                self.translator.get( 27 ),
                self.translator.get( 109 )%str( ex ) )
        except Exception, ex:
            traceback.print_exc( ex )
            Dialog().ok( self.translator.get( 27 ), str( ex ) )

    def onControlHook( self, control ):
        """
        Method that is called by BaseWindowDialog class.  This method is intended to
        be overridden by subclasses to perform custom logic.
        
        Return values:

        0   Event was not consumed by the hook.  Event will be handled
            internally.
        1   Event was consumed by hook.  No further processing will be done.
            (default)

        BaseWindowDialog catches exceptions and displays dialog.  Therefore this
        type of logic does not need to replicated in this hook.
        """
        return 1
        
# =============================================================================
class DialogWin(object):
    
    def __init__(self):
        pass
    
    def choose(self, event):
        return xbmcgui.Dialog().choose(event)
    
    def ok(self, title, line1, line2 = "", line3 = ""):
        return xbmcgui.Dialog().ok(title, line1, line2, line3)
    
    def select(self, title, li):
        return xbmcgui.Dialog().select(title, li)
    
    def yesno(self, title, line1, line2 = "", line3 = ""):
        return xbmcgui.Dialog().yesno(title, line1, line2, line3)
    
# =============================================================================
def Dialog():
    return DialogWin()

# =============================================================================
class ChannelIconCache( util.FileCache ):

    def __init__( self, settings, conn ):
        util.FileCache.__init__(
            self,
            picBase + "channels",
            numDays=0 ) # never delete these
        self.settings = settings
        self.conn = conn
        
    def buildPath( self, channel ):
        file = self.getIconFile( channel )
        if file:
            file = self.cachePath + os.sep + file
        log.debug("ChannelIconCache.buildPath() => %s"%file )
        return file

    def getIconFile( self, channel ):
        file = channel.icon()
        if file:
            file = string.replace( file, "/", os.sep )
            file = os.path.basename( file )
        log.debug("ChannelIconCache.getIconFile() => %s"%file )
        return file

    def storeFile( self, chan ):

        localPath = None
        file = chan.icon()
        if file:
            host = self.settings.get( "mythtv_host" )
            port = int( self.settings.get( "mythtv_port" ) )
            remotePath = "myth://%s:%d%s"%(host,port,file)
            localPath = self.buildPath( chan )

            rc = self.conn.transferFile(remotePath, localPath, host)
            if rc != 0:
                localPath = None
            #TODO: why? del c
            
        log.debug("ChannelIconCache.storeFile(%s) => %s"%(chan,localPath))
        return localPath

# =============================================================================
class ThumbnailCache(util.FileCache):
    
    def __init__(self, cachePath, conn):
        util.FileCache.__init__(self, cachePath)
        self.conn = conn

    def buildPath(self, program):
        return self.cachePath + os.sep + "%s_%s_%s.png" % (program.chanid(), program.starttime(), program.endtime())

    @timed
    def storeFile(self, program, backendHost):
        """
        Stores the thumbnail for program in the cache and returns absolute path of cached file.
         
        @param program: program whose thumbnail we wish to retrieve a cached copy of
        @param backendHost: host of backend that recorded the program
        @return: path to cached file on success, None on failure
        """
        log.debug("storeFile(program=%s, host=%s)" % (program, backendHost))
        pathOfFileInCache = self.buildPath(program)

        if not program.hasLocalThumbnail():
            log.debug('Requesting backend generate thumbnail for %s' % program.filename())
            if not self.conn.generateThumbnail(program, backendHost):
                log.warn('Backend could not generate thumb for %s' % program.filename())
            else:
                shutil.copyfile(program.getLocalThumbnailPath(), pathOfFileInCache)
        else:        
            shutil.copyfile(program.getLocalThumbnailPath(), pathOfFileInCache)
        return pathOfFileInCache