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
import domain
import logging
import mythdb
import os
import re
import socket
import sre
import string
import time
import TVState
import util
import xbmc

from util import timed
from xml.dom import minidom

log =     logging.getLogger('mythtv.core')    # mythtv core logger
wirelog = logging.getLogger('mythtv.wire')    # wire level protocol logger
mlog =    logging.getLogger('mythtv.method')  # method entry/exit logger

# TODO: Remove ourHost
try:
    global ourHost
    ourHost = socket.gethostname() 
except:
    ourHost = xbmc.getIPAddress()  # Host to use in the mythconverg settings table
    
global chainid    # TODO: Why global? What is this?
global chainpos   # TODO: Why global? What is this?
global chainCnt   # TODO: Why global? What is this?

#
# MythTV Protcol Constants
#
protocol = { 
    'initVersion'   :8,         # Initial protocol version when negotiating conn with backend (expecting REJECT)
    'clientVersion' :40,        # Protocol version this client supports (expecting ACCEPT)
    'recordSize'    :46,        # Size of each record (aka num fields)
    'sep'           :"[]:[]"    # MythTV protocol token separator
}

protocol_record_sizes = {
    40:46,
    41:46,
    42:46,
    43:47
}

socket.setdefaulttimeout(20)
        
def formatSize(sizeKB, gb=False):
    size = float(sizeKB)
    if size > 1024*1024 and gb:
        value = str("%.2f %s"% (size/(1024.0*1024.0), "GB")) # FIXME: Translate string 63
    elif size > 1024:
        value = str("%.2f %s"% (size/(1024.0), 'MB')) # FIXME: Translate string 62
    else:
        value = str("%.2f %s"% (size, 'KB')) # FIXME: Translate string 61
    return re.sub(r'(?<=\d)(?=(\d\d\d)+\.)', ',', value)

def formatSeconds(secs):
    """
    Returns number of seconds into a nicely formatted string --> 00h 00m 00s
    The hours and minutes are left off if zero 
    """
    assert secs >= 0, 'Seconds must be > 0'
    time_t = time.gmtime(secs)
    hours = time_t[3]   # tm_hour
    mins = time_t[4]    # tm_min 
    seconds = time_t[5] # tm_sec
    result = ""
    if hours > 0:
        result += "%sh" % hours
        if mins > 0 or seconds > 0:
            result += " "
    if mins > 0:
        result += "%sm" % mins
        if seconds > 0:
            result += " "
    if (len(result) == 0) or (len(result) > 0 and seconds > 0):
        result += "%ss"%seconds
    return result
    
def decodeLongLong(thirtyTwoBitLow, thirtyTwoBitHigh):
    """Returns a 64 bit long for the given 32bit low and high integers"""
    return thirtyTwoBitLow & 0xffffffffL | (thirtyTwoBitHigh << 32)

def encodeLongLong(sixtyFourBitLong):
    """Returns tuple (lower 32bits, higher 32bits) for the given 64 bit long"""
    return sixtyFourBitLong & 0xffffffffL, sixtyFourBitLong >> 32

def frames2seconds(frames, fps):
    """
    Converts a number of frames (long) to number of seconds (float w/ 2 decimal precision) 
    with given fps (float) 
    """
    return float('%.2f'%(float(long(frames) / float(fps))))

def seconds2frames(seconds, fps):
    """
    Converts number of seconds (float) to number of frames (long) with fiven fps (float)
    """  
    return long(float(seconds) * float(fps))

def createChainID():
    """Return a new chainID as a string suitable for spawning livetv"""
    # Based on livetvchain.cpp:InitializeNewChain(...)
    # Match format: live-zeus-2008-12-04T11:41:52
    return "live-%s-%s" % (socket.gethostname(), time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()))

# =============================================================================
class ProtocolException(Exception):
    """
    Thrown on protcol version mismatch between frontend and backend or
    general protocol related errors.
    """ 
    pass

class ClientException(Exception): 
    """TODO: When thrown?"""
    pass

class ServerException(Exception): 
    """
    TODO: When thrown?
    TODO: Rename to MythException
    """
    pass

class SettingsException(Exception): 
    pass

class StatusException(Exception): 
    pass

# =============================================================================
class Connection(object):
    """
    TODO: Update to support multiple storage groups - getFreeSpace()
    
    TODO: This was declared at module level but was never referenced.
          It is managed w/in the scope of this class though and the
          comment is useful.
          
          ## Used so we can 'share' the ringbuf between xbox clients
          ##  - If it's True WE created the ringbuf, else someelse did!
          ourConnection = False
          
    TODO: What is difference between MONITOR and PLAYBACK in mythtv
          protocol?
          
    TODO: Rename to MythSession
    """
    
    def __init__(self, settings, db, translator, platform):
        """
        @param settings: Mythbox settings
        @param db: mysql db connection
        @param translator: localized strings
        @param platform: Platform instance 
        """
        self.db = db
        self.settings = settings
        self.translator = translator
        self.platform = platform
        self.initialise()
        
    #def __del__(self):
    #    # TODO: Only close if we haven't already
    #    self.close()

    @timed
    def initialise(self):
        """
        Initializes this connection and attempts to connect to the master
        myth backend server.
        """
        try:
            self.host = self.settings.get("mythtv_host")
            self.port = int(self.settings.get("mythtv_port"))

            # True if we initiated the request for the tuner to start playing/recording, false otherwise
            self.ourConnection = True

            # Command socket used to talk to the backend
            self.cmdSock = self.connect(self.host)
            self.isConnected = True
        except:
            self.isConnected = False
            raise

    def connect(self, server, Playback=False, Monitor=True):
        """ 
        Return a socket after successfully connecting to the myth backend server.
        
        Used in three scenarios:
            - connect to server as Player
            - connect to server as Monitor
            - connect to server as raw socket connection
        
        @param server: mythv backend hostname as string
        """
        log.debug("Connection.connect(%s,%s,%s)"%(server, Playback, Monitor))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server, self.port))
        
        if Monitor or Playback:
            if bool(self.settings.get('mythtv_version_override')):
                if not 'serverVersion' in protocol:
                    rejectSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    rejectSocket.connect((server, self.port))
                    try:
                        # induce reject
                        self.negotiateProtocol(rejectSocket, server, protocol['initVersion'])
                    except ProtocolException, pe:
                        # override recordsize for server version
                        protocol['serverVersion'] = pe.protocolVersion
                        protocol['recordSize'] = protocol_record_sizes[pe.protocolVersion]
                        log.debug('Server talks protocol %s' % protocol['serverVersion'])
                    rejectSocket.close()
                    
                self.negotiateProtocol(s, server, protocol['serverVersion'])
            else:
                self.negotiateProtocol(s, server, protocol['clientVersion'])
            
        # TODO: These are mutually exclusive but both can be true when 
        #       sent in as arguments to this method. Check w/ assertion   
        if Monitor:
            self.annMonitor(s)
        elif Playback:
            self.annPlayback(s)
            
        return s

    def reConnect(self):
        # TODO: Not convinced we need this. If we do, refactor as a decorator
        #       to be non-invasive
         
        # If we loose our connection reconnect
        log.debug("Connection.reConnect()" )
        self.cmdSock = self.connect( self.host, False, True )

        if not self.isConnected:
            self.close()
            raise ProtocolException, "Unable to connect to backend"

    def close(self):
        if self.cmdSock:
            if int(self.isConnected) > 0:
                self.sendMsg(self.cmdSock, ['DONE'])
                self.isConnected = 0
            self.cmdSock.shutdown(socket.SHUT_RDWR)
            self.cmdSock.close()
            self.cmdSock = None
            
        if self.db:
            self.db.close()
                
    @timed            
    def negotiateProtocol(self, s, theHost, protocolVersion):
        """ 
        Returns the int version of the MythTV protocol the server supports. 
        Raises ProtocolException if this client does not support the server
        protocol version.
        """
        #clientVersion = protocol['clientVersion']
        clientVersion = protocolVersion
        msg = "MYTH_PROTO_VERSION %s" % clientVersion
        reply = self.sendRequest(s, [msg])
        
        if reply:
            serverResponse = reply[0]
            serverVersion  = int(reply[1])
            wirelog.debug('negotiateProtocol: %s => %s %s' % (msg, serverResponse, serverVersion))
            
            if (clientVersion < serverVersion):
                pe = ProtocolException("Server talks MythTV protocol version %s but we only support version %s."%(
                    serverVersion, clientVersion))
                pe.protocolVersion = int(serverVersion)
                raise pe   
                    
