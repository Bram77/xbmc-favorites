# -*- coding: cp1252 -*-
#===============================================================================
# UitzendingGemist v2.0
# 
# Continuation of a script by BaKMaN ((http://xbox.readrss.com). Basic idea and part of the scripting credits go to him. 
# This version is now working with the current verion of www.uitzendinggemist.nl. 
# 
# Here is the changelog v1.2 to v2.0
# - fixed: now again working with www.uitzendinggemist.nl
# - fixed: working ASF streams
# - added: support for multiple episodes of a programm
# - changed: split window-class into to parts: program-window and episode-window
# - added: new background
# - changed: layout
# - fixed: display most recent programms, instead of the first in alphabetical ranking
# 
# Know limitations:
# - due to the listing on www.uitzendinggemist.nl not all programms are listed. Just the most recent ones.
# 
# History:
# *** Uitzendinggemist*** version 1.0 by BaKMaN
# - Born out of Dutchstream, more working streams though.
# - Many high quality streams (500k+) from www.omroep.nl
# - Shows which are broadcasted on Dutch TV station Nederland 1, 2 and 3
# - including Kopspijkers, Radar, Kassa, Nova, Zembla, many, many more...
# - 29-10-2006 v1.2 Cookie handling added, streams working again.# Based on many scripts; lots came from the gamespotplus script by jsd
#===============================================================================

import os.path
import sys, traceback
import xbmcgui
sys.path.append(os.path.join(os.getcwd().replace(";",""),'libs'))
#sys.path.insert(1, os.path.join(os.getcwd().replace(";",""),'libs'))

#===============================================================================
# Handles an AttributeError during intialization
#===============================================================================
def HandleInitAttributeError(loadedModules):
    if(globalLogFile != None):
        globalLogFile.critical("AtrributeError during intialization", exc_info=True)
        if ("config" in loadedModules):
            globalLogFile.debug("'config' was imported from %s", config.__file__)
        if ("logger" in loadedModules):
            globalLogFile.debug("'logger' was imported from %s", logger.__file__)
        if ("uriopener" in loadedModules):
            globalLogFile.debug("'uriopener' was imported from %s", uriopener.__file__)
        if ("common" in loadedModules):
            globalLogFile.debug("'common' was imported from %s", common.__file__)
        if ("update" in loadedModules):
            globalLogFile.debug("'update' was imported from %s", update.__file__)
    else:
        traceback.print_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        if ("config" in loadedModules):
            print("'config' was imported from %s" % config.__file__)
        if ("logger" in loadedModules):
            print("'logger' was imported from %s" % logger.__file__)
        if ("uriopener" in loadedModules):
            print("'uriopener' was imported from %s" % uriopener.__file__)
        if ("common" in loadedModules):
            print("'common' was imported from %s" % common.__file__)
        if ("update" in loadedModules):
            print("'update' was imported from %s" % update.__file__)   
    return  

#===============================================================================
# Here the script starts
#===============================================================================
# Check for function: Plugin or Script
if hasattr(sys, "argv") and len(sys.argv) > 1:
    #===============================================================================
    # PLUGIN: Import XOT stuff
    #===============================================================================
    try:
        import config
        import logger
        globalLogFile = logger.Customlogger(os.path.join(config.rootDir, config.logFileNamePlugin), config.logLevel, config.logDual, append=True)
        import uriopener
        globalUriHandler = uriopener.UriHandler()
        import common
        config.skinFolder = common.GetSkinFolder()
        import plugin
        tmp = plugin.XotPlugin()    
    except AttributeError:
        HandleInitAttributeError(dir())
    except:
        #globalLogFile.critical("Error initializing %s plugin", config.appName, exc_info=True)
        try:
            orgEx = sys.exc_info()
            globalLogFile.critical("Error initializing %s plugin", config.appName, exc_info=True)
        except:
            print "Exception during the initialisation of the script. No logging information was present because the logger was not loaded."
            traceback.print_exception(orgEx[0], orgEx[1], orgEx[2])       
else:
    #===============================================================================
    # SCRIPT: Setup the script
    #===============================================================================
    try:
        pb = xbmcgui.DialogProgress()
        import config
        pb.create("Initialising %s" % (config.appName), "Importing configuration")
        
        pb.update(10,"Initialising Logger")
        import logger
        globalLogFile = None
        globalLogFile = logger.Customlogger(os.path.join(config.rootDir, config.logFileName), config.logLevel, config.logDual)
        
        pb.update(25,"Initialising UriHandler")
        import uriopener
        globalUriHandler = uriopener.UriHandler()
        
        pb.update(30,"Importing common libraries")
        import common
        common.DirectoryPrinter(config.rootDir)
        
        pb.update(40,"Determining SkinFolder")
        config.skinFolder = common.GetSkinFolder()        
        
        globalLogFile.info("************** Starting %s version v%s **************", config.appName, config.version)
        globalLogFile.info("Skinfolder = %s", config.skinFolder)
        print("************** Starting %s version v%s **************" % (config.appName, config.version))
        
        #check for updates
        pb.update(50,"Checking for updates")
        import update
        try:
            #pass
            update.CheckVersion(config.version, config.updateUrl)
        except:
            globalLogFile.critical("Error checking for updates", exc_info=True)
        
        pb.update(60,"Checking for Cache folder")
        #check for cache folder. If not present. Create it!
        if os.path.exists(config.cacheDir)!=True:
             os.mkdir(config.cacheDir)
        
        pb.update(80, "Cleaning up Cachefolder")
        #cleanup the cachefolder
        common.CacheCleanUp()
        
        pb.close()
        
        #===============================================================================
        # Now starting the real app
        #===============================================================================
        if not pb.iscanceled():
            import progwindow
            
            MyWindow = progwindow.GUI(config.appSkin ,config.rootDir, config.skinFolder)
            MyWindow.doModal()
            del MyWindow
    
    except AttributeError:
        HandleInitAttributeError(dir())        
    except:
        try:
            orgEx = sys.exc_info()
            globalLogFile.critical("Error initializing %s script", config.appName, exc_info=True)
        except:
            print "Exception during the initialisation of the script. No logging information was present because the logger was not loaded."
            traceback.print_exception(orgEx[0], orgEx[1], orgEx[2])            
        pb.close()
        
        
