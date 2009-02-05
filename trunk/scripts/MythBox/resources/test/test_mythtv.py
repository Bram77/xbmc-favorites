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

import logging.config
import mythdb
import mythtv
import os
import tempfile
import unittest
import util

from mockito import *

log = logging.getLogger('mythtv.unittest')

# =============================================================================
class FunctionsTest(unittest.TestCase):
    
    def test_decodeLongLong(self):
        self.assertEquals(0, mythtv.decodeLongLong(0, 0))
        self.assertEquals(1, mythtv.decodeLongLong(1, 0))
        self.assertEquals(0xffffffff00000001, mythtv.decodeLongLong(1, 0xffffffff))
        self.assertEquals(0x00000000ffffffff, mythtv.decodeLongLong(0xffffffff, 0x0))
        self.assertEquals(0xffffffff00000000, mythtv.decodeLongLong(0x0, 0xffffffff))
        self.assertEquals(0xffffffffffffffff, mythtv.decodeLongLong(0xffffffff, 0xffffffff))
    
    def test_encodeLongLong(self):
        lowWord, highWord = mythtv.encodeLongLong(0L)
        self.assertEquals(0, lowWord)
        self.assertEquals(0, highWord)

        lowWord, highWord = mythtv.encodeLongLong(1L)
        self.assertEquals(1, lowWord)
        self.assertEquals(0, highWord)
        
        lowWord, highWord = mythtv.encodeLongLong(0xffffffff00000001)
        self.assertEquals(1, lowWord)
        self.assertEquals(0xffffffff, highWord)

        lowWord, highWord = mythtv.encodeLongLong(0x00000000ffffffff)
        self.assertEquals(0xffffffff, lowWord)
        self.assertEquals(0x0, highWord)

        lowWord, highWord = mythtv.encodeLongLong(0xffffffffffffffff)
        self.assertEquals(0xffffffff, lowWord)
        self.assertEquals(0xffffffff, highWord)
        
    def test_frames2seconds(self):
        s = mythtv.frames2seconds(1000, 29.97)
        log.debug('1000 frames @ 29.97fps = %s seconds' % s)
        self.assertEquals(33.37, s)
        
        s = mythtv.frames2seconds(0, 29.97)
        log.debug('0 frames @ 29.97fps = %s seconds' % s)
        self.assertEquals(0.0, s)
        
        s = mythtv.frames2seconds(99999999L, 29.97)
        log.debug('99999999L frames @ 29.97fps = %s seconds' % s)
        self.assertEquals(3336669.97, s)
    
    def test_seconds2frames(self):
        s = mythtv.seconds2frames(33.37, 29.97)
        log.debug('33.37 seconds @ 29.97fps = %s frames' % s)
        self.assertEquals(1000L, s)

        s = mythtv.seconds2frames(0, 29.97)
        log.debug('0 seconds @ 29.97fps = %s frames' % s)
        self.assertEquals(0L, s)
        
        s = mythtv.seconds2frames(3336669.97, 29.97)
        log.debug('3336669.97 seconds @ 29.97fps = %s frames' % s)
        self.assertEquals(99999999L, s)
        
    def test_formatSeconds(self):
        self.assertEquals('0s', mythtv.formatSeconds(0.00))
        self.assertEquals('1s', mythtv.formatSeconds(1.99))
        self.assertEquals('5m', mythtv.formatSeconds(60*5))
        self.assertEquals('5m 45s', mythtv.formatSeconds(60*5+45))
        self.assertEquals('3h 5m 45s', mythtv.formatSeconds(3*60*60 + 60*5 + 45))
        self.assertEquals('3h', mythtv.formatSeconds(3*60*60))
        self.assertEquals('3h 59m', mythtv.formatSeconds(3*60*60 + 60*59))
        self.assertEquals('3h 5s', mythtv.formatSeconds(3*60*60 + 5))

    def test_createChainID(self):
        id = mythtv.createChainID()
        log.debug('Chain ID = %s' % id)
        self.assertTrue(id is not None) 

