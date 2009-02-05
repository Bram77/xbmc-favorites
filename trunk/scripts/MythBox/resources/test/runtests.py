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
import test_domain
import test_mythdb
import test_mythtv
import test_player
import unittest
import test_util

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.findTestCases(test_util))
    suite.addTest(unittest.findTestCases(test_mythdb))
    suite.addTest(unittest.findTestCases(test_mythtv))
    suite.addTest(unittest.findTestCases(test_domain))
    suite.addTest(unittest.findTestCases(test_player))
    return suite

if __name__ == "__main__":
    logging.config.fileConfig('mythbox_log.ini')
    testSuite = suite()
    unittest.TextTestRunner(verbosity = 3).run(testSuite)

