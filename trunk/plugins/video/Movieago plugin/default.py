import urllib,urllib2,re,xbmcplugin,xbmcgui

#Movieago.com plugin 2008
Thumb=[]

def Programmeindex(url,name):
        res=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        p=re.compile('<a href="(.+?)"><img title="Video Info::<table><tr><td width=.+?.+?.+? valign=.+?.+?.+?>.+?</td><td width=.+?.+?.+?  valign=.+?.+?.+?>:</td><td width=.+?.+?.+?>(.+?)</td>')
        match=p.findall(a)
        for url,name in match:
                res.append((url,name))
        return res

def Vidlinks(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('file=(.+?)&')
        match=p.findall(link)
        cache=match[0]
        req = urllib2.Request(cache)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link2=response.read()
        response.close()
        clean=re.sub('&amp;','&',link2)
        p=re.compile('\r\n<location>(.+?)</location>\r\n<image>.+?</image>\r\n')
        match=p.findall(clean)
        for vidlink in match:
                pass
        #Get another version.
        p=re.compile('\n<location>(.+?)</location>\n<image>.+?</image>')
        match=p.findall(clean)
        for vidlink in match:
                pass
        #Get thumbs
        try:
                p=re.compile('\r\n<location>.+?</location>\r\n<image>(.+?)</image>\r\n')
                match=p.findall(clean)
                Tb=match[0]
                Thumb.append(Tb)
                return vidlink
        
        except IndexError:
                
                p=re.compile('\n<location>.+?</location>\n<image>(.+?)</image>')
                match=p.findall(clean)
                Tb=match[0]
                Thumb.append(Tb)
                return vidlink
        
        

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
        thumb=Thumb[0]
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumb)
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
        
def showCats():
        addDir("ACTION","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,1/",1)
        addDir("ANIMATION","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,12/",1)
        addDir("ANIME","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,9/",1)
        addDir("CLASSIC MOVIES","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,23/",1)
        addDir("COMEDY","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,2/",1)
        addDir("DOCUMENTARY","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,10/",1)
        addDir("DRAMA","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,4/",1)
        addDir("FAMILY","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,11/",1)
        addDir("FANTASY","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,5/",1)
        addDir("HORROR","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,3/",1)
        addDir("MISC MOVIES","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,6/",1)
        addDir("MUSIC VIDEOS","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,14/",1)
        addDir("SPORTS","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,7/",1)
        addDir("STAND-UP COMEDY","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,16/",1)
        addDir("THRILLER","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,15/",1)
        addDir("TV-SHOWS","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,8/",1)
        addDir("VIDEO CLIPS","http://www.movieago.com/component/option,com_seyret/Itemid,26/catid,13/",1)

def showtvcats():
        addDir("ACTION  / ADVENTURE","http://www.movieago.com/content/category/6/40/61/",1)
        addDir("ANIMATION","http://www.movieago.com/content/category/6/41/63/",1)
      
def showShows(url,name):
        shows=Programmeindex(url,name)
        for url,name in shows:
                addDir(name,url,2)
                            
def Videolinks(url):
        Vids=Vidlinks(url)
        addLink("Watch Video",Vids)
                

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
        print "show link to video: "+url
        Videolinks(url)
elif mode==3:
        print "Tv cats: "+url
        showtvcats()
xbmcplugin.endOfDirectory(int(sys.argv[1]))
