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

import logging
import mythtv
import os
import threading
import time
import ui
import util
import xbmc
import xbmcgui

log = logging.getLogger('mythtv.ui')
mlog = logging.getLogger('mythtv.method')

mythPlayer = None

# Interval in millis to sleep when we're waiting around for 
# async xbmc events to take complete
SLEEP_MILLIS = 250

# =========================================================================f====
class MythPlayer(xbmc.Player):
    """
    Plays mythtv recordings with support for bookmarks, commercial skipping,
    etc 
    """
    
    def __init__(self):
        xbmc.Player.__init__(self)    
        self._active = True
    
    def __del__(self):
        log.warn("\n\n\n\n\t\tGC'ing player\n\n\n")
            
    # Public ------------------------------------------------------------------
      
    def playRecording(self, program, commSkipper):
        """
        Plays the given program. Blocks until playback is stopped or until the 
        end of the recording is reached
        """
        mlog.debug('> playRecording(%s)' % program.title())
        assert not self.isPlaying(), 'Player is already playing a video'
        self._reset(program)
        self._commSkipper = commSkipper
        
        
        self.play(self._program.getLocalPath(), self._buildPlayList())
        
        
        #myth://dbname:dbpassword@hostname:port/recordings/filename.mpg
                
        #        url = 'myth://' + \
        #              program.settings.get('mysql_database') + \
        #              ':' + \
        #              program.settings.get('mysql_password') + \
        #              '@' + \
        #              program.settings.get('mythtv_host') + \
        #              '/recordings/' + \
        #              program.getBareFilename()
        #
        #        #':' + \
        #        #program.settings.get('mythtv_port') + \
        #              
        #        log.debug('URL = "%s"' % url)
        #        
        #        self.play(str(url))
        
        self._waitForPlaybackCompleted()
        self._active = False
        mlog.debug('< playRecording(...)')

    def getProgram(self):
        return self._program
    
    def getTracker(self):
        return self._tracker
    
    # Callbacks ---------------------------------------------------------------

    def onPlayBackStarted(self):
        if self._active:
            try:
                try:
                    log.debug('> onPlayBackStarted')
                    self._bookmarker.onPlayBackStarted()
                finally:
                    self._tracker.onPlayBackStarted()
                    self._commSkipper.onPlayBackStarted()
                    log.debug('< onPlayBackStarted')
            except:
                # Called on a separate thread -- log exceptions instead of raising them            
                log.exception('onPlayBackStarted catchall')
            
    def onPlayBackStopped(self):
        if self._active:
            try:
                try:
                    log.debug('> onPlayBackStopped')
                    self._tracker.onPlayBackStopped()
                    self._commSkipper.onPlayBackStopped()
                    self._bookmarker.onPlayBackStopped()
                finally:
                    self._playbackCompletedLock.set()
                    log.debug('< onPlayBackStopped')
            except:
                # Called on a separate thread -- log exceptions instead of raising them
                log.exception('onPlayBackStopped catchall')
            
    def onPlayBackEnded(self):
        if self._active:
            try:
                try:
                    log.debug('> onPlayBackEnded')
                    self._tracker.onPlayBackStopped()
                    self._commSkipper.onPlayBackEnded()
                    self._bookmarker.onPlayBackEnded()
                finally:
                    self._playbackCompletedLock.set()
                    log.debug('< onPlayBackEnded')
            except:
                # Called on a separate thread -- log exceptions instead of raising them
                log.exception('onPlayBackEnded catchall')

    # Private -----------------------------------------------------------------
    
    def _reset(self, program):
        self._program = program
        self._playbackCompletedLock = threading.Event()
        self._playbackCompletedLock.clear()
        self._tracker = PositionTracker(self)
        self._bookmarker = Bookmarker(self, self._program)
        
    def _waitForPlaybackCompleted(self):
        while not self._playbackCompletedLock.isSet():
            #log.debug('Waiting for playback completed...')
            xbmc.sleep(SLEEP_MILLIS)

    def _buildPlayList(self):
        mlog.debug("> _buildPlayList")
        
        playlistItem = xbmcgui.ListItem()
        title = self._program.fullTitle()
        comms = self._program.getCommercials()
        if len(comms) > 0:
            title += '(%s breaks - ' % len(comms)
            for b in self._program.getCommercials():
                title += mythtv.formatSeconds(b.start)
                title += ', '
            title += ')'
                
        playlistItem.setInfo("video", {"Genre" : self._program.category(), "Studio" : self._program.formattedChannel(), "Title": title, "Plot": self._program.formattedDescription()} )
        #playlistItem.setProperty('AspectRatio', '1.85 : 1')
        playlistItem.setIconImage(self._program.getLocalThumbnailPath())
        playlistItem.setThumbnailImage(self._program.getLocalThumbnailPath())
            
        mlog.debug("< _buildPlayList")
        return playlistItem
        
