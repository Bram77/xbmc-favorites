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
import os
import socket
import sre
import string
import time
import ui
import util

from ffmpeg import FFMPEG

log = logging.getLogger('mythtv.core')
mlog = logging.getLogger('mythtv.method')

#from libs/libmythtv/programinfo.h
FL_COMMFLAG  = 0x01
FL_CUTLIST   = 0x02
FL_AUTOEXP   = 0x04
FL_EDITING   = 0x08
FL_BOOKMARK  = 0x10

gRecStatusTrans = \
{ \
    '-5': 88, # Deleted
    '-4': 89, # Stopped
    '-3': 90, # Recorded
    '-2': 91, # Recording
    '-1': 92, # WillRecord
    '0' : 93, # Unknown
    '1' : 94, # ManualOverride
    '2' : 95, # PreviousRecording
    '3' : 96, # CurrentRecording
    '4' : 97, # EarlierShowing
    '5' : 98, # TooManyRecordings
    '6' : 99, # Cancelled
    '7' :100, # Conflict
    '8' :101, # LaterShowing
    '9' :102, # Repeat
    '10':103, # Overlap
    '11':104, # LowDiskSpace
    '12':105, # TunerBusy
}

gRecSchedTypeTrans = \
{ \
    1 :111, # Once
    2 :112, # Daily
    3 :113, # Channel
    4 :114, # Always
    5 :115, # Weekly
    6 :116, # Find One
    7 :117, # Override
    8 :118, # Don't Record
    9 :119, # Find Daily
    10:120, # Find Weekly
}

gRecSchedTypeLongTrans = \
{ \
    1 :135, # Once
    2 :136, # Daily
    3 :137, # Channel
    4 :138, # Always
    5 :139, # Weekly
    6 :140, # Find One
    7 :141, # Override
    8 :142, # Don't Record
    9 :143, # Find Daily
    10:144, # Find Weekly
}

gRecSchedDupInTrans = \
{ \
    1 :149, # Current recordings
    2 :150, # Previous recordings
    3 :151, # Both
    4 :152, # New episodes
    15:153, # All
}

gRecSchedDupMethodTrans = \
{ \
    1 :145, # None
    2 :146, # Subtitle
    4 :147, # Description
    6 :148, # Subtitle and Description
}

def dbTime2MythTime(dt):
    """
    Converts a time from the database into a format MythTV understands. 
    
    @param dt: a datetime, timedelta, or string time returned from the pure python mysql module
    @return: time in mythtv format as a string
    """
    if type(dt) is str:
        # TODO: Remove me - pure python mysql support
        s = sre.sub( "[T:|\\-| ]", "", dt) 
    elif type(dt) is datetime.datetime:
        # Native MySQLdb
        s = dt.strftime("%Y%m%d%H%M%S")
    elif type(dt) is datetime.timedelta:
        s = time.strftime("%H%M%S",time.gmtime(dt.seconds))
    elif type(dt) is datetime.date:
        s = dt.strftime("%Y%m%d")  
    else:
        raise Exception, 'cannot convert time of unexpected type %s' % type(dt)
    return s

def ctime2MythTime(ctimeLong):
    """
    Converts a long representing a ctime into a format MythTV understands. 
     
    @param ctimeLong: millis elapsed since some date in 1970 as a string or int
    @return: time as a string in 'MythTV' format: YYYYMMDDHHmmSS 
    """
    return time.strftime("%Y%m%d%H%M%S", time.localtime(float(ctimeLong)))

# =============================================================================
class CommercialBreak(object):
    """
    Commercial break with a starting and ending position in seconds relative
    to the start of the recording.
    """
    
    def __init__(self, start, end):
        """
        start and end of commercial break are float values
        """
        assert end > start, 'Starting time of the commercial break cannot be after the end time'
        self.start = start
        self.end = end
    
    def __repr__(self):
        return "%s {start = %s, end = %s, duration = %s}" % (
            type(self).__name__,                                                  
            mythtv.formatSeconds(self.start),
            mythtv.formatSeconds(self.end),
            mythtv.formatSeconds(self.duration()))
    
    def duration(self):
        """out float - Duration of this commercial in seconds"""
        return self.end - self.start
    
    def isDuring(self, position):
        """
        in  float Current position 
        out bool  Returns True if position (in seconds) in within the commercial
                  break, False otherwise.
        """
        return position >= self.start and position <= self.end
    
# =============================================================================
class Channel(object):
    """
    Abstract base class to represent a channel in the mythtv system.
    """
    
    def chanid(self):
        raise NotImplementedError, "Abstract base class"

    def channum(self):
        raise NotImplementedError, "Abstract base class"

    def callsign(self):
        raise NotImplementedError, "Abstract base class"

    def name(self):
        raise NotImplementedError, "Abstract base class"

    def icon(self):
        raise NotImplementedError, "Abstract base class"

    def tunerid(self):
        raise NotImplementedError, "Abstract base class"
    
