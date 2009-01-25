"""
    Plugin for watching Youtube vidoes based on your Last.fm account
"""
#thanks to Tim Bormans for opening up the api to me (tv.timbormans.com)

import xbmc,xbmcgui,xbmcplugin,access
import sys,re,urllib,urllib2

if ( __name__ == "__main__" ):

    class MyPlayer( xbmc.Player ) :
        
        def __init__ ( self ):
            xbmc.Player.__init__( self )
            
        def onPlayBackStarted(self):
            global apiURL
            global genre

            print 'playback started'
            
            #xbmc.executebuiltin('XBMC.ActivateWindow(fullscreenvideo)')

            info=access.getVideoInfo(apiURL)
            url=info[0]
            artist=info[1]
            title=info[2]
            thumb=info[3]
            queueVid(url,artist,title,thumb)

            while (1):
                try:
                    xbmc.sleep(1000)
                    self.getTime()
                except:
                    print 'broke out of loop'
                    self.onPlayBackStarted()
                    objPL=xbmc.PlayList(1)
                    p.play(objPL)
                    break

        def onPlayBackStopped(self):
            sys.modules.clear()

        def onPlayBackEnded(self):
            print "onPlayBackEnded"
            

    def queueVid(url,artist,title,thumb):
        global genre
        
        playlist = xbmc.PlayList(1)
        listitem = xbmcgui.ListItem(artist+" - "+str(title), thumbnailImage=thumb)
        listitem.setInfo('video', {'Title': artist+" - "+str(title), 'Genre': genre+' radio on LastTube'})
        listitem.setProperty('startedBy','LastTube')
        playlist.add(url, listitem)

        print 'item queued'
        #xbmcgui.Dialog().ok('','item got queued')
            
    def startPlayback(term,mode):
        global genre

        dialog = xbmcgui.DialogProgress()

        if mode==1:
            global apiURL
            apiURL='/user/'+term+'/topartists.xml'
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
            
        print "start term",term
        print "start playback apiURL",apiURL
        print "start playback mode",mode
        
        info=access.getVideoInfo(apiURL)
        url=info[0]
        artist=info[1]
        title=info[2]
        thumb=info[3]

        objPL=xbmc.PlayList(1)
        objPL.clear()
        queueVid(url,artist,title,thumb)
        p.play(objPL)

    def search(title, mode):
        keyb = xbmc.Keyboard('', title)
        keyb.doModal()
        if (keyb.isConfirmed()):
            term = keyb.getText()
            startPlayback(term, mode)

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
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def showCatsNoUser():
        addDir("1. Search by Last.FM User","blah",2,"")
        addDir("2. Search for Similar Artists","blah",3,"")
        addDir("3. Search by Tag","blah",4,"")
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getLastFMUserName():
        try:
            dUser=xbmc.executehttpapi('GetGuiSetting(3;lastfm.username)')
            p=re.compile('<li>(.*)')
            match=p.findall(dUser)
            for dUser in match:
                return dUser
        except:
            return ""

    ############ MAIN ###########

    p=MyPlayer()
    params=get_params()

    url=None
    name=None
    mode=None
    apiURL=None
    genre=None
    dUser=getLastFMUserName()
    y=1

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
        startPlayback(dUser,mode)
    elif mode==2:
        search('Search by Last.FM User',mode)
    elif mode==3:
        search('Search for Similar Artists',mode)
    elif mode==4:
        search('Search by Tag',mode)
