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
import logging.config
import mockito
import mythdb
import mythtv
import unittest
import util

log = logging.getLogger('mythtv.unittest')

# =============================================================================
class MythDatabaseTest(unittest.TestCase):

    def setUp(self):
        self.translator = mockito.Mock()
        self.platform = util.Platform()
        self.settings = mythtv.MythSettings(self.platform, self.translator)
        privateConfig = util.OnDemandConfig()
        self.settings.put('mysql_host', privateConfig.get('mysql_host'))
        self.settings.put('mysql_password', privateConfig.get('mysql_password'))
        self.settings.put('mythtv_host', privateConfig.get('mythtv_host'))
        self.db = mythdb.MythDatabase(self.settings, self.translator)

    def tearDown(self):
        self.db.close()
        
    def test_constructor(self):
        self.assertTrue(self.db)

    def test_getChannels(self):
        channels = self.db.getChannels()
        for i, channel in enumerate(channels):
            log.debug("%d - %s"%(i+1, channel))
        self.assertTrue(len(channels) > 0)
        
    def test_getRecordingGroups(self):
        groups = self.db.getRecordingGroups()
        self.assertTrue(len(groups) > 0)
        groupsMap = {}
        for i, group in enumerate(groups):
            groupName = group[0]
            groupSize = group[1]
            groupsMap[groupName] = groupSize  
            log.debug('%d - Recording Group = %s, Size = %s'%(i+1, groupName, groupSize))
        self.assertTrue('All Groups' in groupsMap)

    def test_getRecordingTitles_InAllGroups(self):
        titles = self.db.getRecordingTitles('All Groups')
        self.assertTrue(len(titles) > 0)
        total = titles[0][1]
        for i, title in enumerate(titles):
            titleName = title[0]
            titleCount = title[1]
            log.debug('%d - %s x %s' %(i+1, titleCount, titleName))

    def test_getRecordingTitles_ForNonExistantRecordingGroupReturnsAllShowsWithCountOfZero(self):
        titles = self.db.getRecordingTitles('bogus group')
        self.assertEquals(1, len(titles))
        self.assertEquals('All Shows', titles[0][0])
        self.assertEquals(0, titles[0][1])

    def test_getRecordingTitles_ForDeletedRecordingsGroup(self):
        deleted = self.db.getRecordingTitles('Deleted')
        for i, title in enumerate(deleted):
            titleName = title[0]
            titleCount = title[1]
            log.debug('%d - Deleted recording %s recorded %s times' % (i+1, titleName, titleCount))
        self.assertTrue(len(deleted) > 0)

    def test_getTuners(self):
        tuners = self.db.getTuners()
        self.assertTrue(len(tuners) > 0, 'No tuners found')
        for i, tuner in enumerate(tuners):
            log.debug('%d - %s' %(i+1, tuner))
            self.assertTrue(not tuner.tunerID is None)
            self.assertTrue(not tuner.hostname is None)
            self.assertTrue(not tuner.signalTimeout is None)
            self.assertTrue(not tuner.channelTimeout is None)

    def test_getProgramListings(self):
        now = datetime.datetime.now()
        programs = self.db.getProgramListings(now, now)
        log.debug('getProgramListings() =>')
        for i, p in enumerate(programs):
            log.debug('  %d - %s' % (i+1, p))
        self.assertTrue(programs)
        
    def test_getMythSetting_KeyWithNoHostname(self):
        s = self.db.getMythSetting('mythfilldatabaseLastRunStatus')
        log.debug('mythfillstatus = %s' % s)
        self.assertFalse(s is None)

    def test_getMythSetting_KeyNotFound(self):
        s = self.db.getMythSetting('blahblah')
        self.assertTrue(s is None)

    def test_getMythSetting_KeyWithHostname(self):
        # TODO: Uncomment with setMythSetting() implemented
        pass
    
    def test_getRecordingSchedules_All(self):
        schedules = self.db.getRecordingSchedules()
        for i, s in enumerate(schedules):
            log.debug('%d - %s' % (i+1, s))
        self.assertTrue(schedules)
        
    def test_getRecordingSchedules_ForChannel(self):
        # TODO
        pass
    
    def test_getRecordingSchedules_ForRecording(self):
        # TODO
        pass

# =============================================================================
if __name__ == "__main__":
    logging.config.fileConfig('mythbox_log.ini')
    unittest.main()        