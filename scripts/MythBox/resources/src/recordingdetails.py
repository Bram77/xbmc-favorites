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
import player
import ui

log = logging.getLogger('mythtv.ui')
mlog = logging.getLogger('mythtv.method')

# =============================================================================
def showWindow(program, conn, db, settings, translator, thumbCache):
    """
    Function to create the recorded show details window.

    Returns:
    - 1 if show was deleted
    - 0 otherwise
    """
    win = Window(
        conn=conn, 
        db=db, 
        settings=settings, 
        translator=translator, 
        thumbCache=thumbCache)
    
    win.loadShowDetails(program)
    win.doModal()
    retVal = win.isDeleted
    del win
    log.debug("showWindow() => %d"%retVal)
    return retVal

# =============================================================================
class Window(ui.BaseWindow):
    
    def __init__(self, *args, **kwargs):
        """Requires kwargs conn, db, settings, translator, thumbCache"""
        ui.BaseWindow.__init__(self, *args, **kwargs)
        self.isDeleted = 0
        #TODO: Inject via constructor
        #self.player = player.getPlayer()
        self.loadskin("recordedshowdetails.xml")
        self.autoExpireLabel = self.controls['autoexpire'].control

    def autoexpire(self):
        log.debug('Window.autoexpire()')
        self.db.setRecordedAutoexpire(
            self.program.chanid(),
            self.program.starttime(),
            not self.program.autoexpire())
        # reload program details
        self.refresh()

    def delete(self):
        mlog.debug('Window.delete()')

        rc = ui.Dialog().yesno(self.translator.get(28), self.translator.get(65))
        if rc:
            self.conn.deleteRecording(self.program)
            self.isDeleted = 1
            self.close()

    def rerecord(self):
        mlog.debug('Window.rerecord()')

        rc = ui.Dialog().yesno(self.translator.get(28), self.translator.get(65))
        if rc:
            self.conn.rerecordRecording(self.program)
            self.isDeleted = 1
            self.close()

    def loadShowDetails(self, program):
        log.debug('Window.loadShowDetails(%s)' % program)
        self.program = program
        if self.program.autoexpire():
            self.autoExpireLabel.setLabel(self.translator.get(49)) # save
        else:
            self.autoExpireLabel.setLabel(self.translator.get(50)) # expire

        self.populateShowDetails(self.program)

        try:
            thumbFile = self.thumbCache.findFile(self.program , self.program.hostname())
            
            if not thumbFile:
                ui.Dialog().ok(self.translator.get(27), self.translator.get(85))
            else:
                self.controls['screenshot'].control.setImage(thumbFile)
        except:
            log.exception('Failed to load screenshot thumbnail')
            raise
        
    def onControlHook(self, control):
        id = self.getcontrolid(control)
        log.debug("Window.onControlHook( %s )"%id)
        
        if id == "play":
            p = player.MythPlayer()
            p.playRecording(self.program, player.NoOpCommercialSkipper(p, self.program))
            del p # induce GC so on* callbacks unregistered
#            self.player.playRecording(
#                self.program, 
#                player.NoOpCommercialSkipper(self.player, self.program))
        elif id == "playskip":
            p = player.MythPlayer()
            p.playRecording(self.program, player.TrackingCommercialSkipper(p, self.program))
            del p # induce GC so on* callbacks unregistered
#            self.player.playRecording(
#                self.program,
#                player.TrackingCommercialSkipper(self.player, self.program))
        elif id == "autoexpire":
            self.autoexpire()
        elif id == "delete":
            self.delete()
        elif id == "rerecord":
            self.rerecord()
        elif id == "refresh":
            self.refresh()
        return True

    def populateShowDetails(self, s):
        log.debug("Window.populateShowDetails(%s)"%s)

        # populate title
        self.controls['show_title'].control.reset()
        self.controls['show_title'].control.addLabel(s.fullTitle())

        # populate air date
        self.controls['show_air_date'].control.setLabel(s.formattedAirDate())

        # populate channel
        self.controls['show_channel'].control.setLabel(s.formattedChannel())

        # populate orig air
        self.controls['show_orig_air'].control.setLabel(s.formattedOrigAirDate())

        # populate description
        self.controls['show_descr'].control.reset()
        self.controls['show_descr'].control.addLabel(s.formattedDescription())

        # populate category
        self.controls['show_category'].control.setLabel(s.category())

        # populate autoexpire
        ctl = self.controls['show_autoexpire'].control
        if s.autoexpire():
            ctl.setLabel(self.translator.get(58))
        else:
            ctl.setLabel(self.translator.get(59))

        # populate file size
        self.controls['show_file_size'].control.setLabel(s.formattedFileSize())

        # enable comm skip button
        self.controls['playskip'].control.setEnabled(self.program.hasCommercials())

    def refresh(self):
        self.program = self.conn.getSingleProgram(
            self.program.chanid(),
            self.program.starttime(),
            self.program.endtime())
        self.loadShowDetails(self.program)
