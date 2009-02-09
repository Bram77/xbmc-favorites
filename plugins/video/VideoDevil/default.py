import xbmc, xbmcgui
import sys, os, re
import urllib, urllib2

__plugin__ = 'VideoDevil'
__author__ = 'sfaxman'
__url__ = 'http://code.google.com/p/xbmc-addons/'
__svn_url__ = 'http://xbmc-addons.googlecode.com/svn/trunk/plugins/video/VideoDevil/'
__credits__ = 'sfaxman'
__version__ = '1.4'

rootDir = os.getcwd()
if rootDir[-1] == ';':rootDir = rootDir[0:-1]

class Main:
    def __init__(self):
        self.pDialog = None
        self.curr_file = ''
        self.run()

    def updateDirectory(self, url, dir):
        opener = urllib2.build_opener()
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        urlfile = opener.open(req)
        fc = urlfile.read()
        resvn = re.compile(r'<li><a href="([^"]+)', re.IGNORECASE + re.DOTALL + re.MULTILINE)
        self.pDialog = xbmcgui.DialogProgress()
        self.pDialog.create('VideoDevil - ' + xbmc.getLocalizedString(30059), '', xbmc.getLocalizedString(30051))
        for name in resvn.findall(fc):
            if name != '../' and name != 'default.py' and name != 'dummy':
                new_url = url + name.replace(' ', '%20')
                if name.endswith('/'):
                    new_url = url + name.replace(' ', '%20')
                    new_dir = os.path.join(dir, name)
                    if not os.path.exists(new_dir):
                        os.mkdir(new_dir)
                    if self.updateDirectory(new_url, new_dir) == -1:
                        self.pDialog.close()
                        return -1
                else:
                    new_url = url + name.replace(' ', '%20')
                    if name == 'default.py':
                        new_path = os.path.join(cacheDir, name)
                    else:
                        new_path = os.path.join(dir, name)
                    self.curr_file = name
                    try:
                        urllib.urlretrieve(new_url, new_path, self.file_report_hook)
                    except:
                        traceback.print_exc(file = sys.stdout)
                        self.pDialog.close()
                        dialog = xbmcgui.Dialog()
                        dialog.ok('VideoDevil Error', name)
                        return -1
        self.pDialog.close()
        return 0

    def file_report_hook(self, count, blocksize, totalsize):
        percent = int(float(count * blocksize * 100) / totalsize)
        self.pDialog.update(percent, self.curr_file, xbmc.getLocalizedString(30051))
        if (self.pDialog.iscanceled()):
            raise

    def run(self):
        if len(sys.argv[2]) > 2 and sys.argv[2][5:] == 'update':
            if self.updateDirectory(__svn_url__, rootDir) == 0:
                dialog = xbmcgui.Dialog()
                dialog.ok('VideoDevil', xbmc.getLocalizedString(30060))
            xbmc.executebuiltin('Container.Refresh')
        else:
            import videodevil
            videodevil.Main()
            #sys.modules.clear()

win = Main()
