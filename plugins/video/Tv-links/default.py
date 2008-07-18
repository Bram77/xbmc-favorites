import urllib,urllib2,base64,re,sys,xbmcplugin,xbmcgui,socket

#TV-LINKS.CC FOR XBMC 2008 - VOINAGE.

#set socket timeout globally in seconds ( only for bastard youku)
timeout = 30
socket.setdefaulttimeout(timeout)


def ExtractMediaUrl(url, data):
        
        if url.find("megavideo.com") > 0:
                codeRegex = '<ROW url="(.+?)" runtime=".+?" runtimehms=".+?" size=".+?" waitingtime=".+?" k=".+?"></ROW>'
                codeResults = re.findall(codeRegex, data, re.DOTALL + re.IGNORECASE)
                if len(codeResults) > 0:
                        code = codeResults[-1]
                        dictionary = {"0":":","%24": ".", "%25": "/", "%3A": "0", "%3B": "1", "8": "2", "9": "3", "%3E": "4", "%3F": "5", "%3C": "6", "%3D": "7", "2": "8", "3": "9", "a": "k", "b": "h", "c": "i", "d": "n", "e": "o", "f": "l", "g": "m", "h": "b", "i": "c", "k": "a", "l": "f", "m": "g", "n": "d", "o": "e", "p": "z", "s": "y", "%7E": "t", "y": "s","%7C": "v", "%7D": "w", "z": "p"}
                        return RegexReplaceDictionary(code, dictionary) 
                else:
                        return ""
        
def RegexReplaceDictionary(string, dictionary):
      
        rc = re.compile('|'.join(map(re.escape, dictionary)))
        def Translate(match):
                return dictionary[match.group(0)]
        return rc.sub(Translate, string)

def CATS():
        addDir("ANIME","http://tv-links.cc/anime/",2,"http://www.tv-links.cc/images/logo.jpg")
        addDir("ASIAN","http://tv-links.cc/asian/index.html",6,"http://www.tv-links.cc/images/logo.jpg")
        addDir("TELEVISION","http://www.tv-links.cc/tv/",2,"http://www.tv-links.cc/images/logo.jpg")
        addDir("MOVIES","http://tv-links.cc/movie/",5,"http://www.tv-links.cc/images/logo.jpg")
        addDir("CARTOONS","http://tv-links.cc/cartoon/",2,"http://www.tv-links.cc/images/logo.jpg")
        addDir("DOCUMENTARIES","http://tv-links.cc/documentary/",2,"http://www.tv-links.cc/images/logo.jpg")
        
def ALPHABET():
        addDir('#','http://tv-links.cc/movie/index.html',1,'')
        addDir('A','http://tv-links.cc/movie/a.html',1,'')
        addDir('B','http://tv-links.cc/movie/b.html',1,'')
        addDir('C','http://tv-links.cc/movie/c.html',1,'')
        addDir('D','http://tv-links.cc/movie/d.html',1,'')
        addDir('E','http://tv-links.cc/movie/e.html',1,'')
        addDir('F','http://tv-links.cc/movie/f.html',1,'')
        addDir('G','http://tv-links.cc/movie/g.html',1,'')
        addDir('H','http://tv-links.cc/movie/h.html',1,'')
        addDir('I','http://tv-links.cc/movie/i.html',1,'')
        addDir('J','http://tv-links.cc/movie/j.html',1,'')
        addDir('K','http://tv-links.cc/movie/k.html',1,'')
        addDir('L','http://tv-links.cc/movie/l.html',1,'')
        addDir('M','http://tv-links.cc/movie/m.html',1,'')
        addDir('N','http://tv-links.cc/movie/n.html',1,'')
        addDir('O','http://tv-links.cc/movie/o.html',1,'')
        addDir('P','http://tv-links.cc/movie/p.html',1,'')
        addDir('Q','http://tv-links.cc/movie/q.html',1,'')
        addDir('R','http://tv-links.cc/movie/r.html',1,'')
        addDir('S','http://tv-links.cc/movie/s.html',1,'')
        addDir('T','http://tv-links.cc/movie/t.html',1,'')
        addDir('U','http://tv-links.cc/movie/u.html',1,'')
        addDir('V','http://tv-links.cc/movie/v.html',1,'')
        addDir('W','http://tv-links.cc/movie/w.html',1,'')
        addDir('X','http://tv-links.cc/movie/x.html',1,'')
        addDir('Y','http://tv-links.cc/movie/y.html',1,'')
        addDir('Z','http://tv-links.cc/movie/z.html',1,'')
