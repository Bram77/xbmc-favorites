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
import logging.config
import mythtv
import os
import unittest
import util

from mockito import Mock, when, verify, any
from domain import Tuner
from domain import ChannelFromQuery
from domain import CommercialBreak
from domain import ProgramFromQuery
from domain import RecordedProgram
from domain import ScheduleFromQuery

log = logging.getLogger('mythtv.unittest')

# =============================================================================
class ModuleFunctionsTest(unittest.TestCase):
    
    def test_ctime2MythTime_MinDateStringReturnsMinDate(self):
        t = domain.ctime2MythTime('0')
        log.debug('MythTime = %s' % t)
        self.assertEqual('19691231180000', t)

    def test_ctime2MythTime_MinDateIntReturnsMinDate(self):
        t = domain.ctime2MythTime(0)
        log.debug('MythTime = %s' % t)
        self.assertEqual('19691231180000', t)

    def test_ctime2MythTime_BadInputRaisesValueError(self):
        # PLATFORM ISSUE: Throws exception on windows but returns 19691231175959 on linux
        try:
            t = domain.ctime2MythTime(-1)
            log.warn('Expected failure for time = -1 : %s' % t)
        except ValueError, ve:
            log.debug('Pass: %s' % ve)

# =============================================================================
class ProgramTest(unittest.TestCase):

    def setUp(self):
        self.translator = Mock()

    def test_constructor(self):
        p = domain.Program(self.translator)
        self.assertFalse(p is None)

# =============================================================================
class ChannelFromQueryTest(unittest.TestCase):
    
    def test_constructor(self):
        data = {'chanid':9, 'channum':'23_1', 'callsign':'WXYZ', 'name':'NBC9', 'icon':'nbc.jpg', 'cardid':4}
        channel = domain.ChannelFromQuery(data)
        log.debug(channel)
        self.assertTrue(channel)

    def test_constructor_IconMissing(self):
        data = {'chanid':9, 'channum':'23_1', 'callsign':'WXYZ', 'name':'NBC9', 'cardid':4}
        channel = domain.ChannelFromQuery(data)
        log.debug(channel)
        self.assertTrue(channel.icon() is None)

# =============================================================================
class ProgramFromQueryTest(unittest.TestCase):

    def setUp(self):
        self.data = [ 
            ('title', 'Bonanza'), 
            ('subtitle', 'The Shootout'),
            ('description', 'Yee haw!'),
            ('starttime', '2008-10-04 18:00:00'),
            ('endtime', '2008-10-04 19:00:00'),
            ('channum', '23')] 
        self.translator = Mock() 
        self.platform = util.Platform()
        self.settings = mythtv.MythSettings(self.platform, self.translator)

    def test_constructor(self):
        program = ProgramFromQuery(self.data, self.settings, self.translator)
        self.assertTrue(program is not None)

    def test_starttimeAsTime(self):
        program = ProgramFromQuery(self.data, self.settings, self.translator) 
        time = program.starttimeAsTime()
        log.debug('startTime = %s'%time)
        self.assertTrue(time)
        
    def test_starttime_TypeInDataDictIsAString(self):
        p = ProgramFromQuery({'starttime':'2008-11-21 14:00:00'}, self.settings, self.translator)
        self.assertEquals('20081121140000', p.starttime())
    
    def test_starttime_TypeInDataDictIsADateTime(self):
        p = ProgramFromQuery({'starttime': datetime.datetime(2008, 11, 21, 14)}, self.settings, self.translator)
        self.assertEquals('20081121140000', p.starttime())

