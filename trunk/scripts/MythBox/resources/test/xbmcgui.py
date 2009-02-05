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

log = logging.getLogger('mythtv.unittest')

"""
Mock xbmcgui
"""

def lock():
    log.debug('xbmcgui.lock() called')

def unlock():
    log.debug('xbmcgui.unlock() called')

# =============================================================================
class DialogProgress(object):
    """
    Mock progress bar
    """

    def create(self, msg):
        self.canceled = False
        log.debug('DialogProgress::create(' + msg + ')')

    def update(self, percent, msg1, msg2, msg3) : 
        log.debug('DialogProgress::update(' + str(percent) + ', ' + msg1 + ', ' + msg2 + ', ' + msg3 + ')')

    def iscanceled(self):
        log.debug('DialogProgress::iscanceled() : ' + str(self.canceled))
        return self.canceled

    def close(self):
        log.debug('DialogProgress::close()')
        self.canceled = True

# =============================================================================
class Window(object):
    """
    Mock window
    """

    def getWidth(self):
        return 1920

    def getHeight(self):
        return 1080

    def addControl(self, control):
        log.debug('calling window.addControl(%s)' % control)

    def setFocus(self, control):
        log.debug('calling Window.setFocus(%s)' % control)
        
    def doModal(self):
        log.debug('calling Window.doModal()')

# =============================================================================
class WindowDialog(object):
    
    def onAction(self, action):
        """
        This method will recieve all actions that the main program will send
        to this window.
        By default, only the PREVIOUS_MENU action is handled.
        Overwrite this method to let your script handle all actions.
        Don't forget to capture ACTION_PREVIOUS_MENU, else the user can't close this window.
        """
        pass    

# =============================================================================
class Dialog(object):
    pass

    def ok(self, msg1, msg2):
        log.debug('ok(msg1, msg2)')
        
# =============================================================================
class Control( object ):
    
    def __init__(self, type, top, left, width, height):
        log.debug('creating Control...')

    def controlUp(self, control):
        log.debug('caling Control::controlUp()')

    def controlDown(self, control): 
        log.debug('calling Control::controlDown()')

    def controlLeft(self, control):
        log.debug('calling Control::controlLeft()')

    def controlRight(self, control):
        log.debug('calling Control::controlRight()')

# =============================================================================
class ControlLabel(object):
    """
    Mock label
    """

    def __init__(self, top, left, width, height, text, fontStyle = None, fontColor = None,
                 disabledColor = None, alignment = None, hasPath = None):
        log.debug('creating ControlLabel...')

# =============================================================================
class ControlFadeLabel(Control):

    def __init__(self,top, left, width, height, fontStyle, fontColor, alignment):
        log.debug('creating ControlFadeLabel...')

# =============================================================================
class ControlButton(Control):

    def __init__(self,
                 x, y, width, height,
                 label = "",
                 focusTexture = '0xFFFFFFFF', noFocusTexture = '0xFFFFFFFF',
                 textXOffset = 0, textYOffset = 0, alignment = 0, font = 'font13',
                 textColor='0xFFFFFFFF', disabledColor='0x60ffffff'):
        log.debug('creating ControlButton...')

# =============================================================================
class ControlList(Control):

    def __init__(self, top, left, width, height, font = "", itemTextXOffset=1, space=1, itemHeight=20):
        log.debug('creating ControlList...')

# =============================================================================
class ControlImage(Control):

    def __init__(self, x, y, w, h, tx):
        pass

# =============================================================================    
class ControlTextBox(Control):
    
    def __init__(self, x, y, w, h, fnt, tcol):
        pass
    
# =============================================================================    
class ControlCheckMark(Control):
    
    def __init__(self, x, y, w, h, l, checkWidth, checkHeight, alignment, textColor):
        pass