def ASIAN():
        addDir('CHINESE MOVIES','http://tv-links.cc/asian/chinese_movies.html',7,'')
        addDir('CHINESE DRAMA','http://tv-links.cc/asian/chinese_drama.html',7,'')
        addDir('JAPANESE MOVIES','http://tv-links.cc/asian/japanese_movies.html',7,'')
        addDir('JAPANESE DRAMA','http://tv-links.cc/asian/japanese_drama.html',7,'')
        addDir('KOREAN MOVIES','http://tv-links.cc/asian/korean_movies.html',7,'')
        addDir('KOREAN DRAMA','http://tv-links.cc/asian/korean_drama.html',7,'')
        
        
def INDEXMOVIE(url,name):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        code=re.sub('&amp;','',link)
        response.close()        
        p=re.compile('<li><a href="(.+?)" >(.+?)</a></li>')
        match=p.findall(code)
        for url2,name in match:
                linkage="http://tv-links.cc"+url2
                res.append((linkage,name))
        for url,name in res:
                addDir(name,url,3,"http://www.tv-links.cc/images/logo.jpg")
               

def INDEXOTHER(url,name):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        code=re.sub('&amp;','',link)
        p=re.compile('<li><a href="(.+?)" >(.+?)</a></li>')
        match=p.findall(code)
        for url2,name in match:
                url2=url+url2
                addDir(name,url2,3,"http://www.tv-links.cc/images/logo.jpg")
                
def INDEXASIAN(url,name):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        code=re.sub('&amp;','',link)
        p=re.compile('<li><a href="(.+?)" >(.+?)</a></li>')
        match=p.findall(code)
        for url2,name in match:
                url2="http://tv-links.cc/asian/"+url2
                addDir(name,url2,3,"http://www.tv-links.cc/images/logo.jpg")
        

def PROCESSLINKS(url,name):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile("<br><img src='(.+?)' width='75' height='112'><BR>")
        match=p.findall(link)
        for thumbnail in match:
               thumb=re.sub(" ","%20",thumbnail)
        p=re.compile('<A target="_blank"  href=".+?l=(.+?)" onclick=".+?">(.+?)</a>')
        match=p.findall(link)
        for url,name in match:
                url=base64.decodestring(url)
                try:
                        addDir(name,url,4,thumb)
                
                except UnboundLocalError: 
                        addDir(name,url,4,"http://www.tv-links.cc/images/logo.jpg")
                      
                
