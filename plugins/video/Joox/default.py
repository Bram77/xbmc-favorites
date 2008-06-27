import urllib,urllib2,re,xbmcplugin,xbmcgui,base64
#joox V2008

def INDEXCATS():
        req = urllib2.Request('http://joox.net/')
        req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('\n          <a href=".+?(.+?)">(.+?)</a>')
        match=p.findall(link)
        for url,name in match:
                url="http://joox.net"+url
                addDir(name,url,1,"")
       
def INDEX(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('          <a href=".+?(.+?)">(.+?)</a><br />')
        match=p.findall(link)
        for url,name in match:
                url="http://joox.net"+url
                addDir(name,url,2,"")
                
def EPISODES(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('          <a href=".+?(.+?)">(.+?)</a><br />')
        match=p.findall(link)
        for li,name in match:
                url="http://joox.net"+li
                addDir(name,url,3,"")

def VIDEOLINK(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('videoFile: "(.+?)"')
        match=p.findall(link)
        for url in match:
                url="http://joox.net"+url
                addLink("WATCH VIDEO",url,"")
        p=re.compile('<a href="(.+?)">Download this video</a>')
        match=p.findall(link)
        for url in match:
                if url.find('messagefromme')>0:
                        url="http://127.0.0.1:64653/streamplug/"+base64.urlsafe_b64encode(url)+'?.ogm'
                        addLink("WATCH STREAMPLUG - Play with DvD player & run Veohproxy",url,"")
                else:
                        pass
                        #addLink('WATCH VIDEO',url,"")
                

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
        EPISODES(url)
elif mode==3:
        print "GET INDEX OF PAGE : "+url
        VIDEOLINK(url)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