# =============================================================================
class ChannelFromQuery(Channel):
    """Channel sourced from the MythTV database."""
    
    def __init__(self, data):
        self._data = dict(data)
        # make sure icon() returns a reasonable value when it is not available
        if not 'icon' in self._data or not self._data['icon'] or self._data['icon'] == "none":
            self._data['icon'] = None

    def chanid(self):
        """Return unique channel id as an int""" 
        return self._data['chanid']
    
    def channum(self): 
        """Return channel number as a string"""
        return self._data['channum']
    
    def callsign(self): 
        """Return callsign as a string"""
        return self._data['callsign']
    
    def name(self): 
        """Return channel name as a string"""
        return self._data['name']
    
    def icon(self): 
        """Return absolute path to file containing channel icon as a string"""
        return self._data['icon']
    
    def tunerid(self):
        """Return unique id of tuner which can play/record this channel as an int""" 
        return self._data['cardid']

    def __repr__(self):
        return '%s {chanid=%s, channum=%s, callsign=%s, tunerid=%s, name=%s, icon=%s}' % (
                type(self).__name__,
                self.chanid(),
                self.channum(),
                self.callsign(),
                self.tunerid(),
                self.name(),
                self.icon())

# =============================================================================
class Program(object):
    """
    Base class which represents a TV show in the MythTV system. 
    - Could be an existing recorded program
    - Could be a yet to be recorded scheduled program. 
    """
    def __init__(self, translator):
        self.translator = translator

    def title(self):
        raise Exception, "Abstract base class"

    def subtitle(self):
        raise Exception, "Abstract base class"

    def description(self):
        raise Exception, "Abstract base class"

    def category(self):
        raise Exception, "Abstract base class"

    def chanid(self):
        raise Exception, "Abstract base class"

    def chanstr(self):
        raise Exception, "Abstract base class"

    def origairdate(self):
        raise Exception, "Abstract base class"

    def callsign(self):
        raise Exception, "Abstract base class"

    def starttime(self):
        raise Exception, "Abstract base class"

    def endtime(self):
        raise Exception, "Abstract base class"

    def starttimeAsTime(self):
        starttime = self.starttime()
        if str(starttime[4:5]) == "-":
            return datetime.datetime(
                int(starttime[0:4]), 
                int(starttime[5:7]), 
                int(starttime[8:10]), 
                int(starttime[11:13]), 
                int(starttime[14:16]) )
        else:
            return datetime.datetime(
                int(starttime[0:4]), 
                int(starttime[4:6]), 
                int(starttime[6:8]), 
                int(starttime[8:10]), 
                int(starttime[10:12]) )

    def endtimeAsTime(self):
        endtime = self.endtime()
        if str(endtime[4:5]) == "-":
            return datetime.datetime(
                int(endtime[0:4]), 
                int(endtime[5:7]), 
                int(endtime[8:10]), 
                int(endtime[11:13]), 
                int(endtime[14:16]) )
        else: 
            return datetime.datetime(
                int(endtime[0:4]), 
                int(endtime[4:6]), 
                int(endtime[6:8]), 
                int(endtime[8:10]), 
                int(endtime[10:12]) )
    
    def getLength(self):
        return abs(self.endtimeAsTime() - self.starttimeAsTime())
    
    def setStartTime( self, newstarttime ):
        raise Exception, "Abstract base class"
    
    def setEndTime( self, newendtime ):
        raise Exception, "Abstract base class"
    
    def __repr__(self):
        return "%s {chan = %s, start = %s, end = %s, title = '%s', Sub = %s, desc = '%.10s'}" % (
            type(self).__name__,
            self.chanstr(),                                                                                           
            self.starttimeAsTime(), 
            self.endtimeAsTime(), 
            self.title(), 
            self.subtitle(), 
            self.description())

    def formattedAirDate(self):
        """Returns air times as a formattted string for display purposes"""
        value = ""
        value += self.starttimeAsTime().strftime( "%A %b %d, %I:%M%p" )
        value += " - " + self.endtimeAsTime().strftime( "%I:%M%p" )
        if abs( self.starttimeAsTime() - self.endtimeAsTime() ) > datetime.timedelta( days = 1):
            value += " +1"
        return value

    def formattedChannel(self):
        """Returns chanstr callsign for display purposes"""
        value = self.chanstr()
        if self.callsign():
            value += " " + self.callsign()
        return value

    def fullTitle(self):
        """returns Title - subtitle if subtitle exists"""
        fullTitle = ""
        if self.title():
            fullTitle += self.title()
        if self.subtitle() and not sre.match( '^\s+$', self.subtitle() ):
            fullTitle += " - " + self.subtitle()
        return fullTitle
        
    def formattedOrigAirDate(self):
        """returns original air date or the localized string 
           for no airdate if no airdate exists"""
        value = self.translator.get(45)
        try:
            if self.origairdate():
                value = self.origairdate()
        except:
            pass
        return value

    def formattedDescription(self):
        value = self.translator.get(46)
        if self.description():
            value = self.description()
        return value[:200]