# =============================================================================
class Bookmarker(object):
    """Mimics XBMC video player's builtin auto resume functionality"""
    
    def __init__(self, player, program):
        self._player = player
        self._program = program
        
    def onPlayBackStarted(self):
        self._resumeFromBookmark()
        
    def onPlayBackStopped(self):
        self._saveLastPositionAsBookmark()
        
    def onPlayBackEnded(self):
        self._clearBookmark()

    def _clearBookmark(self):
        if self._program.hasBookmark():
            self._program.setBookmark(0.0) 

    def _resumeFromBookmark(self):
        bookmarkSecs = self._program.getBookmark()
        if bookmarkSecs > 0:
            fb = mythtv.formatSeconds(bookmarkSecs)
            log.debug('Resuming recording at bookmarked position of %s' % fb)
            ui.showPopup(self._program.title(), 'Resuming at %s)' %(fb))
            self._player.seekTime(bookmarkSecs)
            while self._player.getTime() < bookmarkSecs:
                log.debug('Waiting for player time %s to seek past bookmark of %s' %(
                    mythtv.formatSeconds(self._player.getTime()), fb))
                xbmc.sleep(SLEEP_MILLIS)
        else:
            log.debug('Recording has no bookmark')

    def _saveLastPositionAsBookmark(self):
        lastPos = self._player.getTracker().getLastPosition()
        log.debug('Setting bookmark on %s to %s' %(
            self._program.title(), mythtv.formatSeconds(lastPos)))
        try:
            self._program.setBookmark(lastPos)
        except:
            log.exception('_saveLastPositionAsBookmark catchall')

# =============================================================================
class PositionTracker(object):
    """
    Tracks the last position of the player. This is necessary because 
    Player.getTime() is not valid after the callback to 
    Player.onPlayBackStopped().  
    """
    
    HISTORY_SECS = 5  # Number of seconds of history to keep around

    def __init__(self, player):
        self._player = player
        self._lastPos = 0.0
        self._tracker = util.BoundedEvictingQueue((1000/SLEEP_MILLIS) * self.HISTORY_SECS)
        self._history = []
        
    def onPlayBackStarted(self):
        log.debug('Starting position tracker...')
        self._tracker = threading.Thread(
            name='Position Tracker', 
            target = self._trackPosition)
        self._tracker.start()
    
    def onPlayBackStopped(self):
        if self._tracker.isAlive():
            log.debug('Position tracker stop called. Still alive = %s' % self._tracker.isAlive())
        else:
            log.debug('Position tracker thread already dead.')

    def onPlayBackEnded(self):
        self.onPlayBackStopped()
        
    def getHistory(self, howFarBack):
        """Returns a list of the TrackerSamples from 'howFarBack' seconds ago to."""
        endPos = self._lastPos
        startPos = endPos - howFarBack
        slice = []
        for sample in self._history:
            if startPos <= sample.pos and sample.pos <= endPos:
                slice.append(sample)
        log.debug('Tracker history for %s secs = [%s] %s' % (howFarBack, len(slice), slice))
        return slice
    
    def getLastPosition(self):
        return self._lastPos
    
    def _trackPosition(self):
        """Method run in a separate thread. Tracks last position of player is long as it is playing"""
        try:
            while self._player.isPlaying():
                self._lastPos = self._player.getTime()
                self._history.append(TrackerSample(time.time(), self._lastPos))
                log.debug('Tracker time = %s' % self._lastPos)
                xbmc.sleep(SLEEP_MILLIS)
            log.debug('Position tracker thread exiting with lastPos = %s' % self.getLastPosition())
        except:
            log.exception('_trackPosition catchall')

# =============================================================================
class TrackerSample(object):
    
    def __init__(self, time, pos):
        self.time = time
        self.pos  = pos
    
    def __repr__(self):
        return 'Sample {time = %s, pos = %s}' % (self.time, self.pos)         
            
# =============================================================================
class ICommercialSkipper(object):
    """Common interface for commercial skipping implementations."""
    
    def __init__(self, player, program):
        self._player = player
        self._program = program
    
    def onPlayBackStarted(self):
        raise NotImplementedError, 'Abstract base class'
    
    def onPlayBackStopped(self):
        raise NotImplementedError, 'Abstract base class'

    def onPlayBackEnded(self):
        raise NotImplementedError, 'Abstract base class'
    
# =============================================================================
class NoOpCommercialSkipper(ICommercialSkipper):

    def __init__(self, player, program):
        ICommercialSkipper.__init__(self, player, program)

    def onPlayBackStarted(self):
        pass
    
    def onPlayBackStopped(self):
        pass

    def onPlayBackEnded(self):
        pass
    
