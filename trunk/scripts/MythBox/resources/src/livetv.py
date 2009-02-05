#
#  MythBox for XBMC - http://mythbox.googlecode.com
#  Copyright (C) 2009 analogue@yahoo.com
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

import datetime
import logging
import mythtv
import player
import time
import threading
import ui
import util
import xbmcgui
import xbmc

log = logging.getLogger('mythtv.ui')
mlog = logging.getLogger('mythtv.method')

def compareChannelAsc( x, y ):
    if x.callsign() == y.callsign():
        return cmp( x.chanid(), y.chanid() )
    else:
        return x.callsign() < y.callsign()

def compareChannelDesc( y, x ):
    if x.callsign() == y.callsign():
        return cmp( x.chanid(), y.chanid() )
    else:
        return x.callsign() < y.callsign()

def compareTitleAsc( x, y ):
    if x.title() == y.title():
        return cmp( x.starttime(), y.starttime() )
    else:
        return cmp( x.title(), y.title() )

def compareTitleDesc( y, x ):
    if x.title() == y.title():
        return cmp( x.starttime(), y.starttime() )
    else:
        return cmp( x.title(), y.title() )
    

def showWindow(winDialog, program, conn, db, settings, translator):
    """Creates the livetv window."""
    log.debug( "> livetv.showWindow()" )
    win = Window(conn=conn, db=db, settings=settings, translator=translator)
    win.loadskin("livetv.xml")
    win.loadPrograms(program)
    if winDialog != None:
        winDialog.close()
        
    if program != None:
        win.show()
        win.playSelected(None)
    else:
        win.doModal()
    del win
    log.debug("< livetv.showWindow()")

# =============================================================================
class Window(ui.BaseWindow):
    
    #
    # TODO: Major cleanup. Remove cruft no longer used
    #       
        
    def __init__(self, *args, **kwargs):
        """Requires kwargs conn, db, settings, translator"""
        ui.BaseWindow.__init__(self, *args, **kwargs)
        log.debug("> LIVETV Window.init")

        self.player = None
        self.channels = None
        self.programs=[]
        self.focusControl = None
        self.curChannel = 0
        self.ringBufferName = ""
        self.stopping = False
        self.playing = False
        self.recLoaded = False

        self.filePrefix = ""
        log.debug("  LIVETV Window.init [A]")        
        self.lastFile = ""
        self.lastChainPos = -1

        self.fullpath = ""
        self.loopPause = 0.5 # (seconds) how long to wait between loops while playing
        self.chainCheck = 3 # (seconds) how long to wait between check for new tvchains
        self.chainCheckCount = self.chainCheck * ( 1 / self.loopPause )
        self.programReload = 360 # (seconds) How long to wait before reloading program information (so the info is upto date)
        self.programReloadCount = self.programReload * ( 1 / self.loopPause )
        self.conflictCheck = 30 # (seconds) How long to wait between checks for conflicts
        self.conflictCheckCount = self.conflictCheck * ( 1 / self.loopPause )
        log.debug("  LIVETV Window.init [B]")        
        self.lastMin = int(time.strftime("%M", time.localtime() ))
        self.curEncoder = -1
        self.nextRec = False
        
        # TODO: This controls whether viewing live tv also records it.
        #       '0' - Just watch livetv
        #       '1' - Save livetv as a recording
        # TODO: Remove hardcoded '0' - ignoring value in settings.xml for now
        self.recordedFormat = '0'
        
        log.debug("  LIVETV Window.init [C] - Creating Playlist")
        # create a new playlist to add tvchains to
        try:
            self.tvplaylist = xbmc.PlayList(1)
        except: 
            self.tvplaylist = xbmc.PlayList(3)
        log.debug("  LIVETV Window.init [D] - Done")

        self.osd = None
        self.recosd = None
        log.debug('< LIVETV Window.init')

