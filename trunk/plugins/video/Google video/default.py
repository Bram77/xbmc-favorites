import urllib,urllib2,re,sys,xbmcplugin,xbmcgui,socket

#Google Plugin - By Voinage 2008.
#set socket timeout globally in seconds for bad server days.
timeout = 50
socket.setdefaulttimeout(timeout)



def SEARCH():
        
        if xbmcplugin.getSetting("Search Duration : Short") == "true":
                dur="&dur=1"
                SITE(dur)
        elif xbmcplugin.getSetting("Search Duration : Medium") == "true":
                dur="&dur=2"
                SITE(dur)
        elif xbmcplugin.getSetting("Search Duration : Long") == "true":
                dur="&dur=3"
                SITE(dur)
        else:
                dur="&dur="
                SITE(dur)

def SITE(dur):
        
        if xbmcplugin.getSetting("site : GOOGLE") == "true":
                site="+site%3Avideo.google.com"
                GOOGLESEARCH(dur,site)
        elif xbmcplugin.getSetting("site : YOUTUBE") == "true":
                site="+site%3Ayoutube.com"
                GOOGLESEARCH(dur,site)
        elif xbmcplugin.getSetting("site : GUBA") == "true":
                site="+site%3Aguba.com"
                GOOGLESEARCH(dur,site)
        elif xbmcplugin.getSetting("site : YOUKU") == "true":
                site="+site%3Ayouku.com"
                GOOGLESEARCH(dur,site)
        elif xbmcplugin.getSetting("site : TUDOU") == "true":
                site="+site%3Atudou.com"
                GOOGLESEARCH(dur,site)
        elif xbmcplugin.getSetting("site : VEOH") == "true":
                site="+site%3Aveoh.com"
                GOOGLESEARCH(dur,site)
        elif xbmcplugin.getSetting("site : MYSPACE") == "true":
                site="+site%3Amyspace.com"
                GOOGLESEARCH(dur,site)
        elif xbmcplugin.getSetting("site : DAILYMOTION") == "true":
                site="+site%3Adailymotion.com"
                GOOGLESEARCH(dur,site)
        elif xbmcplugin.getSetting("site : TRILULILU") == "true":
                site="+site%3Atrilulilu.ro"
                GOOGLESEARCH(dur,site)
        #elif xbmcplugin.getSetting("Download Video") == "true":
        #        
        else:
                site=""
                GOOGLESEARCH(dur,site)
        
       
def GOOGLESEARCH(dur,site):
        res=[]
        keyb = xbmc.Keyboard('', 'Search Google Video')
        keyb.doModal()
        if (keyb.isConfirmed()):
                search = keyb.getText()
                test=search
                encode=urllib.quote_plus(search)
                encode2=urllib.quote(test)
                req = urllib2.Request('http://video.google.com/videosearch?hl=en&q='+encode+site+'&btnG=Google+Search&lr='+dur+'&so=0&num=100#')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                code=re.sub('&#39;','',link)
                code2=re.sub('&amp;','',code)
                code3=re.sub('&quot;','',code2)
                p=re.compile('<a href="(.+?)" target="_top"><img src="(.+?)"></a></div>\n<div class="rl-thumbnail-rollover" onclick=".+?"></div>\n<div class="favicon" style=".+?"></div>\n<div class=".+?" title=".+?"></div>\n</div>\n<div class="rl-metadata">\n<div class="rl-title" onclick=".+?">\n<a href=".+?" target="_top">\n(.+?)\n</a>')
                match=p.findall(code3)
                for url,thumbnail,name in match:
                        url="http://video.google.com"+url
                        res.append((url,thumbnail,name))
                p=re.compile('<img src="(.+?)"></a></div>\n<div class="rl-thumbnail-rollover" onclick=".+?"></div>\n<div class="favicon" style="display:none;"></div>\n</div>\n<div class="rl-metadata">\n<div class="rl-title" onclick=".+?">\n<a href="(.+?)" target="_top">\n(.+?)\n</a>\n</div>')
                match=p.findall(code3)
                for thumbnail,url,name in match:
                        url="http://video.google.com"+url
                        res.append((url,thumbnail,name))
                for url,thumbnail,name in res:
                        addDir(name,url,2,thumbnail)
                p=re.compile('<a id="main-pagi-next" href="(.+?)">\n')
                nextpage=p.findall(link)
                try:
                        page="http://video.google.com"+nextpage[0]
                        addDir(" NEXT PAGE",page,1,"")
                except IndexError:
                        pass
def INDEX(name,url):

        req=urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        code=re.sub('&#39;','',link)
        code2=re.sub('&amp;','',code)
        code3=re.sub('&quot;','',code2)
        p=re.compile('<a href="(.+?)" target="_top"><img src="(.+?)"></a></div>\n<div class="rl-thumbnail-rollover" onclick=".+?"></div>\n<div class="favicon" style=".+?"></div>\n<div class=".+?" title=".+?"></div>\n</div>\n<div class="rl-metadata">\n<div class="rl-title" onclick=".+?">\n<a href=".+?" target="_top">\n(.+?)\n</a>')
        match=p.findall(code3)
        for url,thumbnail,name in match:
                url="http://video.google.com"+url
                addDir(name,url,2,thumbnail)         
        p=re.compile('<a id="main-pagi-next" href="(.+?)">\n')
        nextpage=p.findall(link)
        try:
                page="http://video.google.com"+nextpage[0]
                addDir(" NEXT PAGE",page,1,"")
        except IndexError:
                pass
        
def VIDEO(name,url):
        if url.find('youtube')>0:
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()        
                p=re.compile('<img class="video-thumbnail" src=".+?/vi/(.+?)/.+?jpg"')
                match=p.findall(link)
                bit=match[0]
                req = urllib2.Request('http://www.youtube.com/watch?v='+bit)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                p=re.compile('"t": "(.+?)"')
                match=p.findall(link)
                for youtube in match:
                        linkage="http://www.youtube.com/get_video?video_id="+bit+"&t="+youtube
                        high="http://www.youtube.com/get_video?video_id="+bit+"&t="+youtube+"&fmt=18"
                        addLink(name+"-YOUTUBE",linkage,"http://www.webtvwire.com/wp-content/uploads/2007/06/youtube.jpg")
                        addLink(name+"-YOUTUBE Hi-def",high,"http://www.webtvwire.com/wp-content/uploads/2007/06/youtube.jpg")
        else:
               req = urllib2.Request(url)
               req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
               response = urllib2.urlopen(req)
               link=response.read()
               response.close()
               p=re.compile('right-click <a href="(.+?)">')
               p=re.compile('.+?videoUrl.+?.+?.+?.+?(.+?)%26sigh')
               match=p.findall(link)
               for url2 in match:
                       GOOG=urllib.unquote(url2)
                       addLink(name,GOOG,"")
        
       
                
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
        SEARCH()
elif mode==1:
        print "PAGE"
        INDEX(name,url)
elif mode==2:
        print "index of : "+url
        VIDEO(name,url)
        
xbmcplugin.endOfDirectory(int(sys.argv[1]))
