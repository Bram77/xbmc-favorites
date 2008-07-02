#much code was taken from voinage's tv shack (and his helpful tips in the forums)
#thanks to nuka1195 & others for help in the forums & irc
#thanks to thor918 for the MyPlayer class.
#thanks to Tim Bormans for opening up the api to me (tv.timbormans.com)

import xbmc,xbmcgui,xbmcplugin,access
import re,urllib,urllib2

#globals:
y=1
dUser=""

class MyPlayer( xbmc.Player ) :
    
    def __init__ ( self ):
        xbmc.Player.__init__( self )
        
    def onPlayBackStarted(self):
        global apiURL
        global genre
        
        xbmc.sleep(2000)
        info=access.getVideoInfo(apiURL)
        url=info[0]
        artist=info[1]
        title=info[2]
        thumb=info[3]
        queueVid(url,artist,title,thumb)

        xbmc.executebuiltin('XBMC.ActivateWindow(fullscreenvideo)')

    def onPlayBackStopped(self):
        global y

        #y=1 # < was working,just wouldn't end loop
        y=0  #untested, should** work and end loop
        

def queueVid(url,artist,title,thumb):
    global genre
    
    playlist = xbmc.PlayList(1)
    listitem = xbmcgui.ListItem(artist+" - "+title, thumbnailImage=thumb)
    listitem.setInfo('video', {'Title': artist+" - "+title, 'Genre': genre+' radio on LastTube'})
    listitem.setProperty('startedBy','LastTube')
    playlist.add(url, listitem)
        
def startPlayback(term):
    global apiURL
    global genre

    mode=int(params["mode"])

    if mode==1:
        apiURL='/user/'+dUser+'/topartists.xml'
        genre=dUser+'\'s'
    if mode==2:
        apiURL='/user/'+term+'/topartists.xml'
        genre=term+'\'s'
    if mode==3:
        apiURL='/artist/'+term+'/similar.xml'
        genre=term+'\'s similar artists'
    if mode==4:
        apiURL='/user/'+term+'/topartists.xml'
        genre=term
    
    info=access.getVideoInfo(apiURL)
    url=info[0]
    artist=info[1]
    title=info[2]
    thumb=info[3]

    objPL=xbmc.PlayList(1)
    objPL.clear()
    queueVid(url,artist,title,thumb)
    p.play(objPL)

def search(title):
    keyb = xbmc.Keyboard('', title)
    keyb.doModal()
    if (keyb.isConfirmed()):
        term = keyb.getText()
        startPlayback(term)

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                  param[splitparams[0]]=splitparams[1]
                            
    return param


def addDir(name,url,mode,thumbnail):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    return ok

def showCats():
    addDir("1. "+dUser+"'s Top Artists","blah",1,"")
    addDir("2. Search by Last.FM User","blah",2,"")
    addDir("3. Search for Similar Artists","blah",3,"")
    addDir("4. Search by Tag","blah",4,"")

def showCatsNoUser():
    addDir("1. Search by Last.FM User","blah",2,"")
    addDir("2. Search for Similar Artists","blah",3,"")
    addDir("3. Search by Tag","blah",4,"")

def getLastFMUserName():
    dUser=xbmc.executehttpapi('GetGuiSetting(3;lastfm.username)')
    p=re.compile('<li>(.*)')
    match=p.findall(dUser)
    for dUser in match:
        return dUser

############ MAIN ###########

p=MyPlayer()
params=get_params()

url=None
name=None
mode=None
apiURL=None
genre=None
dUser=getLastFMUserName()

try:
    url=urllib.unquote_plus(params["url"]) 
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass

if mode==None and dUser=="":
    showCatsNoUser()
elif mode==None or url==None:
    showCats()
elif mode==1:
    startPlayback('')
elif mode==2:
    search('Search by Last.FM User')
elif mode==3:
    search('Search for Similar Artists')
elif mode==4:
    search('Search by Tag')
        
xbmcplugin.endOfDirectory(int(sys.argv[1]))

#keep plugin alive with loop
#this is only necessary so it can auto-queue items
while (y==1):
    xbmc.sleep( 1000 ) # sleeps for one second (thanks Nuka1195)