#            if not self.isAccept(reply, clientVersion):
#                log.debug('sending proto version again since first reply wasnt accepted')
#                secondReply = self.sendRequest(s, ["MYTH_PROTO_VERSION %s" % serverVersion])
#                secondServerResponse = secondReply[0]
#                secondServerVersion  = int(secondReply[1])
#
#                # make sure server ACCEPT'ed us on second try..
#                if self.isAccept(secondReply, serverVersion):
#                    wirelog.debug('Server talking protocol version %s' % secondServerVersion)
#                else:
#                    wirelog.error("Couldn't negotiate protocol version with server")
            return int(serverVersion)
        else:
            return 0

    @timed
    def annPlayback(self, cmdSock):
        reply = self.sendRequest(cmdSock, ["ANN Playback %s 0" % ourHost])
        if not self.isOk(reply):
            raise ServerException, "Backend playback refused: %s" % reply
    
    @timed
    def annMonitor(self, cmdSock):
        reply = self.sendRequest(cmdSock, ["ANN Monitor %s 0" % ourHost])
        if not self.isOk(reply):
            raise ServerException, "Backend monitor refused: %s" % reply

    @timed
    def annFileTransfer(self, backendHost, filePath):
        """
        Announce file transfer to backend.
        
        @param backendHost : Hostname of backend that recorded the file to transfer
        @param filePath    : myth style URL of file to tranfer. Ex: myth://somehost:port/blah.mpg
        @return            : list[reply[], socket] 
        """
        s = self.connect(backendHost, False, False)
        self.sendMsg(s, ["ANN FileTransfer %s" % ourHost,filePath])
        reply = self.readMsg(s)
        if not self.isOk(reply):
            raise ServerException("Backend filetransfer refused: %s" % reply)
        del reply[0]    # remove OK
        return [reply,s]
        
    def checkFile(self, rec):
        # TODO: Whats this for? Not used currently
        msg = rec.data()[:]
        msg.insert(0,'QUERY_CHECKFILE')
        reply = self.sendRequest(msg)
        return reply[0]

    def getSetting(self, key, hostname):
        """
        Returns domain.MythSetting for the given key and hostname
        """
        command = 'QUERY_SETTING %s %s' %(key, hostname)
        reply = self.sendRequest(self.cmdSock, [command])
        return reply
        # TODO: Unfinished!
    
    def getChannels(self):
        # straight passthrough to db
        return self.db.getChannels()
    
    @timed
    def getTuners(self):
        """out Tuner[] - Get available tuners (aka encoder, recorder, capturecard, cardinput)"""
        tuners = self.db.getTuners()
        # inject each tuner w/ this session before returning
        for t in tuners:
            t.conn = self
        return tuners
    
    @timed
    def getFramesWritten(self, tuner):
        """For a tuner that is recording, return the number of frames written as an int"""
        reply = self.sendRequest(self.cmdSock, ['QUERY_RECORDER %d' % tuner.tunerID, 'GET_FRAMES_WRITTEN'])
        return decodeLongLong(int(reply[1]), int(reply[0]))

    @timed
    def getTunerFrameRate(self, tuner):
        """For a tuner that is recording, return the framerate as a float"""
        reply = self.sendRequest(self.cmdSock, ['QUERY_RECORDER %d' % tuner.tunerID, 'GET_FRAMERATE'])
        return float(reply[0])

    @timed 
    def getCurrentRecording(self, tuner):
        """For a tuner that is recording, return the program info as a ProgramFromQuery"""
        reply = self.sendRequest(self.cmdSock, ['QUERY_RECORDER %d' % tuner.tunerID, 'GET_CURRENT_RECORDING'])
        program = domain.RecordedProgram(reply, self, self.settings, self.translator, self.platform)
        return program
        
    @timed
    def getTunerShowing(self, showName):
        """ 
        Returns the tunerID of the first tuner either recording or watching 
        the given showname, otherwise returns -1
              
        TODO: Change return type to domain.Tuner or None
        TODO: Rename to getTunerWatchingOrRecording(...)
        """ 
        tuners = self.db.getTuners()
        for tuner in tuners:
            tvState = int(self.sendRequest(self.cmdSock, ["QUERY_REMOTEENCODER %d"%tuner.tunerID, "GET_STATE" ])[0])
            curRecording = self.sendRequest(self.cmdSock, ["QUERY_RECORDER %d"%tuner.tunerID, "GET_RECORDING"])[0]
            
            if tvState == TVState.OK:  # not busy
                break
            elif tvState == TVState.Error:
                log.warning('QUERY_REMOTEENCODER::GET_STATE = Error')
                break
            elif tvState == TVState.WatchingPreRecorded:
                log.warning('TODO: What should we do here?')
                break
            elif tvState in [TVState.WatchingLiveTV, TVState.RecordingOnly]:
                if showName == curRecording:
                    return int(tuner.tunerID)
            else:
                break
        return -1

    @timed
    def getTunerStatus(self, encoder="All"):
        """
        When getting the status of a single tuner, returns current status as a string
        When getting the status of all tuners, returns a list of current status strings

        TODO: Fix so always returns the same type -- a list
        """
        if string.upper(encoder) == "ALL":
            curStatus = []
            encoders = self.db.getTuners()

            for tuner in encoders:
                log.debug("tuner: %s" %str(tuner))
                curStatus.append(self.getTunerStatus(str(tuner.tunerID)))
        else:
            theState = self.sendRequest(self.cmdSock, ["QUERY_REMOTEENCODER %s"%encoder, "GET_STATE"])
            curRecording = self.sendRequest(self.cmdSock, ["QUERY_RECORDER %s"%encoder, "GET_RECORDING"])
            if theState[0] == "0":
                curStatus = "Tuner %s is not recording" % encoder
            elif theState[0] == "1":
                curStatus = "Tuner %s is Currently Watching %s on %s. Show will end at %s."%(
                            encoder, curRecording[0], curRecording[7], time.strftime("%I:%M%p", time.localtime(float(curRecording[27]))))
            elif theState[0] == "4":
                curStatus = "Tuner %s is Currently Recording %s on %s. Recording will finish at %s"%(
                            encoder, curRecording[0], curRecording[7], time.strftime("%I:%M%p", time.localtime(float(curRecording[27]))))
            elif theState[0] == "-1":
                curStatus = "Tuner %s is Currently not Connected"%encoder
            elif theState[0] == "bad":
                curStatus = "Tuner %s is Currently not Connected"%encoder
            else:
                curStatus = "Tuner %s has an Unknown State: %s."%(encoder, theState[0])
        return curStatus

    @timed
    def getNumFreeTuners(self):
        return int(self.sendRequest(self.cmdSock, ['GET_FREE_RECORDER_COUNT'])[0])

    @timed
    def getNextFreeTuner(self, afterRecorderID):
        """ 
        Returns the (int recorderID, string IP, int port) of the next free recorder after the passed in int recorderID
        """
        # TODO: Write unit test
        command = 'GET_NEXT_FREE_RECORDER'
        reply = self.sendRequest(self.cmdSock, [command, str(afterRecorderID)])
        recorderID = int(reply[0])
        if reply[0] == -1:
            # No recorders available
            return None, None, None
        else:
            # Success
            backendServer = reply[1]
            backendPort = reply[2]
            return (recorderID, backendServer, int(backendPort))

    @timed
    def spawnLiveTV(self, tuner, channum):
        """
        Instructs myth backend to start livetv on the given tuner. 
        A unique chainID is generated and returned if successful. 
        A ProtocolException is raised otherwise.
        
        @param tuner: Tuner to start live tv on
        @param channum: channel to tune as string 
        @return: generated chainID as string
        """
        # void SpawnLiveTV(QString chainid, bool pip, QString startchan);
        chainID = createChainID()
        pip = str(int(False))
        reply = self.sendRequest(self.cmdSock, ["QUERY_RECORDER %s" % tuner.tunerID, "SPAWN_LIVETV", chainID, pip, channum])
        log.debug('spawnLiveTV response = %s' % reply)
        if not self.isOk(reply):
            raise ServerException('Error spawning live tv on tuner %s with reply %s' % (tuner, reply))
        return chainID
        
    @timed
    def stopLiveTV(self, tuner):
        """
        Stops live tv. Throws ServerException on error. 
        
        @param tuner: Tuner on which livetv has already been started
        """
        reply = self.sendRequest(self.cmdSock, ["QUERY_RECORDER %s" % tuner.tunerID, "STOP_LIVETV"])
        log.debug('stopLiveTV response = %s' % reply)
        if not self.isOk(reply):
            raise ServerException('Error stopping live tv on tuner %s with reply %s' % (tuner, reply))
                
    @timed
    def getFreeTuner(self):
        """
        Returns the (int recorderID, str IP address, int port) of a recorder that is not busy, tuple of -1 otherwise
        """
        command = 'GET_FREE_RECORDER'
        reply = self.sendRequest(self.cmdSock, [command])
        if reply[0] == "-1":
            # No recorders available
            return (-1, '', -1)
        else:
            recorderID = reply[0]
            backendServer = reply[1]
            backendPort = reply[2]
            return (int(recorderID), backendServer, int(backendPort))
               
    def finishRecording(self, encID):
        # TODO: Not used - consider deleting
        try:
            reply = self.sendRequest( self.cmdSock, ["QUERY_RECORDER %s"%encID, "FINISH_RECORDING"])
            log.debug( "FINISH RECORDING: %s" % reply)
            if string.upper(reply[0]) == "OK":
                return True
            else:
                return False
        except:
            # TODO: Raise instead?
            log.exception('finishRecording: encID = %s'%encID)
            
    def cancelNextRecording(self, encID):
        # TODO: Not used - consider deleting
        try:
            reply = self.sendRequest(self.cmdSock, ["QUERY_RECORDER %s"%encID, "CANCEL_NEXT_RECORDING"])
            log.debug ( "CANCEL NEXT RECORDING: %s"%reply)
            if reply == "ok":
                return True
            else:
                return False
        except:
            # TODO: Raise instead?
            log.exception('cancelNextRecording: encID = %s'%str(encID))
    
    @timed                 
    def isTunerRecording(self, tunerID):
        """
        @param tunderID: int tuner id
        @return: True if tuner is currently recording, False otherwise.
        """
        command = ['QUERY_RECORDER %d'%tunerID, 'IS_RECORDING']
        reply = self.sendRequest(self.cmdSock, command)
        if reply[0] == "0":
            return False
        elif reply[0] == "1":
            return True
        else:
            raise ProtocolException, "Invalid response '%s' received for command '%s'"%(reply[0], command)
        
    def isPendingRecording(self, encID,  minutesNotice=1):
        """ Check if there is a Recording Pending on this encoder (Used by OSD) """
        # TODO: Not used - consider deleting
        try:
            ## Get the seconds till the NEXT recording on this Encoder in the next 5 minutes!
            recordings = self.getPendingRecordings(6)
            for r in recordings:
                # Might be inputid() or sourceid() ???
                if str(r.cardid()) == str(encID):
                    stTime = r.recstarttime()
                    ## If the rec start time isn't set use the normal start time!
                    if int(stTime) == 0:
                        stTime = r.starttimets()

                    nxtTime = int(stTime) - int(time.time())
                    if nxtTime < ( 60 * minutesNotice ) and nxtTime > 0:
                        log.debug("Found pending recording for Encoder %s and it starts in %s seconds" % ( str(encID), str(nxtTime) ) )
                        return [r.title(),r.subtitle(),nxtTime]
        except:
            # TODO: Raise instead?
            log.exception('isPendingRecording: encID = %d  minutesNotice = %s'%(encID, minutesNotice))
        return None
                    
    def getTunerFilePosition(self, tuner):
        """For a tuner that is recording, return the current position in the file as an int"""
        reply = self.sendRequest(self.cmdSock, ["QUERY_RECORDER %d" % tuner.tunerID, "GET_FILE_POSITION"])
        return decodeLongLong(int(reply[1]), int(reply[0]))

    def buildMsg(self, msg):
        msg = string.join(msg, protocol['sep'])
        return "%-8d%s" % (len(msg), msg)

    @timed
    def deleteRecording(self, rec):
        """
        @param rec: RecordedProgram to delete
        @return: TODO
        """
        msg = rec.data()[:]
        msg.insert(0, 'DELETE_RECORDING')
        msg.append('0')
        reply = self.sendRequest(self.cmdSock, msg)
        if sre.match('^-?\d+$', reply[0]):
            rc = int(reply[0])
        else:
            raise ServerException, reply[0]
        log.debug("deleted recording %s with response %s"%(rec.title(), rc))
        return rc    # number deleted

    @timed
    def rerecordRecording(self, rec):
        """
        @param rec: RecordedProgram to delete and re-record
        @return: TODO
        """
        msg = rec.data()[:]
        msg.insert(0, 'DELETE_RECORDING')
        msg.append('0')
        reply = self.sendRequest(self.cmdSock, msg)
        if sre.match('^-?\d+$', reply[0]):
            rc1 = int(reply[0])
        else:
            raise ServerException, reply[0]
        msg = rec.data()[:]
        msg.insert(0, 'FORGET_RECORDING')
        msg.append('0')
        reply = self.sendRequest(self.cmdSock, msg)
        if sre.match('^-?\d+$', reply[0]):
            rc2 = int(reply[0])
        else:
            raise ServerException, reply[0]
        
        log.debug("deleted and allowed re-record of [%s] with results %s and %s" %(rec.title(), rc1, rc2))
        return rc1    # number deleted

    @timed
    def generateThumbnail(self, program, backendHost):
        """
        Request the backend generate a thumbnail for a program. The backend generates 
        the thumbnail and persists it do the filesystem regardless of whether a 
        thumbnail existed or not. Thumbnail path = recording path + '.png'  
        
        @param program: Program
        @param backendHost: string
        @return: True if successful, False otherwise 
        """
        msg = program.data()[:]
        
        # clear out fields - this is based on what mythweb does
        # mythtv-0.16
        msg[0] = ' '    # title
        msg[1] = ' '    # subtitle
        msg[2] = ' '    # description
        msg[3] = ' '    # category
                        # chanid
        msg[5] = ' '    # channum
        msg[6] = ' '    # chansign
        msg[7] = ' '    # channame
                        # filename
        msg[9] = '0'    # upper 32 bits
        msg[10] = '0'   # lower 32 bits
                        # starttime
                        # endtime
        msg[13] = '0'   # conflicting
        msg[14] = '1'   # recording
        msg[15] = '0'   # duplicate
                        # hostname
        msg[17] = '-1'  # sourceid
        msg[18] = '-1'  # cardid
        msg[19] = '-1'  # inputid
        msg[20] = ' '   # recpriority
        msg[21] = ' '   # recstatus
        msg[22] = ' '   # recordid
        msg[23] = ' '   # rectype
        msg[24] = '15'  # dupin
        msg[25] = '6'   # dupmethod
                        # recstarttime
                        # recendtime
        msg[28] = ' '   # repeat
        msg[29] = ' '   # program flags
        msg[30] = ' '   # recgroup
        msg[31] = ' '   # commfree
        msg[32] = ' '   # chanoutputfilters
                        # seriesid
                        # programid
                        # dummy lastmodified
                        
        msg[36] = '0'   # dummy stars
                        # dummy org airdate
        msg[38] = '0'   # hasAirDate
        msg[39] = '0'   # playgroup
        msg[40] = '0'   # recpriority2
        msg[41] = '0'   # parentid
                        # storagegroup
        msg.append('')  # trailing separator
        msg.insert(0, 'QUERY_GENPIXMAP')

        s = self.connect(backendHost, Playback=False, Monitor=True)
        reply = self.sendRequest(s, msg)
        result = self.isOk(reply)
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        return result

    @timed
    def getThumbnailCreationTime(self, program, backendHost):
        """
        Get the time at which the thumbnail for a program was generated.
        
        @param program: Program
        @param backendHost: string
        @return: datetime of thumbnail generation or None if never generated 
        """
        msg = program.data()[:]
        
        # clear out fields - this is based on what mythweb does
        # mythtv-0.16
        msg[0] = ' '    # title
        msg[1] = ' '    # subtitle
        msg[2] = ' '    # description
        msg[3] = ' '    # category
                        # chanid
        msg[5] = ' '    # channum
        msg[6] = ' '    # chansign
        msg[7] = ' '    # channame
                        # filename
        msg[9] = '0'    # upper 32 bits
        msg[10] = '0'   # lower 32 bits
                        # starttime
                        # endtime
        msg[13] = '0'   # conflicting
        msg[14] = '1'   # recording
        msg[15] = '0'   # duplicate
                        # hostname
        msg[17] = '-1'  # sourceid
        msg[18] = '-1'  # cardid
        msg[19] = '-1'  # inputid
        msg[20] = ' '   # recpriority
        msg[21] = ' '   # recstatus
        msg[22] = ' '   # recordid
        msg[23] = ' '   # rectype
        msg[24] = '15'  # dupin
        msg[25] = '6'   # dupmethod
                        # recstarttime
                        # recendtime
        msg[28] = ' '   # repeat
        msg[29] = ' '   # program flags
        msg[30] = ' '   # recgroup
        msg[31] = ' '   # commfree
        msg[32] = ' '   # chanoutputfilters
                        # seriesid
                        # programid
                        # dummy lastmodified
                        
        msg[36] = '0'   # dummy stars
                        # dummy org airdate
        msg[38] = '0'   # hasAirDate
        msg[39] = '0'   # playgroup
        msg[40] = '0'   # recpriority2
        msg[41] = '0'   # parentid
                        # storagegroup
        msg.append('')  # trailing separator
        msg.insert(0, 'QUERY_PIXMAP_LASTMODIFIED')

        s = self.connect(backendHost, Playback=False, Monitor=True)
        reply = self.sendRequest(s, msg)
        #result = self.isOk(reply)
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        dt = datetime.datetime.fromtimestamp(float(reply[0]))
        return dt
    
    @timed
    def getPendingRecordings(self, cnt="ALL", query='QUERY_GETALLPENDING'):
        log.debug("getting pending recordings = %s" % query)
        retRows = []
        offset = 0
        reply = self.sendRequest(self.cmdSock, [query,'2'])
        # determine how many rows were retrieved
        numRows = int( reply[1] )
        offset += 2

        if string.upper(str(cnt)) != "ALL":
            numRows = int(cnt)

        for i in range(0,numRows):
            retRows.append(domain.RecordedProgram(
                    reply[offset:offset+protocol['recordSize']],
                    self, 
                    self.settings, 
                    self.translator,
                    self.platform))
            offset += protocol['recordSize']
        return retRows

    @timed
    def getRecordings(self, recgroup='default', title='all shows'):
        """
        Returns a list of RecordedProgram for the given recording
        group and show title (both case insensetive)
        """
        query='QUERY_RECORDINGS Delete' # Delete = order recordings newest to oldest
        log.debug("getting recordings matching (%s, %s, %s)" % (query, recgroup, title))
 
        """
        Sample response (Protocol 40):

        0  32[]:[]   -- total number of recordings 
        1  Check, Please[]:[]
        2  []:[]
        3  []:[]
        4  Public affairs[]:[]
        5  1111[]:[]
        6  11_1[]:[]
        7  WTTW-HD[]:[]
        8  WTTW-HD[]:[]
        9  myth://192.168.1.11:6543/1111_20081018020000.mpg[]:[]
        10 0[]:[]
        11 990891036[]:[]
        12 1224313200[]:[]
        13 1224315000[]:[]
        14 0[]:[]
        15 0[]:[]
        16 0[]:[]
        17 zaran[]:[]
        18 0[]:[]
        18 0[]:[]
        20 0[]:[]
        21 0[]:[]
        22 -2[]:[]
        23 143[]:[]
        24 0[]:[]
        25 15[]:[]
        26 6[]:[]
        27 1224313200[]:[]
        28 1224315000[]:[]
        29 0[]:[]
        30 36[]:[]
        31 Default[]:[]
        32 0[]:[]
        33 []:[]
        34 EP00452387[]:[]
        35 SH004523870000[]:[]
        36 1224313972[]:[]
        37 0.000000[]:[]
        38 2001-07-20[]:[]
        39 1[]:[]
        40 Default[]:[]
        41 0[]:[]
        42 0[]:[]
        43 Default[]:[]
        44 0[]:[]
        45 0[]:[]
        46 0[]:[]
        -------------------
        47 Seinfeld[]
        ...
        """
        retRows = []
        offset = 0
        reply = self.sendRequest(self.cmdSock, [query])
        numRows = int(reply[0])
        offset += 1

        for i in range(0, numRows):
            tmpArray = reply[offset:offset+protocol['recordSize']]
            if ((string.upper(tmpArray[30]) == string.upper(recgroup) or string.upper(recgroup) == "ALL GROUPS")
                and (string.upper(tmpArray[0]) == string.upper(title) or string.upper(title) == "ALL SHOWS")):
                retRows.append(domain.RecordedProgram(tmpArray, self, self.settings, self.translator, self.platform))
            offset += protocol['recordSize']
        return retRows

    @timed
    def getBookmark(self, program):
        """
        Return the frame number of the bookmark as a long for the passed in program or 
        zero if no bookmark is found.
        """
        command = 'QUERY_BOOKMARK %s %s' %(program.chanid(), program.starttimets())
        reply = self.sendRequest(self.cmdSock, [command])
        bookmarkFrame = decodeLongLong(int(reply[1]), int(reply[0])) 
        log.debug('bookmarkFrame = int %s int %s => long %s' %(reply[0], reply[1], bookmarkFrame))
        return bookmarkFrame
    
    @timed
    def setBookmark(self, program, frameNumber):
        """
        Sets the bookmark for the given program to frameNumber. 
        Raises ServerException on failure.
        """
        lowWord, highWord = encodeLongLong(frameNumber)
        command = 'SET_BOOKMARK %s %s %s %s' %(
            program.chanid(), program.starttimets(), highWord, lowWord)
        reply = self.sendRequest(self.cmdSock, [command])
        
        if reply[0] == 'OK':
            log.debug("Bookmark frameNumber set to %s" % frameNumber)
        elif reply[0] == 'FAILED':
            raise ServerException(
                "Failed to save position in program '%s' to frame %s. Server response: %s" %(
                program.title(), frameNumber, reply[0]))
        else:
            raise ProtocolException('Unexpected return value: %s' % reply[0])
    
    @timed
    def getCommercialBreaks(self, program):
        """
        Return a list of CommercialBreaks for the given recording in 
        chronological order.
        """
        COMM_START = 4
        COMM_END   = 5
        
        command = 'QUERY_COMMBREAK %s %s' %(program.chanid(), program.starttimets())
        reply = self.sendRequest(self.cmdSock, [command])
        #log.debug('response lines = %s' % len(reply))
        numRecs = int(reply[0])
        commBreaks = []
        
        if numRecs == -1:
            return commBreaks
        
        if numRecs % 2 != 0:
            raise  ClientException, 'Expected an even number of comm break records but got %s instead' % numRecs
        
        recSize = 3
        for i in xrange(0, numRecs, 2):  # skip by 2's -- 1 for start + 1 for end
            baseIndex = i * recSize
            #log.debug('baseIndex = %s'%baseIndex)
            commFlagStart = int(reply[baseIndex + 1])
            if commFlagStart != COMM_START:
                raise ProtocolException, 'Expected COMM_START for record %s but got %s instead' % ((i+1), commFlagStart)
            else:
                frameHigh = int(reply[baseIndex + 2])
                frameLow  = int(reply[baseIndex + 3])
                frameStart = decodeLongLong(frameLow, frameHigh)
                commFlagEnd = int(reply[baseIndex + 4])
                if commFlagEnd != COMM_END:
                    raise ProtocolException, 'Expected COMM_END for record %s but %s instead' %((i+2), commFlagEnd)
                else:
                    frameHigh = int(reply[baseIndex + 5])
                    frameLow  = int(reply[baseIndex + 6])
                    frameEnd = decodeLongLong(frameLow, frameHigh)
                    commBreak = domain.CommercialBreak(
                        frames2seconds(frameStart, program.getFrameRate()),
                        frames2seconds(frameEnd, program.getFrameRate()))
                    commBreaks.append(commBreak)
        log.debug('%s commercials in %s' %(len(commBreaks), program.title()))
        return commBreaks
        
    @timed    
    def getSingleProgram(self, chanid, starttime, endtime):
        shows = self.getRecordings("ALL GROUPS","ALL SHOWS")
        for s in shows:
            log.debug("comparing chanid=%s starttime=%s endtime=%s"%(
                s.chanid(), s.starttime(), s.endtime()))
            if s.chanid() == chanid and \
                s.starttime()[:-4] == starttime[:-4] and \
                s.endtime() == endtime:
                log.debug("< mythtv.getSingleProgram() => %s"%s)
                return s
        return None

    def isAccept(self, msg, protocolVersion):
        return msg[0] == "ACCEPT" and msg[1] == str(protocolVersion)

    def isOk(self, msg):
        """
        @return: True if myth response message indicates request completed OK, false otherwise
        """
        if msg == None or len(msg) == 0:
            return False
        else:
            return string.upper(msg[0]) == "OK"

    def getFreeSpace(self):
        """
        Returns a list with : [free space, total space, used space] in bytes

        TODO: Update so support multiple storage groups. For now, just return
              the stats on the first storage group
        """
        # 
        # Sample response with multiple storage groups as of protocol 40
        #
        # (this example is actually off by 1, zaran below is correct)
        #
        # theP4[]:[]/media/mainlv/mythtv[]:[]1[]:[]-1[]:[]0[]:[]63799104[]:[]0[]:[]61376252[]:[]theP4[]:[]/media/disk/mythtv/data[]:[]0[]:[]-1[]:[]0[]:[]75884640[]:[]0[]:[]73477128
        # 0--->     1------------------>     2     3      4     5------>     6     7------>     8--->     9--------------------->     10    11     12   13------>     14    15----->
        #
        # zaran[]:[]/usr2/mythtv[]:[]0[]:[]-1[]:[]2[]:[]0[]:[]477505408[]:[]0[]:[]140160576 + rinse & repeat for each additional storage group
        # 0         1                2     3      4     5     6             7     8
        #

        space = []
        try:
            reply = self.sendRequest( self.cmdSock, ["QUERY_FREE_SPACE"] )
            totalSpace = reply[6]
            usedSpace = reply[8]
            freeSpace = int(totalSpace) - int(usedSpace)
            space.append(formatSize(freeSpace, True))
            space.append(formatSize(totalSpace, True))
            space.append(formatSize(usedSpace, True))
        except:
            log.exception('getFreeSpace')
            space.append("")
            space.append("")
            space.append("")
        return space

    def getLoad(self):
        """
        Returns list of cpu loads for the last 1, 5, and 15 minutes
        """
        reply = self.sendRequest( self.cmdSock, ["QUERY_LOAD"])
        log.debug('Load = %s' % reply)
        load = []
        load.append(reply[0])
        load.append(reply[1])
        load.append(reply[2])
        return load

    def getUptime(self):
        """
        Returns a list (one element) with the uptime of the backend in seconds.
        If a non-unix based host, returns the string 'Could not determine uptime.'
        """
        # TODO: Not used - consider deleting
        reply = self.sendRequest(self.cmdSock, ["QUERY_UPTIME"])
        log.debug ('Uptime = %s' % reply)
        return reply

    @timed
    def getMythFillStatus(self):
        start = self.db.getMythSetting("mythfilldatabaseLastRunStart")
        end = self.db.getMythSetting("mythfilldatabaseLastRunEnd")
        status = self.db.getMythSetting("mythfilldatabaseLastRunStatus")
        fillStatus = "Programming guide info retrieved on %s" % start
        if end > start:
            fillStatus += " and ended on %s" % end
        fillStatus += ". %s" % status
        return fillStatus

    @timed
    def getGuideData(self):
        lastShow = self.db.getLastShow()
        dataStatus = ""
        if lastShow == None:
            dataStatus = "There's no guide data available! Have you run mythfilldatabase?"
        else:
            timeDelt = lastShow - datetime.datetime.now()
            daysOfData = timeDelt.days + 1
            log.debug("days of data: %s" % daysOfData)
            log.debug("End Date: %s Now: %s Diff: %s" % (lastShow, datetime.datetime.now(), str(lastShow - datetime.datetime.now())))
            dataStatus = "There's guide data until %s (%s" % (lastShow.strftime("%Y-%m-%d %H:%M"), daysOfData)
            if daysOfData == 1:
                dataStatus += "day"
            else:
                dataStatus += "days"
            dataStatus += ")."
        if daysOfData <= 3:
            dataStatus += "WARNING: is mythfilldatabase running?"
        return dataStatus

    def readMsg(self, s):
        ## Was getting errors with this (s.recv was string that couldn't be converted to int!)
        retMsg = ""
        try:
            retMsg = s.recv(8)
            #wirelog.debug("REPLY: %s"%retMsg)
            reply = ""
            if string.upper(retMsg) == "OK":
                return "OK"
            wirelog.debug("retMsg: [%d] %s"% (len(retMsg), retMsg))
            n = int(retMsg)
            #wirelog.debug("reply len: %d" % n)
            i = 0
            while i < n:
                #wirelog.debug (" i=%d n=%d " % (i,n))
                reply += s.recv(n - i)
                i = len(reply)

            wirelog.debug("read  <- %s" % reply)
            return reply.split(protocol['sep'])
        except:
            log.exception("Error reading message: %s" % retMsg)
            raise

            # TODO: Handle timeout gracefully
            #        
            #            if str(ex) == "timed out" :
            #                # self.reConnect()
            #                log.debug("readMsg: Timed Out")
            #                return "timeout"
            #            elif ex[1] == "Connection reset by peer":
            #                self.reConnect()
            #                return "reset"
            #            else:
            #                log.debug ("READ MSG ERROR: %s" %str(ex) )
            #                log.debug ("RETURNED: %s" %str(retMsg) )
            #                #traceback.print_exc()

    def sendMsg(self, s, req):
        try: 
            msg = self.buildMsg(req)
            wirelog.debug("write -> %s" % msg)
            s.send(msg)
        except:
            # TODO: Raise instead?
            wirelog.exception('Error sending msg over socket')
            
    def sendRequest(self, s, msg):
        #wirelog.debug("> sendRequest: %s" % msg)
        
        # TODO: should we arbitrarily re-est the conn?
        if s == None:
            s = self.connect(self.host, False, False)
            
        self.sendMsg(s, msg)
        reply = self.readMsg(s)
        #wirelog.debug("< sendRequest: %s" % reply)
        return reply
        
    def sendRequestAndCheckReply(self, msg, errorMsg="Unexpected reply from server: "):
        wirelog.debug( "> sendRequestAndCheckReply: %s" % msg) 
        reply = self.sendRequest(msg)
        if not self.isOk(reply):
            wirelog.debug("reply = %s" % reply)
            raise ServerException, errorMsg + str(reply)
        else: 
            wirelog.debug("< sendRequestAndCheckReply") 
                
    def getFileSize(self, backendPath, theHost):
        """
        Method to retrieve remote file size.  The backendPath is in the format
        described by the transferFile method.
        """
        # TODO: Not used - consider deleting
        rc = 0
        ft,s = self.annFileTransfer(theHost, backendPath)
        log.debug("ft=<%s>" % ft)
        rc = long(ft[2])
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        s = None
        return rc
        
    def rescheduleNotify(self, schedule = None):
        """
        Method to instruct the backend to reschedule recordings.  If the
        schedule is not specified, all recording schedules will be rescheduled
        by the backend.
        """
        mlog.debug("> rescheduleNotify(schedule= %s)" % schedule)
        s = self.connect(self.host, False, True)
        recordId = None
        if schedule:
            recordId = schedule.recordid()
        if recordId == None:
            recordId = 0
        reply = self.sendRequest(s, ["RESCHEDULE_RECORDINGS %d" % recordId])
        if int(reply[0]) < 0:
            raise ServerException, "Reschedule notify failed: %s" % reply
        mlog.debug("< rescheduleNotify")

    def transferFile(self, backendPath, destPath, backendHost):
        """
        Transfer a file from the remote backendPath to destPath. 
        The file could be a recording or a thumbnail for a recording. 
        
        @param backendPath: myth url to file. Ex: myth://<host>:<port><path>
        @param destPath: destinal file on local filesystem     
        @param backendHost: The backend that recorded the file.
        @return 0 on success, -1 on failure
        """
        # TODO: Improve readability
        #
        # while file not fully transferred
        #    request data on cmdSocket
        #    read data on dataSocket
        #    send response on cmdSocket
        #
        mlog.debug("> transferFile")
        rc = 0
        maxTransferBufferSize   = 1*1024*1024   # 1MB

        thisCmdSock = self.connect(backendHost, False, True)
        ft,s = self.annFileTransfer(backendHost, backendPath)
        
        log.debug("ft = %s" % ft)
        n = long(ft[2])
        if n > 0:
            msg = ['QUERY_FILETRANSFER ' + ft[0], 'REQUEST_BLOCK', ft[2]]
            self.sendMsg(thisCmdSock, msg)
            i = 0
            tries = 0
            response = 0
            fh = file(destPath, "w+b")
            while i < n:
                log.debug("waiting for %d bytes"%(n-i))
                sz = n - i
                if sz > maxTransferBufferSize:
                    sz = maxTransferBufferSize 
                data = s.recv(sz)
                sz = len(data)
                log.debug("received %d bytes"%sz)
                i += sz
                if sz > 0:
                    fh.write(data)
                    log.debug("wrote %d bytes" % sz)
                else:
                    tries += 1
                    if tries >= 3:
                        rc = -1 # premature EOF
                        break
                    else:
                        reply = self.readMsg(thisCmdSock)
                        response = 1
                        log.debug("reply = %s"%reply)
            if not response:
                reply = self.readMsg(thisCmdSock)
                log.debug("reply = %s"%reply)

            fh.close()
            if rc < 0:
                os.remove(destPath)
        else:
            rc = -1
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        s = None
        thisCmdSock.shutdown(socket.SHUT_RDWR)
        thisCmdSock.close()
        thisCmdSock = None
        mlog.debug("< transferFile rc=%d" % rc)
        return rc

