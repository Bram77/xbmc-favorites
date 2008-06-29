import urllib,urllib2,re,sys,xbmcplugin,xbmcgui,socket

#Grab that music Plugin - By Voinage 2008.

def INDEX():
        res=[]
        keyb = xbmc.Keyboard('', 'ENTER YOUR SONG TITLE OR ARTIST NAME')
        keyb.doModal()
        if (keyb.isConfirmed()):
                search = keyb.getText()
                encode=urllib.quote_plus(search)                
                req = urllib2.Request('http://grabthatmusic.com/index.php?q='+encode+'&page=1&')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                p=re.compile('<h2>Artist: <span>(.+?)</span></h2>\n\t\t\t\t<h2>Title: <span>(.+?)</span></h2>\n\t\t\t\t<h2><span style="color: #239841;"><a style="color: #239841;" title="(.+?)">')
                match=p.findall(link)
                for artist,song,mp3 in match:
                        mp3=re.sub(' ','%20',mp3)
                        addLink(artist+" "+song,mp3)
                next='http://grabthatmusic.com/index.php?q='+encode+'&page=1&'
                p=re.compile('http://grabthatmusic.+?/index.+?q=(.+?)&page=(.+?)&')
                match2=p.findall(next)
                for code,page in match2:
                        url="http://grabthatmusic.com/index.php?q="+code+"&"+"page="+str(int(page)+1)+"&"
                        addDir('   NEXT PAGE',url,1)
                
def INDEX2(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('<h2>Artist: <span>(.+?)</span></h2>\n\t\t\t\t<h2>Title: <span>(.+?)</span></h2>\n\t\t\t\t<h2><span style="color: #239841;"><a style="color: #239841;" title="(.+?)">')
        match=p.findall(link)
        for artist,song,mp3 in match:
                mp3=re.sub(' ','%20',mp3)
                addLink(artist+" "+song,mp3)
        p=re.compile('http://grabthatmusic.+?/index.+?q=(.+?)&page=(.+?)&')
        match2=p.findall(url)
        for code,page in match2:
                next="http://grabthatmusic.com/index.php?q="+code+"&"+"page="+str(int(page)+1)+"&"
                addDir('   NEXT PAGE',next,1)

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

      
def addLink(name,url):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png")
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name)
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
        print "categories"
        INDEX()
elif mode==1:
        print "index of : "+url
        INDEX2(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