# =============================================================================
class EdlCommercialSkipper(ICommercialSkipper):
    """
    Creates an Mplayer compatible EDL skip file with the comm breaks 
    retrieved from the mythbacked. Writes the file to the same directory
    that the file being played resides in (thats where XBMC will be looking
    for the file) with a .edl extension.
    
    EDL skip files broken in xbmc (getTime() returning negative values) so
    this is useless for now.
    """
    def __init__(self, player, program):
        ICommercialSkipper.__init__(self, player, program)
        self._writeSkipFile()
    
    def onPlayBackStarted(self):
        # Too late to build skip file; done in constructor
        pass
    
    def onPlayBackStopped(self):
        if self._edlFile:
            os.remove(self._edlFile)

    def onPlayBackEnded(self):
        if self._edlFile:
            os.remove(self._edlFile)
    
    def _writeSkipFile(self):
        commBreaks = self._program.getCommercials()
        contents = ''
        if len(commBreaks) > 0:
            for cb in commBreaks:
                contents += '%.2f %.2f 0%s' %(cb.start, cb.end, os.linesep)
            self._edlFile = self._program.getLocalPath()
            lastDot = self._edlFile.rfind('.')
            self._edlFile = self._edlFile[:lastDot] + ".edl"
            log.debug('edl skip file = %s' % self._edlFile)
            log.debug('edl skip file contents = \n%s' % contents)
            f = open(self._edlFile, 'w')
            f.write(contents)
            f.close()

# =============================================================================
class TrackingCommercialSkipper(ICommercialSkipper):
    """
    Commercial skipper that monitores the position of the currently playing file
    and skipps commercials accordingly.
    """
    
    def __init__(self, player, program):
        ICommercialSkipper.__init__(self, player, program)
        
    def onPlayBackStarted(self):
        log.debug('program in skipper = %s' % self._program.title())
        self._breaks = self._program.getCommercials()
        # Has a value when video position falls in a comm break
        self._currentBreak = None  

        for b in self._breaks:
            log.debug('break = %s' % b)
 
        self._skipper = threading.Thread(name='Tracking Commercial Skipper', target = self._trackCommercials)
        self._skipper.start()
    
    def onPlayBackStopped(self):
        if self._skipper.isAlive():
            log.debug('Commercial tracker stop called. Still alive = %s' % self._skipper.isAlive())
        else:
            log.debug('Commercial tracker thread already dead')
    
    def onPlayBackEnded(self):
        self.onPlayBackStopped()    

    def _isInBreak(self, pos):
        for b in self._breaks:
            if b.isDuring(pos):
                self._currentBreak = b
                return True
        self._currentBreak = None
        return False    
    
    def _trackCommercials(self):
        """Method run in a separate thread to skip over commercials"""
        try:
            if len(self._breaks) == 0:
                log.debug('Recording %s has no comm breaks, exiting comm tracker' % self._program.title())
                return
            
            while self._player.isPlaying():
                pos = self._player.getTime()
                if self._isInBreak(pos):
                    log.debug('entered comm break = %s' % self._currentBreak)
                    if self._isCloseToStartOfCommercial(pos) and not self._wasUserSkippingAround(pos): 
                        log.debug('Comm skip activated!')
                        ui.showPopup(self._program.title(), 
                            'Skipping commercial %s' % mythtv.formatSeconds(self._currentBreak.duration()))
                        self._player.seekTime(self._currentBreak.end)
                        self._waitForPlayerToPassCommercialBreak()
                    else:
                        log.debug('Position in comm skip region but not activated')
                xbmc.sleep(SLEEP_MILLIS)
            log.debug('Commercial tracker thread exiting')
        except:
            log.exception('_trackCommercials catchall')
            
    def _wasUserSkippingAround(self, currPos):
        """
        Check last 2 seconds of history for number of samples.
        A high number of samples indicates that user was probably 
        not skipping around in the video hence the comm skip would 
        be a good thing.
        """
        wasSkipping = False
        samplePeriodSecs = 2 # TODO: Pass in as param to method call

        # If currPos is too close to the start of the video..assume not 
        # skipping around
        if currPos > samplePeriodSecs:
            requiredSamples = 6  # TODO: Derive as percentage instead of hardcoding
            numSamples = len(self._player.getTracker().getHistory(samplePeriodSecs))
            log.debug('Samples in last %s seconds = %s' %(samplePeriodSecs, numSamples))
            wasSkipping = numSamples < requiredSamples

        log.debug('User was skipping around = %s' % wasSkipping)
        return wasSkipping
    
    def _isCloseToStartOfCommercial(self, currPos):
        """
        check that the current pos is close in proximity to the start of the
        commercial break. assumes that comm break is skipped only if the user
        played directly into the commercial vs. landing inside the commercial
        via ffwd, rewind, etc.
        """
        windowStart = self._currentBreak.start - 1
        windowEnd = self._currentBreak.start + 2
        isClose = currPos >= windowStart and currPos <= windowEnd
        log.debug('User close to start of comm break = %s' % isClose) 
        return isClose

    def _waitForPlayerToPassCommercialBreak(self):
        # TODO: What if user stops playing while in this loop? Add isPlaying() to loop invariant
        # wait for player pos to pass current break
        while self._currentBreak.isDuring(self._player.getTime()):
            xbmc.sleep(SLEEP_MILLIS)