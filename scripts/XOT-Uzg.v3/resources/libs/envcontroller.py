#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

import os, platform, sys

class EnvController:
    def __init__(self):
        """
            Class to determine platform depended stuff
        """
        pass
    
    def GetEnvironment(self, displayOnly = False):
        """
            Get the environment type of the current Python
        """
        #print "os.environ"
        #print platform.architecture()
        env = os.environ.get( "OS", "win32" )
        #print env
        
        if env == "Linux":
            (bits, type) = platform.architecture()
            if bits.count("64") > 0:
                # first the bits of platform.architecture is checked
                return "Linux64"
            elif sys.maxint >> 33:
                # double check using the sys.maxint
                # and see if more than 32 bits are present
                return "Linux64"
            else:
                return "Linux"
        elif env == "OS X":
            return "OS X"
        else: 
            if displayOnly and not env == "win32":
                print "Setting XOT Environment to %s" % env
                return env
            else:
                print "Setting XOT Environment to Win32"
                return "win32"