# =============================================================================
class MythSettings(object):
    """
    Settings reside in $HOME/.xbmc/userdata/script_data/MythBox/settings.xml
    """
    
    settingsTags = [
        'mythtv_host',
        'mythtv_port',
        'mythtv_minlivebufsize',
        'mythtv_tunewait',
        #'mythtv_version_override',  optional
        'mysql_host',
        'mysql_port',
        'mysql_database',
        'mysql_user',
        'mysql_password',
        #'mysql_encoding_override',
        'paths_recordedprefix',
        'paths_ffmpeg',
        'recorded_view_by',
        'upcoming_view_by']

    def __init__(self, platform, translator, filename='settings.xml'):
        self.platform = platform
        self.translator = translator
        self.settingsFilename = filename
        self.settingsPath = platform.getScriptDataDir() + os.sep + self.settingsFilename
        try:
            self.load()
            self.loadMergedDefaults()
        except SettingsException:
            self.dom = self.loadDefaults()
    
    def get(self, tag, dom=None):
        value = ""
        if not dom:
            dom = self.dom
        tmpNode = dom.getElementsByTagName(tag)[0]
        for n in tmpNode.childNodes:
            value += n.nodeValue
        log.debug("<= settings['%s'] = %s"%(tag,value))
        return value
    
    def getRecordingDirs(self):
        """Return list mythtv recording directories on the local filesystem as strings"""
        return self.get('paths_recordedprefix').split(os.pathsep)

    def loadDefaults(self):
        """Default configuration when it doesn't exist"""
        log.debug('loading defaults...')
        # TODO: Set paths_recordedprefix and paths_ffmpeg default based on platform 
        dom = minidom.parseString("""
<mythtv>
  <mythtv_host>localhost</mythtv_host>
  <mythtv_port>6543</mythtv_port>
  <mythtv_minlivebufsize>1024</mythtv_minlivebufsize>
  <mythtv_tunewait>3</mythtv_tunewait>
  <mythtv_version_override>False</mythtv_version_override>
  <mysql_host>localhost</mysql_host>
  <mysql_port>3306</mysql_port>
  <mysql_database>mythconverg</mysql_database>
  <mysql_user>mythtv</mysql_user>
  <mysql_password>change_me</mysql_password>
  <mysql_encoding_override>latin1</mysql_encoding_override>
  <paths_recordedprefix>/var/lib/mythtv/recordings</paths_recordedprefix>
  <paths_ffmpeg>/usr/bin/ffmpeg</paths_ffmpeg>
  <recorded_view_by>2</recorded_view_by>
  <upcoming_view_by>2</upcoming_view_by>
</mythtv>""")
        return dom

    def loadMergedDefaults(self):
        filePath = self.settingsPath
        dom = self.loadDefaults()
        if os.path.exists(filePath):
            for tag in self.settingsTags:
                try:
                    value = self.get(tag)
                except IndexError:
                    value = ""
                    pass
                if len(value) == 0:
                    self.put(tag, self.get(tag, dom), shouldCreate=1)

    def load(self):
        """
        throws SettingsException if settings file not found
        """
        filePath = self.settingsPath
        log.debug("Loading settings from %s" % filePath)
        if not os.path.exists(filePath):
            raise SettingsException('File %s does not exist.' % filePath)
        else:
            # use existing configuration
            self.dom = minidom.parse(filePath)

    def save(self):
        filePath = self.settingsPath
        settingsDir = self.platform.getScriptDataDir()
        
        if not os.path.exists(settingsDir):
            log.debug('Creating mythbox settings dir %s' % self.platform.getScriptDataDir())
            os.makedirs(settingsDir)
            
        if self.dom is not None:
            log.debug("Saving settings to %s" % filePath)
            fh = file(filePath, 'w')
            fh.write(self.dom.toxml())
            fh.close()
        else:
            log.error('Could not save settings. XML dom not set')

    def put(self, tag, value, shouldCreate=0, dom=None):
        tmpNode = None
        if not dom:
            dom = self.dom
        try:
            tmpNode = dom.getElementsByTagName( tag )[0]
        except IndexError:
            if shouldCreate != 1:
                raise
        if not tmpNode:
            tmpNode = dom.getElementsByTagName("mythtv")[0]
            n = dom.createElement(tag)
            tmpNode.appendChild(n)
            tmpNode = n
        if not tmpNode.firstChild:
            n = dom.createTextNode(value)
            tmpNode.appendChild(n)
        else:
            tmpNode.firstChild.nodeValue = value
        log.debug("=> settings['%s'] = %s"%(tag,value))

    def verify(self):
        """Throws SettingsException on invalid settings"""
        for tag in self.settingsTags:
            try:
                self.get(tag)
            except IndexError:
                raise SettingsException('%s %s' % (self.translator.get(34), tag))
        
        MythSettings.verifyMythTVHost(self.get('mythtv_host'))
        MythSettings.verifyMythTVPort(self.get('mythtv_port'))
        MythSettings.verifyMySQLHost(self.get('mysql_host'))
        MythSettings.verifyMySQLPort(self.get('mysql_port'))
        MythSettings.verifyMySQLDatabase(self.get('mysql_database'))
        MythSettings.verifyString(self.get('mysql_user'), 'Enter MySQL user. Hint: mythtv is the MythTV default')
        MythSettings.verifyLiveTVBufferSize(self.get('mythtv_minlivebufsize'))
        MythSettings.verifyRecordingDirs(self.get('paths_recordedprefix'))
        MythSettings.verifyFFMpeg(self.get('paths_ffmpeg'), self.platform)
        self.verifyMySQLConnectivity()
        self.verifyMythTVConnectivity()
        log.debug('verified settings')
    
    def verifyFFMpeg(filepath, platform):
        MythSettings.verifyString(filepath, "Enter the absolute path of your ffmpeg executable")
        if not os.path.exists(filepath):
            raise SettingsException("ffmpeg executable '%s' does not exist." % filepath)
        if not os.path.isfile(filepath):
            raise SettingsException("ffmpeg executable '%s' is not a file" % filepath)
        
        if type(platform) == util.WindowsPlatform:
            pass
        elif type(platform) == util.UnixPlatform:
            if not os.access(filepath, os.X_OK):
                raise SettingsException("ffmpeg executable '%s' is not chmod +x" % filepath)
