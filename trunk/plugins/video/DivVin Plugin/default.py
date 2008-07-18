import urllib2,urllib,re,xbmcplugin,xbmcgui,base64

#DivVin Plugin 2008.

Thumb=[]

def getShows(url,name):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        code=re.sub('#039;','',link)
        code2=re.sub('&s','s',code)
        code3=re.sub('&amp;','&',code2)
        p=re.compile('<span class="grey"><a href="(.+?)">(.+?)</a>')
        match=p.findall(code3)
        for url,name in match:
                res.append((url,name))
        return res


def Vidlinks(url,name):
        res=[]
        req = urllib2.Request("http://www.divvin.com/"+url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('<embed type="video/divx" src="(.+?)"')
        match=p.findall(link)
        for url in match:
                res.append(url)                       
        # Get Flash        
        p=re.compile('file=(.+?)/?OBT_fname')
        match=p.findall(link)
        for url in match:
                res.append(url)
        # Get Thumb
        p=re.compile('<div align="center"><a href="(.+?)" rel="lightbox" title=".+?">')
        match=p.findall(link)
        Tb="http://www.divvin.com/"+match[0]
        Thumb.append(Tb)
        return res

def ogmfile(url,name):
        req = urllib2.Request("http://www.divvin.com/"+url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile("StreamPlugLoadUrl.+?.+?(.+?)\'")
        match=p.findall(link)
        a=match[0]
        url="http://127.0.0.1:64653/streamplug/"+base64.urlsafe_b64encode(a)+'?.ogm'
        pass
        # Get Thumb
        p=re.compile('<div align="center"><a href="(.+?)" rel="lightbox" title=".+?">')
        match=p.findall(link)
        Tb="http://www.divvin.com/"+match[0]
        Thumb.append(Tb)
        return url

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
        thumbnail=Thumb[0]
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
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

def addDirSpecial(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name,iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
        
def showCats():
        addDirSpecial("DIVX MOVIES","http://www.divvin.com/browse.php?type=divx",1,"http://i306.photobucket.com/albums/nn253/voinage/1.png")
        addDirSpecial("FLASH MOVIES","http://www.divvin.com/browse.php?type=flash",1,"http://i306.photobucket.com/albums/nn253/voinage/2.png")
        addDirSpecial("OGM MOVIES","http://www.divvin.com/browse.php?type=ogm",4,"http://i306.photobucket.com/albums/nn253/voinage/3.png")
        
                          
def showShows(url,name):
        shows=getShows(url,name)
        for url,name in shows:
                addDir(name,url,2)

def showogm(url,name):
        shows=getShows(url,name)
        for url,name in shows:
                addDir(name,url,5)
                            
def showvidlink(url,name):
        Vids=Vidlinks(url,name)
        for url in Vids:
                addLink("Watch "+name,url)
                       
def showogmlink(url,name):
        ogm=ogmfile(url,name)
        addLink("Watch "+name,ogm)
        
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
        showCats()
elif mode==1:
        print "index of : "+url
        showShows(url,name)
elif mode==2:
        print "show Page: "+url
        showvidlink(url,name)
elif mode==3:
        print "show Downloads: "+url
        CallDownload(url)
elif mode==4:
        print "show ogm: "+url
        showogm(url,name)
elif mode==5:
        print "show ogm vids: "+url
        showogmlink(url,name)


xbmcplugin.endOfDirectory(int(sys.argv[1]))





       