#    def cleanupPlayer(self):
#        """Apparently called to clean stuff up when done playing livetv"""
#        self.loadingShow(False)
#        
#        if self.db and self.recordedFormat != "1":
#            self.db.setMythSetting("XBMCClientChainID", mythtv.ourHost, "")            
#            self.db.setMythSetting("XBMCClientStatus", mythtv.ourHost, "0")
#            self.db.setMythSetting("XBMCClientEncoder", mythtv.ourHost, "-1")
#
#        #self.db = None
#        del self.player
#        self.player = None
#        self.playing = False
#        self.loadingRemove()
#        self.loadPrograms(None)

    def loadPrograms(self, program):
        """
        Called immediately after construction from client (after loadSkin(...))
        - retrives all channels
        - retrieves all programs showing on all channels now
        - builds listbox of [chan# - callsign - prog name] (sorted by channel)
        - selects the passed in program in listbox if found
        - updates show details based on current selection
        
        depends none
        """
        
        # TODO: Why clearing out schedules when not referenced in this method?
        self.schedules = []
        
        # Only load channels once...
        if self.channels == None:
            self.channels = self.db.getChannels()
            self.channels.sort(compareChannelAsc)
        
        now = datetime.datetime.now()
        xbmcgui.lock()
        
        try:
            # Refresh program listings every time...
            self.programs = self.db.getProgramListings(now, now)
            self.programs = self.fixProgramList()
            
            cnt = 0
            # don't need to actually UPDATE the list when we are playing TV
            if not self.playing:
                channelListControl = self.controls["show_list"].control
                channelListControl.reset()
                for p in self.programs:
                    if p != None:
                        channelListControl.addItem(p.chanstr() + " " + p.callsign() + " - " + p.fullTitle())
                        if program != None:
                            if program.chanstr() == p.chanstr():
                                self.curChannel = cnt
                    else:
                        channelListControl.addItem(
                            str(self.channels[cnt].channum()) + " " + self.channels[cnt].callsign() + " - No Programs Found")
                    cnt += 1
                channelListControl.selectItem(self.curChannel)
                self.updateShowDetails(self.curChannel)
        finally:
            xbmcgui.unlock()

    def containsChannel(self, progs, chan):
        for p in progs:
            if p != None:
                if p.chanid() == chan.chanid():
                    return True
        return False
    
    def fixProgramList(self):
        """
        So we got a list of channels from the db and
        we got a list of programs from the db.
        Well, the list of programs may not include a program for every
        single channel we have, so just create an array holding 
        the program for each channel and put a None in the slots for
        which we do not have a channel -> program match.
        
        depends self.channels
        depends self.programs
        out ProgramFromQuery[]
        """
        mlog.debug ('>livetv.Windows.fixProgramList()')
        newProgs = []
        for chan in self.channels:
            foundProg = False
            try:
                for p in self.programs:
                    if self.containsChannel(newProgs, chan):
                        foundProg = True
                    else:
                        if p.chanid() == chan.chanid():
                            newProgs.append(p)
                            foundProg = True
            except:
                log.exception("fixProgramList")
                raise
            
            if not foundProg:
                newProgs.append(None)
                
        mlog.debug ('<livetv.Windows.fixProgramList()')
        return newProgs
                
    def updateShowDetails(self, pos):
        """
        Maps index position to a Program and populates details.
        in int selected index of listbox
        """
        if pos < len(self.programs):
            show = self.programs[pos]
            self.populateShowDetails(show)

    def loadingRemove(self):
        self.isLoading = False
        self.hidegroup("popup")
            
    def showIconImg( self, img, path="" ):
        c = self.controls['popup_icon'].control
        self.removeControl( c )
        del c

        x = int(self.getvalue( self.getoption( "popup_channel_x" ) ) )
        y = int(self.getvalue( self.getoption( "popup_channel_y" ) ) )
        w = int(self.getvalue( self.getoption( "popup_channel_w" ) ) )
        h = int(self.getvalue( self.getoption( "popup_channel_h" ) ) )

        texture = img
        tx = util.findMediaFile( texture )
        if tx == None:
            tx = path + texture
 
        c = xbmcgui.ControlImage( x, y, w, h, tx )
        self.addControl( c )
        self.controls['popup_icon'].control = c

    def loadingShow(self, isTuning):
        """
        Sets labels on the popup control based on whether we're
        tuning, recording, stopping, or closing.
        
        in bool True  - means we're starting watching livetv
                False - means we're stopping livetv
                
        depends recordedFormat        
        """
        # self.loadingRemove()
        self.group = "main"
        self.showgroup("popup", False)
        
        # populate title
        self.isLoading = True
        prog = self.programs[self.curChannel]
        
        if prog != None:
            theShowName = self.programs[self.curChannel].fullTitle()
            theChanID = self.programs[self.curChannel].chanstr()
            theChanName = self.programs[self.curChannel].callsign()
        else:
            theShowName = "No Program Details Available"
            theChanID = self.channels[self.curChannel].channum()
            theChanName = self.channels[self.curChannel].callsign()

        if isTuning:
            if self.recordedFormat == "1":
                chanTxt = "Recording " + theChanName + " Please Wait..."
            else:
                chanTxt = "Tuning " + theChanName + " Please Wait..."
        else:
            if self.recordedFormat == "1":
                chanTxt = "Stopping " + theChanName + " Please Wait..."
            else:
                chanTxt = "Closing " + theChanName + " Please Wait..."
            theShowName = ""

        self.controls['popup_title'].control.setLabel(theChanName)
        self.controls['popup_line_a'].control.reset()
        self.controls['popup_line_a'].control.addLabel(chanTxt)
        self.controls['popup_line_b'].control.reset()
        self.controls['popup_line_b'].control.addLabel(theShowName)
        # TODO: Fix me
        self.showIconImg( 'channels\\' + str(theChanID) + ui.picType, ui.picBase)

    def updateLoadLine( self, txt ):
        self.controls['popup_line_c'].control.reset()
        self.controls['popup_line_c'].control.addLabel( txt )

    def populateShowDetails(self, show):
        """in Program"""
        
        # TODO: What does this mean?
        # Remove the loading image just incase it hasn't already been removed
        # self.loadingRemove()
        
        fullTitle = ""
        airDate = ""
        channel = ""
        origAir = ""
        desc = ""
        
        if show != None:
            fullTitle = show.fullTitle()
            airDate = show.formattedAirDate()
            channel = show.formattedChannel()
            origAir = show.formattedOrigAirDate()
            desc = show.formattedDescription()
        else:
            fullTitle = "Unavailable"
            airDate = ""
            channel = "%s %s" % (self.channels[self.curChannel].channum(), self.channels[self.curChannel].callsign())
            origAir = ""
            desc = "Program Information is Unavailable for this Channel"
            
        # populate title
        self.controls['show_title'].control.reset()
        self.controls['show_title'].control.addLabel(fullTitle)
        log.debug( "show_title = %s" % fullTitle)
        
        # populate air date
        self.controls['show_air_date'].control.setLabel(airDate)
        log.debug("show_air_date = %s" % airDate)
        
        # populate channel
        self.controls['show_channel'].control.setLabel(channel)
        log.debug("show_channel= %s" % channel)
        
        # populate orig air
        self.controls['show_orig_air'].control.setLabel(origAir)
        log.debug("show_orig_air = %s" % origAir)
        
        # populate description
        self.controls['show_descr'].control.reset()
        self.controls['show_descr'].control.addLabel(desc)
        log.debug("show_descr = %s" % desc)

