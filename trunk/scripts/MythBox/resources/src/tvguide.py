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

import datetime
import livetv
import logging
import domain
import os
import scheduledetails
import ui
import util
import xbmcgui

log = logging.getLogger('mythtv.ui')
mlog = logging.getLogger('mythtv.method')

def showWindow(winDialog, conn, db, settings, translator):
    """ Function to create the tv guide window.  """
    mlog.debug("> tvguide.showWindow()")
    ui.checkSettings(settings)
    win = Window(conn=conn, db=db, settings=settings, translator=translator)
    win.loadskin("tvguide.xml")
    win.loadGuide()
    winDialog.close()    
    win.doModal()
    del win
    mlog.debug("< tvguide.showWindow()")

# =============================================================================
class Window(ui.BaseWindow):

    # Mapping of Myth TV category names to color names (used as a file prefix)
    # in the tv guide.
    categoryColors = {
        "Adults only"       : "red",
        "Basketball"        : "blue",
        "Children"          : "green",
        "Children-music"    : "green",
        "Children-special"  : "green",
        "Fishing"           : "blue",
        "Hockey"            : "blue",
        "News"              : "olive",
        "Newsmagazine"      : "olive",
        "Romance"           : "purple",
        "Romance-comedy"    : "purple",
        "Science"           : "cyan",
        "Science fiction"   : "orange",
        "Sitcom"            : "yellow",
        "Soap"              : "purple",
        "Sports"            : "blue",
        "Sports event"      : "blue",
        "Sports non-event"  : "blue",
        "Talk"              : "purple",
        "Travel"            : "cyan",
    }
    
    def __init__(self, *args, **kwargs):
        """Requires kwargs conn, db, settings, translator"""
        ui.BaseWindow.__init__(self, *args, **kwargs)
        self.doLiveTV = False
        self.programs = []
        self.startTime = None
        self.endTime = None
        self.startChan = None
        self.endChan = None
        self.channels = None
        self.channelSpan = 2
        self.hourSpan = 2.0
        self.initialized = False
        self.channelCtls = []
        self.timeLabelCtls = []
        self.progButtonCtls = []  # list of all buttons that represent tv guide - left to right, top to bottom
        self.topCtls = []
        self.bottomCtls = []
        self.leftCtls = []
        self.rightCtls = []
        self.prevFocus = None
        self.prevButtonInfo = None
        self.lock = 0

    def addProgramControl(self, program, info, relX, relY, width, height):
        """ Adds a control (button overlayed with a label) for a program in the guide """
        
        mlog.debug("> addProgramControl(program=%s, info=%s, relX=%d, relY=%d, width=%d, height=%d)"%(
            program, info, relX, relY, width, height))
        
        info['program'] = program
        if not program:
            info['nodata'] = True
            info['starttime'] = None
            info['title'] = self.translator.get(108) # 'No data'
            category = None
        else:
            info['nodata'] = False
            info['starttime'] = program.starttime()
            info['title'] = program.title()
            if program.starttimeAsTime() < self.startTime:
                info['title'] = "< " + info['title']
            if program.endtimeAsTime() > self.endTime:
                info['title'] += " >"
            category = program.category()
        info['start'] = relX
        info['end'] = relX + width
        
        # Create a button for navigation and hilighting. For some reason,
        # button labels don't get truncated properly.
        info['control'] = c = xbmcgui.ControlButton(
            relX + self.guide_x, 
            relY + self.guide_y, 
            width, 
            height, 
            "",      # Text empty on purpose. Label overlay responsible for this
            util.findMediaFile('button-focus.png'), # TODO: Find better focus texture
            #util.findMediaFile( self.getTexture(category, isFocus=True) ),
            util.findMediaFile( self.getTexture(category, isFocus=False) ),
            alignment=(ui.ALIGN_CENTER_Y | ui.ALIGN_TRUNCATED ) )
        self.addControl(c)
        
        # Create a label to hold the name of the program.  Label text seems to
        # get truncated correctly...
        info['label'] = c = xbmcgui.ControlLabel(
            relX + self.guide_x, 
            relY + self.guide_y, 
            width, 
            height,
            info['title'],
            alignment=ui.ALIGN_CENTER_Y | ui.ALIGN_TRUNCATED )
        self.addControl(c)
        
        self.progButtonCtls.append( info )
        mlog.debug( "< addProgramControl()" )
        return c

    def checkPageUp(self, focusControl):
        """
        Method to check and to do a page up in the tv guide.

        Returns:
        - False if no page change was done.
        - True if a page change was done.
        """
        paged = False
        if focusControl in self.topCtls:
            log.debug( "page up detected" )
            paged = True
            if self.startChan == 0:
                # wrap around
                pages = len( self.channels ) // self.channelSpan
                index = len( self.channels ) - (
                    len( self.channels ) % self.channelSpan) - pages
                self.setChannel( index )
            else:
                self.setChannel( self.startChan - (self.channelSpan - 1) )
            self.loadGuide()

            # check if we need to fix focus
            if not self.prevFocus:
                # find the control in the bottom row where previous button's
                # start falls within start/end range of control
                ctls = list( self.progButtonCtls )
                ctls.reverse()
                chanid = ctls[0]['chanid']
                start = self.prevButtonInfo['start']
                for c in ctls:
                    if chanid == c['chanid']:
                        if start >= c['start'] and \
                            start < c['end']:
                            self.prevFocus = c['control']
                            self.setFocus( self.prevFocus )
                            break
                    else:
                        break
        return paged

    def checkPageDown( self, focusControl ):
        """
        Method to check and to do a page down in the tv guide.

        Returns:
        - False if no page change was done.
        - True if a page change was done.
        """
        paged = False
        if focusControl in self.bottomCtls:
            log.debug( "page down detected" )
            paged = True
            if self.endChan == len( self.channels ) - 1:
                # wrap around
                self.setChannel( 0 )
            else:
                self.setChannel( self.startChan + (self.channelSpan - 1) )
            self.loadGuide()

            # check if we need to fix focus
            if not self.prevFocus:
                # find the control in the top row where previous button's start
                # falls within start/end range of control
                chanid = self.progButtonCtls[0]['chanid']
                start = self.prevButtonInfo['start']
                for c in self.progButtonCtls:
                    if chanid == c['chanid']:
                        if start >= c['start'] and \
                            start < c['end']:
                            self.prevFocus = c['control']
                            self.setFocus( self.prevFocus )
                            break
                    else:
                        break
        return paged

    def checkPageLeft( self, focusControl ):
        """
        Method to check and to do a page left in the tv guide.

        Returns:
        - False if no page change was done.
        - True if a page change was done.
        """
        paged = False
        if focusControl in self.leftCtls:
            log.debug( "page left detected" )
            paged = True
            delta = self.hourSpan - 0.5
            startTime = self.startTime - datetime.timedelta( hours=delta )
            self.setTime( startTime )
            self.loadGuide()

            # check if we need to fix focus
            if not self.prevFocus:
                chanid = self.prevButtonInfo['chanid']
                found = False
                prev = None
                # find the right most program on the same channel
                for c in self.progButtonCtls:
                    if not found and c['chanid'] == chanid:
                        found = True
                    elif found and c['chanid'] != chanid:
                        break
                    prev = c
                self.prevFocus = prev['control']
                self.setFocus( self.prevFocus )
                self.prevButtonInfo = None
        return paged

    def checkPageRight( self, focusControl ):
        """
        Method to check and to do a page right in the tv guide.

        Returns:
        - False if no page change was done.
        - True if a page change was done.
        """
        paged = False
        if focusControl in self.rightCtls:
            log.debug( "page right detected" )
            paged = True
            delta = self.hourSpan - 0.5
            startTime = self.startTime + datetime.timedelta( hours=delta )
            self.setTime( startTime )
            self.loadGuide()

            # check if we need to fix focus
            if not self.prevFocus:
                chanid = self.prevButtonInfo['chanid']
                found = False
                prev = None
                ctls = self.progButtonCtls
                ctls.reverse()
                # find the left most program on the same channel
                for c in ctls:
                    if not found and c['chanid'] == chanid:
                        found = True
                    elif found and c['chanid'] != chanid:
                        break
                    prev = c
                self.prevFocus = prev['control']
                self.setFocus( self.prevFocus )
                self.prevButtonInfo = None
        return paged

    def doNavigation( self ):
        """
        Method to do navigation between controls and store lists of top,
        bottom, left, and right controls to detect when page changes must
        occur.
        """
        count = 0
        self.topCtls = []
        self.bottomCtls = []
        self.leftCtls = []
        self.rightCtls = []
        topChanId = None
        prevChanId = None
        prevCtl = None
        #
        # Loop through all buttons doing left to right, right to left, and
        # top to bottom navigation. Also keep track of top, left, and right
        # controls that are used to detect page up, left, and right.
        #
        for c in self.progButtonCtls:
            #log.debug( "title=[%s]"%c['title'] )
            if not topChanId:
                topChanId = c['chanid']
            if c['chanid'] == topChanId:
                # first row of controls are top controls
                self.topCtls.append( c['control'] )
                #log.debug( "top ctl=[%s]"%c['control'] )

            # do left to right and right to left navigation
            if not prevChanId:
                prevChanId = c['chanid']
            elif prevChanId != c['chanid']:
                # changed channel rows so previous control is a control on
                # right edge
                self.rightCtls.append( prevCtl )
                prevCtl = None
                prevChanId = c['chanid']
            if prevCtl:
                prevCtl.controlRight( c['control'] )
                c['control'].controlLeft( prevCtl )
                prevCtl = c['control']
            if not prevCtl:
                # control not set so this must be a control on left edge
                self.leftCtls.append( c['control'] )
                prevCtl = c['control']

            # now find the appropriate control below current one
            chanid = None
            found = False
            for c2 in self.progButtonCtls:
                if not found and c2['control'] == c['control']:
                    found = True
                elif found and not chanid and c2['chanid'] != c['chanid']:
                    chanid = c2['chanid']
                if found and chanid and chanid == c2['chanid']:
                    if c['start'] >= c2['start'] and c['start'] < c2['end']:
                        c['control'].controlDown( c2['control'] )
                        #log.debug( "%s VVV %s"%(c['title'],c2['title']) )
                        count += 1
                        break
                elif found and chanid and chanid != c2['chanid']:
                    break
        log.debug( "down count=%d"%count )
        count = 0
        ctls = list(self.progButtonCtls)
        ctls.reverse()
        bottomChanId = None
        
        #
        # Loop through all buttons in reverse to do bottom to top navigation.
        #
        for c in ctls:
            #log.debug( "title=[%s]"%c['title'] )
            if not bottomChanId:
                bottomChanId = c['chanid']
            if c['chanid'] == bottomChanId:
                # first row of controls are bottom controls
                self.bottomCtls.append( c['control'] )
                #log.debug( "bottom ctl=[%s]"%c['control'] )

            # now find the control that is above the current one
            chanid = None
            found = False
            for c2 in ctls:
                if not found and c2['control'] == c['control']:
                    found = True
                elif found and not chanid and c2['chanid'] != c['chanid']:
                    chanid = c2['chanid']
                if found and chanid and chanid == c2['chanid']:
                    if c['start'] >= c2['start'] and c['start'] < c2['end']:
                        c['control'].controlUp( c2['control'] )
                        #log.debug( "%s ^^^ %s"%(c['title'],c2['title']) )
                        count += 1
                        break
                elif found and chanid and chanid != c2['chanid']:
                    break
        log.debug( "up count=%d"%count )

        # if we have any controls, then the very last control on right edge
        # was missed in first loop (right controls are detected by row changes
        # but the last row quits the loop before detecting the control)
        if len( ctls ) > 0:
            # Note: This grabs last control from the reverse list of controls.
            self.rightCtls.append( ctls[0]['control'] )
        #log.debug( "right ctl=[%s]"%ctls[0]['control'] )

        log.debug("top count    = %d" % len(self.topCtls))
        log.debug("bottom count = %d" % len(self.bottomCtls))
        log.debug("left count   = %d" % len(self.leftCtls))
        log.debug("right count  = %d" % len(self.rightCtls))

    def getTexture(self, category, isFocus):
        """
        Method to figure out name of texture (png file) to use for the passed category.
        """
        # determine color
        if not category:
            color = "shade"
        else:
            if category in self.categoryColors:
                color = self.categoryColors[category]
            else:
                color = "shade"

        # determine alpha value
        if isFocus:
            alpha = "50"
        else:
            alpha = "25"

        # build texture file name
        return "%s_%s.png"%(color,alpha)

    def loadGuide(self):
        """
        Method to load and display the tv guide information.  If this is
        the first time being called, it initializes the tv guide
        parameters.
        """
        mlog.debug('> tvguide.Window.loadGuide()')

        if self.prevFocus:
            for c in self.progButtonCtls:
                if c['control'] == self.prevFocus:
                    self.prevButtonInfo = c
                    self.prevFocus = None
                    break

        if not self.initialized:
            # load variables from skin
            self.channel_x = int(self.getvalue( self.getoption( "channel_x" ) ))
            self.channel_h = int(self.getvalue( self.getoption("channel_h" ) ))
            self.channel_w = int(self.getvalue( self.getoption( "channel_w" ) ))
            self.channel_dx = int(self.getvalue( self.getoption( "channel_dx" )) )
            self.time_y = int(self.getvalue( self.getoption( "time_y" ) ))
            self.time_h = int(self.getvalue( self.getoption( "time_h" ) ))
            self.guide_x = int(self.getvalue( self.getoption( "guide_x" ) ))
            self.guide_y = int(self.getvalue( self.getoption( "guide_y" ) ))
            self.guide_dx = int(self.getvalue( self.getoption( "guide_dx" ) ))
            self.guide_dy = int(self.getvalue( self.getoption( "guide_dy" ) ))
            self.guide_w = int(self.getvalue( self.getoption( "guide_w" ) ))
            self.guide_h = int(self.getvalue( self.getoption( "guide_h" ) ))

            # calculate pixels per hour used repeatedly
            self.widthPerHour = self.guide_w / self.hourSpan 

            # calculate channel span that fits into guide height
            self.channelSpan = int(self.guide_h / (self.guide_dy+self.channel_h) )
            log.debug( "channelSpan=[%d]"%self.channelSpan )

            # allocate the remainder to vertical spacing between channels
            # TODO: Fix gaps betweek rows: 
            #remainder = self.guide_h // (self.guide_dy+self.channel_h)
            remainder = 0
            log.debug('remainder = ' + str(remainder))
            self.guide_dy += (remainder / self.channelSpan)

            # initialize channel range and time range
            self.channels = self.db.getChannels()
            self.setChannel( 0 )
            self.setTime(datetime.datetime.now() - datetime.timedelta( minutes=30 ) )
            self.initialized = True

        self.programs = self.db.getProgramListings(
            self.startTime, self.endTime,
            self.channels[self.startChan].chanid(),
            self.channels[self.endChan].chanid() )
        log.debug("found %d rows" % len(self.programs))

        self.render()

        if not self.prevButtonInfo:
            # set focus to the first control on the screen
            if len( self.progButtonCtls ) > 0:
                self.prevFocus = self.progButtonCtls[0]['control']
                self.setFocus( self.prevFocus )
            else:
                raise Exception, "No program information available."

    def onActionHook(self, action):
        """Method that is called whenever an event occurs in the GUI."""
        mlog.debug("> tvguide.Window.onActionHook( action=[%s] )" % action)
        ctl = self.getFocus()

        actionConsumed = False
        if action == ui.ACTION_MOVE_DOWN:
            actionConsumed = self.checkPageDown( self.prevFocus )
        elif action == ui.ACTION_MOVE_UP:
            actionConsumed =  self.checkPageUp( self.prevFocus )
        elif action == ui.ACTION_MOVE_LEFT:
            actionConsumed = self.checkPageLeft( self.prevFocus )
        elif action == ui.ACTION_MOVE_RIGHT:
            actionConsumed = self.checkPageRight( self.prevFocus )
        if not actionConsumed:
            self.prevFocus = ctl

        log.debug( "< tvguide.Window.onActionHook()" )
        return actionConsumed

    def onControlHook(self, control):
        """Method called when a control is selected/clicked."""
        mlog.debug("> tvguide.Window.onControlHook()")

        try:
            actionConsumed = 1
            xbmcgui.Dialog().ok('Info', 'Scheduling coming soon..')
