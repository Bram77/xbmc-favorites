#
#  MythBox for XBMC - http://mythbox.googlecode.com
#  Copyright (C) 2009 analogue@yahoo.com
#  Copyright (C) 2005 Tom Warkentin <tom@ixionstudios.com>
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

from mythtv import MythSettings, SettingsException
import logging
import mythtv
import time
import ui
import xbmc
import xbmcgui

from msg import *

log = logging.getLogger('mythtv.ui')
mlog = logging.getLogger('mythtv.method')

def showWindow(loadingWin, settings, translator, platform):
    win = Window(settings=settings, translator=translator, platform=platform)
    win.loadskin("settings.xml")
    #win.loadSettings()
    win.refreshControls()
    loadingWin.close()
    win.doModal()
    del win

# =============================================================================
class Window(ui.BaseWindow):

    def __init__(self, *args, **kwargs):
        """
        @keyword settings: MythSettings
        @keyword translator: Translator
        @keyword platform: Platform
        """
        ui.BaseWindow.__init__(self, *args, **kwargs)
        self.platform = kwargs['platform']
        self.dom = None
        self.isDirty = False

#    def loadSettings(self):
#        log.debug("loadSettings()")
#        try:
#            #self.settings.load()
#            #self.settings.verify()
#        except mythtv.SettingsException, ex:
#            log.exception(str(ex))
#            ui.Dialog().ok(self.translator.get(S_ERROR), '%s  %s' % (ex, self.translator.get(S_SETTING_DATED)))
#            self.settings.loadMergedDefaults()
#            self.isDirty = True
#            pass

    def changeSettings(self, id):
        log.debug("changeSettings(%s)"%id)
        kbd = xbmc.Keyboard(self.settings.get(id), id)
        kbd.doModal()
        if kbd.isConfirmed():
            value = kbd.getText()
            log.debug("value = %s" % value)
            
            try:
                if id == 'mythtv_host':
                    MythSettings.verifyMythTVHost(value)
                elif id == 'mythtv_port':
                    MythSettings.verifyMythTVPort(value)
                elif id == 'mysql_host':
                    MythSettings.verifyMySQLHost(value)
                elif id == 'mysql_port':
                    MythSettings.verifyMySQLPort(value)
                elif id == 'mythtv_minlivebufsize':
                    MythSettings.verifyLiveTVBufferSize(value)
                elif id == 'mythtv_tunewait':
                    MythSettings.verifyTuneWait(value)
                elif id == 'mysql_password':
                    pass  # password can be empty
                elif id == 'mysql_database':
                    MythSettings.verifyMySQLDatabase(value)
                elif id == 'mysql_user':
                    MythSettings.verifyString(value, 'Enter mysql user name to access MythTV database')
                elif id == 'paths_recordedprefix':
                    MythSettings.verifyRecordingDirs(value)
                elif id == 'paths_ffmpeg':
                    MythSettings.verifyFFMpeg(value, self.platform)
                else:
                    xbmcgui.Dialog().ok(self.translator.get(S_ERROR), 'Unknown handler for id %s' % id)
                    return
    
                # No exceptions thrown..save value to settings
                self.settings.put(id, value)
                self.controls[id].control.setLabel(value)
            except mythtv.SettingsException, se:
                xbmcgui.Dialog().ok(self.translator.get(S_ERROR), str(se))
        else:
            log.debug('keyboard input unconfirmed')
                
#            if value:
#                log.debug("stored value = %s" % value)
#                self.settings.put(id, value)
#                self.controls[id].control.setLabel(value)
#
#                # if configuring mythtv host and mysql host is not set, use
#                # mythtv host as default
#                if id == "mythtv_host":
#                    mysqlHost = ""
#                    try:
#                        mysqlHost = self.settings.get("mysql_host")
#                    except IndexError:
#                        pass
#                    if mysqlHost == "":
#                        self.settings.put("mysql_host", value)
#                        self.controls["mysql_host"].control.setLabel(value)

                # mark screens as dirty
#                self.isDirty = True

    def onActionHook(self, action):
        mlog.debug("Window.onActionHook( action = %s )" % action)
        actionConsumed = False
        if action in (ui.ACTION_PARENT_DIR, ui.ACTION_PREVIOUS_MENU):
            try:
                self.settings.verify()
                self.settings.save()
                actionConsumed = False
            except SettingsException:
                quit = xbmcgui.Dialog().yesno('Error', 'Settings have not been tested successfully', 'MythBox cannot be used until settings are verified', 'Do you want to exit MythBox?')
                if quit:
                    actionConsumed = False
                else:
                    actionConsumed = True

