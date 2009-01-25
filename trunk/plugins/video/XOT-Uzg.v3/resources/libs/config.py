#===============================================================================
# LICENSE - CC BY-NC-SA
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-Share Alike 3.0 Unported License. To view a copy 
# of this licence, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ or 
# send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA. 
#===============================================================================

import os, logging

rootDir = os.getcwd().replace(";","")
rootDir = os.path.join(rootDir, '')

cacheDir = os.path.join(rootDir,'cache','')

cacheValidTime = 7*24*3600
webTimeOut = 30

appName = "XOT-Uzg (XOT-Uzg.v3)"
appSkin = "uzg-progwindow.xml"
contextMenuSkin = "uzg-contextmenu.xml"
updaterSkin = "xot-updater.xml"

logLevel = logging.DEBUG
logDual = True
logFileName = "uzg.log"
logFileNamePlugin = "uzgPlugin.log"

xotDbFile = os.path.join(rootDir,"xot.db")

version = "3.2.0b3"
updateUrl = "http://www.rieter.net/uitzendinggemist/index.php?currentversion="

skinFolder = "" #get's set from default.py