#            if util.which(path) is None:
#                raise SettingsException('ffmpeg executable error: %s' % path)
        else:
            raise SettingsException('Unsupported platform: %s' % platform)
        
    def verifyRecordingDirs(recordingDirs):
        MythSettings.verifyString(recordingDirs, "Enter one or more '%s' separated MythTV recording directories" % os.pathsep)
        for dir in recordingDirs.split(os.pathsep):
            if not os.path.exists(dir):
                raise SettingsException("Recording directory '%s' does not exist." % dir)
            if not os.path.isdir(dir):
                raise SettingsException("Recording directory '%s' is not a directory." % dir)
    
    def verifyMythTVConnectivity(self):
        try:
            session = Connection(self, db=None, translator=self.translator, platform=self.platform)
            session.close()
        except Exception, ex:
            raise SettingsException("Connect to MythTV failed: %s" % ex)
    
    def verifyMySQLConnectivity(self):
        try:
            db = mythdb.MythDatabase(self, self.translator)
            db.close()
            del db
        except Exception, ex:
            raise SettingsException("Connect to MySQL failed: %s" % ex)
            
    def verifyMythTVHost(host):
        MythSettings.verifyString(host, 'Enter MythTV master backend hostname or IP address')
        MythSettings.verifyHostnameOrIPAddress(host, "MythTV master backend hostname '%s' cannot be resolved to an IP address."%host)
    
    def verifyMythTVPort(port):
        errMsg = 'Enter MythTV master backend port. Hint: 6543 is the MythTV default'
        MythSettings.verifyString(port, errMsg)
        MythSettings.verifyNumberBetween(port, 0, 65336, errMsg)
        
    def verifyMySQLHost(host):
        MythSettings.verifyString(host, 'Enter MySQL server hostname or IP address')
        MythSettings.verifyHostnameOrIPAddress(host, "MySQL server hostname '%s' cannot be resolved to an IP address."%host)

    def verifyMySQLPort(port):
        errMsg = 'Enter MySQL server port. Hint: 3306 is the MySQL default'
        MythSettings.verifyString(port, errMsg)
        MythSettings.verifyNumberBetween(port, 0, 65336, errMsg)

    def verifyTuneWait(numSeconds):
        errMsg = 'Enter time to wait for tuning in seconds (1-60)'
        MythSettings.verifyString(numSeconds, errMsg)
        MythSettings.verifyNumberBetween(numSeconds, 1, 60, errMsg)
        
    def verifyMySQLDatabase(dbName):
        MythSettings.verifyString(dbName, 'Enter MySQL database name. Hint: mythconverg is the MythTV default')
        
    def verifyLiveTVBufferSize(numKB):
        MythSettings.verifyString(numKB, 'LiveTV buffer size must be a value between 1 and 10000 KB')
        MythSettings.verifyNumberBetween(numKB, 1, 10000, 'LiveTV buffer size is invalid. Enter a value between 1 and 10000')
        
    def verifyHostnameOrIPAddress(host, errMsg):
        try:
            socket.gethostbyname(host)
        except Exception:
            raise SettingsException("%s %s" % (errMsg, ''))

    def verifyString(s, errMsg):
        if s is None or s.strip() == '':
            raise SettingsException(errMsg)
        
    def verifyNumberBetween(num, min, max, errMsg):
        n = None
        try:
            n = int(num)
        except Exception:
            raise SettingsException("%s %s" % (errMsg, ''))
        if not min < n < max:
            raise SettingsException(errMsg)
    #
    # Python's wonky way of doing 'static' methods.
    # Dammit, Guido, what were you smoking?
    #
    verifyFFMpeg = staticmethod(verifyFFMpeg)
    verifyMythTVHost = staticmethod(verifyMythTVHost)
    verifyMythTVPort = staticmethod(verifyMythTVPort)
    verifyLiveTVBufferSize = staticmethod(verifyLiveTVBufferSize)
    verifyMySQLHost = staticmethod(verifyMySQLHost)
    verifyMySQLPort = staticmethod(verifyMySQLPort)
    verifyMySQLDatabase = staticmethod(verifyMySQLDatabase)
    verifyRecordingDirs = staticmethod(verifyRecordingDirs)
    verifyTuneWait = staticmethod(verifyTuneWait)
    verifyString = staticmethod(verifyString)
    verifyNumberBetween = staticmethod(verifyNumberBetween)
    verifyHostnameOrIPAddress = staticmethod(verifyHostnameOrIPAddress)        