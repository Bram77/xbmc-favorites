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

import codecs
import logging
import mockito
import os
import string
import unittest
import test_util
import xbmc

from xml.dom import minidom, Node

log = logging.getLogger('mythtv.unittest')

# ============================================================================
class Translator(object):
    """
    Real XBMC uses xbmc.Language but the unit tests don't have access to this
    so this is a mock impl that will read strings.xml
    """
    def __init__(self, platform, langInfo):
        """
        platform - subclass of Platform for this box
        langinfo - instance of XBMCLangInfo
        """
        self.platform = platform
        self.langInfo = langInfo
        self.strings = {}
        self.loadStrings()

    def loadStrings(self):
        # Determine codec for GUI so that loaded messages can be encoded for
        # GUI immediately
        language = self.langInfo.getSetting('language.charsets.gui')
        log.debug("language = %s"%language )
        (e,d,r,w) = codecs.lookup( language )

        # Build language string file name. If the file does not exist, default
        # to 'english'.
        languageDir = os.getcwd() + os.sep + 'language' + os.sep

        lang = string.lower( xbmc.getLanguage() )
        langFile = languageDir + lang + os.sep + 'strings.xml'
        if not os.path.exists( langFile ) and lang != "english":
            langFile = languageDir + "english" + os.sep + "strings.xml"
        log.debug("langFile = %s"%langFile )

        # parse the string file
        dom = minidom.parse( langFile )

        # load up localized string hash from file
        for n in dom.getElementsByTagName("string"):
            strId = None
            strValue = None

            # assume one and only one id node
            tmpNode = n.getElementsByTagName("id")[0]
            for m in tmpNode.childNodes:
                if m.nodeType == Node.TEXT_NODE:
                    strId = int( m.nodeValue )

            # assume one and only one value node
            tmpNode = n.getElementsByTagName("value")[0]
            for m in tmpNode.childNodes:
                if m.nodeType == Node.TEXT_NODE:
                    strValue = m.nodeValue

            # only add it if an id has been specified
            if strId >= 0:
                (val,num) = e( strValue )
                self.strings[strId] = val
                log.debug("adding translation %s = %s" % (strId, val))

        # free up dom tree
        dom.unlink()
        del dom

    def get(self, id):
        retStr = None
        try:
            retStr = self.strings[id]
        except:
            retStr = "<Undefined>"
            pass
        log.debug("translated %d => %s" % (id, retStr))
        return retStr

# =============================================================================
class XBMCSettings(object):

    def __init__(self, filePath = None):
        log.debug("XBMCSettings constructed - filePath = %s"%str(filePath))
        self.domTree = None
        self.tagsSeen = {}
        self.loadSettings(filePath)

    def loadSettings(self, filePath):
        log.debug("loadSettings(%s)" % filePath)
        #
        # TODO: Remove OS specific stuff
        #
        if not filePath:
            if os.name != "nt":
                filePath = '.' + os.sep + 'test' + os.sep + 'settings.xml'
            else:
                filePath='E:' + os.sep + 'TDATA' + os.sep + '0face008' + os.sep + 'settings.xml'

        self.domTree = minidom.parse(filePath)

    def getSetting(self, tag):
        value = None
        if not tag in self.tagsSeen:
            path = tag.split('.')
            dom = self.domTree
            while len(path) > 0:
                search = path[0]
                path.remove(search)
                #log.debug("search = %s"%search )
                dom = dom.getElementsByTagName(search)[0]
            if dom:
                value = ""
                for n in dom.childNodes:
                    value += n.nodeValue
                #log.debug("value = %s"%value )
                self.tagsSeen[tag] = value
        else:
            value = self.tagsSeen[tag]
        log.debug("returned (tag = %s, value = %s)"%(tag, value))
        return value

# =============================================================================
class XBMCLangInfo(XBMCSettings):
    
    def __init__(self, platform):
        log.debug("XBMCLangInfo created %s"%id(self))
        self.platform = platform
        filePath = "" #platform.getXbmcRoot() FIXME
        filePath += os.sep + 'language' + os.sep + xbmc.getLanguage() + os.sep + 'langinfo.xml'
        XBMCSettings.__init__(self, filePath)

# =============================================================================    
class TranslatorTest(unittest.TestCase):

    def setUp(self):
        self.platform = mockito.Mock()
        self.langInfo = XBMCLangInfo(self.platform)
        
    def test_getString_Success(self):
        localizedStrings = Translator(self.platform, self.langInfo)
        s = localizedStrings.get(0)
        log.debug('localized string(0) = ' + s)
        self.assertEquals('Myth TV', s)

    def test_getString_ReturnsUndefined(self):
        localizedStrings = Translator(self.platform, self.langInfo)
        s = localizedStrings.get(999)
        log.debug('localized string(999) = ' + s)
        self.assertEquals('<Undefined>', s)
        
# =============================================================================
class XBMCSettingsTest(unittest.TestCase):

    def test_getSetting_Success(self):
        settings = XBMCSettings(test_util.MockPlatform().getXbmcUserSettingsRoot() + os.sep + 'userdata' + os.sep + 'guisettings.xml')
        s = settings.getSetting('settings.lookandfeel.enablemouse')
        log.debug('settings.lookandfeel.language = ' + s)
        self.assertTrue(s in ['true', 'false'])
        
# =============================================================================
class XBMCLangInfoTest(unittest.TestCase):

    def test_getSetting_Success(self):
        langInfo = XBMCLangInfo(test_util.MockPlatform())
        s = langInfo.getSetting('language.charsets.gui')
        log.debug('language.charsets.gui = ' + s)
        self.assertEquals('CP1252', s)

    def test_getSetting_NotDefinedThrowsIndexError(self):
        try:
            langInfo = XBMCLangInfo(test_util.MockPlatform())
            s = langInfo.getSetting('undefined.setting')
        except IndexError:
            pass
            