# =============================================================================
#
# TODO: Rename to UpcomingProgram? GuideProgram? YetToAirProgram? ForecastProgram?
#
class ProgramFromQuery(Program):
    """
    Program sourced from the PROGRAM database table.
      
    See mythdb.Database for the query that generates the data dictonary passed into
    the constructor.
    """
    def __init__(self, data, settings, translator):
        Program.__init__(self, translator)
        
        if type(data) is dict:
            # Native MysQLdb
            self._data = data    
        else:
            # TODO: Remove me - pure python mysql
            self._data = dict(data)  
            
        self.settings = settings

    def data(self):
        return self._data

    def title(self):
        return self._data["title"]

    def subtitle(self):
        return self._data["subtitle"]

    def description(self):
        return self._data["description"]

    def category(self):
        return self._data["category"]

    def chanid(self):
        return int(self._data["chanid"])

    def chanstr(self):
        """Channel number as a string -- '5_1'"""
        # TODO: Why would channum not exist? 
        if not self._data["channum"]:  
            return ""
        else:
            return self._data["channum"]

    def origairdate(self):
        key = "origairdate"
        if "originalairdate" in self._data:
            key = "originalairdate"
        try:
            if len( self._data[ key ] ) == 4:
                return self._data[ key ]
        except:
            pass
        return None

    def hostname(self):
        try:
            return self._data["hostname"]
        except:
            return None

    def basename(self):
        try:
            return self._data["basename"]
        except:
            return None

    def remotePath(self):
        log.debug( '> domain.ProgramFromQuery.remotePath()' )
        remoteFile = self.basename()
        remotePath = self.settings.get("paths_recordedprefix")
        shostIp = self.settings.get( "mythtv_host" )
        host = self.hostname()
        try:
            hostIp = socket.gethostbyname(host)
            snet = hostIp[:6]
            ssnet = shostIp[:6]
            log.debug(snet + " " + ssnet)
            
            # if the first 6 characters of both addresses don't match then
            # chances are the 'internet' address of the host has been
            # found so just use the setting IP
            if snet <> ssnet:
                hostIp = shostIp
        except:
            hostIp = shostIp
        
        log.debug ('Host: %s hostIp: %s'%(host, hostIp))
        # we should do this substitute anyway?!
        remotePath = sre.sub( '\%h', hostIp, remotePath )

        if sre.match( "^[Ss][Mm][Bb]:", remotePath ) and not sre.match( "^\d", host ):
            host = sre.sub( '\..*$', '', host )
            remotePath = string.replace( remotePath, '\\', '/' )

        if remotePath[len(remotePath)-1] != '/':
            remotePath += '/'
        remotePath += remoteFile   

        log.debug('< domain.ProgramFromQuery.remotePath() => [%s]'%remotePath)
        return str(remotePath)

    def callsign(self):
        return self._data["callsign"] 

    def seriesid(self):
        return self._data[ "seriesid" ]
    
    def programid(self):
        return self._data[ "programid" ]
    
    def recordid(self):
        return self._data[ "recordid" ]
    
    def manualid(self):
        return self._data[ "manualid" ]
    
    def icon(self):
        return self._data[ "icon" ]
    
    def channame(self):
        return self._data[ "channame" ]
    
    def starttime(self):
        """Returns starttime as a string - 20081121140000"""
        return dbTime2MythTime(self._data["starttime"])
    
    def endtime(self):
        """Returns endtime as a string - 20081121140000"""
        return dbTime2MythTime(self._data["endtime"])
    
    def recstarttime(self):
        return self.starttime()
    
    def recendtime(self):
        return self.endtime()
    
    def isduplicate(self):
        if self._data["isduplicate"] == '0':
            return False
        else:
            return True
    
    def setStartTime( self, newstarttime ):
        if hasattr(newstarttime, "strftime" ):
            self._data[ "starttime" ] = newstarttime.strftime( "%Y%m%d%H%M%S" )
        else:
            self._data[ "starttime" ] = newstarttime
    
    def setEndTime( self, newendtime ):
        if hasattr(newendtime, "strftime" ):
            self._data[ "endtime" ] = newendtime.strftime( "%Y%m%d%H%M%S" )
        else:
            self._data[ "endtime" ] = newendtime

