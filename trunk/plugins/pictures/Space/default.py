import urllib,urllib2,re,xbmcplugin,xbmcgui



def INDEXCATS():
        res=[]
        numb=87
        for i in range(1,9):
                req = urllib2.Request('http://abovespaceandtime.blip.tv/?sort=date;date=;view=archive;user=abovespaceandtime;nsfw=dc;s=posts;page='+str(i))
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req).read()
                eps=re.compile('meta name="image_src" content="(.+?)" />\n\t\t\t\n                        \n                        \t<meta name=".+?" content=\'video\' />\n                          \t<meta name="video_height" content=".+?" />\n                          \t<meta name="video_width" content=".+?" />\n\t\t\t  \t\n\t\t\t  \t\t<meta name="video_type" content="" />\n\t\t\t  \t\t<meta name="video_src" content="(.+?)" />').findall(response)           
                for thumb,url in eps:
                        res.append((thumb,url))
        for thumb,url in res:
                numb=numb-1
                addLink('Watch Episode '+str(numb),url,thumb)
                
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

xbmcplugin.endOfDirectory(int(sys.argv[1]))
