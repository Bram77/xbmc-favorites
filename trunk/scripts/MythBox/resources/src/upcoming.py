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

import logging
import sre
import time
import traceback
import ui
import util
import xbmcgui

from datetime import datetime
from time import strftime

log = logging.getLogger('mythtv.ui')
mlog = logging.getLogger('mythtv.method')

def compareDateAsc( x, y ):
    if x.starttime() == y.starttime():
        return cmp( x.chanid(), y.chanid() )
    else:
        return cmp( x.starttime(), y.starttime() )

def compareDateDesc( y, x ):
    if x.starttime() == y.starttime():
        return cmp( x.chanid(), y.chanid() )
    else:
        return cmp( x.starttime(), y.starttime() )

def compareTitleAsc( x, y ):
    if x.title() == y.title():
        return cmp( x.starttime(), y.starttime() )
    else:
        return cmp( x.title(), y.title() )

def compareTitleDesc( y, x ):
    if x.title() == y.title():
        return cmp( x.starttime(), y.starttime() )
    else:
        return cmp( x.title(), y.title() )

def showWindow(winDialog, conn, db, settings, translator):
    """Function to create the recorded show window."""
    mlog.debug( "> upcoming.showWindow()" )

    ui.checkSettings(settings)
    win = Window(conn=conn, db=db, settings=settings, translator=translator)
    win.loadskin( "upcomingshows.xml" )
    win.loadList()
    winDialog.close()    
    win.doModal()
    del win
    mlog.debug( "< upcoming.showWindow()" )

# =============================================================================
class Window(ui.BaseWindow):
    
    VIEW_BY_MIN         = 0     # must be smallest sequential value
    VIEW_BY_DATE_ASC    = 1
    VIEW_BY_DATE_DESC   = 2
    VIEW_BY_TITLE_ASC   = 3
    VIEW_BY_TITLE_DESC  = 4
    VIEW_BY_MAX         = 5     # must be largest sequential value

    def __init__(self, *args, **kwargs):
        """Requires kwargs conn, db, settings, translator"""
        ui.BaseWindow.__init__(self, *args, **kwargs)
        self.recordings = []
        self.focusControl = None

        self.viewByLabel = { 
            self.VIEW_BY_DATE_ASC: 38, 
            self.VIEW_BY_TITLE_ASC: 39, 
            self.VIEW_BY_DATE_DESC: 69, 
            self.VIEW_BY_TITLE_DESC: 70 
        }

        try:
            self.viewBy = int(self.settings.get("upcoming_view_by" ))
        except IndexError:
            self.viewBy = self.VIEW_BY_DATE_DESC
            self.settings.put("upcoming_view_by", "%d"%self.viewBy, shouldCreate=1)
            pass

    def buildListEntry( self, row ):
        mlog.debug( '> upcoming.Window.buildListEntry()' )
        entry = strftime("%a %d/%m %I:%M%p",time.localtime(float(row.recstarttime())))
        if row.cardid():
            entry += " - Encoder %s" % row.cardid()
        if row.channame():
            entry += " - %s" % row.channame()
        if row.title():
            entry += " - %s"%row.title()
        if row.subtitle() and not sre.match( '^\s+$', row.subtitle() ):
            entry += "-%s" %row.subtitle()