def RESOLVELINKS(url):
        
        if url.find("tudou.com") > 0:
                new=re.sub('/v/','/programs/view/',url)
                req = urllib2.Request(new)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                p=re.compile('<div class="shareButton"><a href=".+?iid=(.+?)" target="_blank">')
                match=p.findall(link)
                for code in match:
                        pass
                url2="http://www.tudou.com/player/v2.php?id="+code
                req = urllib2.Request(url2)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                p=re.compile("<f w='.+?'>(.+?)</f></v>")
                match=p.findall(link)
                for linkage in match:
                        addLink("WATCH VIDEO TUDOU",linkage,"http://www.ojointernet.com/wp-content/uploads/tudou_logo.png")
                pass        
        if url.find("megavideo.com") > 0:
                url=url[:-45]
                code=re.sub('http://www.megavideo.com/v/','',url)
                req = urllib2.Request('http://keepvid.com/megaupload/keepvid.php','url=http%3A%2F%2Fwww.megavideo.com%2F%3Fv%3D'+code+'&site=aa')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.15) Gecko/20080623 Firefox/2.0.0.15')
                response = urllib2.urlopen(req)
                link = response.read()
                p=re.compile('<br /><a href="(.+?)"><b>&#155;&#155; Download &#139;&#139;</b>')
                mega=p.findall(link)
                addLink("MEGAVIDEO LINK",mega[0],"")
        
                pass
        if url.find("google.com") > 0:
                code2=re.sub('http://video.google.com/googleplayer.swf.+?=','http://video.google.com/videoplay?docid=',url)
                req = urllib2.Request(code2)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                p=re.compile('right-click <a href="(.+?)">')
                p=re.compile('.+?videoUrl.+?.+?.+?.+?(.+?)%26sigh')
                match=p.findall(link)
                for url2 in match:
                        GOOG=urllib.unquote(url2)
                        addLink("WATCH GOOGLE HIGH QUALITY",GOOG,"http://img324.imageshack.us/img324/424/logo2ej.gif")
                pass
        if url.find('veoh.com/videodetails') > 0:
                code=re.sub('http://www.veoh.com/videodetails.+?permalinkId=','',url)
                code2=re.sub('&id=.+?&player=videodetailsembedded&videoAutoPlay=.+?','',code)
                url2='http://127.0.0.1:64652/'+code2+"?.avi"
                addLink("WATCH VEOH HIGH QUALITY",url2,"http://www.seanborg.com/images/Veoh%20Logo.jpg")
                pass
        if url.find("veoh.com/videos/") > 0:
                code=re.sub('http://www.veoh.com/videos/','',url)
                url2='http://127.0.0.1:64652/'+code+"?.avi"
                addLink("WATCH VEOH HIGH QUALITY",url2,"http://www.seanborg.com/images/Veoh%20Logo.jpg")
        if url.find("veoh.com/static/")>0:
                code=re.sub('http://www.veoh.com/static/flash/players/.+?permalinkId=','',url)
                code2=re.sub('&id=anonymous&player=videodetailsembedded&videoAutoPlay=.+?&version=.+?','',code)
                url2='http://127.0.0.1:64652/'+code2+"?.avi"
                addLink("WATCH VEOH HIGH QUALITY",url2,"http://www.seanborg.com/images/Veoh%20Logo.jpg")
                pass
        if url.find("veoh.com/veohplayer.swf")>0:
                code=re.sub('http://www.veoh.com/veohplayer.+?permalinkId=','',url)
                code2=re.sub('&id=.+?&player=videodetailsembedded&videoAutoPlay=.+?','',code)
                url2='http://127.0.0.1:64652/'+code2+"?.avi"
                addLink("WATCH VEOH HIGH QUALITY",url2,"http://www.seanborg.com/images/Veoh%20Logo.jpg")
                pass
        if url.find('guba') >0:
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                p=re.compile('null, null, null,\r\n.+"(.+?)" ')
                match=p.findall(link)
                for url in match:
                        addLink("WATCH GUBA FLV",url,"")
                #GET ORIGINAL FORMAT
                p=re.compile('\r\n <option value="(.+?)">.+?</option>')
                match=p.findall(link)
                for url in match:
                        addLink("WATCH GUBA HIGH QUALITY AVI",url,"http://www.last100.com/wp-content/uploads/2007/09/guba_logo.png")
                pass
        if url.find('youtube') >0:
                code=re.sub('http://www.youtube.com/v/','',url)
                req = urllib2.Request('http://www.youtube.com/watch?v='+code)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                p=re.compile('"t": "(.+?)"')
                match=p.findall(link)
                for url in match:
                        linkage="http://www.youtube.com/get_video?video_id="+code+"&t="+url
                        addLink("WATCH YOUTUBE VIDEO",linkage,"http://www.webtvwire.com/wp-content/uploads/2007/06/youtube.jpg")
                pass
        if url.find('youku') >0:
                res=[]
                code=re.sub('http://player.youku.com/player.php/sid/','',url)
                code2=re.sub('/v.swf','',code)
                DECODE='http://clipnabber.com/gethint.php'
                YOUKU2='http://v.youku.com/v_show/id_'+code2+'=.html'
                data = "mode=1&url="+YOUKU2
                req = urllib2.Request(DECODE,data)
                response = urllib2.urlopen(req)
                results = response.read()
                p=re.compile('<a href=(.+?)><strong>(.+?)</strong></a>&nbsp;&nbsp;&nbsp;')
                final=p.findall(results)
                for url,name in final:
                        res.append((url,name))
                for url,name in res:
                        addLink("WATCH YOUKU - "+name,url,"http://www.21314.cn/images/logo_youku.gif")
                pass
        if url.find('dailymotion')>0:
                code=re.sub('http://www.dailymotion.com/swf/','http://www.dailymotion.com/video/',url)
                req = urllib2.Request(code)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                p=re.compile('url=rev=.+?&uid=.+?&lang=en&callback=.+?&preview=.+?&video=(.+?)%40%40spark')
                match=p.findall(link)
                for url1 in match:
                        decode=urllib.unquote(url1)
                        url2="http://www.dailymotion.com"+decode
                addLink("DAILYMOTION VIDEO",url2,"")
        if url.find('myspace')>0:
                code=re.sub('http://.+?myspace.com/videos/vplayer..+?m=','',url)
                f=urllib2.urlopen("http://mediaservices.myspace.com/services/rss.ashx?type=video&mediaID="+code)
                myspace=f.read()
                comp=re.compile('<media:content url="(.+?)"')
                for url in comp.findall(myspace):
                        addLink("MYSPACE LINK",url,"")
                        
                
                                          

                   
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
        print "TV LINKS CATEGORIES :"
        CATS()
elif mode==1:
        print "INDEXMOVIE : "+url
        INDEXMOVIE(url,name)
elif mode==2:
        print "INDEXOTHER : "+url
        INDEXOTHER(url,name)
elif mode==3:
        print "PROCESS BASE64 DECODE LINKS: "+url
        PROCESSLINKS(url,name)
elif mode==4:
        print "RESOLVE LINKS : "+url
        RESOLVELINKS(url)
elif mode==5:
        print "A-Z MOVIE LINKS : "+url
        ALPHABET()
elif mode==6:
        print "ASIAN CATS : "+url
        ASIAN()
elif mode==7:
        print "INDEX OF : "+url
        INDEXASIAN(url,name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