# =============================================================================
class RecordedProgram(Program):
    """
    Implementation of a Program that contains data retrieved for an 
    actual recording that exists on the mythbackend.
    """

    def __init__(self, data, conn, settings, translator, platform):
        """
        @param data: list of fields from mythbackend. libs/libmythtv/programinfo.cpp in the mythtv source 
               describes the ordering of these fields.
        @param conn: Connection
        @param settings: MythSettings
        @param translator: Translator
        @param platform: Platform
        """
        Program.__init__(self, translator)
        self._data = data[:]
        self._conn = conn
        self.settings = settings
        self._platform = platform
        self._fps = None
        self._commercials = None
        self._localPath = None

    def data(self):
        return self._data
    
    def title(self):
        return self._data[0]
    
    def subtitle(self):
        return self._data[1]
    
    def description(self):
        return self._data[2]
    
    def category(self):
        return self._data[3]
    
    def chanid(self):
        """Return unique channel ID as int"""
        return int(self._data[4])
    
    def setChannelID(self, channelID):
        """Set channel ID as int"""
        self._data[4] = str(channelID)
        
    def chanstr(self):
        if not self._data[5]:
            return ""
        else:
            return self._data[5]
        
    def callsign(self):
        return self._data[6]
    
    def channame(self):
        return self._data[7]
    
    def filename(self):
        # str scrubs unicode
        return str(self._data[8])
    
    def fshigh(self):		# high word of file size
        # TODO: change to private scope
        return int(self._data[9])
    
    def fslow(self):		# low word of file size
        # TODO: change to private scope
        return int(self._data[10])
    
    def starttimets(self):
        return int(self._data[11])
    
    def endtimets(self):
        return int(self._data[12])
    
    def starttime(self):
        if int(self._data[11]) < 0:
            return ctime2MythTime(self._data[26])
        else:
            return ctime2MythTime(self._data[11])
    
    def endtime(self):
        if int(self._data[12]) < 0:
            return ctime2MythTime(self._data[27])
        else:
            return ctime2MythTime(self._data[12])
    
    def duplicate(self):
        return self._data[15]
    
    def hostname(self):
        return self._data[16]
    
    def sourceid(self):
        return self._data[17]
    
    def cardid(self):
        return self._data[18]
    
    def inputid(self):
        return self._data[19]
    
    def recpriority(self):
        # TODO: Schedule returns this as an int. Make sure this is consistent if/when used
        return self._data[20]
    
    def recstatus(self):
        return self._data[21]
        
    def recordid(self):
        return self._data[22]
    
    def rectype(self):
        return self._data[23]
    
    def recdups(self):
        raise mythtv.ProtocolException, "unsupported call for protocol version"
    
    def recstarttime(self):
        return self._data[26]
    
    def recendtime(self):
        return self._data[27]
    
    def repeat(self):
        return self._data[28]
    
    def programflags(self):
        return int(self._data[29])
    
    def setProgramFlags(self, flags):
        self._data[29] = str(flags)
        
    def recgroup(self):
        return self._data[30]

    def origairdate(self):
        try:
            if int(self._data[38]) <> 0:
                return self._data[37]
            else:
                return None
        except:
            # TODO: Do we need this catch this?
            return None
    
    def autoexpire(self):
        return (self.programflags() & FL_AUTOEXP) != 0
    
    def isCommFlagged(self):
        return (self.programflags() & FL_COMMFLAG) != 0 
        
    def hasCommercials(self):
        return len(self.getCommercials()) > 0
    
    def getCommercials(self):
        """Return list of CommercialBreaks"""
        if not self.isCommFlagged():
            self._commercials = []
        if self._commercials is None:
            self._commercials = self._conn.getCommercialBreaks(self)
        return self._commercials
    
    def hasBookmark(self):
        return (self.programflags() & FL_BOOKMARK) != 0
    
    def setBookmark(self, seconds):
        """Sets the bookmark as a float value in seconds"""
        mlog.debug('> setBookmark %s' % seconds)
        self._conn.setBookmark(self, mythtv.seconds2frames(seconds, self.getFrameRate()))
        self.setProgramFlags(self.programflags() | FL_BOOKMARK)
        mlog.debug('< setBookmark %s' % seconds)
    
    def getBookmark(self):
        """Returns the bookmark in seconds as  float value or 0.0 if a bookmark does not exist"""
        seconds = mythtv.frames2seconds(self._conn.getBookmark(self), self.getFrameRate())
        if seconds:
            return seconds
        else:
            return 0.0;
    
    def editing(self):
        return (self.programflags() & FL_EDITING) != 0
    
    def cutlist(self):
        return (self.programflags() & FL_CUTLIST) != 0

    def rawFileSize(self):
        # TODO: Use decodeLongLong/encodeLongLong
        return (((self.fshigh() + (self.fslow() < 0)) * 4294967296 + self.fslow()) / 1024.0)
    
    def formattedFileSize(self):
        value = self.translator.get(46)
        # TODO: Use decodeLongLong/encodeLongLong
        size = (self.fshigh() + (self.fslow() < 0)) * 4294967296 + self.fslow()
        value = mythtv.formatSize(size / 1024.0, True)
        return value

    def getLocalPath(self):
        # Get myth:// style path and cut off everything except for the base file name. 
        # Check each local recording dir for existance of the file until we get a hit
        if self._localPath is not None:
            return self._localPath
        else:
            mythPath = self.filename()
            fileOnly = mythPath[mythPath.rfind("/")+1:]
            for localDir in self.settings.getRecordingDirs():
                localPath = localDir + os.sep + fileOnly
                if os.path.exists(localPath):
                    log.debug('Local path for %s is %s' % (self.filename(), localPath))
                    self._localPath = str(localPath) # scrub unicode
                    return self._localPath
            raise mythtv.ClientException('Could not determine local path for recording %s' % mythPath) 

    def getBareFilename(self):
        mythPath = self.filename()
        fileOnly = mythPath[mythPath.rfind("/")+1:]
        return fileOnly
        
    def getLocalThumbnailPath(self):
        return self.getLocalPath() + ".png"

    def hasLocalThumbnail(self):
        """
        Return True if the mythbacked has generated a thumbnail file and the thumbnail 
        is accessible via the local filesystem, False otherwise
        """
        return os.path.exists(self.getLocalThumbnailPath())

    def translatedRecStatus(self):
        return self.translator.get(gRecStatusTrans[self.recstatus()] )

    def getFrameRate(self):
        """
        Extracts the FPS from the physical file on first call and returns 
        the cached value thereafter as a float. Requires ffmpeg
        """
        if not self._fps:
            ffmpegParser = FFMPEG(
                ffmpeg=self.settings.get('paths_ffmpeg'),
                closeFDs=(type(self._platform) != util.WindowsPlatform))  # close_fds borked on windows
            
            try:
                metadata = ffmpegParser.get_metadata(self.getLocalPath())
            except:
                log.exception('ffmpeg parsing failed')
                metadata = None
                
            log.debug('ffmpeg metadata for %s = %s' % (self.getLocalPath(), metadata))
            if metadata:
                self._fps = float(metadata.frame_rate)
            else:
                self._fps = 29.97
                log.error("""Could not determine FPS for file %s so defaulting to %s FPS.
                             Make sure you have the ffmpeg executable in your path. 
                             Commercial skipping may be inaccurate""" % (self._fps, self.getLocalPath()))
                ui.showPopup('Error', 'FFMpeg could not determine framerate. Comm skip may be inaccurate')
        return self._fps
        
    def __repr__(self):
        return "%s {chan = %s, start = %s, end = %s, file = %s, title = '%s', Sub = %s, desc = '%.10s', hostname = %s}" % (
            type(self).__name__,                                                                                                                                       
            self.chanstr(),                                                                                           
            self.starttimeAsTime(), 
            self.endtimeAsTime(), 
            self.filename(),
            self.title(), 
            self.subtitle(), 
            self.description(), 
            self.hostname())

