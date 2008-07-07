#############################################################################
#
# tvgids
# v0.7 by BaKMaN (msn@digitallyactive.com)
#
# - v0.5 new release
# - v0.7 changed paths
#
# Based on many scripts; lots came from the gamespotplus script by jsd
#
#############################################################################

from string import *
import urllib, re, random, string, os.path
import xbmc, xbmcgui

try: Emulating = xbmcgui.Emulating
except: Emulating = False

ACTION_MOVE_LEFT       =  1
ACTION_MOVE_RIGHT      =  2
ACTION_MOVE_UP         =  3
ACTION_MOVE_DOWN       =  4
ACTION_PAGE_UP         =  5
ACTION_PAGE_DOWN       =  6
ACTION_SELECT_ITEM     =  7
ACTION_HIGHLIGHT_ITEM  =  8
ACTION_PARENT_DIR      =  9
ACTION_PREVIOUS_MENU   = 10
ACTION_SHOW_INFO       = 11
ACTION_PAUSE           = 12
ACTION_STOP            = 13
ACTION_NEXT_ITEM       = 14
ACTION_PREV_ITEM       = 15
ACTION_XBUTTON	       = 18

#############################################################################
# autoscaling values
#############################################################################

HDTV_1080i = 0      #(1920x1080, 16:9, pixels are 1:1)
HDTV_720p = 1       #(1280x720, 16:9, pixels are 1:1)
HDTV_480p_4x3 = 2   #(720x480, 4:3, pixels are 4320:4739)
HDTV_480p_16x9 = 3  #(720x480, 16:9, pixels are 5760:4739)
NTSC_4x3 = 4        #(720x480, 4:3, pixels are 4320:4739)
NTSC_16x9 = 5       #(720x480, 16:9, pixels are 5760:4739)
PAL_4x3 = 6         #(720x576, 4:3, pixels are 128:117)
PAL_16x9 = 7        #(720x576, 16:9, pixels are 512:351)
PAL60_4x3 = 8       #(720x480, 4:3, pixels are 4320:4739)
PAL60_16x9 = 9      #(720x480, 16:9, pixels are 5760:4739)

######################################################################

RootDir = os.getcwd()
if RootDir[-1]==';': RootDir=RootDir[0:-1]
if RootDir[-1]!='\\': RootDir=RootDir+'\\'

imageDir = RootDir + "\\images\\"
constructURL = "http://www.filmtotaal.nl/module.php?section=tvgids&zender="
nuoptv = "http://www.filmtotaal.nl/module.php?section=nuoptv"
# kanalen
zenders = [('1', 'Nederland 1','NED1'), ('2', 'Nederland 2','NED2'), ('3', 'Nederland 3','NED3'), ('4', 'RTL 4','RTL4'), ('5', 'RTL 5','RTL5'), ('6', 'SBS 6','SBS6'), ('7', 'RTL 7','RTL7'), ('28', 'RTL 8','RTL8'), ('8', 'Veronica','Veronica'), ('9', 'NET 5','NET5'), ('10', 'Een','Een'), ('11', 'Ketnet','Ketnet'), ('12', 'Canvas','Canvas'), ('13', 'BBC 1','BBC1'), ('14', 'BBC 2','BBC2'), ('15', 'TMF', 'TMF'), ('16', 'MTV','MTV'), ('17', 'Eurosport','Eurosport'), ('18', 'Cartoon Network','CN'), ('19', 'Discovery Channel','Discovery'), ('20', 'National Geographic','NG'), ('21', 'Animal Planet','AP'), ('22', 'BBCWorld','BBCWorld'), ('23', 'ARD','ARD'), ('24', 'ZDF','ZDF'), ('25', 'Canalplus+ Rood','Canal1'), ('26', 'Canalplus+ Blauw','Canal2'), ('27', 'Nickelodeon','Nickelodeon')]

######################################################################

urldata         = None
urlheaders      = {

    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)',

    'Accept-Language': 'en-us',    

}

######################################################################
    
class zenderItem:
	def __init__(self, name, zender,zenderid):
		self.name = name
		self.zender = zender
		self.zenderid = zenderid

class programmaItem:
	def __init__(self, tijd, titel, zenderid):
		self.tijd = strip(tijd)
		self.titel = strip(titel)
		self.zenderid = strip(zenderid)
######################################################################
		