# =============================================================================
class MythSettingsTest(unittest.TestCase):

    def setUp(self):
        self.translator = Mock()
        self.platform = Mock()
        
    def test_constructor_NonExistentSettingsFilesLoadsDefaults(self):
        when(self.platform).getScriptDataDir().thenReturn(tempfile.gettempdir())
        s = mythtv.MythSettings(self.platform, self.translator)
        self.assertEquals('localhost', s.get('mysql_host'))
        self.assertEquals('3306', s.get('mysql_port'))
        self.assertEquals('mythconverg', s.get('mysql_database'))
        self.assertEquals('mythtv', s.get('mysql_user'))
        self.assertEquals('change_me', s.get('mysql_password'))

    def test_constructor_LoadExistingSettingsFile(self):
        # Setup
        settingsDir = 'resources' + os.sep + 'test'
        settingsFile = 'test_mythtv_settings.xml'
        settingsPath = settingsDir + os.sep + settingsFile 
        when(self.platform).getScriptDataDir().thenReturn(settingsDir)
        self.assertTrue(os.stat(settingsPath), 'Expected settings file to exist')
        
        # Test
        s = mythtv.MythSettings(self.platform, self.translator, settingsFile)
        
        # Verify
        self.assertEquals('test_host', s.get('mysql_host'))
        self.assertEquals('9999', s.get('mysql_port'))
        self.assertEquals('test_database', s.get('mysql_database'))
        self.assertEquals('test_user', s.get('mysql_user'))
        self.assertEquals('test_password', s.get('mysql_password'))

    def test_saveSettings_LoadedDefaultsCreatesNewSettingsFile(self):
        filename = 'settings.xml'
        settingsPath = tempfile.gettempdir() + os.sep + 'mythbox_settings_dir'
        filepath = settingsPath + os.sep + filename
        when(self.platform).getScriptDataDir().thenReturn(settingsPath)
        
        try:
            self.assertFalse(os.path.exists(filepath))
            s = mythtv.MythSettings(self.platform, self.translator)
            s.save()
            self.assertTrue(os.path.exists(filepath))
        finally:
            try:
                os.remove(filepath)
                os.rmdir(settingsPath)
            except:
                pass
        
    def test_getRecordingDirs_SingleDirectory(self):
        when(self.platform).getScriptDataDir().thenReturn(tempfile.gettempdir())
        settings = mythtv.MythSettings(self.platform, self.translator)
        settings.put('paths_recordedprefix', '/mnt/mythtv')
        log.debug("Recording prefix = %s" % settings.get('paths_recordedprefix'))
        dirs = settings.getRecordingDirs()
        self.assertEquals(1, len(dirs))
        self.assertEquals('/mnt/mythtv', dirs[0])

    def test_getRecordingDirs_ManyDirectories(self):
        when(self.platform).getScriptDataDir().thenReturn(tempfile.gettempdir())
        settings = mythtv.MythSettings(self.platform, self.translator)
        settings.put('paths_recordedprefix', os.pathsep.join(['a','b', 'c']))
        log.debug("Recording prefix = %s" % settings.get('paths_recordedprefix'))
        dirs = settings.getRecordingDirs()
        self.assertEquals(3, len(dirs))
        self.assertEquals(['a','b','c'], dirs)
        
    def test_verifyMythTVHost_ValidHostname(self):
        mythtv.MythSettings.verifyMythTVHost('localhost')

    def test_verifyMythTVHost_ValidIPAddress(self):
        mythtv.MythSettings.verifyMythTVHost('127.0.0.1')

    def test_verifyMythTVHost_InvalidHostname(self):
        try:
            mythtv.MythSettings.verifyMythTVHost('bogus host name')
            self.fail('expected failure')
        except mythtv.SettingsException, se:
            log.debug('PASS: %s' % se)

    def test_verifyMythTVHost_InvalidIPAddress(self):
        try:
            mythtv.MythSettings.verifyMythTVHost('324.23.12.23')
            self.fail('expected failure')
        except mythtv.SettingsException, se:
            log.debug('PASS: %s' % se)
            
    def test_verifyMythTVHost_EmptyHostname(self):
        try:
            mythtv.MythSettings.verifyMythTVHost('')
            self.fail('expected failure')
        except mythtv.SettingsException, se:
            log.debug('PASS: %s' % se)

    def test_verifyMythTVHost_BlankHostname(self):
        try:
            mythtv.MythSettings.verifyMythTVHost('      ')
            self.fail('expected failure')
        except mythtv.SettingsException, se:
            log.debug('Error = %s' % se)
            
    def test_verifyMythTVPort_ValidPort(self):
        mythtv.MythSettings.verifyMythTVPort('1001')
            
    def test_verifyMythTVPort_PortLessThanZeroRaisesSettingsException(self):
        try:
            mythtv.MythSettings.verifyMythTVPort('-34')
            self.fail('expected failure')
        except mythtv.SettingsException, se:
            log.debug('PASS: %s' % se)
            

    def test_verifyMythTVPort_PortGreaterThanMaxPortNumberRaisesSettingsException(self):
        try:
            mythtv.MythSettings.verifyMythTVPort('101234')
            self.fail('expected failure')
        except mythtv.SettingsException, se:
            log.debug('PASS: %s' % se)

    def test_verifyMythTVPort_NonNumericPortRaisesSettingsException(self):
        try:
            mythtv.MythSettings.verifyMythTVPort('abc')
            self.fail('expected failure')
        except mythtv.SettingsException, se:
            log.debug('PASS: %s' % se)

    def test_verifyMythTVPort_EmptyPortRaisesSettingsException(self):
        try:
            mythtv.MythSettings.verifyMythTVPort('')
            self.fail('expected failure')
        except mythtv.SettingsException, se:
            log.debug('PASS: %s' % se)

    def test_verifyMySQLConnectivity_OK(self):
        when(self.platform).getScriptDataDir().thenReturn(tempfile.gettempdir())
        settings = mythtv.MythSettings(self.platform, self.translator)
        
        privateConfig = util.OnDemandConfig()
        settings.put('mysql_host', privateConfig.get('mysql_host'))
        settings.put('mysql_database', privateConfig.get('mysql_database'))
        settings.put('mysql_user', privateConfig.get('mysql_user'))
        settings.put('mysql_password', privateConfig.get('mysql_password'))
        settings.verifyMySQLConnectivity()

    def test_verifyMySQLConnectivity_InvalidUsernamePasswordThrowsSettingsException(self):
        when(self.platform).getScriptDataDir().thenReturn(tempfile.gettempdir())
        settings = mythtv.MythSettings(self.platform, self.translator)
        privateConfig = util.OnDemandConfig()
        settings.put('mysql_host', privateConfig.get('mysql_host'))
        settings.put('mysql_database', privateConfig.get('mysql_database'))
        settings.put('mysql_user', 'bogususer')
        settings.put('mysql_password', 'boguspassword')
        try:
            settings.verifyMySQLConnectivity()
            self.fail('expected failure on invalid username and password')
        except mythtv.SettingsException, se:
            log.debug('PASS: %s' % se)
        except:
            self.fail('expected SettingsException')
        
    def test_verifyMythTVConnectivity_OK(self):
        when(self.platform).getScriptDataDir().thenReturn(tempfile.gettempdir())
        settings = mythtv.MythSettings(self.platform, self.translator)
        privateConfig = util.OnDemandConfig()
        settings.put('mythtv_host', privateConfig.get('mythtv_host'))
        settings.put('mythtv_port', privateConfig.get('mythtv_port'))
        settings.verifyMythTVConnectivity()

    def test_verifyMythTVConnectivity_InvalidPortThrowsSettingsException(self):
        when(self.platform).getScriptDataDir().thenReturn(tempfile.gettempdir())
        settings = mythtv.MythSettings(self.platform, self.translator)
        privateConfig = util.OnDemandConfig()
        settings.put('mythtv_host', privateConfig.get('mythtv_host'))
        settings.put('mythtv_port', "9999")
        try:
            settings.verifyMythTVConnectivity()
            self.fail('expected failure on invalid port')
        except mythtv.SettingsException, se:
            log.debug("PASS: %s" % se)
        except Exception, ex:
            self.fail('Unexpected ex type: %s' % ex)
        
    def test_verifyRecordingDirs_EmptyStringThrowsSettingsException(self):
        try:
            mythtv.MythSettings.verifyRecordingDirs('   ')
            self.fail('expected failure')
        except mythtv.SettingsException, se:
            log.debug('PASS: %s' % se)

    def test_verifyRecordingDirs_InvalidDirThrowsSettingsException(self):
        try:
            mythtv.MythSettings.verifyRecordingDirs('someBogusDir' + os.sep + 'anotherBogusDir')
            self.fail('expected failure')
        except mythtv.SettingsException, se:
            log.debug('PASS: %s' % se)

    def test_verifyRecordingDirs_OneInvalidOutOfManyOKThrowsSettingsException(self):
        try:
            mythtv.MythSettings.verifyRecordingDirs(tempfile.gettempdir() + os.pathsep + 'someBogusDir' + os.pathsep + os.getcwd())
            self.fail('expected failure')
        except mythtv.SettingsException, se:
            log.debug('PASS: %s' % se)

    def test_verifyRecordingDirs_OKSingleDirectory(self):
        mythtv.MythSettings.verifyRecordingDirs(tempfile.gettempdir())
        
    def test_verifyRecordingDirs_OKManyDirectories(self):
        mythtv.MythSettings.verifyRecordingDirs(
            tempfile.gettempdir() + os.pathsep + 
            os.getcwd() + os.pathsep + 
            tempfile.gettempdir() + os.pathsep + 
            os.getcwd())
        
    def test_verifyFFMpeg_OK(self):
        platform = util.getPlatform()
        if (type(platform) == util.UnixPlatform):
            try:
                mythtv.MythSettings.verifyFFMpeg('/bin/true', platform)
            except mythtv.SettingsException:
                self.fail("expected /bin/true to be a valid executable")
        else:
            log.warn('Test not supported on this platform: %s' % platform)

    def test_verifyFFMpeg_ThrowsExceptionOnNonExistentExecutable(self):
        platform = util.getPlatform()
        if (type(platform) == util.UnixPlatform):
            try:
                mythtv.MythSettings.verifyFFMpeg('/bin/bogus_exe_name', platform)
                self.fail("expected failure on invalid exe name")
            except mythtv.SettingsException, ex:
                log.debug('PASS: %s' % ex)
        else:
            log.warn('Test not supported on this platform: %s' % platform)
        