# =============================================================================
class ListItem(object):

 
    def __init__(self, label = "", label2 = "", iconImage = None, thumbnailImage = None):
        """
        Creates a new ListItem.
        label          : [opt] string or unicode - label1 text.
        label2         : [opt] string or unicode - label2 text.
        iconImage      : [opt] string - icon filename.
        thumbnailImage : [opt] string - thumbnail filename.
 
        example:
        - listitem = xbmcgui.ListItem('Casino Royale', '[PG-13]', 'blank-poster.tbn', 'poster.tbn')
        """
        pass

    def addContextMenuItem(self, labelAndActionTuples):
        """
        addContextMenuItem([(label, action,)*]) -- Adds item(s) to the context menu for media lists.
     
        [(label, action,)*] : list - A list of tuples consisting of label and action pairs.
          - label           : string or unicode - item's label.
          - action          : string - any built-in function to perform.
     
        List of functions - http://xbmc.org/wiki/?title=List_of_Built_In_Functions 
     
        example:
          - listitem.addContextMenuItem([('Theater Showtimes', 'XBMC.RunScript(q:\\scripts\\showtimes\\default.py,Iron Man)',)])
        """
        pass

    def getLabel(self):
        """
        getLabel() -- Returns the listitem label.
     
        example:
        - label = self.list.getSelectedItem().getLabel()
        """
        pass 
    
    def getLabel2(self):
        """
        getLabel2() -- Returns the listitem's second label.
     
        example:
            - label2 = self.list.getSelectedItem().getLabel2()
        """
        pass 

    def getProperty(self, key):
        """
        getProperty(key) -- Returns a listitem property as a string, similar to an infolabel.
        key            : string - property name.
     
        *Note, Key is NOT case sensitive.
               You can use the above as keywords for arguments and skip certain optional arguments.
               Once you use a keyword, all following arguments require the keyword.
     
        example:
            - AspectRatio = self.list.getSelectedItem().getProperty('AspectRatio')
        """
        pass 
    
    def isSelected(self):
        """
        isSelected() -- Returns the listitem's selected status.
     
        example:
            - is = self.list.getSelectedItem().isSelected()
        """
        pass

    def select(self, isSelected):
        """
        select(selected) -- Sets the listitem's selected status.
        selected        : bool - True=selected/False=not selected
        example:
        - self.list.getSelectedItem().select(True)
        """
        pass

    def setIconImage(self, icon):
        """
        setIconImage(icon) -- Sets the listitem's icon image.
        icon            : string - image filename.
        example:
        - self.list.getSelectedItem().setIconImage('emailread.png')
        """
        pass

    def setInfo(self, type, infoLabels):
        """
        setInfo(type, infoLabels) -- Sets the listitem's infoLabels.
     
        type           : string - type of media(video/music/pictures).
        infoLabels     : dictionary - pairs of { label: value }.
     
        *Note, To set pictures exif info, prepend 'exif:' to the label. Exif values must be passed
               as strings, separate value pairs with a comma. (eg. {'exif:resolution': '720,480'}
            See CPictureInfoTag::TranslateString in PictureInfoTag.cpp for valid strings.
        You can use the above as keywords for arguments and skip certain optional arguments.
        Once you use a keyword, all following arguments require the keyword.
     
        example:
        - self.list.getSelectedItem().setInfo('video', { 'Genre': 'Comedy' })
        """
        pass

    def setLabel(self, label):
        """
        setLabel(label) -- Sets the listitem's label.
         
        label          : string or unicode - text string.
         
        example:
          - self.list.getSelectedItem().setLabel('Casino Royale')
        """
        pass

    def setLabel2(self, label2):
        """
        setLabel2(label2) -- Sets the listitem's second label.
     
        label2         : string or unicode - text string.
         
        example:
            - self.list.getSelectedItem().setLabel2('[pg-13]')
        """
        pass

    def setProperty(self, key, value):
        """
        setProperty(key, value) -- Sets a listitem property, similar to an infolabel.
     
        key            : string - property name.
        value          : string or unicode - value of property.
         
        *Note, Key is NOT case sensitive.
               You can use the above as keywords for arguments and skip certain optional arguments.
               Once you use a keyword, all following arguments require the keyword.
         
        example:
          - self.list.getSelectedItem().setProperty('AspectRatio', '1.85 : 1')
        """
        pass

    def setThumbnailImage(self, thumb):
        """
        setThumbnailImage(thumb) -- Sets the listitem's thumbnail image.
         
        thumb           : string - image filename.
         
        example:
          - self.list.getSelectedItem().setThumbnailImage('emailread.png')
        """
        pass