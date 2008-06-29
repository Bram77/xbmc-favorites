import urllib,urllib2,re,xbmcplugin,xbmcgui,base64,socket
#joox V2008


socket.setdefaulttimeout(30)


def INDEXCATS():
        addDir('ANIME','http://joox.net/cat/3',1,'')
        addDir('BOLLYWOOD','http://joox.net/cat/142',1,'')
        addDir('CARTOONS','http://joox.net/cat/112',1,'')
        addDir('DOCUMENTARIES','http://joox.net/cat/44',1,'')
        addDir('MOVIES','http://joox.net/cat/2',4,'')
        addDir('STAND-UP','http://joox.net/cat/137',1,'')
        addDir('TV-SHOWS','http://joox.net/cat/1',1,'')
        addDir('FOREIGN','http://joox.net/cat/33',1,'')
       
def INDEX(url):
        try:
                f=urllib.urlopen(url)
                a=f.read()
                code=re.sub('" style="color:white;','',a)
                f.close()
                p=re.compile('          <a href=".+?(.+?)">(.+?)</a><br />')
                match=p.findall(code)
                for url,name in match:
                        addDir(name,"http://joox.net"+url,2,"")
        except IOError:
                f=urllib.urlopen(url)
                a=f.read()
                code=re.sub('" style="color:white;','',a)
                f.close()
                p=re.compile('          <a href=".+?(.+?)">(.+?)</a><br />')
                match=p.findall(code)
                for url,name in match:
                        addDir(name,"http://joox.net"+url,2,"")
                
def INDEX2(url):
        try:
                f=urllib.urlopen(url)
                a=f.read()
                code=re.sub('" style="color:white;','',a)
                f.close()
                p=re.compile('          <a href=".+?(.+?)">(.+?)</a><br />')
                match=p.findall(code)
                for url,name in match:
                        addDir(name,"http://joox.net"+url,5,"")
        except IOError:
                f=urllib.urlopen(url)
                a=f.read()
                code=re.sub('" style="color:white;','',a)
                f.close()
                p=re.compile('          <a href=".+?(.+?)">(.+?)</a><br />')
                match=p.findall(code)
                for url,name in match:
                        addDir(name,"http://joox.net"+url,5,"")
        
                
def EPISODES(url):
        try:
                f=urllib.urlopen(url)
                a=f.read()
                code=re.sub('" style="color:white;','',a)
                f.close()
                p=re.compile('<img src="pages/.+?i=(.+?)" alt="" /></div>')
                match=p.findall(code)
                if len(match)>0:
                        thumb=urllib.unquote(match[0])
                else:
                        thumb=""
                p=re.compile('          <a href=".+?(.+?)">(.+?)</a><br />')
                match=p.findall(code)
                for url,name in match:
                        addDir(name,"http://joox.net"+url,5,thumb)
        except IOError:
                f=urllib.urlopen(url)
                a=f.read()
                code=re.sub('" style="color:white;','',a)
                f.close()
                p=re.compile('<img src="pages/.+?i=(.+?)" alt="" /></div>')
                match=p.findall(code)
                if len(match)>0:
                        thumb=urllib.unquote(match[0])
                else:
                        thumb=""
                p=re.compile('          <a href=".+?(.+?)">(.+?)</a><br />')
                match=p.findall(code)
                for url,name in match:
                        addDir(name,"http://joox.net"+url,5,thumb)

def PARTS(url):
        try:
                f=urllib.urlopen(url)
                a=f.read()
                f.close()
                p=re.compile('<img src="pages/.+?i=(.+?)" alt="" /></div>')
                match=p.findall(a)
                if len(match)>0:
                        thumb=urllib.unquote(match[0])
                else:
                        thumb=""
                p=re.compile('\n\n                (.+?) <br /><br />\n')
                match=p.findall(a)
                p=re.compile('<a href="(.+?)">(.+?)</a>')
                parts=p.findall(match[0])
                for url,name in parts:
                        addDir(name,"http://joox.net"+url,3,thumb)
        except IOError:
                f=urllib.urlopen(url)
                a=f.read()
                f.close()
                p=re.compile('<img src="pages/.+?i=(.+?)" alt="" /></div>')
                match=p.findall(a)
                if len(match)>0:
                        thumb=urllib.unquote(match[0])
                else:
                        thumb=""
                p=re.compile('\n\n                (.+?) <br /><br />\n')
                match=p.findall(a)
                p=re.compile('<a href="(.+?)">(.+?)</a>')
                parts=p.findall(match[0])
                for url,name in parts:
                        addDir(name,"http://joox.net"+url,3,thumb)
                
       

def VIDEOLINK(url):
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        p=re.compile('<a href="(.+?)">Download this video</a>')
        match=p.findall(a)
        for url in match:
                if url.find('messagefromme')>0:
                        url="http://127.0.0.1:64653/streamplug/"+base64.urlsafe_b64encode(url)+'?.ogm'
                        addLink("WATCH STREAMPLUG - Play with DvD player & run Veohproxy",url,"")
                elif url.find('fliqz')>0:
                        addLink("WATCH FLIQZ",url+"?.flv","")
                elif url.find('beta.vreel.net')>0:
                        f=urllib.urlopen(url)
                        a=f.read()
                        f.close()
                        p=re.compile('<param name="src" value="(.+?)" />')
                        match=p.findall(a)
                        for url in match:
                                addLink("VREEL",url,"")
                elif url.find('torrent')>0:
                        addLink("OTHER",url+"?.avi","")
                elif url.find('vreel-')>0:
                        addLink("VREEL",url,"")
                else:
                        addLink("WATCH VIDEO","http://joox.net"+url+"?.avi","")
                        

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

def addLink(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok


def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
        
              
params=get_params()
url=None
name=None
mode=None
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
print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
if mode==None or url==None or len(url)<1:
        print "CATEGORY INDEX : "
        INDEXCATS()
elif mode==1:
        print "GET INDEX OF PAGE : "+url
        INDEX(url)
elif mode==2:
        print "GET INDEX OF PAGE : "+url
        EPISODES(url)
elif mode==3:
        print "GET INDEX OF PAGE : "+url
        VIDEOLINK(url)
elif mode==4:
        print "GET INDEX OF PAGE : "+url
        INDEX2(url)
elif mode==5:
        print "GET INDEX OF PAGE : "+url
        PARTS(url)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
