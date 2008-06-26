import urllib,urllib2,re,sys,xbmcplugin,xbmcgui,socket

#Google Plugin - By Voinage 2008.
#set socket timeout globally in seconds for bad server days.
timeout = 50
socket.setdefaulttimeout(timeout)



def SEARCH():
        
        if xbmcplugin.getSetting("Search Duration : Short") == "true":
                dur="&dur=1"
                (dur)
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
                req = urllib2.Request('http://video.google.com/videosearch?hl=en&q='+encode+''+site+'&btnG=Google+Search&lr='+dur+'&so=0&num=100#')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                code=re.sub('&#39;','',link)
                code2=re.sub('&amp;','',code)
                code3=re.sub('&quot;','',code2)
                p=re.compile('<a href="(.+?)" target="_top"><img src="(.+?)"></a></div>\n<div class="rl-thumbnail-rollover" onclick=".+?"></div>\n<img class="favicon" style="display:none;"></img>\n</div>\n<div class="rl-metadata">\n<div class="rl-title" onclick=".+?">\n<a href=".+?" target="_top">\n(.+?)\n</a>\n</div>')
                match=p.findall(code3)
                for url,thumbnail,name in match:
                        url="http://video.google.com"+url
                        res.append((url,thumbnail,name))
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
        p=re.compile('<a href="(.+?)" target="_top"><img src="(.+?)"></a></div>\n<div class="rl-thumbnail-rollover" onclick=".+?"></div>\n<img class="favicon" style="display:none;"></img>\n</div>\n<div class="rl-metadata">\n<div class="rl-title" onclick=".+?">\n<a href=".+?" target="_top">\n(.+?)\n</a>\n</div>')
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
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('<div class="original-text">\n<a href="(.+?)">')
        match=p.findall(link)
        for videolink in match:
                pass
                if videolink.find('guba.com')>0:
                        req = urllib2.Request(videolink)
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                        response = urllib2.urlopen(req)
                        link=response.read()
                        response.close()
                        p=re.compile('null, null, null,\r\n.+"(.+?)" ')
                        match=p.findall(link)
                        for guba in match:
                                addLink("FLV Format",guba,"http://www.last100.com/wp-content/uploads/2007/09/guba_logo.png")
                        #GET ORIGINAL FORMAT
                        p=re.compile('\r\n <option value="(.+?)">(.+?)</option>')
                        match=p.findall(link)
                        for url2,name in match:
                                addLink(name,url2,"http://www.last100.com/wp-content/uploads/2007/09/guba_logo.png")
                if videolink.find('youtube.com')>0:
                        code=re.sub('http://www.youtube.com/.+?v=','',videolink)
                        code2=re.sub('&hl=en','',code)
                        req = urllib2.Request(videolink)
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                        response = urllib2.urlopen(req)
                        link=response.read()
                        response.close()
                        p=re.compile('"t": "(.+?)"')
                        match=p.findall(link)
                        for youtube in match:
                                linkage="http://www.youtube.com/get_video?video_id="+code2+"&t="+youtube
                                #H264="http://www.youtube.com/get_video?video_id="+code2+"&fmt=18"+"&t="+youtube+"?.avi"
                                addLink(name+"-YOUTUBE",linkage,"http://www.webtvwire.com/wp-content/uploads/2007/06/youtube.jpg")
                                #addLink(name+"-YOUTUBE H264 High Def",H264,"http://www.webtvwire.com/wp-content/uploads/2007/06/youtube.jpg")
                if videolink.find('veoh.com')>0:
                        res=[]
                        req = urllib2.Request(videolink)
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                        response = urllib2.urlopen(req)
                        link=response.read()
                        response.close()
                        try:
                                p=re.compile('<input type="hidden" name="ad_videoPermalink" value="(.+?)" id="ad_videoPermalink" />')
                                match=p.findall(link)
                                for veoh in match:
                                        veohurl="http://127.0.0.1:64652/"+veoh+"?.avi"
                                        res.append(veohurl)
                                p=re.compile('<a href="http://www.veoh.com/videos/(.+?).?confirmed=1"')
                                match=p.findall(link)
                                for veoh in match:
                                        veohurl="http://127.0.0.1:64652/"+veoh+"?.avi"
                                        res.append(veohurl)
                                for veoh2 in res:
                                        addLink(name+"- VEOH AVI",veoh2,"http://www.seanborg.com/images/Veoh%20Logo.jpg")
            
                        except:
                                pass
                if videolink.find('tudou.com')>0:
                        req = urllib2.Request(videolink)
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                        response = urllib2.urlopen(req)
                        link=response.read()
                        response.close()
                        p=re.compile('<div class="shareButton"><a href=".+?iid=(.+?)" target="_blank">')
                        match=p.findall(link)
                        for code in match:
                                pass
                        i=0
                        url2="http://www.tudou.com/player/v2.php?id="+code
                        req = urllib2.Request(url2)
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                        response = urllib2.urlopen(req)
                        link=response.read()
                        response.close()
                        p=re.compile("<f w='.+?'>(.+?)</f>")
                        match=p.findall(link)
                        for linkage in match:
                                i=i+1
                                addLink(name+"- TUDOU-server "+str(i),linkage,"http://www.ojointernet.com/wp-content/uploads/tudou_logo.png")
                if videolink.find('youku.com')>0:
                        res=[]
                        DECODE='http://clipnabber.com/gethint.php'
                        data = "mode=1&url="+videolink
                        req = urllib2.Request(DECODE,data)
                        response = urllib2.urlopen(req)
                        results = response.read()
                        p=re.compile('<a href=(.+?)><strong>(.+?)</strong></a>&nbsp;&nbsp;&nbsp;')
                        final=p.findall(results)
                        for youku,name2 in final:
                                res.append((youku,name2))
                        for youku1,name3 in res:
                                addLink(name3+"- YOUKU ( Play with DVD Player )",youku1,"http://www.21314.cn/images/logo_youku.gif")
                if videolink.find('dailymotion.com')>0:
                        req = urllib2.Request(videolink)
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                        response = urllib2.urlopen(req)
                        link=response.read()
                        response.close()
                        p=re.compile('url=rev=.+?&uid=.+?&lang=en&callback=.+?&preview=.+?&video=(.+?)%40%40spark')
                        match=p.findall(link)
                        decode=urllib.unquote(match[0])
                        url2="http://www.dailymotion.com"+decode
                        addLink(name+"- DAILYMOTION",url2,"")
                if videolink.find('trilulilu.ro')>0:
                        videolink=videolink+"voinage"
                        p=re.compile('http://www.trilulilu.ro/(.+?)/(.+?)voinage')
                        match=p.findall(videolink)
                        for username,vid in match:
                                url2="http://fs14.trilulilu.ro/stream.php?type=video&hash="+vid+"&username="+username+"&key="+" HTTP/1.1?.flv"
                                addLink(name+"- TRILULILU",url2,"")
                
                        
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
        if url.find('myspace.com')>0:
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                p=re.compile('\n<div class="original-text">\n<a href="http://.+?myspace.com/index.+?fuseaction=.+?=(.+?)">Video in original context</a>\n')
                myspace=p.findall(link)
                pass
                req = urllib2.Request("http://mediaservices.myspace.com/services/rss.ashx?type=video&mediaID="+myspace[0])
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link2=response.read()
                response.close()
                comp=re.compile('<media:content url="(.+?)"')
                myspace2=comp.findall(link2)
                if len(myspace2)>0:
                        addLink(name+"- MYSPACE",myspace2[0],"")
                else:
                        addDir("MYSPACE HAVE DELETED THIS VIDEO","http://WWW.MYSPACE.COM",1,"")
       
                
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