#    def playTV(self, chanid):
#        """
#        Either starts a livetv recording or just livetv playing.
#        
#        in str chanid Start live tv on this channel
#        out 0 if an error occured
#            1 if successful
#        """
#        log.debug('> LiveTVPlayer.play, ChanID=%s' % chanid)
#        try:
#            try:
#                # TODO: Issues
#                #       1. Share same player that 'Watch Recordings' users or create new one?
#                #       2. Eiter case, determine injection strategy
#                player = player.getPlayer()
#    
#                if self.player.isPlaying() and len(self.ringBufferName) > 0:
#                    # TODO: Flags seems like hokey..refactor
#                    # flag to indicate script is stopping playback
#                    self.stopping = True  
#                    self.player.stop()
#                else:
#                    self.stopping = False
#    
#                self.filePrefix = self.settings.get("paths_recordedprefix")
#                self.host = self.settings.get("mythtv_host")
#                
#                if self.recordedFormat == "1":
#                    self.doLiveRecord(chanid)
#                else:
#                    self.doLiveRingBuffer(chanid)
#            except:
#                # TODO: Pair with lock. What about unlock if no exception?
#                xbmcgui.unlock()     
#                log.exception('playTV')
#                return 0
#        finally:
#            self.cleanupPlayer()
#        log.debug('< LiveTV.play')
#        return 1

