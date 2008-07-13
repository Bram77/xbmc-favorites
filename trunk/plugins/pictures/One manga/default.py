import urllib,urllib2,re,xbmcplugin,xbmcgui
#One Manga

def INDEXCATS():
        res=[]
        url='http://www.onemanga.com/directory/'
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        code=re.sub('&#39;','',link)
        code2=re.sub('&amp;','&',code)
        response.close()
        p=re.compile('<td class="ch-subject"><a href="(.+?)" >(.+?)</a> <span>.+?</span>\n      </td>\n      <td class="last-chapter"><a href=".+?">.+?</a></td>\n      <td><span class="completed">(.+?)</span></td>')
        match=p.findall(code2)
        for url,name,status in match:
                res.append((url,name,status))
        p=re.compile('<td class="ch-subject"><a href="(.+?)" >(.+?)</a> <span>.+?</span>\n      </td>\n      <td class="last-chapter"><a href=".+?">.+?</a></td>\n      <td>(.+?)</td>')
        match=p.findall(code2)
        for url,name,status in match:
                if not status.find('span')>0:
                        res.append((url,name,status))
        for url,name,status in res:
                addDir(name+" Status / Last update: "+status,url,1)
                
def INDEX(url):
        req = urllib2.Request("http://www.onemanga.com"+url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('<td class="ch-subject"><a href="(.+?)">(.+?)</a></td>\n')
        match=p.findall(link)
        for url,name in match:
                addDir(name,url,2)

                
def IMAGE(url,name):
        res=[]
        req = urllib2.Request('http://www.onemanga.com'+url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('>(.+?)</option>\n\n')
        match=p.findall(link)
        i=0
        for page in match:
                f=urllib.urlopen('http://www.onemanga.com'+url+page)
                a=f.read()
                f.close()
                p=re.compile('<img class="manga-page" src="(.+?)" alt=""')
                match=p.findall(a)
                for image in match:
                        res.append(image)
                pass
        for image in res:
                i=i+1
                addLink(name +"Page "+str(i),image)
               
                
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
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage="http://www.library.northwestern.edu/govinfo/resource/internat/camera.png")
        liz.setInfo( type="Pictures", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok
        


def addDir(name,url,mode):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolderBig.png")
        liz.setInfo( type="Pictures", infoLabels={ "Title": name } )
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
        IMAGE(url,name)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