# =============================================================================
class Schedule(object):
    """
    Abstract base class to represent a recording schedule in the mythtv system.

    This class is baed on the Myth TV RECORD table.
    """

    def __init__(self, translator):
        self.translator = translator

    def recordid(self):
        raise NotImplementedError, "Abstract base class"
    
    def type(self):
        raise NotImplementedError, "Abstract base class"
    
    def chanid(self):
        raise NotImplementedError, "Abstract base class"
    
    def channum(self):
        raise NotImplementedError, "Abstract base class"
    
    def callsign(self):
        raise NotImplementedError, "Abstract base class"
    
    def channame(self):
        raise NotImplementedError, "Abstract base class"
    
    def icon(self):
        raise NotImplementedError, "Abstract base class"
    
    def starttime(self):
        raise NotImplementedError, "Abstract base class"
    
    def startdate(self):
        raise NotImplementedError, "Abstract base class"
    
    def endtime(self):
        raise NotImplementedError, "Abstract base class"
    
    def enddate(self):
        raise NotImplementedError, "Abstract base class"
    
    def title(self):
        raise NotImplementedError, "Abstract base class"
    
    def subtitle(self):
        raise NotImplementedError, "Abstract base class"
    
    def description(self):
        raise NotImplementedError, "Abstract base class"
    
    def category(self):
        raise NotImplementedError, "Abstract base class"
    
    def profile(self):
        raise NotImplementedError, "Abstract base class"
    
    def recpriority(self):
        raise NotImplementedError, "Abstract base class"
    
    def autoexpire(self):
        raise NotImplementedError, "Abstract base class"
    
    def maxepisodes(self):
        raise NotImplementedError, "Abstract base class"
    
    def maxnewest(self):
        raise NotImplementedError, "Abstract base class"
    
    def startoffset(self):
        raise NotImplementedError, "Abstract base class"
    
    def endoffset(self):
        raise NotImplementedError, "Abstract base class"
    
    def recgroup(self):
        raise NotImplementedError, "Abstract base class"
    
    def dupmethod(self):
        raise NotImplementedError, "Abstract base class"
    
    def dupin(self):
        raise NotImplementedError, "Abstract base class"
    
    def station(self):
        raise NotImplementedError, "Abstract base class"
    
    def seriesid(self):
        raise NotImplementedError, "Abstract base class"
    
    def programid(self):
        raise NotImplementedError, "Abstract base class"
    
    def search(self):
        raise NotImplementedError, "Abstract base class"
    
    def autotranscode(self):
        raise NotImplementedError, "Abstract base class"
    
    def autocommflag(self):
        raise NotImplementedError, "Abstract base class"
    
    def autouserjob1(self):
        raise NotImplementedError, "Abstract base class"
    
    def autouserjob2(self):
        raise NotImplementedError, "Abstract base class"
    
    def autouserjob3(self):
        raise NotImplementedError, "Abstract base class"
    
    def autouserjob4(self):
        raise NotImplementedError, "Abstract base class"
    
    def findday(self):
        raise NotImplementedError, "Abstract base class"
    
    def findtime(self):
        raise NotImplementedError, "Abstract base class"
    
    def findid(self):
        raise NotImplementedError, "Abstract base class"
    
    def inactive(self):
        raise NotImplementedError, "Abstract base class"
    
    def parentid(self):
        raise NotImplementedError, "Abstract base class"
    
    def __repr__(self):
        return "%s {recordid=%s, type=%s, title=%s, subtitle=%s, starttime=%s, endtime=%s startdate=%s, enddate=%s}" % (
            type(self).__name__,
            str(self.recordid()),
            str(self.type()),
            self.title(),
            self.subtitle(),
            self.starttime(),
            self.endtime(),
            self.startdate(),
            self.enddate())
    
    def formattedChannel(self):
        text = ""
        if self.channum():
            text += self.channum()
        if self.callsign():
            text += " - " + self.callsign()
        return text

    def formattedDuplicateMethod(self):
        return self.translator.get(gRecSchedDupMethodTrans[self.dupmethod()] )
    
    def formattedDuplicateIn(self):
        return self.translator.get(gRecSchedDupInTrans[self.dupin()] )
    
    def formattedStartDate(self):
        value = ""
        value += self.startdateAsTime().strftime( "%a, %b %d" )
        return value
    
    def formattedTime(self):
        text = "%s:%s - %s:%s"%(
            self.starttime()[0:2],
            self.starttime()[2:4],
            self.endtime()[0:2],
            self.endtime()[2:4])
        if self.startdate() != self.enddate():
            text += " +1"
        return text
    
    def formattedType(self):
        return self.translator.get(gRecSchedTypeTrans[self.type()])
    
    def formattedTypeLong(self):
        return self.translator.get(gRecSchedTypeLongTrans[self.type()])
    
    def fullTitle(self):
        """returns Title - subtitle if subtitle exists"""
        fullTitle = ""
        if self.title():
            fullTitle += self.title()
        if self.subtitle() and not sre.match( '^\s+$', self.subtitle() ):
            fullTitle += " - " + self.subtitle()
        return fullTitle

    def startdateAsTime(self):
        startdate = self.startdate()
        return datetime.datetime(
            int(startdate[0:4]), int(startdate[4:6]), int(startdate[6:8]),
            0, 0 )