#        start = strptime( row.starttime(), "%Y%m%d%H%M%S" )
#        entry = strftime( "%m/%d %I:%M %p", start ) + "   "
#        if row.title():
#            entry += row.title()
#        if row.subtitle() and not sre.match( '^\s+$', row.subtitle() ):
#            entry += " - " + row.subtitle()
#
        mlog.debug( '< upcoming.Window.buildListEntry()' )
        return entry

    def loadList( self ):
        mlog.debug( '> upcoming.Window.loadList()' )

        recordings = self.conn.getPendingRecordings()

        if self.viewBy == self.VIEW_BY_DATE_ASC:
            recordings.sort( compareDateAsc )
        elif self.viewBy == self.VIEW_BY_DATE_DESC:
            recordings.sort( compareDateDesc )
        elif self.viewBy == self.VIEW_BY_TITLE_ASC:
            recordings.sort( compareTitleAsc )
        elif self.viewBy == self.VIEW_BY_TITLE_DESC:
            recordings.sort( compareTitleDesc )

        ctl = self.controls["show_list"].control

        xbmcgui.lock()
        try:
            self.controls["view_by"].control.setLabel( \
                self.translator.get( self.viewByLabel[self.viewBy] ) )

            ctl.reset()
            self.recordings = []
            now = datetime.now().strftime( "%Y%m%d%H%M%S" )
            for r in recordings:
                if r.endtime() >= now:
                    ctl.addItem( self.buildListEntry( r ) )
                    self.recordings.append( r )
            if len( self.recordings ) > 0:
                self.populateShowDetails( 0 )
            xbmcgui.unlock()
        except:
            xbmcgui.unlock()
            raise

        try:
            freeSpace = self.conn.getFreeSpace()
            self.controls['free_space'].control.setLabel(freeSpace[0])
        except Exception:
            self.controls['free_space'].control.setLabel(self.translator.get( 45 ))

        mlog.debug( '< upcoming.Window.loadList()' )

    def onActionHook( self, action ):
        mlog.debug( "> upcoming.Window.onActionHook( action=[%s] )"%action )
        self.focusControl = self.getFocus()

        if action == ui.ACTION_PREVIOUS_MENU:
            self.settings.save()
        mlog.debug( "< upcoming.Window.onActionHook()" )
        return 0

    def onActionPostHook( self, action ):
        mlog.debug( "> upcoming.Window.onActionPostHook()" )
        # check if the action was to move up or down
        if action == ui.ACTION_MOVE_UP or \
            action == ui.ACTION_MOVE_DOWN or \
            action == ui.ACTION_SCROLL_UP or \
            action == ui.ACTION_SCROLL_DOWN:

            # check if the control in focus is the show list
            id = self.getcontrolid( self.focusControl )
            if id == "show_list":
                # give gui time to update
                time.sleep( 0.10 )

                # get selected show and populate details
                self.populateShowDetails(
                    self.focusControl.getSelectedPosition() )
        mlog.debug( "< upcoming.Window.onActionPostHook()" )

    def onControlHook( self, control ):
        mlog.debug( "> upcoming.Window.onControlHook()" )
        id = self.getcontrolid( control )

        if id == "view_by":
            self.viewBySelected()
        elif id == "show_list":
            self.showSelected( control )
        elif id == "refresh":
            self.loadList()
        mlog.debug( "< upcoming.Window.onControlHook()" )
        return 1

    def populateShowDetails( self, pos ):
        mlog.debug( "> upcoming.Window.populateShowDetails( pos=%d)"%pos )

        if pos < len( self.recordings ):
            row = self.recordings[pos]

            # populate title
            self.controls['show_title'].control.reset()
            title = row.fullTitle()
            self.controls['show_title'].control.addLabel( title )
            log.debug( "show_title=[%s]"%title )

            # populate air date
            self.controls['show_air_date'].control.setLabel( \
                row.formattedAirDate() )
            log.debug( "show_air_date=[%s]"%row.formattedAirDate() )

            # populate channel
            self.controls['show_channel'].control.setLabel( \
                row.formattedChannel() )
            log.debug( "show_channel=[%s]"%row.formattedChannel() )

            # populate orig air
            self.controls['show_orig_air'].control.setLabel( \
                row.formattedOrigAirDate() )
            log.debug( "show_orig_air=[%s]"%row.formattedOrigAirDate() )

            # populate description
            self.controls['show_descr'].control.reset()
            self.controls['show_descr'].control.addLabel( \
                row.formattedDescription() )
            log.debug( "show_descr=[%s]"%row.formattedDescription() )

            # populate notes
            self.controls['show_notes'].control.reset()
            self.controls['show_notes'].control.addLabel( \
                row.translatedRecStatus() )
            log.debug( "show_notes=[%s]"%row.translatedRecStatus() )

        mlog.debug( "< upcoming.Window.populateShowDetails( pos=%d)"%pos )

    def showSelected( self, control ):
        mlog.debug( "> upcoming.Window.showSelected()" )

        pos = control.getSelectedPosition()
        if pos < len( self.recordings ):
            #rc = recordingdetails.showWindow(self.recordings[pos])
            rc = 0
            # refresh list if show was deleted
            if rc == 1:
                self.loadList()

        mlog.debug( "< upcoming.Window.showSelected()" )

    def viewBySelected( self ):
        mlog.debug( "> upcoming.Window.viewBySelected()" )

        # switch to next view by
        self.viewBy += 1
        if self.viewBy >= self.VIEW_BY_MAX:
            self.viewBy = self.VIEW_BY_MIN+1

        # store the setting change
        self.settings.put("upcoming_view_by", "%d" % self.viewBy, shouldCreate=1)

        # refresh the listing
        self.loadList()

        mlog.debug( "< upcoming.Window.viewBySelected()" )

# =============================================================================
if __name__ == "__main__":
    try:
        loadingWin = xbmcgui.DialogProgress()
        loadingWin.create("Upcoming Shows","Loading Upcoming Shows","Please Wait...")    
        util.initialize()
        showWindow(loadingWin)
    except Exception, ex:
        traceback.print_exc()
        ui.Dialog().ok('Shit blew up!', str(ex))
