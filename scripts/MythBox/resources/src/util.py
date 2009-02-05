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

import ConfigParser
import dircache
import logging
import os
import Queue
import sre
import string
import sys
import time
import xbmc

from decorator import decorator

log = logging.getLogger('mythtv.core')
mlog = logging.getLogger('mythtv.method')
plog = logging.getLogger('mythtv.perf')

# =============================================================================
global __gFileLocations
__gFileLocations = {}

# =============================================================================
#
# Global platform instance
#
__platform = None

def getPlatform():
    global __platform
    if __platform == None:
        if 'win32' in sys.platform:
            __platform = WindowsPlatform()
        elif 'linux' in sys.platform:
            __platform = UnixPlatform()
        elif 'darwin' in sys.platform:
            __platform = UnixPlatform()
        else:
            __platform = UnixPlatform()
    return __platform

#import xbmc
#def get_system_platform():
#    """ 
#    get platform on which xbmc run 
#    """
#    platform = "unknown"
#    if xbmc.getCondVisibility( "system.platform.linux" ):
#        platform = "linux"
#    elif xbmc.getCondVisibility( "system.platform.xbox" ):
#        platform = "xbox"
#    elif xbmc.getCondVisibility( "system.platform.windows" ):
#        platform = "windows"
#    elif xbmc.getCondVisibility( "system.platform.osx" ):
#        platform = "osx"
#    print "Platform: %s"%platform
#    return platform

# =============================================================================

@decorator
def timed(func, *args, **kw):
    """
    Decorator for logging method execution times. 
    Make sure 'mythtv.perf' logger in is set to WARN or lower. 
    Only execution times in excess of 1 second will be logged.
    """
    if plog.isEnabledFor(logging.DEBUG):
        t1 = time.time()
        result = func(*args, **kw)
        t2 = time.time()
        diff = t2 - t1
        if diff > 1:
            plog.warning("TIMER: %s took %s seconds" % (func.__name__, diff))
        return result
    else:
        return func(*args, **kw)

# =============================================================================
def which(program, all=False):
    """emulates unix' "which" command (with one argument only)"""
    
    def is_exe(exe):
        return os.path.exists(exe) and os.access(exe, os.X_OK)

    def full_exes(program):
        for path in os.environ['PATH'].split(os.pathsep):
            log.debug('Checking PATH %s for %s' %(path, program))
            exe = os.path.join(path, program)
            if is_exe(exe):
                yield exe

    ppath, pname = os.path.split(program)
    if ppath:
        if is_exe(program):
            return program
    else:
        paths = full_exes(program)
        if not all:
            try:
                return paths.next()
            except StopIteration:
                return None
        else:
            return list(paths)
    return None

# =============================================================================
def currentMethod(depth = 0):
    return sys._getframe(depth + 1).f_code.co_name

# =============================================================================
def findMediaFile(filename):

    retPath = None
    if filename in __gFileLocations:
        retPath = __gFileLocations[filename];
    else:
        skinDir = getSkinDir()
        filePath = skinDir + "media" + os.sep + filename
        if os.path.exists( filePath ):
            retPath = filePath

        if not retPath:
            filePath = os.getcwd() + os.sep + "skin" + os.sep + \
                "shared" + os.sep + "media" + os.sep + filename
            if os.path.exists( filePath ):
                retPath = filePath

        if retPath:
            globals()['__gFileLocations'][filename] = retPath
    log.debug("findMediaFile(%s) => %s"%(filename, retPath))
    return retPath