#    def checkPlayInfo(self):
#        #log.debug( '> LiveTV.checkPlayInfo' )
#        time.sleep(self.loopPause)
#        # After 'self.programReload' minutes reload the program listings
#        if self.programReloadCount == 0:
#            # this is really only used for the future OSD
#            #self.loadPrograms()
#            self.programReloadCount = self.programReload * ( 1 / self.loopPause )
#        else:
#            self.programReloadCount -= 1
#        
#        self.checkConflict()
#        self.checkChains()
#        #log.debug( '< LiveTV.checkPlayInfo' )

#    def checkChains(self):
#        if self.chainCheckCount == 0:
#            ## Need to check for our tvchains and stick them at the end of the playlist?
#            newChains = [] # SP: self.db.getChainFiles( mythtv.chainid, None, self.lastChainPos, 1, True )
#            for fp in newChains:
#                fullpath = self.filePrefix + "/" + fp["recorded.basename"]
#                self.tvplaylist.add( fullpath )
###                self.player.playnext()
###                time.sleep( 1 )
#                log.debug("ADDED FILE: %s" % fullpath)
#                self.lastFile = fullpath
#                self.lastChainPos = fp["tvchain.chainpos"]
#            self.chainCheckCount = self.chainCheck * ( 1 / self.loopPause )
#        else:
#            self.chainCheckCount -= 1

    def playSelected(self, control):
        """Play show selected in passed in list control or 'show_list' if None"""
        if control == None:
            control = self.controls["show_list"].control
        self.curChannel = control.getSelectedPosition()
        if self.curChannel < len(self.channels):
            channel = self.channels[self.curChannel]
            brain = LiveTVBrain(self.conn, self.db, self.settings)
            brain.watchLiveTV(channel)
            del brain
            
    def onControlHook(self, control):
        log.debug("> livetv.Window.onControlHook()")

        id = self.getcontrolid(control)
        log.debug("ID: %s" % id)
#            if id == "view_by":
#                self.viewBySelected()
        if id == "show_list":
            self.playSelected(control)
        elif id == "refresh":
            self.loadPrograms(None)

        log.debug("< livetv.Window.onControlHook()")
        return 1

    def onActionHook(self, action):
        log.debug("> livetv.Window.onActionHook( action=[%s] )" % action)
        self.focusControl = self.getFocus()
        if action == ui.ACTION_PREVIOUS_MENU:
            try:
                self.settings.save() # whats the point of saving here?
            except:
                pass
        log.debug("< livetv.Window.onActionHook()")
        return 0

    def onActionPostHook(self, action):
        log.debug("> livetv.Window.onActionPostHook( action=[%s] )" % action)
        # check if the action was to move up or down
        if action in (ui.ACTION_MOVE_UP, 
                      ui.ACTION_MOVE_DOWN,
                      ui.ACTION_SCROLL_UP,
                      ui.ACTION_SCROLL_DOWN):

            # check if the control in focus is the show list
            id = self.getcontrolid(self.focusControl)

            if id == "show_list":
                self.curChannel = self.focusControl.getSelectedPosition()
                # give gui time to update
                time.sleep(0.10)

                # get selected show and populate details
                self.updateShowDetails(self.focusControl.getSelectedPosition())
        log.debug("< livetv.Window.onActionPostHook()")

