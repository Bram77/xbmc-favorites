import urllib,urllib2,re,xbmcplugin,xbmcgui,NVDecode

#NINJAVIDEO PLUGIN FOR XBMC- all platforms 2008.#
#Thanks to unbehagen for the decryption code NVDecode.py & Coolblaze for the Megavideo algo
#A collaboration of goodwill.


def indexcats():
        addDir("1. ANIME","http://www.ninjavideo.net/anime",1)
        addDir( "2. MOVIES","http://www.ninjavideo.net/movies",1)
        addDir( "3. TV SHOWS","http://www.ninjavideo.net/tvshows",1)
        addDir("6. DOCUMENTARIES","http://www.ninjavideo.net/docus",1)
        addDir( "5. CARTOONS","http://www.ninjavideo.net/cartoons",1)
        addDir( "7. SPORTS","http://www.ninjavideo.net/sports",1)
        addDir( "8. MUSIC","http://www.ninjavideo.net/music",1)
        addDir( "4. COMEDY","http://www.ninjavideo.net/comedy",1)
        addDir("9. LATEST VIDEOS","http://www.ninjavideo.net/latest.xml",5)

def latest(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req);link=response.read();response.close();code=re.sub('&amp;','&',link)
        latest=re.compile('<title>(.+?)</title><link>http://www.ninjavideo.net(.+?)</link>').findall(code)
        for name,url in latest:
                addDir(name,url,4)
      
def shows(url):
        
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
                addDir(name,url,2)
                
       
