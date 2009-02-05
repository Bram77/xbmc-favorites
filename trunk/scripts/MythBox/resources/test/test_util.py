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
import os
import time
import unittest
import util

from util import BoundedEvictingQueue, getPlatform
from util import timed

log = logging.getLogger('mythtv.unittest')

# =============================================================================
class ModuleTest(unittest.TestCase):
    
    def test_getPlatform(self):
        platform = util.getPlatform()
        self.assertTrue(platform is not None)
    
    def test_which_ExecutableFound(self):
        platform = util.getPlatform()
        if type(platform) == util.WindowsPlatform:
            exe = "cmd.exe"
        elif type(platform) == util.UnixPlatform:
            exe = "true"
        else:
            log.warn("Skipping test. Platform not supported")
            return
        exepath = util.which(exe)
        log.debug('which found %s' % exepath)
        self.assertFalse(exepath is None)    

    def test_which_ExecutableNotFound(self):
        platform = util.getPlatform()
        if type(platform) == util.WindowsPlatform:
            exe = "bogus_executable_name.exe"
        elif type(platform) == util.UnixPlatform:
            exe = "bogus_executable_name"
        else:
            log.warn("Skipping test. Platform not supported")
            return
        exepath = util.which(exe)
        self.assertTrue(exepath is None)    
            
# =============================================================================
class TimedDecoratorTest(unittest.TestCase):
    
    def test_DecoratorPrintsOutWarningWhenExecutionTimeExceedsOneSecond(self):
        self.foo()
        # observe results
        
    @timed
    def foo(self):
        log.debug('waiting 1.2 seconds...')
        time.sleep(1.2)

# =============================================================================
class PlatformTest(unittest.TestCase):

    def test_getScriptDirNotNull(self):
        platform = util.UnixPlatform()
        self.assertTrue(platform.getScriptDir() is not None)
        
    def test_getScriptDataDirNotNull(self):
        platform = util.UnixPlatform()
        self.assertTrue(platform.getScriptDataDir() is not None)

# =============================================================================
class UnixPlatformTest(unittest.TestCase):
    
    def test_getFFMpegExecutableName(self):
        platform = util.UnixPlatform()
        self.assertEquals('ffmpeg', platform.getFFMpegExecutableName())
        
    def test__str__NotNull(self):
        platform = util.UnixPlatform()
        s = "%s" % platform
        log.debug('\n%s' % platform)
        self.assertTrue(s is not None)

# =============================================================================
class WindowsPlatformTest(unittest.TestCase):
    
    def test_getFFMpegExecutableName(self):
        platform = util.WindowsPlatform()
        self.assertEquals('ffmpeg.exe', platform.getFFMpegExecutableName())
        
# =============================================================================    
class NativeTranslatorTest(unittest.TestCase):

    def test_getString_Success(self):
        translator = util.NativeTranslator(os.getcwd())
        s = translator.get(0)
        log.debug('localized = %s' % s)
        self.assertEquals('TODO', s)
             
# =============================================================================
class BoundedEvictingQueueTest(unittest.TestCase):
    
    def test_put_FillingToCapacityPlusOneEvictsFirstItem(self):
        q = BoundedEvictingQueue(3)
        q.put(1)
        q.put(2)
        q.put(3)
        self.assertTrue(q.full())
        q.put(4)
        self.assertTrue(q.full())
        self.assertEquals(3, q.qsize())
        self.assertEquals(2, q.get())
        self.assertFalse(q.full())
        self.assertEquals(3, q.get())
        self.assertEquals(4, q.get())
        self.assertTrue(q.empty())
        
# =============================================================================
#
# Requires interactivity 
#        
#class OnDemandConfigTest(unittest.TestCase):
#            
#    def test_get_NonExistentKey(self):
#        config = util.OnDemandConfig('crap.ini')
#        value = config.get('blah')
#        log.debug('Value = %s' % value)
        
# =============================================================================
class MockPlatform(util.Platform):
    """
    Mock platform impl that directs unit tests to load resources from the  
    ./resources/test/mock* directories 
    """
    def getXbmcRoot(self):
        return os.getcwd() + os.sep + 'resources' + os.sep + 'test' + os.sep + 'test_util' + os.sep + 'xbmc'

    def getXbmcUserSettingsRoot(self):
        return os.getcwd() + os.sep + 'resources' + os.sep + 'test' + os.sep + 'test_util' + os.sep + 'dotxbmc'
    
# =============================================================================
if __name__ == "__main__":
    logging.config.fileConfig('mythbox_log.ini')
    unittest.main()