# =============================================================================
class LiveTVBrain(object):
    
    def __init__(self, session, db, settings):
        self._session = session
        self._db = db
        self._settings = settings          
        self._tuner = None
    
    def watchLiveTV(self, channel):
        """
        Blocks until livetv watching completed.
        
        in  Channel - Channel the couch potato would likeB to watch
        out Tuner   - Tuner picked to watch live tv
        raises ServerException if tuner not available
        """
        progress = xbmcgui.DialogProgress()
        progress.create('Watch TV', 'Finding tuner...')
        self._tuner = self._findAvailableTunerWithChannel(channel)
        
        progress.update(20, 'Watch TV', 'Tuning channel...')
        self._tuner.startLiveTV(channel.channum())
        
        progress.update(40, 'Watch TV', 'Starting recording...')
        self._tuner.waitForRecordingToStart(timeout=60)
        
        liveBuffer = None
        try:
            liveBuffer = int(self._settings.get('mythtv_minlivebufsize'))
        except:
            liveBuffer = 1024
        
        progress.update(60, 'Watch TV', 'Buffering...')
        self._tuner.waitForRecordingWritten(numKB=liveBuffer, timeout=60)
        
        progress.update(80, 'Watch TV', 'Starting player...')
        whatsPlaying = self._tuner.getWhatsPlaying()
        log.debug('Currently playing = %s' % whatsPlaying.getLocalPath())
        
        progress.close()
        livePlayer = LiveTVPlayer()
        livePlayer.addListener(self)
        livePlayer.playRecording(whatsPlaying, player.NoOpCommercialSkipper(player, whatsPlaying))
        del livePlayer # induce GC so on* callbacks unregistered
        return self._tuner
    
    def getLiveTVStatus(self):
        return self._tuner.getLiveTVStatus()

    #
    # Callbacks initiated by LiveTVPlayer
    # 
    def onPlayBackStarted(self):
        pass
    
    def onPlayBackStopped(self):
        self._tuner.stopLiveTV()
            
    def onPlayBackEnded(self):
        self._tuner.stopLiveTV()

    #
    # Private
    #
    def _findAvailableTunerWithChannel(self, channel):
        """
        in  Channel - channel to fine a tuner for
        out Tuner   - tuner that is availble for livetv, None otherwise
        raises ServerException if a tuner is not currently available
        """
        
        # 1. Check at least one tuner available
        numFreeTuners = self._session.getNumFreeTuners()
        if numFreeTuners <= 0:
            raise mythtv.ServerException('All tuner(s) are busy.')
        
        # 2. Make sure available tuner can watch requested channel
        tuners = self._session.getTuners()
        for i, tuner in enumerate(tuners):
            if not tuner.isRecording() and tuner.hasChannel(channel):
                log.debug("Found tuner %s to view channel %s" % (tuner.tunerID, channel.channum()))
                return tuner
            
        raise mythtv.ServerException('A tuner capable of viewing channel %s is not available.' % channel.channum())
    
# =============================================================================
class LiveTVPlayer(player.MythPlayer):
    
    def __init__(self):
        player.MythPlayer.__init__(self)
        self.listeners = []  
    
    def addListener(self, listener):
        self.listeners.append(listener)
        
    def onPlayBackStarted(self):
        log.debug('> onPlayBackStarted')
        if self._active:
            try:
                for listener in self.listeners:
                    try: 
                        listener.onPlayBackStarted()
                    except:
                        log.exception('listener %d callback blew up' % listener)
            finally:
                log.debug('< onPlayBackStarted')
            
    def onPlayBackStopped(self):
        log.debug('> onPlayBackStopped')
        if self._active:
            try:
                for listener in self.listeners:
                    try: 
                        listener.onPlayBackStopped()
                    except:
                        log.exception('listener %d callback blew up' % listener)
            finally:
                self._playbackCompletedLock.set()
                log.debug('< onPlayBackStopped')
            
    def onPlayBackEnded(self):
        log.debug('> onPlayBackEnded')
        if self._active:
            try:
                for listener in self.listeners:
                    try: 
                        listener.onPlayBackEnded()
                    except:
                        log.exception('listener %d callback blew up' % listener)
            finally:
                self._playbackCompletedLock.set()
                log.debug('< onPlayBackEnded')

    def _reset(self, program):
        """
        Overrides super impl
        """
        self._program = program
        self._playbackCompletedLock = threading.Event()
        self._playbackCompletedLock.clear()