# =============================================================================
def findSkinFile( filename, width, height ):
    """
    Function to find the appropriate skin file based on screen resolution.

    Resolution              Directories checked under $SCRIPTHOME/skin/shared
    ======================= =================================================
    1920x1080               1080i, 720p, ntsc16x9, pal16x9, ntsc, pal, shared
    1280x720                720p, ntsc16x9, pal16x9, ntsc, pal, shared
    720x480                 ntsc, pal, shared
    otherwise               pal, ntsc, shared
    """

    # figure out which directories to check
    retDir = None
    if filename in __gFileLocations:
        retDir = __gFileLocations[filename]
    else:
        dirsToCheck = []
        if width == 1920 and height == 1080:
            dirsToCheck = ['1080i', '720p', 'ntsc16x9', 'pal16x9', 'ntsc', 'pal']
        elif width == 1280 and height == 720:
            dirsToCheck = ['720p', 'ntsc16x9', 'pal16x9', 'ntsc', 'pal']
        elif width == 720 and height == 480:
            dirsToCheck = ['ntsc16x9','pal16x9','ntsc', 'pal']
        #elif width == 720 and height == 576:
        else:
            dirsToCheck = ['pal', 'ntsc']

        mainSkinDir = getSkinDir()
        sharedSkinDir = os.getcwd() + os.sep + "skin" + os.sep + "shared" + os.sep

        if mainSkinDir == sharedSkinDir:
            doShared = False
        else:
            doShared = True
            
        # check directories until the file is found once
        # first check 'custom' skins, then 'shared'
        log.debug("Checking %s exists" % mainSkinDir)
        
        if os.path.exists( mainSkinDir ):
            
            for dir in dirsToCheck:
                skinDir = mainSkinDir + dir + os.sep + filename
                
                log.debug("skinDir = %s"%skinDir )
                if os.path.exists( skinDir ):
                    retDir = skinDir
                    break
            
        if not retDir and doShared:
            # have moved all 'shared' skins into similar directory structure
            # so search those directories too
            for dir in dirsToCheck:
                skinDir = sharedSkinDir + dir + os.sep + filename
                log.debug("skinDir = %s"%skinDir )
                if os.path.exists( skinDir ):
                    retDir = skinDir
                    break
        
        if retDir:
            globals()['__gFileLocations'][filename] = retDir
        else:
            raise Exception, "Unable to find skin file '%s' in subdirs of '%s'."%(filename, getSkinDir())
    
    log.debug('findSkinFile(%s, %d, %d) => %s'%(filename, width, height, retDir))
    return retDir

# =============================================================================
def loadFile(fileName, width, height):
    """ 
    Loads skin xml file and resolves embedded #include directives.
    Returns completely loaded file as a string. 
    """
        
    log.debug("loadFile(%s, %d, %d)"%(fileName, width, height ) )
    s = ""
    f = file( fileName )
    for l in f.readlines():
        # log.debug(fileName + ":" + l) 
        m = sre.match( '^#include (.*)$', l )
        if m:
            incFile = m.group(1)
            incFile = incFile.strip()
            if sre.match( '^\w+\.xml$', incFile ):
                # need to find skin file
                incFile = findSkinFile( incFile, width, height )
            elif sre.match( '\%SKINDIR\%', incFile ):
                incFile = string.replace(incFile, "%SKINDIR%", getSkinDir())
            else:
                # convert path separators to proper path separator - just in case
                incFile = string.replace( incFile, "/", os.sep )
                incFile = string.replace( incFile, "\\", os.sep )

                # assume relative path provided
                path = os.path.dirname( fileName )
                path += os.sep + incFile
                incFile = path
            s += loadFile( incFile, width, height )
        else:
            s += l
    f.close()
    return s

# =============================================================================
def loadSkin(skinName, width, height):
    """
    Function to load the specified skin for the specified resolution.  When a
    file is loaded, it is checked for include statements.  An attempt is made
    to resolve all includes until no more includes are left.

    On success, the function returns a string containing the skin XML with all
    include statements resolved.

    On failure, the function returns None.
    """
    fileName = findSkinFile(skinName, width, height)
    skinXml = loadFile(fileName, width, height)
    return skinXml
    
# =============================================================================
def getSkinDir():
    """
    Function to return the path to the skin directory.  This will return
    something like:

    ./skin/Project Mayhem/

    Note: This is different than what xbmc.getSkinDir() returns.
    
    TODO: Write unit test
    """
    global skinDir # TODO: Why global?
    skinDir = os.getcwd() + os.sep + "skin" + os.sep + string.lower(xbmc.getSkinDir()) + os.sep
    try:
        s = os.stat(skinDir)
    except OSError:
        nextSkinDir = os.getcwd() + os.sep + "skin" + os.sep + "shared" + os.sep
        log.warn("MythBox Skin Directory %s NOT found - Using default skindir %s" %(skinDir, nextSkinDir))
        try:
            s = os.stat(nextSkinDir)
        except OSError:
            raise Exception, "Default skindir fallback failed - %s." % nextSkinDir
    return skinDir

# =============================================================================
def initialize():
    """
    Initialize utility module.  Should be called on startup before calling any
    other methods.
    
    TODO: Remove me
    """
    globals()["__gFileLocations"] = {}
    log.info(" ============ MythBox Started ================")