class MainWindow(xbmcgui.Window):
        def __init__(self):
            if Emulating: xbmcgui.Window.__init__(self)
            if not Emulating:
                self.setCoordinateResolution(PAL_4x3)

            self.bg = xbmcgui.ControlImage(0,0,720,576, imageDir + "background.png")
            self.addControl(self.bg)

            self.tekst = xbmcgui.ControlLabel(273,66,250,30, ": Zenderoverzicht")
            self.addControl(self.tekst)        

            self.info = xbmcgui.ControlImage(50,122,27,26, imageDir + "x.png")
            self.addControl(self.info)
            
            self.infotekst = xbmcgui.ControlLabel(80,124,250,30, "Nu op TV")
            self.addControl(self.infotekst)

            self.loading = xbmcgui.ControlLabel(220, 140,250,30, "Een ogenblik...")
            self.addControl(self.loading)
            self.loading.setVisible(0)
            
            self.programmas = xbmcgui.ControlList(220, 140, 420 , 400,'font14','0xFFDDDDDD')
            self.addControl(self.programmas)
            
            self.zenders = xbmcgui.ControlList(220, 140, 420 , 400,'font14','0xFFDDDDDD')
            self.addControl(self.zenders)
            
            if not Emulating:
                self.zenders.setItemHeight(48)
                self.zenders.setImageDimensions(60,39)
                self.programmas.setItemHeight(48)
                self.programmas.setImageDimensions(60,39)
                
            self.programmaItems = []
            self.zenderItems = []
            self.state = 0

            self.setFocus(self.zenders)
            self.Parsezenders()

        ######################################################################
                
        def onAction(self, action):
                if action == ACTION_PREVIOUS_MENU:
                    self.close()
                elif action == ACTION_PARENT_DIR and self.state == 1:
                    self.state = 0
                    self.programmas.setVisible(0)
                    self.zenders.setVisible(1)
                    self.setFocus(self.zenders)
                elif action == ACTION_XBUTTON and self.state != 3:
                    self.state = 3
                    self.zenders.setVisible(0)
                   
                    self.ParseProgrammas(1)
                elif action == ACTION_XBUTTON and self.state == 3:
                    self.state = 0
                    self.programmas.setVisible(0)
                    self.zenders.setVisible(1)
                    self.Parsezenders()
                    self.setFocus(self.zenders)
                    
                  
                    
        ######################################################################
                        
	def onControl(self, control):
		if control == self.zenders and self.state == 0:
                    self.state = 1
                    self.getkanaal = self.zenderItems[self.zenders.getSelectedPosition()].zenderid
                    self.kanaalName = self.zenderItems[self.zenders.getSelectedPosition()].name
                    self.zenders.setVisible(0)
                    
                    self.ParseProgrammas(self.getkanaal)
                    self.setFocus(self.programmas)
    
                    
        ######################################################################

        def Parsezenders(self):
            self.removeControl(self.info)
            self.tekst.setLabel(": Zenderoverzicht")
            self.infotekst.setLabel("Nu op TV")
            self.addControl(self.info)
            
            self.zendersItems = []
            self.zenders.reset()
                                    
            for item in zenders: 
                tmp = zenderItem(item[1], item[2],item[0])
                self.zenderItems.append(tmp)

            for m in self.zenderItems:
                if not Emulating:
                    thumb = imageDir + "channels\\" + str(m.zender) + ".png"
                    Kanaal = xbmcgui.ListItem("    " + m.name,"" ,"", thumb)
                    self.zenders.addItem(Kanaal)
                else:
                    self.zenders.addItem(m.name)
                    print(m.zender + ' - ' + m.zenderid)
                 
                 
        ######################################################################
                        
        def ParseProgrammas(self, zender):
            self.loading.setVisible(1)
            self.programmas.setVisible(0)
            self.programmaItems = []
            self.programmas.reset()

            if self.state != 3:
                zenderurl =  constructURL + zender
                self.tekst.setLabel(": Zenderoverzicht")
            else:
                zenderurl = nuoptv
                self.tekst.setLabel(": Nu op TV")
                self.removeControl(self.info)
                self.infotekst.setLabel("Per zender")
                self.addControl(self.info)
                
            f = urllib.urlopen(zenderurl,urldata, urlheaders)
            data = f.read()

            f.close()

            # programma's
            result =  re.compile('class=\'fp_weektips_dagkop\'.*?>(.*?)</td>.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>',  re.DOTALL + re.IGNORECASE)
            programmadata = result.findall(data)

            for item in programmadata: 
                tmp = programmaItem(item[0], item[1],item[2])
                self.programmaItems.append(tmp)

            for m in self.programmaItems:
                    thumb = imageDir + "channels\\" + str(m.zenderid) + ".png"
                   
                    Kanaal = xbmcgui.ListItem("  " + m.tijd + ' - ' + m.titel,"" ,"", thumb)
                    self.programmas.addItem(Kanaal)
            self.loading.setVisible(0)
            self.programmas.setVisible(1)
            self.setFocus(self.programmas)

                
        ######################################################################                

win = MainWindow()
win.doModal()
del win