#            else:
#                # user agreed to lose changes - reload settings from file
#                try:
#                    self.settings.load()
#                except mythtv.SettingsException:
#                    pass
#
#        actionConsumed = True
        return actionConsumed

    def onActionPostHook(self, action):
        # show the appropriate group of controls depending on which is in focus
        if action in (ui.ACTION_MOVE_UP, ui.ACTION_MOVE_DOWN, ui.ACTION_MOVE_LEFT, ui.ACTION_MOVE_RIGHT) :
            # give GUI time to process action
            time.sleep( 0.10 )
            id = self.getcontrolid(self.getFocus()) 
            if id in ("menu_mythtv_mythtv", "menu_mysql_mythtv", "menu_paths_mythtv"):
                self.showgroup("mythtv")
            elif id in ("menu_mythtv_mysql", "menu_mysql_mysql", "menu_paths_mysql"):
                self.showgroup("mysql")
            elif id in ("menu_mythtv_paths", "menu_mysql_paths", "menu_paths_paths"):
                self.showgroup("paths")

    def onControlHook(self, control):
        id = self.getcontrolid(control)
        log.debug("Window.onControlHook( id = %s)"%id)

        #--------------------------------------------------------------------
        # This is redundant but left in here because the XBMC emulator
        # does not support Window.getFocus() yet.
        
        if id in ("menu_mythtv_mythtv", "menu_mysql_mythtv", "menu_paths_mythtv"):
            self.showgroup("mythtv")
        elif id in ("menu_mythtv_mysql", "menu_mysql_mysql", "menu_paths_mysql"):
            self.showgroup("mysql")
        elif id in ("menu_mythtv_paths", "menu_mysql_paths", "menu_paths_paths"):
            self.showgroup("paths")
        elif id in ("menu_mythtv_test", "menu_mysql_test", "menu_paths_test"):
            self.testSettings()
        elif id in ("menu_mythtv_save", "menu_mysql_save", "menu_paths_save"):
            self.saveSettings()
        elif id in ("mythtv_host",
                    "mythtv_port",
                    "mythtv_minlivebufsize",
                    "mythtv_tunewait",
                    "mysql_host",
                    "mysql_port",
                    "mysql_database",
                    "mysql_user",
                    "mysql_password",
                    "paths_recordedprefix",
                    "paths_ffmpeg"):
            self.changeSettings(id)
        return 1

    def refreshControls(self):
        log.debug("Window.refreshControls()")
        tagNames = [
            'mythtv_host', 
            'mythtv_port',
            'mythtv_minlivebufsize', 
            'mythtv_tunewait', 
            'mysql_host', 
            'mysql_port', 
            'mysql_database', 
            'mysql_user',
            'mysql_password',
            'paths_recordedprefix',
            'paths_ffmpeg']

        for tag in tagNames:
            value = ""
            try:
                value = self.settings.get(tag)
            except IndexError:
                pass
            self.controls[tag].control.setLabel(value)

    def saveSettings(self):
        log.debug("Window.saveSettings()")
        self.settings.save()
        self.settings.load()
        self.isDirty = False
        ui.Dialog().ok(self.translator.get(S_INFO), self.translator.get(S_SETTINGS_SAVED))

    def testSettings(self):
        try:
            self.settings.verify()
            xbmcgui.Dialog().ok('MythBox', self.translator.get(S_INFO), 'Settings OK')
        except mythtv.SettingsException, ex:
            xbmcgui.Dialog().ok('MythBox', self.translator.get(S_ERROR), str(ex)) 
        
#        errors = 0
#        try:
#            self.conn.getFreeSpace()
#        except Exception, ex:
#            log.exception(str(ex))
#            errors += 1
#            ui.Dialog().ok(self.translator.get(S_ERROR), self.translator.get(S_CONNECT_MYTHTV_FAILED), str(ex))
#
#        try:
#            self.db.getChannels()
#        except Exception, ex:
#            log.exception(str(ex))
#            errors += 1
#            ui.Dialog().ok(self.translator.get(S_ERROR), self.translator.get(S_CONNECT_MYSQL_FAILED), str(ex))
#
#        if errors == 0:
#            ui.Dialog().ok(self.translator.get(S_INFO), self.translator.get(S_SETTINGS_OK))