# =============================================================================
class ScheduleFromQuery(Schedule):
    """
    Implementation of a Schedule object obtained from a query to the record
    table in the mythtv database.
    """
    def __init__(self, data, translator):
        Schedule.__init__(self, translator)
        
        if type(data) is dict:
            # Native MysQLdb
            self._data = data    
        else:
            # TODO: Remove me - pure python mysql
            self._data = dict(data)  
        
        if not 'icon' in self._data or not self._data['icon'] or self._data['icon'] == "none":
            self._data['icon'] = None
    
    def data(self):
        """out dict"""
        return self._data

    def recordid(self):
        """out int Unique schedule ID - 275L"""
        if self._data['recordid']:
            return int( self._data['recordid'] )
        else:
            #TODO: When would this not be populated?
            return None
    
    def type(self):
        """Return schedule type as int - See gRecSchedTypeTrans"""
        return int(self._data['type'])
    
    def chanid(self):
        """out int - Example: 1112L"""
        return self._data['chanid']
    
    def channum(self):
        """out str - Example: 11_2"""
        return self._data['channum']
    
    def callsign(self):
        """out str - Example: WTTW-DT"""
        return self._data['callsign']
    
    def channame(self):
        """out str - Example: WTTW-DT""" 
        return self._data['channame']
    
    def icon(self):
        """out str - Example: /home/mythtv/.mythtv/channels/wttw_chicago.jpg"""
        return self._data['icon']
    
    def starttime(self):
        """out str - Example: 123000, Rawtype: datetime.timedelta"""
        return dbTime2MythTime(self._data['starttime'])
    
    def startdate(self):
        """out str - Example: 20081124, Raw type: datetime.date""" 
        return dbTime2MythTime(self._data['startdate'])
    
    def endtime(self):
        """out str - Example: 113000, Rawtype: datetime.timedelta"""
        return dbTime2MythTime(self._data['endtime'])
    
    def enddate(self):
        """out str - Example: 20081101, Rawtype: datetime.date"""
        return dbTime2MythTime(self._data['enddate'])
    
    def title(self):
        """out str - Example: Austin City Limits"""
        return self._data["title"]
    
    def subtitle(self):
        """out str - Example: Gnarls Barkley; Thievery Corporation"""
        return self._data["subtitle"]
    
    def description(self):
        """out str - Example: Gnarls Barkley performs songs from their album "The Odd Couple"; Thievery Corporation performs songs from "Radio Retaliation."""
        return self._data["description"]
    
    def category(self):
        """out str - Example: Music"""
        return self._data['category']
    
    def profile(self):
        """out str - Example: Default"""
        return self._data['profile']
    
    def recpriority(self):
        """Return recording priority as int - Example: 50"""
        return int(self._data['recpriority'])
    
    def autoexpire(self):
        """out bool - Rawtype 0 or 1"""
        return bool(self._data['autoexpire'])
    
    def maxepisodes(self):
        """Return max episodes to keep as int - Min value is zero"""
        return int(self._data['maxepisodes'])
    
    def maxnewest(self):
        """Return <TODO: what does this value mean?> as int - Min value is zero"""
        return int(self._data['maxnewest'])
    
    def startoffset(self):
        """Return start offset as int"""
        return int(self._data['startoffset'])
    
    def endoffset(self):
        """Return end offset as int"""
        return int(self._data['endoffset'])
    
    def recgroup(self):
        """out str - Example: Default"""
        return self._data['recgroup']
    
    def dupmethod(self):
        """Return duplice check method as int - See gRecSchedDupMethodTrans""" 
        return int(self._data['dupmethod'])
    
    def dupin(self):
        """Return <TODO:What does this mean?> as int"""
        return int(self._data['dupin'])
    
    def station(self):
        """out str - Example: WTTW-DT"""
        return self._data['station']
    
    def seriesid(self):
        """out str - Example: EP00000439"""
        return self._data['seriesid']
    
    def programid(self):
        """out str - Example: EP000004390402"""
        return self._data['programid']
    
    def search(self):
        """out int"""
        return self._data['search']
    
    def autotranscode(self):
        """out bool - Raw type is 0 or 1""" 
        return bool(self._data['autotranscode']) 
    
    def autocommflag(self):
        """out bool - Raw type 0 or 1"""
        return bool(self._data['autocommflag'])
    
    def autouserjob1(self):
        """out bool - Raw type 0 or 1"""
        return bool(self._data['autouserjob1'])
    
    def autouserjob2(self):
        """out bool - Raw type 0 or 1"""
        return bool(self._data['autouserjob2'])
    
    def autouserjob3(self):
        """out bool - Raw type 0 or 1"""
        return bool(self._data['autouserjob3'])
    
    def autouserjob4(self):
        """out bool - Raw type 0 or 1"""
        return bool(self._data['autouserjob4'])
    
    def findday(self):
        """out int"""
        return self._data['findday']
    
    def findtime(self):
        """out datetime.timedelta"""
        return self._data['findtime']
    
    def findid(self):
        """out int - Example: 733735L"""
        return self._data['findid']
    
    def inactive(self):
        """out bool"""
        return bool(self._data['inactive'])  # raw value is 0 or 1
    
    def parentid(self):
        """out int"""
        return self._data['parentid']

