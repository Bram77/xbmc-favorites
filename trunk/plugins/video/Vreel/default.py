import urllib,urllib2,re,xbmcplugin,xbmcgui,base64
#joox V2008

def INDEXCATS():
        res=[]
        req = urllib2.Request('http://beta.vreel.net/index.php?q=channels')
        req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('\n                <a href="(.+?)">(.+?)</a>')
        match=p.findall(link)
        for url,name in match:
                url="http://beta.vreel.net/"+url
                res.append((url,name))
        for url,name in res:
                addDir(name,url,1,"")
        addDir("0. SEARCH VREEL","http://beta.vreel.net",3,"")
                
def SEARCH():
        res=[]
        keyb = xbmc.Keyboard('', 'Search Vreel')
        keyb.doModal()
        if (keyb.isConfirmed()):
                search = keyb.getText()
                encode=urllib.quote(search)
                req = urllib2.Request('http://beta.vreel.net/index.php?q=search&k='+encode)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                p=re.compile('index.php.+?q=search&k=(.+?)">next</a>')
                match=p.findall(link)
                for url in match:
                        next="http://beta.vreel.net/index.php?q=search&k="+url
                addDir("    NEXT PAGE",next,4,"")
                pass
                p=re.compile('<a href="(.+?)"><img width="149" height="104" src=".+?(.+?)" border="0"/></a></td>\n\t\t\t\t<td style="padding-left: 20px; padding-top: 5px; width: 300px"><font size="5"><a href=".+?">(.+?)</a>')
                match=p.findall(link)
                for url,thumbnail,name in match:
                        thumbnail="http://beta.vreel.net/"+thumbnail
                        url="http://beta.vreel.net/"+url
                        res.append((url,thumbnail,name))
                for url,thumbnail,name in res:
                        addDir(name,url,2,thumbnail)
       
def INDEX(url):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('index.php.+?q=channels&id=(.+?)">.+?</a>')
        match=p.findall(link)
        next="http://beta.vreel.net/index.php?q=channels&id="+str(match[-1])
        addDir("    NEXT PAGE",next,1,"")
        pass
        p=re.compile('<a href="(.+?)"><img src=".+?(.+?)" width="149" height="104" border="0" /></a>\n\t<br><font size="5"><a href=".+?" style="font-size: 11px">(.+?)</a></font><br />\n\tDescription:(.+?)<br />')
        match=p.findall(link)
        for url,thumbnail,name,desc in match:
                thumbnail="http://beta.vreel.net/"+thumbnail
                url="http://beta.vreel.net/"+url
                res.append((url,thumbnail,name,desc))
        for url,thumbnail,name,desc in res:
                addDir(name+" "+desc,url,2,thumbnail)

def INDEX2(url):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('index.php.+?q=search&k=(.+?)">next</a>')
        match=p.findall(link)
        for url in match:
                next="http://beta.vreel.net/index.php?q=search&k="+url
        try:
                addDir("    NEXT PAGE",next,4,"")
        except UnboundLocalError:
                pass
        p=re.compile('<a href="(.+?)"><img width="149" height="104" src=".+?(.+?)" border="0"/></a></td>\n\t\t\t\t<td style="padding-left: 20px; padding-top: 5px; width: 300px"><font size="5"><a href=".+?">(.+?)</a>')
        match=p.findall(link)
        for url,thumbnail,name in match:
                thumbnail="http://beta.vreel.net/"+thumbnail
                url="http://beta.vreel.net/"+url
                res.append((url,thumbnail,name))
        for url,thumbnail,name in res:
                addDir(name,url,2,thumbnail)
                
def VIDEOLINK(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('<param name="src" value="(.+?)" />')
        match=p.findall(link)
        for url in match:
                addLink("WATCH VIDEO",url,"")
                
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
        VIDEOLINK(url)
elif mode==3:
        print "GET INDEX OF PAGE : "+url
        SEARCH()
elif mode==4:
        print "GET INDEX OF PAGE : "+url
        INDEX2(url)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
