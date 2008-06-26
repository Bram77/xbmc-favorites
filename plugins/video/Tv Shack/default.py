import urllib,urllib2,re,xbmcplugin,xbmcgui

################################
#     TV SHACK PLUGIN 2008.    #
#############VOIN###############
Thumb=[]

def shows(url,name):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        clean=re.sub('&eacute;','ea',link)
        clean2=re.sub('&amp;','&',clean)
        clean3=re.sub('&quot;','',clean2)
        clean4=re.sub('&nbsp;<font class=".+?">.+?</font>','',clean3)
        p=re.compile('<a href="(.+?)".+?class=".+?">(.+?)<a class=".+?">.+?</a>')
        match=p.findall(clean4)
        for url,name in match:
                res.append((url,name))
        return res

def seasons(url):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        clean=re.sub('&eacute;','ea',link)
        clean2=re.sub('&amp;','&',clean)
        clean3=re.sub('&quot;','',clean2)
        clean4=re.sub('&nbsp;<font class=".+?">.+?</font>','',clean3)
        p=re.compile('<a href=".+?.+?(.+?)".+?class=".+?">(.+?)<a class=".+?">.+?</a>')
        match=p.findall(clean4)
        for url2,name in match:
                season=url+url2
                res.append((season,name))
                pass
        #get thumb
        p=re.compile('<img src="(.+?)"/>')
        match=p.findall(clean4)
        Tb=match[1]
        Thumb.append(Tb)
        return res

def episodes(url,name):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        clean=re.sub('&eacute;','ea',link)
        clean2=re.sub('&amp;','&',clean)
        clean3=re.sub('&quot;','',clean2)
        clean4=re.sub('&nbsp;<font class=".+?">.+?</font>','',clean3)
        p=re.compile('<a href="(.+?)".+?class=".+?">(.+?)<a class=".+?">.+?</a>')
        match=p.findall(clean4)
        for url,name in match:
                res.append((url,name))
                pass
        #get thumb
        p=re.compile('<img src="(.+?)"/>')
        match=p.findall(clean4)
        Tb=match[1]
        Thumb.append(Tb)
        return res

def searchTVSHACK():
        res=[]
        keyb = xbmc.Keyboard('', 'Search TV Shack')
        keyb.doModal()
        if (keyb.isConfirmed()):
                search = keyb.getText()
                encode=urllib.quote(search)
                req = urllib2.Request('http://tvshack.net/search/'+encode)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                clean=re.sub('&eacute;','ea',link)
                clean2=re.sub('&amp;','&',clean)
                clean3=re.sub('&quot;','',clean2)
                clean4=re.sub('&nbsp;<font class=".+?">.+?</font>','',clean3)
                p=re.compile('<a href="(.+?)".+?class=".+?">(.+?)<a class=".+?">.+?</a>')
                match=p.findall(clean4)
                for url,name in match:
                        res.append((url,name))
                return res

def vidlink(url):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        clean=re.sub('&eacute;','ea',link)
        clean2=re.sub('&amp;','&',clean)
        clean3=re.sub('&quot;','',clean2)
        clean4=re.sub('&nbsp;<font class=".+?">.+?</font>','',clean3)
        p=re.compile(".+?unescape.+?'(.+?)'.+?")
        match=p.findall(clean4)
        for vidlinks in match:
                decode=urllib.unquote(vidlinks)
                res.append(decode)
        return res
            

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

      
def addLink(name,url,thumbnail):
        
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode,thumbnail):
        
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
        
def showCats():
        addDir("1. ANIME","http://tvshack.net/anime",1,"")
        addDir("2. MOVIES","http://tvshack.net/movies",2,"")
        addDir("3. T.V SHOWS","http://tvshack.net/tv_shows",1,"")
        addDir("4. COMEDY","http://tvshack.net/comedy",2,"")
        addDir("5. DOCUMENTARIES","http://tvshack.net/documentaries",2,"")
        addDir("6. MISC","http://tvshack.net/misc",2,"")
        addDir("7. SEARCH TV SHACK","http://tvshack.net/search/",5,"")
               
  
def showallshows(url,name):
        show_index=shows(url,name)
        for url,name in show_index:
                addDir(name,url,3,"")
                
def showallmovies(url,name):
        show_index=shows(url,name)
        for url,name in show_index:
                addDir(name,url,6,"")
                
def showallseasons(url):
        season_index=seasons(url)
        for url,name in season_index:
                addDir(name,url,4,Thumb[0])

def showallepisodes(url,name):
        episode_index=episodes(url,name)
        for url,name in episode_index:
                addDir(name,url,6,Thumb[0])

def search():
        res=[]
        searching=searchTVSHACK()
        for url,name in searching:
                p=name.find("TV Shows / ")
                if p==0:
                        addDir(name,url,3,"")
                else:
                        addDir(name,url,6,"")
                                                                    
def Getvidlinks(url):
        vid=vidlink(url)
        b=0
        for i in vid:
                b=b+1
                addLink("Play Video - Part "+str(b),i,"")               

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
        print "Get All other Show Links : "+url
        showallshows(url,name)
elif mode==2:
        print "Get Movies: "+url
        showallmovies(url,name)
elif mode==3:
        print "Get Seasons: "+url
        showallseasons(url)
elif mode==4:
        print "Get Episodes : "+url
        showallepisodes(url,name)
elif mode==5:
        print "Get Search : "+url
        search()
elif mode==6:
        print "Get Vidlinks  :"+url
        Getvidlinks(url)
        

xbmcplugin.endOfDirectory(int(sys.argv[1]))