def seasons(url):
        req = urllib2.Request('http://www.ninjavideo.net'+url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        clean=re.sub('&amp;','&',link)
        clean1=re.sub("\xe2\x80\x99","'",clean)
        clean2=re.sub('\xc5\xab','u',clean1)
        response.close()
        p=re.compile(r'<a href="(.+?)">(.+?)</a>\n')
        match=p.findall(clean2);del match[0:7]
        for url,name in match:
                if name.find('eason')>0:
                        addDir(name,url,3)
                else:
                        addDir(name,url,4)
               
def episodes(url):
        req = urllib2.Request('http://www.ninjavideo.net'+url)
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
                addDir(name,url,4)

def vidlinks(url,name):
        try:
                info=['','0','','','']
        except:
                info=['','0','','','']
               
        if name.find('Flash')>0:
                req = urllib2.Request('http://www.ninjavideo.net'+url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link=response.read()
                clean=re.sub('&amp;','&',link)
                clean1=re.sub("\xe2\x80\x99","'",clean)
                clean2=re.sub('\xc5\xab','u',clean1)
                response.close()
                try:
                        mega=re.compile('<param name="movie" value="http://www.megavideo.com/v/(.+?)">').findall(link)
                        mega[0] = mega[0][0:8]
                        req = urllib2.Request("http://www.megavideo.com/xml/videolink.php?v="+mega[0])
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                        req.add_header('Referer', 'http://www.megavideo.com/')
                        page = urllib2.urlopen(req);response=page.read();page.close()
                        errort = re.compile(' errortext="(.+?)"').findall(response)
                        if len(errort) > 0:
                                addLink(errort[0], '', '')
                        else:
                                s = re.compile(' s="(.+?)"').findall(response)
                                k1 = re.compile(' k1="(.+?)"').findall(response)
                                k2 = re.compile(' k2="(.+?)"').findall(response)
                                un = re.compile(' un="(.+?)"').findall(response)
                                movielink = "http://www" + s[0] + ".megavideo.com/files/" + decrypt(un[0], k1[0], k2[0]) + "/"
                                info = ['','','','','','','','','']
                                addLink(name, movielink+'?.flv','',info)
                                
                        
                except IndexError:
                        episodes(url)
        else:
                strid=re.sub('/.+?/','',url)
                req = urllib2.Request('http://www.ninjavideo.net/video.php?request='+strid)
                req.add_header('User-Agent', 'NinjaVideo Helper/0.3.3')
                response = urllib2.urlopen(req)
                link=NVDecode.decode(response.read())
                match=re.compile('\r\nData: (.+?)\r\n').findall(link)
                method=re.compile('\r\nMethod: (.+?)\r\n').findall(link)
                if match[0].find('flyupload')>0:
                        req = urllib2.Request(match[0])
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                        req.add_header('Cookie','downloadpages=2')
                        response = urllib2.urlopen(req)
                        cookie=response.info()['Set-Cookie'];response.close()
                        backend=re.search(r"backend=(.+?);", cookie).group(0)
                        req = urllib2.Request(response.url+"&c=1")
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                        req.add_header('Cookie',backend+'downloadpages=2')
                        frog = urllib2.urlopen(req);data=frog.read();frog.close()
                        backend=re.search(r'<A HREF="([^"]+)">Download Now</A>', data).group(1)
                        addLink(name,backend,'',info)
                if method[0].find('veoh')>0:
                        req = urllib2.Request('http://www.ninjavideo.net'+url)
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                        response = urllib2.urlopen(req)
                        link=response.read()
                        clean=re.sub('&amp;','&',link)
                        clean1=re.sub("\xe2\x80\x99","'",clean)
                        clean2=re.sub('\xc5\xab','u',clean1)
                        response.close()
                        veoh=re.compile('<a href="(.+?)">Download</a>').findall(link)
                        addLink(name,veoh[0],'',info)
                if match[0].find('archive')>0:
                        addLink(name,match[0],'',info)
                                  
  
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


#####Megavideo - Coolblaze xbc forums.
                                
def ajoin(arr):
    strtest = ''
    for num in range(len(arr)):
        strtest = strtest + str(arr[num])
    return strtest

def asplit(mystring):
    arr = []
    for num in range(len(mystring)):
        arr.append(mystring[num])
    return arr
        
def decrypt(str1, key1, key2):

    __reg1 = []
    __reg3 = 0
    while (__reg3 < len(str1)):
        __reg0 = str1[__reg3]
        holder = __reg0
        if (holder == "0"):
            __reg1.append("0000")
        else:
            if (__reg0 == "1"):
                __reg1.append("0001")
            else:
                if (__reg0 == "2"): 
                    __reg1.append("0010")
                else: 
                    if (__reg0 == "3"):
                        __reg1.append("0011")
                    else: 
                        if (__reg0 == "4"):
                            __reg1.append("0100")
                        else: 
                            if (__reg0 == "5"):
                                __reg1.append("0101")
                            else: 
                                if (__reg0 == "6"):
                                    __reg1.append("0110")
                                else: 
                                    if (__reg0 == "7"):
                                        __reg1.append("0111")
                                    else: 
                                        if (__reg0 == "8"):
                                            __reg1.append("1000")
                                        else: 
                                            if (__reg0 == "9"):
                                                __reg1.append("1001")
                                            else: 
                                                if (__reg0 == "a"):
                                                    __reg1.append("1010")
                                                else: 
                                                    if (__reg0 == "b"):
                                                        __reg1.append("1011")
                                                    else: 
                                                        if (__reg0 == "c"):
                                                            __reg1.append("1100")
                                                        else: 
                                                            if (__reg0 == "d"):
                                                                __reg1.append("1101")
                                                            else: 
                                                                if (__reg0 == "e"):
                                                                    __reg1.append("1110")
                                                                else: 
                                                                    if (__reg0 == "f"):
                                                                        __reg1.append("1111")

        __reg3 = __reg3 + 1

    mtstr = ajoin(__reg1)
    __reg1 = asplit(mtstr)
    __reg6 = []
    __reg3 = 0
    while (__reg3 < 384):
    
        key1 = (int(key1) * 11 + 77213) % 81371
        key2 = (int(key2) * 17 + 92717) % 192811
        __reg6.append((int(key1) + int(key2)) % 128)
        __reg3 = __reg3 + 1
    
    __reg3 = 256
    while (__reg3 >= 0):

        __reg5 = __reg6[__reg3]
        __reg4 = __reg3 % 128
        __reg8 = __reg1[__reg5]
        __reg1[__reg5] = __reg1[__reg4]
        __reg1[__reg4] = __reg8
        __reg3 = __reg3 - 1
    
    __reg3 = 0
    while (__reg3 < 128):
    
        __reg1[__reg3] = int(__reg1[__reg3]) ^ int(__reg6[__reg3 + 256]) & 1
        __reg3 = __reg3 + 1

    __reg12 = ajoin(__reg1)
    __reg7 = []
    __reg3 = 0
    while (__reg3 < len(__reg12)):

        __reg9 = __reg12[__reg3:__reg3 + 4]
        __reg7.append(__reg9)
        __reg3 = __reg3 + 4
        
    
    __reg2 = []
    __reg3 = 0
    while (__reg3 < len(__reg7)):
        __reg0 = __reg7[__reg3]
        holder2 = __reg0
    
        if (holder2 == "0000"):
            __reg2.append("0")
        else: 
            if (__reg0 == "0001"):
                __reg2.append("1")
            else: 
                if (__reg0 == "0010"):
                    __reg2.append("2")
                else: 
                    if (__reg0 == "0011"):
                        __reg2.append("3")
                    else: 
                        if (__reg0 == "0100"):
                            __reg2.append("4")
                        else: 
                            if (__reg0 == "0101"): 
                                __reg2.append("5")
                            else: 
                                if (__reg0 == "0110"): 
                                    __reg2.append("6")
                                else: 
                                    if (__reg0 == "0111"): 
                                        __reg2.append("7")
                                    else: 
                                        if (__reg0 == "1000"): 
                                            __reg2.append("8")
                                        else: 
                                            if (__reg0 == "1001"): 
                                                __reg2.append("9")
                                            else: 
                                                if (__reg0 == "1010"): 
                                                    __reg2.append("a")
                                                else: 
                                                    if (__reg0 == "1011"): 
                                                        __reg2.append("b")
                                                    else: 
                                                        if (__reg0 == "1100"): 
                                                            __reg2.append("c")
                                                        else: 
                                                            if (__reg0 == "1101"): 
                                                                __reg2.append("d")
                                                            else: 
                                                                if (__reg0 == "1110"): 
                                                                    __reg2.append("e")
                                                                else: 
                                                                    if (__reg0 == "1111"): 
                                                                        __reg2.append("f")
                                                                    
        __reg3 = __reg3 + 1

    endstr = ajoin(__reg2)
    return endstr

#########
                                

def addLink(name,url,thumbnail,info):
        ok=True
        def Download(url,dest):
                dp = xbmcgui.DialogProgress()
                dp.create("Ninja Video","Downloading File",url)
                urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
        def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
                try:
                        percent = min((numblocks*blocksize*100)/filesize, 100)
                        print percent
                        dp.update(percent)
                except:
                        percent = 100
                        dp.update(percent)
                if dp.iscanceled():
                        dp.close()
        if xbmcplugin.getSetting("Download File") == "true":
                dialog = xbmcgui.Dialog()
                path = dialog.browse(3, 'Choose Download Directory', 'files', '', False, False, '')
                Download(url,path+name)
        try:
                liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=info[2])
                liz.setInfo( type="Video", infoLabels={ "Title": name , "Genre": info[0], "Year": int(info[1]), "Plot": info[4]} )
        except:
                liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage='http://ia.media-imdb.com/media/imdb/01/I/27/89/15/10.gif')
                liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png")
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
        shows(url)
        
elif mode==2:
        print "index of seasons : "+url
        seasons(url)
        
elif mode==3:
        print "index of episodes : "+url
        episodes(url)
        
elif mode==4:
        print "index of videolinks : "+url
        vidlinks(url,name)

elif mode==5:
        print "index of Latest links : "+url
        latest(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