# =============================================================================
class ConnectionTest(unittest.TestCase):

    def setUp(self):
        self.platform = util.getPlatform()
        self.translator = Mock()
        self.settings = mythtv.MythSettings(self.platform, self.translator)
        
        privateConfig = util.OnDemandConfig()
        self.settings.put('mysql_host', privateConfig.get('mysql_host'))
        self.settings.put('mysql_password', privateConfig.get('mysql_password'))
        self.settings.put('mysql_port', privateConfig.get('mysql_port'))
        self.settings.put('mythtv_host', privateConfig.get('mythtv_host'))
        self.settings.put('mythtv_port', privateConfig.get('mythtv_port'))
        self.settings.put('paths_recordedprefix', privateConfig.get('paths_recordedprefix'))
        
        self.db = mythdb.MythDatabase(self.settings, self.translator)
        self.conn = mythtv.Connection(self.settings, self.db, self.translator, self.platform)

    def tearDown(self):
        self.conn.close()

    def test_negotiateProtocol_ReturnsServerProtocolVersion(self):
        sock = self.conn.connect(self.settings.get('mythtv_host'))
        try:
            version = self.conn.negotiateProtocol(sock, self.settings.get('mythtv_host'), mythtv.protocol['clientVersion'])
            log.debug('Server Protcol = %s'%version)
            self.assertTrue(version > 0)
        finally:
            sock.close()

    def test_getSetting(self):
        reply = self.conn.getSetting('mythfillstatus', 'none')
        log.debug('reply = %s' % reply)
        if reply[0] == "-1":
            pass # fail
        else:
            pass # success
        # TODO : Left off here!
        
    def test_getTunerStatus_ForAllTuners(self):
        tunerStatus = self.conn.getTunerStatus()
        log.debug('Tuner status = %s' % tunerStatus)
        self.assertEquals(len(tunerStatus), len(self.db.getTuners()))

    def test_getTunerStatus_ForSingleTuner(self):
        encoders = self.db.getTuners()
        self.assertTrue(len(encoders) > 0)
        encoderStatus = self.conn.getTunerStatus(str(encoders[0].tunerID))
        log.debug('Tuner status = %s' % encoderStatus)
        self.assertFalse(encoderStatus is None)

    def test_getFreeSpace(self):
        freeSpace = self.conn.getFreeSpace()
        log.debug('Freespace = %s' % freeSpace)
        self.assertEquals(3, len(freeSpace))

    def test_getLoad(self):
        cpuLoads = self.conn.getLoad()
        log.debug('CPU Loads = %s' % cpuLoads)
        self.assertEquals(3, len(cpuLoads))

    def test_getUptime(self):
        uptime = self.conn.getUptime()
        log.debug('Uptime = %s' % uptime)
        self.assertFalse(uptime is None)
        
    def test_getMythFillStatus(self):
        fillStatus = self.conn.getMythFillStatus()
        log.debug('mythfillstatus = %s' % fillStatus)
        self.assertFalse(fillStatus is None)

    def test_getRecordings_AllRecordingGroupsAndTitles(self):
        recordings = self.conn.getRecordings()
        log.debug('Num Recordings = %s' % len(recordings))
        for i, r in enumerate(recordings):
            log.debug('%d - %s' %(i+1, r))
        self.assertTrue(len(recordings) > 0)

    def test_getPendingRecordings(self):
        pending = self.conn.getPendingRecordings()
        log.debug('Pending recordings = %s' % pending)
        self.assertTrue(len(pending) > 0)

    def test_getTunerShowing_NoCardsAreWatchingOrRecordingThePassedInShow(self):
        tunerID = self.conn.getTunerShowing('bogusshow')
        self.assertEquals(-1, tunerID, 'Expected no encoder to be watching or recording a bogus tv show')

    def test_getTunerShowing_ReturnCardThatShowIsBeingWatchedOn(self):
        log.warn("TODO: Write unit test - mockito")

    def test_getTunerShowing_ReturnCardThatShowIsBeingWatchedAndRecordedOn(self):
        log.warn("TODO: Write unit test - mockito")

    def test_getFreeTuner(self):
        recorderID, hostname, port = self.conn.getFreeTuner()
        if recorderID == -1:
            log.debug('No free recorders available')
            self.assertEquals('', hostname)
            self.assertEquals(-1, port)
        else:
            log.debug('Free recorder = id: %d hostname: %s  port: %d'%(recorderID, hostname, port))
            self.assertTrue(recorderID >= 0)
            self.assertTrue(len(hostname) > 0)
            self.assertTrue(port > 0)
        
    def test_getNextFreeTuner(self):
        recorderID, hostname, port = self.conn.getNextFreeTuner(-1)
        if recorderID is None:
            pass
        else:
            log.debug('Next free recorder = id:%d hostname:%s port:%d'%(recorderID, hostname, port))
        #TODO: valid assertions when recorder free and not available
        
    def test_isAccept_MatchReturnsTrue(self):
        msg = ['ACCEPT', '40']
        self.assertTrue(self.conn.isAccept(msg, 40))
        
    def test_isAccept_ProtocolVersionDoesntMatchReturnsFalse(self):
        msg = ['ACCEPT', '41']
        self.assertFalse(self.conn.isAccept(msg, 40))

    def test_isAccept_ResponseDoesntMatchReturnsFalse(self):
        msg = ['FAIL', '41']
        self.assertFalse(self.conn.isAccept(msg, 41))
        
    def test_isOk_OKMessageReturnsTrue(self):
        self.assertTrue(self.conn.isOk(['OK']))

    def test_isOk_OKMessageWithAdditionPayloadReturnsTrue(self):
        self.assertTrue(self.conn.isOk(['OK','foo', 'bar', 'baz']))

    def test_isOk_NoneMessageReturnsFalse(self):
        self.assertFalse(self.conn.isOk(None))
        
    def test_isOk_EmptyMessageReturnsFalse(self):
        self.assertFalse(self.conn.isOk([]))

    def test_isOk_BadMessageReturnsFalse(self):
        self.assertFalse(self.conn.isOk(['Bad']))

    def test_isTunerRecording_InvalidRecorderIDRaisesProtocolException(self):
        self.assertRaises(mythtv.ProtocolException, self.conn.isTunerRecording, -1)
        
    def test_isTunerRecording_False(self):
        freeTunerID, hostname, port = self.conn.getFreeTuner()
        if freeTunerID != -1: 
            result = self.conn.isTunerRecording(freeTunerID)
            log.debug('isTunerRecording(%d) = %s' % (freeTunerID, result))
        else:
            log.warn('no free recorders available to test isTunerRecording()')
            
    def test_isTunerRecording_True(self):
        log.warn("TODO: Write unit test")
    
    def test_getBookmark_Success(self):
        # TODO: only check bookmarked recordings
        programs = self.conn.getRecordings()
        self.assertTrue(len(programs) > 0, 'Cannot run test because no programs returned')
        log.debug('Getting bookmark for %s' % programs[0])
        bookmark = self.conn.getBookmark(programs[0])
        log.debug('bookmark = %s seconds' % bookmark)
        self.assertTrue(bookmark >= 0)
    
    def test_setBookmark_Success(self):
        programs = self.conn.getRecordings()
        self.assertTrue(len(programs) > 0, 'Cannot run test because no programs returned')
        log.debug('Setting bookmark for %s' % programs[0])
        self.conn.setBookmark(programs[0], 1000)
        self.assertEquals(1000, self.conn.getBookmark(programs[0]))

    def test_setBookmark_ChannelIDInvalid(self):
        programs = self.conn.getRecordings()
        self.assertTrue(len(programs) > 0, 'Cannot run test because no programs returned')
        p = programs[0]
        p.setChannelID(999)
        self.assertEquals(999, p.chanid())
        self.assertRaises(mythtv.ServerException, self.conn.setBookmark, p, 500)
        
    def test_getCommercialBreaks(self):
        recordings = self.conn.getRecordings()
        foundRecordingWithCommBreaks = False
        for r in recordings:
            if r.hasCommercials():
                foundRecordingWithCommBreaks = True
                log.debug('Recording %s has comm breaks' % r)
                breaks = self.conn.getCommercialBreaks(r)
                for j, b in enumerate(breaks):
                    log.debug('    %d - comm break = %s' % (j+1, b))
                return
        if not foundRecordingWithCommBreaks:
            log.warn('Could not find any comm flagged recordings to run unit test against')
    
    def test_getNumFreeTuners(self):
        cnt = self.conn.getNumFreeTuners()
        log.debug('Num free tuners = %d' % cnt)
        self.assertTrue(cnt >= 0)
        
    def test_getTuners(self):
        tuners = self.conn.getTuners()
        for t in tuners:
            self.assertTrue(t.conn != None)
       
    def test_generateThumbnail_ReturnsTrue(self):
        programs = self.conn.getRecordings()
        self.assertTrue(len(programs) > 0, 'Cannot run test; No programs in db to play with')
        log.debug('Generating thumbnail for program: %s' % programs[0])
        result = self.conn.generateThumbnail(programs[0], self.settings.get('mythtv_host'))
        self.assertTrue(result)
         
    def test_getThumbnailCreationTime_ThumbnailExists(self):
        programs = self.conn.getRecordings()
        self.assertTrue(len(programs) > 0, 'Cannot run test; No programs in db to play with')
        log.debug('Getting thumbnail creation time for: %s' % programs[0])
        dt = self.conn.getThumbnailCreationTime(programs[0], self.settings.get('mythtv_host'))
        log.debug('datetime = %s' % dt)
        
    def test_getThumbNatilCreationTime_ThumbnailDoesNotExist(self):
        # TODO
        pass
        
    """
    LEGACY TESTS
    ============
    def testSaveSchedule( self ):
        db = Database(...) 
        s = domain.ScheduleFromQuery( dict(
            { 'recordid' : 9999,        'type' : 3,
              'chanid' : 1002,          'starttime' : '03:00:00',
              'startdate' : '20050712', 'endtime' : '04:00:00',
              'enddate' : '20050712',   'title' : 'Tom\'s test',
              'subtitle' : 'Wass\'up',  'description' : 'This is a test.',
              'category' : 'Sitcom',    'profile' : 'Default',
              'recpriority' : 5,        'autoexpire' : 1,
              'maxepisodes' : 3,        'maxnewest' : 0,
              'startoffset' : 0,        'endoffset' : 0,
              'recgroup' : 'Default',   'dupmethod' : 6,
              'dupin' : 15,             'station' : 'CFRN',
              'seriesid' : 'SH999999',  'programid' : 'EP9999999999',
              'search' : 0,             'autotranscode' : 0,
              'autocommflag' : 1,       'autouserjob1' : 0,
              'autouserjob2' : 0,       'autouserjob3' : 0,
              'autouserjob4' : 0,       'findday' : '0',
              'findtime' : '0',         'findid' : 0,
              'inactive' : 0,           'parentid' : 0
            } ) )
        db.saveSchedule( s )
        debug( s )
    """
    
# =============================================================================    
if __name__ == "__main__":
    logging.config.fileConfig('mythbox_log.ini')
    unittest.main()
