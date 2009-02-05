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

import logging
import domain
import os
import ui
import xbmc
import xbmcgui

log = logging.getLogger('mythtv.ui')

def showWindow(schedule, conn, db, settings, translator):
    """
    Function to create the recording schedule details window.

    Returns:
    - 1 if show was deleted
    - 0 otherwise
    """
    log.debug("> scheduledetails.showWindow()")
    win = Window(conn=conn, db=db, settings=settings, translator=translator)
    win.loadskin("scheduledetails.xml")
    win.loadDetails(schedule)
    win.doModal()
    retVal = win.shouldRefresh
    del win
    log.debug("< scheduledetails.showWindow() => %s"%retVal)
    return retVal

# =============================================================================
class Window(ui.BaseWindow):
    
    def __init__(self, *args, **kwargs):
        """Requires kwargs conn, db, settings, translator"""
        ui.BaseWindow.__init__(self, *args, **kwargs)
        self.shouldRefresh = 0
        self.iconCache = ui.ChannelIconCache(self.settings, self.conn)

    def delete(self):
        log.debug('> scheduledetails.Window.delete()')

        if self.schedule.recordid():
            # we have a recordid so it exists in database
            rc = ui.Dialog().yesno( \
                self.translator.get( 28 ), \
                self.translator.get( 157 ) )
            if rc:
                # delete the schedule
                self.db.deleteSchedule( self.schedule )
                self.shouldRefresh = 1

                # notify backend to reschedule
                self.conn.rescheduleNotify()

                # close the window
                self.close()
        else:
            # no recordid so this is a new one - just close window
            self.close()

        log.debug( '< scheduledetails.Window.delete()' )

    def getIntValue( self, id, min=None, max=None ):
        log.debug( '> scheduledetails.Window.getIntValue()' )

        kbd = xbmc.Keyboard( self.schedule.data()[id] )
        kbd.doModal()
        if kbd.isConfirmed():
            value = kbd.getText()
            intVal = None
            log.debug( "value=[%s]"%value )

            try:
                log.debug( "validating integer" )
                intVal = int( value )
            except ValueError:
                ui.Dialog().ok(
                    self.translator.get( 27 ),
                    self.translator.get( 30 ) )
                value = None
            if intVal and min != None and intVal < min:
                ui.Dialog().ok(
                    self.translator.get( 27 ),
                    self.translator.get( 154 )%min )
                value = None
            if intVal and max != None and intVal > max:
                ui.Dialog().ok(
                    self.translator.get( 27 ),
                    self.translator.get( 155 )%max )
                value = None
            if value:
                value = "%d"%int(value)
                log.debug( "stored value=[%s]"%value )
                self.schedule.data()[id] = value
                self.controls[id].control.setLabel( value )

        log.debug( '< scheduledetails.Window.getIntValue()' )
        
    def getListValue( self, id, choices, isLocalized=True ):
        log.debug( '> scheduledetails.Window.getListValue()' )

        valueList = []
        keyList = []
        if type(choices) is dict:
            for k,v in choices.items():
                keyList.append( str(k) )
                if isLocalized:
                    if choices == domain.gRecSchedTypeLongTrans and \
                        k == 3:
                        valueList.append(
                            str(self.translator.get( v )%
                                self.schedule.channum()) )
                    else:
                        valueList.append(
                            str(self.translator.get( v )) )
                else:
                    valueList.append( str(v) )
        elif type(choices) is list:
            valueList = choices
            keyList = choices
        pos = xbmcgui.Dialog().select(
            self.translator.get( 156 ),
            valueList )
        if pos != None:
            log.debug( "pos=[%d]"%pos )
            self.schedule.data()[id] = keyList[pos]
            self.controls[id].control.setLabel( valueList[pos] )

        log.debug( '< scheduledetails.Window.getListValue()' )
        
    def loadDetails(self, schedule):
        log.debug('Schedule = %s' % schedule)
        self.schedule = schedule
        self.populateDetails(self.schedule)

    def onControlHook( self, control ):
        log.debug( "> scheduledetails.Window.onControlHook()" )

        id = self.getcontrolid( control )

        if id == "save":
            self.save()
        elif id == "delete":
            self.delete()
        elif id == "refresh":
            self.refresh()
        elif id in ('autoexpire',
                    'autocommflag',
                    'maxnewest'):
            self.controls[id].control.setSelected(
                not int(self.schedule.data()[id]) )
            self.schedule.data()[id] = "%d"%(not int(self.schedule.data()[id]))
            log.debug( "id=[%s] value=[%s]"%(id,self.schedule.data()[id]) )
        elif id == 'recpriority':
            self.getIntValue( id, -99, 99 )
        elif id == 'maxepisodes':
            self.getIntValue( id, 0 )
        elif id == 'startoffset':
            self.getIntValue( id, -60, 60 )
        elif id == 'endoffset':
            self.getIntValue( id, -60, 60 )
        elif id == 'type':
            self.getListValue( id, domain.gRecSchedTypeLongTrans )
        elif id == 'dupin':
            self.getListValue( id, domain.gRecSchedDupInTrans )
        elif id == 'dupmethod':
            self.getListValue( id, domain.gRecSchedDupMethodTrans )
        elif id == 'profile':
            profileList = [ \
                'Default', 'Live TV', 'High Quality', 'Low Quality' ]
            self.getListValue( id, profileList, isLocalized=False )
        elif id == 'recgroup':
            recgroupList = [ 'Default' ]
            self.getListValue( id, recgroupList, isLocalized=False )

        log.debug( "< scheduledetails.Window.onControlHook()" )
        return 1

    def populateDetails(self, s):
        log.debug( "> scheduledetails.Window.populateDetails()" )

        fmt = self.translator.get( 121 )
        try:
            self.controls['window_title'].control.setLabel( fmt%s.title() )
        except:
            pass
        try:
            if s.chanid() > 0:
                self.controls['channel'].control.setLabel( s.formattedChannel() )
            else:
                self.controls['channel'].control.setLabel(
                    self.translator.get( 46 ) )
        except:
            pass
        try:
            self.controls['date'].control.setLabel( s.formattedStartDate() )
        except:
            pass
        
        try:
            self.controls['time'].control.setLabel( s.formattedTime() )
        except:
            pass
        
        log.debug( "finding file for [%s]"%s )
        
        shost = self.settings.get("mythtv_host")
        file = ui.picBase + 'channels\\' + str(s.channum()) + ui.picType
        if not os.path.exists(file):
            file = None
            if s.icon():
                try:
                    file = self.iconCache.findFile(s, shost)
                except:
                    log.debug(" populateDetails: nothing assigned to file")
            
        if file != None:
            log.debug( "file=[%s]"%file )
            if file:
                c = self.controls['channel_icon'].control
                self.removeControl( c )
                del c
                log.debug( "deleted old control" )
                c = xbmcgui.ControlImage(
                    int(self.getoption('channel_x')),
                    int(self.getoption('channel_y')),
                    int(self.getoption('channel_w')),
                    int(self.getoption('channel_h')),
                    file )
                log.debug( "created control" )
                self.addControl( c )
                log.debug( "added control" )
                self.controls['channel_icon'].control = c
            
        if s.type() == 3:   # channel
            self.controls['type'].control.setLabel(
                s.formattedTypeLong()%s.channum() )
        else:
            self.controls['type'].control.setLabel( s.formattedTypeLong() )

        self.controls['profile'].control.setLabel( s.profile() )

        value = "%d"%s.recpriority()
        self.controls['recpriority'].control.setLabel( value )

        self.controls['recgroup'].control.setLabel( s.recgroup() )

        self.controls['autoexpire'].control.setSelected( s.autoexpire() )

        self.controls['autocommflag'].control.setSelected( s.autocommflag() )

        self.controls['maxnewest'].control.setSelected(s.maxnewest())

        value = "%d"%s.maxepisodes()
        self.controls['maxepisodes'].control.setLabel( value )

        self.controls['dupin'].control.setLabel( s.formattedDuplicateIn() )

        self.controls['dupmethod'].control.setLabel(
            s.formattedDuplicateMethod() )

        value = "%d"%s.startoffset()
        self.controls['startoffset'].control.setLabel( value )

        value = "%d"%s.endoffset()
        self.controls['endoffset'].control.setLabel( "%d"%s.endoffset() )

        log.debug( "< scheduledetails.Window.populateDetails()" )

    def refresh( self ):
        log.debug( "> scheduledetails.Window.refresh()" )

        if self.schedule.recordid():
            # parent window should refresh as well
            self.shouldRefresh = 1

            # retrieve the schedule details
            # TODO: Isn't chanID the first arg?
            scheds = self.db.getRecordingSchedules(self.schedule.recordid() )
            if len( scheds ) == 1:
                self.schedule = scheds[0]
                self.loadDetails( self.schedule )
            else:
                # recording schedule no longer exists
                ui.Dialog().ok(
                    self.translator.get( 26 ),
                    self.translator.get( 122 ) )
                self.close()

        log.debug( "< scheduledetails.Window.refresh()" )

    def save( self ):
        log.debug( "> scheduledetails.Window.save()" )
        if not self.schedule.subtitle():
            self.schedule.data()['subtitle'] = ""
        if not self.schedule.category():
            self.schedule.data()['category'] = ""
        if not self.schedule.description():
            self.schedule.data()['description'] = ""
        self.db.saveSchedule( self.schedule )
        self.shouldRefresh = 2
        self.conn.rescheduleNotify( self.schedule )
        ui.Dialog().ok(
            self.translator.get( 26 ),
            self.translator.get( 158 ) )
        log.debug( "< scheduledetails.Window.save()" )