# =============================================================================
class ScheduleFromProgram(ScheduleFromQuery):
    """
    Implementation of a Schedule object obtained from a ProgramFromQuery object.
    """
    def __init__(self, programFromQuery, translator):
        data = dict()
        ScheduleFromQuery.__init__(self, data, translator)
        self.data()['icon'] = programFromQuery.icon()
        self.data()['title'] = programFromQuery.data()['title']
        self.data()['subtitle'] = programFromQuery.data()['subtitle']
        self.data()['description'] = programFromQuery.data()['description']
        self.data()['category'] = programFromQuery.category()
        self.data()['chanid'] = programFromQuery.chanid()
        self.data()['channum'] = programFromQuery.chanstr()
        self.data()['callsign'] = programFromQuery.callsign()
        self.data()['seriesid'] = programFromQuery.seriesid()
        self.data()['programid'] = programFromQuery.programid()
        self.data()['channame'] = programFromQuery.channame()
        self.data()['recordid'] = None
        self.data()['type'] = "3"   # channel
        starttime = programFromQuery.starttime()
        self.data()['startdate'] = starttime[0:8]
        self.data()['starttime'] = starttime[8:14]
        endtime = programFromQuery.endtime()
        self.data()['enddate'] = endtime[0:8]
        self.data()['endtime'] = endtime[8:14]
        self.data()['profile'] = "Default"
        self.data()['recpriority'] = "0"
        self.data()['autoexpire'] = "0"
        self.data()['maxepisodes'] = "0"
        self.data()['maxnewest'] = "0"
        self.data()['startoffset'] = "0"
        self.data()['endoffset'] = "0"
        self.data()['recgroup'] = "Default"
        self.data()['dupmethod'] = "6"  # Subtitle and Description
        self.data()['dupin'] = "15"     # All
        self.data()['station'] = self.callsign()
        self.data()['search'] = "0"
        self.data()['autotranscode'] = "0"
        self.data()['autocommflag'] = "1"
        self.data()['autouserjob1'] = "0"
        self.data()['autouserjob2'] = "0"
        self.data()['autouserjob3'] = "0"
        self.data()['autouserjob4'] = "0"
        self.data()['findday'] = "0"
        self.data()['findtime'] = "00:00:00"
        self.data()['findid'] = "0"
        self.data()['inactive'] = "0"
        self.data()['parentid'] = "0"