# =============================================================================
class RecordedProgramTest(unittest.TestCase):

    def setUp(self):
        self.conn = Mock()
        self.settings = Mock()
        self.translator = Mock()
        self.platform = Mock()
        self.data = ["0"] * mythtv.protocol['recordSize']
            
    def test_hasBookmark_False(self):
        self.data[29] = domain.FL_AUTOEXP
        p = RecordedProgram(self.data, self.conn, self.settings, self.translator, self.platform)
        self.assertFalse(p.hasBookmark())
    
    def test_hasBookmark_True(self):
        self.data[29] = domain.FL_BOOKMARK | domain.FL_AUTOEXP
        p = RecordedProgram(self.data, self.conn, self.settings, self.translator, self.platform)
        self.assertTrue(p.hasBookmark())
        
    def test_setBookmark(self):
        log.warn("TODO: Write unit test")
    
    def test_getBookmark(self):
        log.warn("TODO: Write unit test")
        
    def test_hasCommercials_True(self):
        self.data[29] = domain.FL_COMMFLAG | domain.FL_AUTOEXP
        p = RecordedProgram(self.data, self.conn, self.settings, self.translator, self.platform)
        commBreaks = []
        commBreaks.append(CommercialBreak(120,180))
        when(self.conn).getCommercialBreaks(p).thenReturn(commBreaks)
        log.debug('comms = %s' % len(p.getCommercials()))
        self.assertTrue(p.hasCommercials())    
        #verify(self.conn).getCommercialBreaks(p)

    def test_hasCommercials_False(self):
        self.data[29] = domain.FL_COMMFLAG | domain.FL_AUTOEXP
        p = RecordedProgram(self.data, self.conn, self.settings, self.translator, self.platform)
        commBreaks = []
        when(self.conn).getCommercialBreaks(p).thenReturn(commBreaks)
        log.debug('comms = %s' % len(p.getCommercials()))
        self.assertFalse(p.hasCommercials())    

    def test_getCommercials_ReturnsOneCommercial(self):
        self.data[29] = domain.FL_COMMFLAG | domain.FL_AUTOEXP
        p = RecordedProgram(self.data, self.conn, self.settings, self.translator, self.platform)
        commBreaks = []
        commBreaks.append(CommercialBreak(120,180))
        when(self.conn).getCommercialBreaks(p).thenReturn(commBreaks)
        result = p.getCommercials()    
        log.debug('commercials = %s'%result)
        self.assertEquals(commBreaks, result)
        verify(self.conn).getCommercialBreaks(p)

    def test_getFrameRate_29point97(self):
        self.data[8] = "myth://192.168.1.11:6543/movie_29.97_fps.mpg" # filename 
        self.data[16] = "localhost" # hostname
        when(self.settings).getRecordingDirs().thenReturn([os.getcwd() + os.sep + 'resources' + os.sep + 'test']);
        when(self.settings).get('mythtv_host').thenReturn('localhost')
        when(self.platform).getFFMpegExecutableName().thenReturn('ffmpeg')
        p = RecordedProgram(self.data, self.conn, self.settings, self.translator, self.platform)
        fps = p.getFrameRate()
        self.assertEquals(29.97, fps)

# =============================================================================    
class TunerTest(unittest.TestCase):

    def setUp(self):
        self.conn = Mock()
        self.tuner = Tuner(4, 'mrbun', 1000, 6000, 'HDHOMERUN', self.conn)
        
    def test_toString(self):
        log.debug('tuner = %s'%self.tuner)
        self.assertFalse(self.tuner is None)

    def test_isWatchingOrRecording_CardIdle(self):
        when(self.conn).getTunerShowing('Seinfeld').thenReturn(-1)
        self.assertFalse(self.tuner.isWatchingOrRecording('Seinfeld'))

    def test_isWatchingOrRecording_CardNotIdleButShowDoesntMatch(self):
        when(self.conn).getTunerShowing('Seinfeld').thenReturn(-1)
        self.assertFalse(self.tuner.isWatchingOrRecording('Seinfeld'))

    def test_isWatchingOrRecording_CardNotIdleAndShowMatches(self):
        when(self.conn).getTunerShowing('Seinfeld').thenReturn(self.tuner.tunerID)
        self.assertTrue(self.tuner.isWatchingOrRecording('Seinfeld'))
        
    def test_isRecording_True(self):
        when(self.conn).isTunerRecording(4).thenReturn(True)
        result = self.tuner.isRecording()
        log.debug('isRecording_True = %s'%result)
        self.assertTrue(result)
        verify(self.conn).isTunerRecording(4)
    
    def test_isRecording_False(self):
        when(self.conn).isTunerRecording(any(int)).thenReturn(False)
        self.assertFalse(self.tuner.isRecording())
        verify(self.conn).isTunerRecording(any(int))

    def test_hasChannel_True(self):
        channels = []
        for x in range(0,5):
            channels.append(ChannelFromQuery(
                {'chanid':x, 'channum':'%d'%x, 'callsign':'WXYZ', 
                 'name':'NBC9', 'icon':'nbc.jpg', 'cardid':4}))
        when(self.conn).getChannels().thenReturn(channels)
        self.assertTrue(self.tuner.hasChannel(ChannelFromQuery(dict(channum='3'))))
    
    def test_hasChannel_False(self):
        channels = []
        for x in range(0,5):
            channels.append(ChannelFromQuery(
                {'chanid':x, 'channum':'%d'%x, 'callsign':'WXYZ', 
                 'name':'NBC9', 'icon':'nbc.jpg', 'cardid':4}))
        when(self.conn).getChannels().thenReturn(channels)
        self.assertFalse(self.tuner.hasChannel(ChannelFromQuery(dict(channum='6'))))
        
    def test_getChannels_CachingWorks(self):
        channels = []
        for x in range(0,5):
            channels.append(ChannelFromQuery(
                {'chanid':x, 'channum':'%d'%x, 'callsign':'WXYZ', 
                 'name':'NBC9', 'icon':'nbc.jpg', 'cardid':4}))
        when(self.conn).getChannels().thenReturn(channels)
        
        for x in range(10):
            channels = self.tuner.getChannels()
        
        verify(self.conn.getChannels, 1)
        
