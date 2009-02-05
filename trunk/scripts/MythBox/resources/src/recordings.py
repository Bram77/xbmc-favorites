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
import recordingdetails
import sre
import string
import time
import traceback
import ui
import util
import xbmcgui

from time import strftime, strptime

log = logging.getLogger('mythtv.ui')
mlog = logging.getLogger('mythtv.method')

# TODO: Looks like duplicate in other class
def compareDateAsc( x, y ):
    if x.starttime() == y.starttime():
        return cmp( x.endtime(), y.endtime() )
    else:
        return cmp( x.starttime(), y.starttime() )

# TODO: Looks like duplicate in other class
def compareDateDesc( y, x ):
    if x.starttime() == y.starttime():
        return cmp( x.endtime(), y.endtime() )
    else:
        return cmp( x.starttime(), y.starttime() )

# TODO: Looks liek duplicate in other class
def compareTitleAsc( x, y ):
    if x.title() == y.title():
        return cmp( x.starttime(), y.starttime() )
    else:
        return cmp( x.title(), y.title() )

# TODO: Looks like duplicate in other class
def compareTitleDesc( y, x ):
    if x.title() == y.title():
        return cmp( x.starttime(), y.starttime() )
    else:
        return cmp( x.title(), y.title() )

def showWindow(parent, conn, db, settings, translator, thumbCache):
    """
    Function to create the recorded show window.
    """
    win = Window(
        conn=conn, 
        db=db, 
        settings=settings, 
        translator=translator,
        thumbCache=thumbCache)
    
    win.loadskin("recordedshows.xml")
    win.loadRecGroupList()
    parent.close()
    win.doModal()
    del win