# TODO: Uncomment once scheduling screens working
#            id = self.getcontrolid( control )
#            program = None
#            for c in self.progButtonCtls:
#                if c['control'] == control:
#                    program = c['program']
#                    break
#            
#            if program:
#                if self.doLiveTV:
#                    log.debug( "launching livetv" )
#                    rc = livetv.showWindow( None, program )
#                else:
#                    log.debug( "converting program to schedule" )
#                    schedule = domain.ScheduleFromProgram( program, self.translator )
#                    log.debug( "launching schedule details window" )
#                    rc = scheduledetails.showWindow( schedule, self.conn, self.db, self.settings, self.translator )
        except Exception, ex:
            log.exception('onControlHook')
            raise ex
        
        log.debug( "< tvguide.Window.onControlHook()" )
        return actionConsumed

    def render(self):
        """
        Method to draw all the dynamic controls that represent the program
        guide information.
        """
        xbmcgui.lock()
        try:
            title = self.translator.get( 107 )
            title += ": %s - %s"%(
                self.startTime.strftime( "%x %X" ),
                self.endTime.strftime( "%x %X" ) )
            self.controls['title'].control.setLabel( title )
            self.renderChannels()
            self.renderTime()
            self.renderPrograms()
            self.doNavigation()
            xbmcgui.unlock()
        except:
            xbmcgui.unlock()
            raise

    def renderChannels(self):
        """Method to draw the channel labels. """
        try:
            for c in self.channelCtls:
                if 'icon' in c:
                    self.removeControl( c['icon'] )
                if 'label' in c:
                    self.removeControl( c['label'] )
                if 'shade' in c:
                    self.removeControl( c['shade'] )
                del c
            self.channelCtls = []

            x = self.channel_x
            y = self.guide_y
            h = (self.guide_h - self.channelSpan * self.guide_dy) / self.channelSpan
            iconW = h
            labelW = self.channel_w - iconW - self.guide_dx
            
            for i in range( self.startChan, self.endChan+1 ):
                c = {}
                
                # create shade image around channel label/icon
                c['shade'] = xbmcgui.ControlImage(x, y, self.channel_w, h, util.findMediaFile("shade_50.png"))
                self.addControl( c['shade'] )

                # create label control
                l = "%s %s"%(self.channels[i].channum(),self.channels[i].callsign())
                c['label'] = xbmcgui.ControlLabel(
                    x+iconW+self.channel_dx, y, labelW, h,
                    l, self.getoption( "channel_font" ),
                    alignment=ui.ALIGN_CENTER_Y )
                self.addControl( c['label'] )
                
                shost = str(self.settings.get( "mythtv_host" ))
                file = ui.picBase + os.sep + 'channels' + os.sep + str(self.channels[i].channum()) + ui.picType
                if not os.path.exists(file):
                    try:
                        file = self.iconCache.findFile( self.channels[i], shost )
                    except:
                        log.debug(" renderChannels: nothing assigned to file")
                    
                log.debug( "file=[%s]"%file )
                if file:
                    # set channel icon
                    c['icon'] = xbmcgui.ControlImage( x, y, iconW, h, file )
                    self.addControl( c['icon'] )

                self.channelCtls.append( c )
                y += h + self.guide_dy
        except:
            log.exception("Failed to render channels")
            raise
        
    def renderPrograms(self):
        """
        Method to draw the program buttons.  This manufactures buttons for
        missing guide data.
        """
        try:
            # clear out old controls
            for c in self.progButtonCtls:
                self.removeControl( c['control'] )
                del c['control']
                self.removeControl( c['label'] )
                del c['label']
            self.progButtonCtls = []

            self.widthPerHour = self.guide_w / self.hourSpan 
            chanH = (self.guide_h-self.channelSpan*self.guide_dy)/self.channelSpan

            # Loop through each channel filling the tv guide area with
            # buttons.
            for i in range( self.startChan, self.endChan+1 ):
                noData = False
                chanX = 0
                chanY = (i-self.startChan) * (chanH + self.guide_dy)
                chanid = self.channels[i].chanid()
            
                # loop until we've filled the row for the channel
                while chanX < self.guide_w:
                    ctlInfo = {}
                    ctlInfo['chanid'] = chanid
                    p = None
                    if not noData:
                        # find the next program for the channel - this assumes
                        # programs are sorted in ascending time order for the channel
                        for prog in self.programs:
                            if prog.chanid() == chanid:
                                p = prog
                                self.programs.remove( prog )
                                break
                    if not p:
                        # no program found - create a no data control for the rest of
                        # the row
                        noData = True
                        w = self.guide_w - chanX
                        self.addProgramControl(
                            program=None, info=ctlInfo,
                            relX=chanX, relY=chanY, width=w, height=chanH )
                        chanX += w
                    else:
                        # found a program but we don't know if it starts at the
                        # current spot in the row for the channel

                        # clamp start time
                        start = p.starttimeAsTime()
                        if start < self.startTime:
                            start = self.startTime

                        # clamp end time
                        end = p.endtimeAsTime()
                        if end > self.endTime:
                            end = self.endTime

                        # calculate x coord and width of label
                        start = start - self.startTime
                        #log.debug( "start=%s"%start )
                        progX = start.seconds / (60.0*60.0) * self.widthPerHour
                        end = end - self.startTime
                        #log.debug( "end=%s"%end )
                        progEndX = end.seconds / (60.0*60.0) * self.widthPerHour
                        progW = progEndX - progX

                        # check if we need no data before control 
                        if progX != chanX:
                            self.addProgramControl(
                                program=None, info=ctlInfo,
                                relX=chanX, relY=chanY,
                                width=(progX - chanX), height=chanH )
                            chanX = progX
                            ctlInfo = {}
                            ctlInfo['chanid'] = chanid

                        # add the control for the program
                        self.addProgramControl(
                            program=p, info=ctlInfo,
                            relX=progX, relY=chanY, width=progW, height=chanH )
                        chanX += progW
        except:
            log.exception("Failed to render programs")
            raise

    def renderTime(self):
        """
        Method to draw the time labels for the tv guide.
        """
        try:
            doInit = False
            if len(self.timeLabelCtls) == 0:
                doInit = True

            numCols = int(self.hourSpan * 2)
            x = self.guide_x
            y = self.time_y
            h = self.time_h
            w = (self.guide_w - numCols * self.guide_dx) / numCols
            t = self.startTime
            lastDay = t.day
            i = 0
            log.debug("numCols=%d guide_w=%d"%(numCols, self.guide_w))
            
            while i < numCols:
                if doInit:
                    log.debug("time label: x=%d y=%d w=%d h=%d"%(x, y, w, h))
                    c = xbmcgui.ControlLabel(x, y, w, h, "", self.getoption("time_font"))
                    self.timeLabelCtls.append(c)
                    self.addControl(c)

                label = None
                if i == 0:
                    label = t.strftime("%a %I:%M%p")
                else:
                    label = t.strftime("%I:%M%p") 
                if t.day != lastDay:
                    label += "+1"
                log.debug("time label = %s" % label)
                
                self.timeLabelCtls[i].setLabel(label)
                t += datetime.timedelta(minutes=30)
                i += 1
                x = x + w + self.guide_dx
                lastDay = t.day
        except:
            log.exception("Failed to render time")
            raise
        
    def setTime(self, startTime):
        """
        Method to change the starting time of the tv guide.  This is used
        to change pages horizontally.
        """
        self.startTime = startTime - datetime.timedelta(
            seconds=startTime.second,
            microseconds=startTime.microsecond )
        min = self.startTime.minute
        if min != 0:
            if min > 30:
                delta = 60 - min
            else:
                delta = 30 - min
            self.startTime = self.startTime + datetime.timedelta( minutes=delta )
        self.endTime = self.startTime + datetime.timedelta( hours=self.hourSpan )
        log.debug( "startTime = %s endTime = %s"%(self.startTime,self.endTime) )
        
    def setChannel(self, chanIndex):
        """
        Method to change the starting channel index of the tv guide.
        This is used to change pages vertically.
        """
        self.startChan = chanIndex
        if self.startChan < 0:
            self.startChan = 0
        self.endChan = self.startChan + self.channelSpan - 1
        if self.endChan > len(self.channels)-1:
            self.endChan = len(self.channels)-1
        log.debug("start channel = %s" % self.channels[self.startChan].channum())
        log.debug("end channel = %s" % self.channels[self.endChan].channum())