# =============================================================================
class Tuner(object):
    """
    MythTV Tuner (aka encoder, recorder, tuner)
    
    int tunerID        - unique identifier
    str hostname       - machine where tuner is located
    int signalTimeout  - in millis
    int channelTimeout - in millis
    str tunerType      - 'HDHOMERUN', etc
    """

    #__slots__ = ('tunerID', 'hostname', 'signalTimeout', 'channelTimeout', 'tunerType', 'conn')
    
    def __init__(self, tunerID, hostname, signalTimeout, channelTimeout, tunerType = '', conn = None):
        self.tunerID = tunerID
        self.hostname = hostname
        self.signalTimeout = signalTimeout
        self.channelTimeout = channelTimeout
        self.tunerType = tunerType
        self.conn = conn
        self._channels = None
        
    def __repr__(self):
        return '%s {tunerID = %s, hostname = %s, signalTimeout = %s, channelTimeout = %s, tunerType = %s}' % (
            type(self).__name__,
            self.tunerID,
            self.hostname,
            self.signalTimeout,
            self.channelTimeout,
            self.tunerType)

    def isWatchingOrRecording(self, showName):
        """
        Return True if this tuner is watching (LiveTV) or recording 
        (according to a schedule) the given showName, False otherwise
        """
        return self.tunerID == self.conn.getTunerShowing(showName)
    
    def isRecording(self):
        """
        Returns True if recording, False Otherwise
        """
        return self.conn.isTunerRecording(self.tunerID)
    
    def waitForRecordingToStart(self, timeout, tick=1):
        """
        Block until backend reports that recording has started.
        
        @param timeout: seconds 
        @param tick: how often to check as a float in seconds
        @raise ClientException: on timeout
        """
        starttime = time.time()
        timedOut = False 
        while not self.isRecording() and not timedOut:
            time.sleep(tick)
            timedOut = (time.time() - starttime) > timeout
            log.debug('Waiting for tuner to start recording...')
        if timedOut:
            raise mythtv.ClientException('Timed out waiting for recording to start on tuner %s' % self)

    def waitForRecordingWritten(self, numKB, timeout, tick=1):
        """
        Block until a given number of kilobytes of the recording have been written to the
        filesystem.
        
        @precondition: isRecording() == true
        @param numKB: kilobytes as int 
        @param timeout: seconds as int before giving up 
        @param tick: interval in seconds as float 
        @raise ClientException: on timeout
        """
        elapsed = 0
        while True:
            currPos = int(self.getRecordingBytesWritten() / 1024)
            if currPos > numKB:
                break
            if elapsed > timeout:
                raise mythtv.ClientException('Timed out waiting for recording to start on tuner %s' % self.tunerID)   
            time.sleep(tick)
            elapsed += tick
            log.debug('Waiting %s seconds for tuner %s to write %d/%d bytes'%(
                      elapsed, self.tunerID, currPos, numKB))
            
    def getRecordingBytesWritten(self):
        """
        @precondition: isRecording() == true
        @return: int
        """
        return self.conn.getTunerFilePosition(self)
        
    def getWhatsPlaying(self):
        """
        Return whatever program is currrently being watched as livetv.
        
        @precondition: isRecording() == True
        @return: RecordedProgram
        """
        return self.conn.getCurrentRecording(self)
        
    def hasChannel(self, channel):
        """
        in  Channel - Does this tuner have this channel
        out bool    - True if this tuner can tune the given channel, false otherwise.
        """
        result = filter(lambda c: c.channum() == channel.channum(), self.getChannels())
        return len(result) == 1
    
    def getChannels(self):
        """Return channels this tuner can view as a list"""
        if self._channels is None:
            self._channels = filter(lambda c: c.tunerid() == self.tunerID, self.conn.getChannels())
        return self._channels
    
    def startLiveTV(self, channum):
        self.conn.spawnLiveTV(self, channum)
    
    def stopLiveTV(self):
        self.conn.stopLiveTV(self)
        
    def getLiveTVStatus(self):
        frames = self.conn.getFramesWritten(self)
        filePos = self.conn.getTunerFilePosition(self)
        frameRate = self.conn.getTunerFrameRate(self)
        #recording = self.conn.getCurrentRecording(self)
        return "Frames written = %s   File pos = %s  FPS = %s" % (frames, filePos, frameRate)        
