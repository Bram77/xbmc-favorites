import urllib,urllib2,re,xbmcplugin,xbmcgui
#NINJAVIDEO PLUGIN FOR XBMC 2008.#

def indexcats():
        addDir("1. ANIME","http://www.ninjavideo.net/anime",1,"http://mediaicons.org/Services/GetIcon.ashx?key=57097&format=2&style=0&type=med")
        addDir( "2. MOVIES","http://www.ninjavideo.net/movies",1,"http://mediaicons.org/Services/GetIcon.ashx?key=59368&format=2&style=0&type=med")
        addDir( "3. TV SHOWS","http://www.ninjavideo.net/tvshows",1,"http://mediaicons.org/Services/GetIcon.ashx?key=17875&format=2&style=0&type=med")
        addDir("6. DOCUMENTARIES","http://www.ninjavideo.net/docus",1,"http://www.planetrapido.com/images/shwpnl.4.scr.jpg")
        addDir( "5. CARTOONS","http://www.ninjavideo.net/cartoons",1,"http://mediaicons.org/Services/GetIcon.ashx?key=87684&format=2&style=0&type=med")
        addDir( "7. SPORTS","http://www.ninjavideo.net/sports",1,"http://mediaicons.org/Services/GetIcon.ashx?key=57089&format=2&style=0&type=med")
        addDir( "8. MUSIC","http://www.ninjavideo.net/music",1,"http://mediaicons.org/Services/GetIcon.ashx?key=56724&format=2&style=0&type=med")
        addDir( "4. COMEDY","http://www.ninjavideo.net/comedy",1,"http://mediaicons.org/Services/GetIcon.ashx?key=7527&format=2&style=0&type=med")

      
def shows(url,name):
        
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        clean=re.sub('&amp;','&',link)
        clean1=re.sub("\xe2\x80\x99","'",clean)
        clean2=re.sub('\xc5\xab','u',clean1)
        response.close()
        p=re.compile('<li><a href="(.+?)">(.+?)</a></li>')
        match=p.findall(clean2)
        del match[0:7]
        for url,name in match:
                addDir(name,url,2,"")
                
       
def seasons(url,name):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        clean=re.sub('&amp;','&',link)
        clean1=re.sub("\xe2\x80\x99","'",clean)
        clean2=re.sub('\xc5\xab','u',clean1)
        response.close()
        p=re.compile('\n<div class="video">\n<p>\n(.+?)</p>\n</div>\n\n')
        match=p.findall(clean2)
        p=re.compile('<a href="(.+?)">(.+?)</a>')
        try:
                match2=p.findall(str(match[0]))
                for url,name in match2:
                        addDir(name,url,3,"")
                        
        except IndexError:
                p=re.compile('\n<a href="(.+?)">(.+?)</a>')
                match3=p.findall(clean2)
                del match3[0:8]
                for url,name in match3:
                        addDir(name,url,4,"")
        
        
def episodes(url,name):
        
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        clean=re.sub('&amp;','&',link)
        clean1=re.sub("\xe2\x80\x99","'",clean)
        clean2=re.sub('\xc5\xab','u',clean1)
        response.close()
        p=re.compile('<a href="(.+?)">(.+?)</a>\n<br />')
        match=p.findall(clean2)
        for url,name in match:
                addDir(name,url,4,"")

def vidlinks(url):
        
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        clean=re.sub('&amp;','&',link)
        clean1=re.sub("\xe2\x80\x99","'",clean)
        clean2=re.sub('\xc5\xab','u',clean1)
        response.close()
        p=re.compile('<param name="src" value="(.+?)" />\n<param name=".+?" value="(.+?)" />')
        match=p.findall(clean2)
        for url,name in match:
                addLink(name,url+"?.avi","")
  
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
        print "main category index : "
        indexcats()
        
elif mode==1:
        print "index of shows : "+url
        shows(url,name)
        
elif mode==2:
        print "index of seasons : "+url
        seasons(url,name)
        
elif mode==3:
        print "index of episodes : "+url
        episodes(url,name)
        
elif mode==4:
        print "index of videolinks : "+url
        vidlinks(url)

elif mode==5:
        print "index Alt : "+url
        ALTERNATE(url,name)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
