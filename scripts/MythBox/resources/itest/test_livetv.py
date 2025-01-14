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

import livetv
import logging.config
import mockito
import mythdb
import mythtv
import time
import unittest
import util

log = logging.getLogger('mythtv.unittest')

# =============================================================================    
class LiveTVBrainTest(unittest.TestCase):

    def setUp(self):
        translator = mockito.Mock()
        platform = mockito.Mock()
        settings = mythtv.MythSettings(platform, translator)
        privateConfig = util.OnDemandConfig()
        settings.put('mysql_host', privateConfig.get('mysql_host'))
        settings.put('mysql_password', privateConfig.get('mysql_password'))
        settings.put('mythtv_host', privateConfig.get('mythtv_host'))
        self.db = mythdb.MythDatabase(settings, translator)
        self.session = mythtv.Connection(settings, self.db, translator, platform)
        self.brain = livetv.LiveTVBrain(self.session, self.db)
    
    def tearDown(self):
        self.session.close()
        
    def test_watchLiveTV(self):
        
#        tuners = self.session.getTuners()
#        for t in tuners:
#            if t.tunerID == 5 and t.isRecording():
#                t.stopLiveTV()
        
        channel = self.session.getChannels()[1]
        log.debug('Attempting to watch %s' % channel)
        tuner = self.brain.watchLiveTV(channel)
        log.debug("Assuming we're watching some tv...")
        
        for x in range(20):
            time.sleep(1)
            log.debug(self.brain.getLiveTVStatus())
            
        log.debug('Stopping live tv...')
        self.brain.onPlayBackStopped()
        log.debug('all done')
        
    def xxxtest_stopAllTuners(self):
        tuners = self.session.getTuners()
        for t in tuners:
            if t.tunerID == 5:
                t.stopLiveTV()

# =============================================================================
if __name__ == "__main__":
    logging.config.fileConfig('mythbox_log.ini')
    unittest.main()