# =============================================================================
class Window(ui.BaseWindow):
    
    VIEW_BY_MIN         = 0     # must be smallest sequential value
    VIEW_BY_DATE_ASC    = 1
    VIEW_BY_DATE_DESC   = 2
    VIEW_BY_TITLE_ASC   = 3
    VIEW_BY_TITLE_DESC  = 4
    VIEW_BY_MAX         = 5     # must be largest sequential value

    def __init__(self, *args, **kwargs):
        """Requires kwargs conn, db, settings, translator, thumbCache"""
        ui.BaseWindow.__init__(self, *args, **kwargs)
        self.recordings = []
        self.focusControl = None
        self.showRecGroup = True
        self.updateEpisodesOnScroll = True
        try:
            self.recGroup = self.settings.get("recorded_default_group")
        except:
            self.recGroup = "default"
        
        self.curTitle = "All Shows (x shows)"
        self.recGroups = []
        self.showTitles = []

        self.viewByLabel = { 
            self.VIEW_BY_DATE_ASC: 38,
            self.VIEW_BY_TITLE_ASC: 39,
            self.VIEW_BY_DATE_DESC: 69,
            self.VIEW_BY_TITLE_DESC: 70 
        }

        try:
            self.viewBy = int(self.settings.get("recorded_view_by" ))
        except IndexError:
            self.viewBy = self.VIEW_BY_DATE_DESC
            self.settings.put("recorded_view_by", "%d"%self.viewBy, shouldCreate=1)
            pass
        
    def loadingRemove(self):
        self.isLoading = False
        self.hidegroup("popup")
            
    def showIconImg( self, img, path="" ):
        c = self.controls['popup_icon'].control
        self.removeControl( c )
        del c

        x = int(self.getvalue(self.getoption("popup_channel_x")))
        y = int(self.getvalue(self.getoption("popup_channel_y")))
        w = int(self.getvalue(self.getoption("popup_channel_w")))
        h = int(self.getvalue(self.getoption("popup_channel_h")))

        texture = img
        tx = util.findMediaFile( texture )
        if tx == None:
            tx = path + texture

        c = xbmcgui.ControlImage(x, y, w, h, tx)
        self.addControl( c )
        self.controls['popup_icon'].control = c

    def loadingShow(self, show):
        # self.loadingRemove()
        self.group = "main"
        self.showgroup("popup", False)

        # populate title
        self.isLoading = True
        theShowDesc = show.formattedDescription()
        theChanID = show.chanstr()
        #theChanName = show.formattedChannel()
        theShowName = show.fullTitle()
        
        chanTxt = "Loading " + str(theShowName) + " Please Wait..."
        log.debug("*** %s: %s - %s" % (chanTxt, theShowName, theShowDesc))
        self.controls['popup_title'].control.setLabel(chanTxt)
        self.controls['popup_line_a'].control.reset()
        self.controls['popup_line_a'].control.addLabel(chanTxt)
        self.controls['popup_line_b'].control.reset()
        self.controls['popup_line_b'].control.addLabel(theShowDesc)

        self.showIconImg('channels\\' + str(theChanID) + ui.picType, ui.picBase)

    def buildListEntry(self, row):
        start = strptime( row.starttime(), "%Y%m%d%H%M%S" )
        entry = strftime( "%m/%d %I:%M %p", start ) + "   "
        if row.title():
            entry += row.title()
        if row.subtitle() and not sre.match( '^\s+$', row.subtitle() ):
            entry += " - " + row.subtitle()
        log.debug('Window.buildListEntry(row = %s) => %s)'%(row, entry))            
        return entry

    def loadRecGroupList(self):
        mlog.debug('Window.loadRecGroupList()')
        if self.showRecGroup:        
            self.recGroups = self.db.getRecordingGroups( )
            log.debug ("%s Recording Groups Found" % str(len(self.recGroups)))
            ctl = self.controls["recgroup_list"].control

            cnt = 0
            curIdx = 0
            recg = self.recGroup

            log.debug(recg)
            xbmcgui.lock()
            
            try:
                ctl.reset()
                try:
                    ctl.setPageControlVisible(False)
                except:
                    pass
                
                for r in self.recGroups:
                    if string.upper(r[0]) == string.upper(recg):
                        curIdx = cnt
                    cnt += 1
                    ctl.addItem( "%s" % (r[0]) )
                    ctl.selectItem( curIdx )
                xbmcgui.unlock()
            except:
                traceback.print_exc()
                xbmcgui.unlock()
        else:
            try:
                ctl = self.controls["recgroup_list"].control
                ctl.setVisible(False)
            except:
                log.error("Unable to remove recgroup control. Maybe it's been removed from the skin?")

        self.loadTitleList()

    def loadTitleList(self):
        mlog.debug('Window.loadTitleList()')

        recg = self.recGroup # self.recGroup[:str(self.recGroup).rfind("(")-1]
        self.showTitles = self.db.getRecordingTitles(recg)
        log.debug ("%s Recording Titles Found for Rec Group %s" % (len(self.showTitles), recg))
        ctl = self.controls["show_list"].control

        ## if rec group has no shows swap back to first group and reload
        if len(self.showTitles) == 1:
            self.recGroup = self.recGroups[1][0]
            self.loadRecGroupList()
            return

        cnt = 0
        curIdx = 0
        curt = string.upper(self.curTitle[:str(self.curTitle).rfind("(")-1])

        log.debug(curt)        
        xbmcgui.lock()
        try:
            ctl.reset()
            try:
                ctl.setPageControlVisible(False)
            except:
                pass
      
            for r in self.showTitles:
                if string.upper(r[0]) == curt:
                    curIdx = cnt
                cnt += 1
                title = r[0]
                ctl.addItem("%s (%s shows)" % (title, r[1]))
            ctl.selectItem(curIdx)
            xbmcgui.unlock()
        except:
            log.exception('loadTitleList')
            xbmcgui.unlock()
        self.loadEpisodeList()
    
    def loadEpisodeList(self):
        mlog.debug('Window.loadEpisodeList()')
        curt = self.curTitle[:str(self.curTitle).rfind("(")-1]
        recg = self.recGroup # self.recGroup[:str(self.recGroup).rfind("(")-1]
        log.debug ("%s - %s" % (recg, curt))
        self.recordings = self.conn.getRecordings(recg, curt)
        log.debug("%s Recordings Found for Title %s" % (len(self.recordings), curt))

        ## If current title has no recordings then swap back to all shows (current title has been deleted)
        if len(self.recordings) == 0 and string.upper(curt) != "ALL SHOWS":
            self.curTitle = "All Shows (x shows)"
            self.loadTitleList()
            return

        try:   
            if self.viewBy == self.VIEW_BY_DATE_ASC:
                self.recordings.sort(compareDateAsc)
            elif self.viewBy == self.VIEW_BY_DATE_DESC:
                self.recordings.sort(compareDateDesc)
            elif self.viewBy == self.VIEW_BY_TITLE_ASC:
                self.recordings.sort(compareTitleAsc)
            elif self.viewBy == self.VIEW_BY_TITLE_DESC:
                self.recordings.sort(compareTitleDesc)
            ctl = self.controls["episode_list"].control
        except:
            log.exception('loadEpisodeList/0')
            raise
        
        xbmcgui.lock()
        try:
            self.controls["view_by"].control.setLabel(\
                self.translator.get(self.viewByLabel[self.viewBy]))

            ctl.reset()
            for r in self.recordings:
                ctl.addItem(self.buildListEntry(r))
            if len(self.recordings) > 0:
                self.populateShowDetails(0)

            xbmcgui.unlock()
        except:
            log.exception('loadEpisodeList/1')
            xbmcgui.unlock()
            raise

        try:
            freeSpace = self.conn.getFreeSpace()
            self.controls['free_space'].control.setLabel(freeSpace[0])
        except Exception:
            self.controls['free_space'].control.setLabel( \
                self.translator.get(45))
            log.exception('loadEpisodeList/2')

    def onActionHook(self, action):
        mlog.debug("Window.onActionHook(action = %s)"%action)
        self.focusControl = self.getFocus()
        if action == ui.ACTION_PREVIOUS_MENU:
            self.settings.save()
        return 0

    def onActionPostHook(self, action):
        mlog.debug("Window.onActionPostHook(action = %s)"%action)
        # check if the action was to move up or down
        if action in (ui.ACTION_MOVE_UP, ui.ACTION_MOVE_DOWN, ui.ACTION_SCROLL_UP, ui.ACTION_SCROLL_DOWN):
            # check if the control in focus is the show list
            id = self.getcontrolid(self.focusControl)
            if id == "recgroup_list":
                if self.updateEpisodesOnScroll:
                    # give gui time to update
                    time.sleep(0.10)
                    # Update episode list with new shows
                    rg = self.recGroups[self.focusControl.getSelectedPosition()]
                    self.recGroup = "%s" % rg[0]
                    self.settings.put("recorded_default_group", "%s"%self.recGroup, shouldCreate=1)
                    self.curTitle = "All Shows (0 shows)"
                    self.loadTitleList()
            elif id == "episode_list":
                # give gui time to update
                time.sleep(0.10)
                # get selected show and populate details
                self.populateShowDetails(self.focusControl.getSelectedPosition())
            elif id == "show_list":
                if self.updateEpisodesOnScroll:
                    # give gui time to update
                    time.sleep(0.10)
                    # Update episode list with new shows
                    ct = self.showTitles[self.focusControl.getSelectedPosition()]
                    self.curTitle = "%s (%s shows)" % (ct[0], ct[1])
                    self.loadEpisodeList()

    def onControlHook(self, control):
        id = self.getcontrolid(control)
        mlog.debug("Window.onControlHook(%s)"%id)

        if id == "view_by":
            self.viewBySelected()
        elif id == "episode_list":
            self.showSelected(control)
        elif id == "recgroup_list":
            if not self.updateEpisodesOnScroll:            
                rg = self.recGroups[self.focusControl.getSelectedPosition()]
                self.recGroup = "%s" % (rg[0])
                self.curTitle = "All Shows (0 shows)"
                self.loadTitleList()
        elif id == "show_list":
            if not self.updateEpisodesOnScroll:
                ct = self.showTitles[self.focusControl.getSelectedPosition()]
                self.curTitle = "%s (%s shows)" % (ct[0], ct[1])
                self.loadEpisodeList()
        elif id == "refresh":
            self.loadRecGroupList()
        return 1

    def populateShowDetails(self, pos):
        mlog.debug("Window.populateShowDetails(pos= %s)"%pos)

        if pos < len(self.recordings):
            row = self.recordings[pos]

            # populate title
            self.controls['show_title'].control.reset()
            self.controls['show_title'].control.addLabel(row.fullTitle())
            log.debug("show_title = %s"%row.fullTitle())

            # populate air date
            self.controls['show_air_date'].control.setLabel(row.formattedAirDate())
            log.debug("show_air_date = %s"%row.formattedAirDate())

            # populate channel
            self.controls['show_channel'].control.setLabel(row.formattedChannel())
            log.debug("show_channel = %s"%row.formattedChannel())

            # populate orig air
            self.controls['show_orig_air'].control.setLabel(row.formattedOrigAirDate())
            log.debug("show_orig_air = %s"%row.formattedOrigAirDate())

            # populate description
            self.controls['show_descr'].control.reset()
            self.controls['show_descr'].control.addLabel(row.formattedDescription())
            log.debug("show_descr = %s"%row.formattedDescription()) 

    def showSelected(self, control):
        mlog.debug("Window.showSelected()")
     
        pos = control.getSelectedPosition()
        
        log.debug('Showing details for show at index %s' % pos)
        
        if pos < len(self.recordings):
            self.loadingShow(self.recordings[pos])
            
            rc = recordingdetails.showWindow(
                self.recordings[pos], 
                self.conn, 
                self.db, 
                self.settings, 
                self.translator,
                self.thumbCache)
            
            self.loadingRemove()
            # refresh list if show was deleted
            if rc == 1:
                self.loadRecGroupList()

    def viewBySelected(self):
        mlog.debug("Window.viewBySelected()")

        # switch to next view by
        self.viewBy += 1
        if self.viewBy >= self.VIEW_BY_MAX:
            self.viewBy = self.VIEW_BY_MIN+1

        # store the setting change
        self.settings.put("recorded_view_by", "%d"%self.viewBy, shouldCreate=1)

        # refresh the listing
        self.loadEpisodeList()