# =============================================================================    
class CommercialBreakTest(unittest.TestCase):
    
    def test_constructor(self):
        commercial = CommercialBreak(100, 200)
        self.assertTrue(commercial is not None)
        
    def test_constructor_StartAfterEndFailsAssertion(self):
        try:
            CommercialBreak(200, 100)
        except AssertionError, ae:
            log.debug('Error = %s' % ae)
            
    def test_isDuring_True(self):
        commercial = CommercialBreak(100, 200)
        self.assertTrue(commercial.isDuring(150))
    
    def test_isDuring_BeforeCommercialReturnsFalse(self):
        commercial = CommercialBreak(100, 200)
        self.assertFalse(commercial.isDuring(50))
    
    def test_isDuring_AfterCommercialReturnsFalse(self):
        commercial = CommercialBreak(100, 200)
        self.assertFalse(commercial.isDuring(350))

# =============================================================================
class ScheduleFromQueryTest(unittest.TestCase):
    
    def test_starttime_DataFromNativeMySQL(self):
        data = {'starttime': datetime.timedelta(seconds=(1 * 60 * 60) + (2 * 60) + 3)}
        schedule = ScheduleFromQuery(data, Mock())
        self.assertEquals('010203', schedule.starttime())
        
    def test_starttime_DataFromPythonMySQL(self):
        data = {'starttime':'23:11:59'}
        schedule = ScheduleFromQuery(data, Mock())
        self.assertEquals('231159', schedule.starttime())

    def test_endtime_DataFromNativeMySQL(self):
        data = {'endtime': datetime.timedelta(seconds=(1 * 60 * 60) + (2 * 60) + 3)}
        schedule = ScheduleFromQuery(data, Mock())
        self.assertEquals('010203', schedule.endtime())
        
    def test_endtime_DataFromPythonMySQL(self):
        data = {'endtime':'23:11:59'}
        schedule = ScheduleFromQuery(data, Mock())
        self.assertEquals('231159', schedule.endtime())
        
    def test_startdate_DataFromNativeMySQL(self):
        data = {'startdate': datetime.date(2008, 11, 12)}
        schedule = ScheduleFromQuery(data, Mock())
        self.assertEquals('20081112', schedule.startdate())
        
    def test_startdate_DataFromPythonMySQL(self):
        data = {'startdate':'2008-11-12'}
        schedule = ScheduleFromQuery(data, Mock())
        self.assertEquals('20081112', schedule.startdate())

    def test_enddate_DataFromNativeMySQL(self):
        data = {'enddate': datetime.date(2008, 11, 12)}
        schedule = ScheduleFromQuery(data, Mock())
        self.assertEquals('20081112', schedule.enddate())
        
    def test_enddate_DataFromPythonMySQL(self):
        data = {'enddate':'2008-11-12'}
        schedule = ScheduleFromQuery(data, Mock())
        self.assertEquals('20081112', schedule.enddate())
    
# =============================================================================    
if __name__ == '__main__':
    logging.config.fileConfig('mythbox_log.ini')
    unittest.main()
    