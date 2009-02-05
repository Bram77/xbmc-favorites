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

import domain
import logging
import scheduledetails
import time
import ui
import xbmcgui

log = logging.getLogger('mythtv.ui')

def compareTypeAsc(x, y):
    if x.type() == y.type():
        return cmp(x.title(), y.title())
    else:
        return cmp(x.formattedType(), y.formattedType())

def compareTypeDesc(y, x):
    if x.type() == y.type():
        return cmp(x.title(), y.title())
    else:
        return x.formattedType() < y.formattedType()

def compareTitleAsc(x, y):
    if x.title() == y.title():
        return x.type() < y.type()
    else:
        return cmp(x.title(), y.title())

def compareTitleDesc(y, x):
    if x.title() == y.title():
        return x.type() < y.type()
    else:
        return cmp(x.title(), y.title())

def showWindow(winDialog, conn, db, settings, translator):
    """
    Function to create the recording schedules window.
    """
    log.debug("> schedules.showWindow()")

    ui.checkSettings(settings)
    win = Window(conn=conn, db=db, settings=settings, translator=translator)
    win.loadskin("schedules.xml")
    win.loadData()
    winDialog.close()    
    win.doModal()
    del win
    log.debug("< schedules.showWindow()")

# =============================================================================
class Window(ui.BaseWindow):
    
    def __init__(self, *args, **kwargs):
        """Requires kwargs conn, db, settings, translator"""
        ui.BaseWindow.__init__(self, *args, **kwargs)
        self.schedules=[]
        self.focusControl = None

    def editSelected(self, control):
        log.debug("> schedules.Window.editSelected()")
        pos = control.getSelectedPosition()
        if pos < len(self.schedules):
            # make a copy of the schedule
            s = domain.ScheduleFromQuery(
                dict(self.schedules[pos].data().items()))

            # launch the schedule details window
            rc = scheduledetails.showWindow(s)

            # check if we should refresh the list
            if rc == 1:
                self.loadData()
            elif rc == 2:
                self.schedules[pos] = s
        log.debug("> schedules.Window.editSelected()")
            
    def loadData( self ):
        log.debug( '> schedules.Window.loadData()' )
        self.schedules = []
        xbmcgui.lock()
        try:
            listControl = self.controls["schedule_list"].control
            listControl.reset()
            self.schedules = self.db.getRecordingSchedules()
            self.schedules.sort( compareTypeAsc )
            for s in self.schedules:
                item = xbmcgui.ListItem()
                label = s.title()
                if s.type() == 3:   # channel
                #    item.setLabel2( s.formattedChannel() )
                    label += " (%s)"%s.formattedChannel()
                else:
                #    item.setLabel2( s.formattedType() )
                    label += " (%s)"%s.formattedType()
                item.setLabel( label )
                listControl.addItem( item )
            #self.updateShowDetails( 0 )
            xbmcgui.unlock()
        except:
            xbmcgui.unlock()
            raise
        log.debug( '< schedules.Window.loadData()' )

    def onActionHook(self, action):
        log.debug("> schedules.Window.onActionHook( action=[%s] )" % action)
        self.focusControl = self.getFocus()
        if action == ui.ACTION_PREVIOUS_MENU:
            try:
                self.settings.save()
            except:
                pass
        log.debug("< schedules.Window.onActionHook()")
        return 0

    def onActionPostHook(self, action):
        log.debug("> schedules.Window.onActionPostHook( action=[%s] )" % action)
        # check if the action was to move up or down
        if action in (ui.ACTION_MOVE_UP,
                      ui.ACTION_MOVE_DOWN,
                      ui.ACTION_SCROLL_UP,
                      ui.ACTION_SCROLL_DOWN):

            # check if the control in focus is the show list
            id = self.getcontrolid(self.focusControl)
            if id == "schedule_list":
                # give gui time to update
                time.sleep(0.10)

                # get selected show and populate details
                #self.updateShowDetails( self.focusControl.getSelectedPosition() )
        log.debug("< schedules.Window.onActionPostHook()")

    def onControlHook(self, control):
        log.debug("> schedules.Window.onControlHook()")

        id = self.getcontrolid(control)
        log.debug("ID: %s" % id)
#            if id == "view_by":
#                self.viewBySelected()
        if id == "schedule_list":
            xbmcgui.Dialog().ok('Info', 'Scheduling coming soon...')
            # TODO: Uncomment when schduling works...
            #self.editSelected(control)
        elif id == "refresh":
            self.loadData()

        log.debug("< schedules.Window.onControlHook()")
        return 1

    def populateScheduleDetails(self, show):
        # populate title
        self.controls['show_title'].control.reset()
        self.controls['show_title'].control.addLabel(show.fullTitle())
        log.debug("show_title=[%s]" % show.fullTitle())
        
        # populate air date
        self.controls['show_air_date'].control.setLabel(show.formattedAirDate())
        
        # populate channel
        self.controls['show_channel'].control.setLabel(show.formattedChannel())
        
        # populate orig air
        self.controls['show_orig_air'].control.setLabel(show.formattedOrigAirDate())
        
        # populate description
        self.controls['show_descr'].control.reset()
        self.controls['show_descr'].control.addLabel(show.formattedDescription())

    def updateShowDetails(self, pos):
        if pos < len(self.schedules):
            s = self.schedules[pos]
            self.populateScheduleDetails(s)