# =============================================================================
class FileCache(object):
    """Cache for files retrieved from a mythbackend"""
    
    def __init__(self, cachePath, numDays=30):
        self.cachePath = cachePath
        self.numDays = numDays
        self._checkOrCreateDir(self.cachePath)
        self._deleteOldFiles(self.cachePath, self.numDays)

    def findFile(self, obj, backendHost):
        """
        Return absolutepath of the cached file for the given (obj, hostname) 
        as a string
        """
        file = self.buildPath(obj) 
        if file and not os.path.exists(file):
            file = self.storeFile(obj, backendHost)
            log.debug('cache MISS for %s' % file)
        else:
            log.debug('cache HIT for %s' % file)
        return file

    def buildPath(self, obj):
        """Subclass should implement"""
        raise NotImplementedError, "Abstract base class"

    def storeFile(self, obj):
        """Subclass should retrieve file to store based on passed in object"""
        raise NotImplementedError, "Abstract base class"

    def _checkOrCreateDir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def _deleteOldFiles(self, path, numDays=120):
        if numDays > 0:
            daysSecs = numDays * (60*60*24)
            t = time.time()
            files = dircache.listdir(path)
            for f in files:
                filePath = path + os.sep + f
                try:
                    s = os.stat(filePath)
                    if s[9] < t - daysSecs:
                        os.remove(filePath)
                        log.debug("deleted file %s from cache"%filePath)
                except OSError:
                    log.exception('_deleteOldFiles')

# =============================================================================
class NativeTranslator(xbmc.Language):
    
    def __init__(self, scriptPath, defaultLanguage=None, *args, **kwargs):
        xbmc.Language.__init__(self, scriptPath, defaultLanguage, *args, **kwargs)
        
    def get(self, id):
        """Alias for getLocalizedString(...)"""
        return self.getLocalizedString(id)

# =============================================================================
class Platform(object):

    def getScriptDir(self):
        """
        Return the directory that this xbmc script resides in.
        
        linux  : $HOME/.xbmc/scripts/MythBox
        windows: TODO
        mac    : TODO
        """
        return os.getcwd()

    def getScriptDataDir(self):
        """
        Return the location of per user settings for this xbmc script.
        
        linux  : $HOME/.xbmc/userdata/script_data/MythBox
        windows: TODO
        mac    : TODO
        """
        return xbmc.translatePath("T:\\script_data") + os.sep + os.path.basename(self.getScriptDir())

    # TODO: Delete me - replaced by 'paths_ffmpeg' setting
    def getFFMpegExecutableName(self):
        raise NotImplementedError('Abstract method')
        
    def __repr__(self):
        bar = "=" * 80
        s = bar + \
"""
platform        = %s 
script dir      = %s
script data dir = %s
ffmpeg exe name = %s
""" % (type(self).__name__, self.getScriptDir(), self.getScriptDataDir(), self.getFFMpegExecutableName())
        s += bar
        return s

# =============================================================================
class UnixPlatform(Platform):

    def getFFMpegExecutableName(self):
        return "ffmpeg"

# =============================================================================
class WindowsPlatform(Platform):

    def getFFMpegExecutableName(self):
        return "ffmpeg.exe"

# =============================================================================
class BoundedEvictingQueue(object):
    """
    Queue with a fixed size that evicts objects in FIFO order when capacity
    has been reached. 
    """

    def __init__(self, size):
        self._queue = Queue.Queue(size)
        
    def empty(self):
        return self._queue.empty()
    
    def qsize(self):
        return self._queue.qsize()
    
    def full(self):
        return self._queue.full()
    
    def put(self, item):
        if self._queue.full():
            self._queue.get()
        self._queue.put(item, False, None)
        
    def get(self):
        return self._queue.get(False, None)
    
# =============================================================================
class OnDemandConfig(object):
    """
    Used by unit tests to query user for values on stdin as they
    are needed (passwords, for example) . Once entered, the value is saved
    to a config file so future invocations can run unattended.  
    """ 
    
    def __init__(self, filename='ondemandconfig.ini', section='default'):
        self.filename = filename
        self.section = section
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.filename)
    
    def get(self, key):
        if not self.config.has_section(self.section):
            self.config.add_section(self.section)
        
        if self.config.has_option(self.section, key):
            value = self.config.get(self.section, key)
        else:
            print "\n==============================="
            print "Enter a value for key %s:" % key
            value = sys.stdin.readline()
            print "Value is stored in %s if you would like to change it later." % self.filename
            print "===============================\n"
            
            value = str(value).strip() # nuke newline
            self.config.set(self.section, key, value)
            inifile = file(self.filename, "w")
            self.config.write(inifile)
            inifile.close()
        return value
