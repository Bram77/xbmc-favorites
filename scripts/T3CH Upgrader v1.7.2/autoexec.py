# Put this file into Q:\scripts folder to be executed when XBMC starts.
import xbmc

# SILENT = do whole upgrade
# NOTIFY = just inform of new build
# NORMAL = Interactive prompt driven
xbmc.executebuiltin("XBMC.RunScript(Q:\\scripts\\T3CH Upgrader\\default.py, NOTIFY)")
