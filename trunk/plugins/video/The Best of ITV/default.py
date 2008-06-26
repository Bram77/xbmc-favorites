import urllib,urllib2,re,sys,socket
import xbmcplugin,xbmcgui
import htmllib

#THE BEST OF ITV & ITV CATCHUP Plugin - By The Voin u.k 2008.
#This script will function no matter where you are in the world.




#[(Webpage,Name of Show)]
def getShows(url,name):
        res=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        code=re.sub('&amp;','&',a)
        p=re.compile('<ProgrammeId>(.+?)</ProgrammeId>\r\n      <ProgrammeTitle>(.+?)</ProgrammeTitle>\r\n')
        match=p.findall(code)
        for url,name in match:
                res.append((url,name))
        return res

def getBestCrimeShows(url,name):
        res=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        p=re.compile('<li><a href="(.+?)"><img src=".+?/.+?/.+?.jpg" alt=".+?"></a><h4><a href=".+?">(.+?)</a></h4>\r\n')
        match=p.findall(a)
        for url,name in match:
                res.append((url,name))
        return res

def getBestPeriodShows(url,name):
        res=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        code=re.sub('&amp;','&',a)
        p=re.compile('<li><a href="(.+?)"><img src=".+?/.+?/.+?.jpg" alt=".+?"></a><h4><a href=".+?">(.+?)</a></h4>\r\n')
        match=p.findall(code)
        for url,name in match:
                res.append((url,name))
        return res

def getBestFamilyShows(url,name):
        res=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        code=re.sub('&amp;','&',a)
        p=re.compile('<li><a href="(.+?)"><img src=".+?/.+?/.+?.jpg" alt=".+?"></a><h4><a href=".+?">(.+?)</a></h4>\r\n')
        match=p.findall(code)
        for url,name in match:
                res.append((url,name))
        return res

def getBestDocumentaryShows(url,name):
        res=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        code=re.sub('&amp;','&',a)
        p=re.compile('<li><a href="(.+?)"><img src=".+?/.+?/.+?.jpg" alt=".+?"></a><h4><a href=".+?">(.+?)</a></h4>\r\n')
        match=p.findall(code)
        for url,name in match:
                res.append((url,name))
        return res

def getBestComedyShows(url,name):
        res=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        code=re.sub('&amp;','&',a)
        p=re.compile('<li><a href="(.+?)"><img src=".+?/.+?/.+?.jpg" alt=".+?"></a><h4><a href=".+?">(.+?)</a></h4>\r\n')
        match=p.findall(code)
        for url,name in match:
                res.append((url,name))
        return res

def getBestChildrensShows(url,name):
        res=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        code=re.sub('&amp;','&',a)
        p=re.compile('<li><a href="(.+?)"><img src=".+?/.+?/.+?.jpg" alt=".+?"></a><h4><a href=".+?">(.+?)</a></h4>\r\n')
        match=p.findall(code)
        for url,name in match:
                res.append((url,name))
        return res

def getBestSoapShows(url,name):
        res=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        code=re.sub('&amp;','&',a)
        p=re.compile('<li><a href="(.+?)"><img src=".+?/.+?/.+?.jpg" alt=".+?"></a><h4><a href=".+?">(.+?)</a></h4>\r\n')
        match=p.findall(code)
        for url,name in match:
                res.append((url,name))
        return res


def getEpisodes(url):
        res=[]
        f=urllib.urlopen("http://www.itv.com/_app/Dynamic/CatchUpData.ashx?ViewType=1&Filter="+url+"&moduleID=115107")
        a=f.read()
        f.close()
        p=re.compile(r'<h3><a href=".+?.html?.+?=.+?&amp;Filter=(.+?)">(.+?)</a></h3>\r\n        <p class="date">.+?</p>\r\n        <p class="progDesc">.+?</p>\r\n')
        match=p.findall(a)
        for url,name in match:
                res.append((url,name))
        return res

def getBestCrimeEps(url,name):
        res=[]
        res2=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        code=re.sub('<br />',' ',a)
        p=re.compile('<a class="nsat" title=".+?".+?href=".+?(.+?)&amp;G=.+?&amp;DF=.+?">.+?.+?.+?.+?.+?</a><br>(.+?)</li>\r\n')
        p=re.compile('title=".+?".+?href=".+?vodcrid=(.+?)&amp;G=.+?">.+?</a><br>(.+?)</li>')
        match=p.findall(code)
        for url,name in match:
                res.append((url,name))
        #Get Another version
        p=re.compile('<a class="playVideo" title="Play" href=".+?vodcrid=(.+?)&amp;DF=.+?"><img src=".+?/.+?/.+?.jpg" alt=".+?"><span>.+?</span></a><.+?>(.+?)</.+?>')
        #p=re.compile('<a title="Play".+?href=".+?vodcrid=(.+?)&amp;DF=.+?">(.+?)</a><br></li>')#used for Miss marple
        match1=p.findall(code)
        for url,name in match1:
                res.append((url,name))
        #Get Another version
        p=re.compile('title="Play".+?href=".+?vodcrid=(.+?)">.+?</a><br>(.+?)</li>')
        match2=p.findall(code)
        for url,name in match2:
                res.append((url,name))
        return res


def getBestPeriodEps(url,name):
        res=[]
        res2=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        code=re.sub('<br />',' ',a)
        p=re.compile('<a class="nsat" title=".+?".+?href=".+?(.+?)&amp;G=.+?&amp;DF=.+?">.+?.+?.+?.+?.+?</a><br>(.+?)</li>\r\n')
        p=re.compile('title=".+?".+?href=".+?vodcrid=(.+?)&amp;G=.+?">.+?</a><br>(.+?)</li>')
        match=p.findall(code)
        for url,name in match:
                res.append((url,name))
        #Get Another version
        p=re.compile('<a class="playVideo" title="Play" href=".+?vodcrid=(.+?)&amp;DF=.+?"><img src=".+?/.+?/.+?.jpg" alt=".+?"><span>.+?</span></a><.+?>(.+?)</.+?>')
        #p=re.compile('<a title="Play".+?href=".+?vodcrid=(.+?)&amp;DF=.+?">(.+?)</a><br></li>')#used for Miss marple
        match1=p.findall(code)
        for url,name in match1:
                res.append((url,name))
        #Get Another version
        p=re.compile('title="Play".+?href=".+?vodcrid=(.+?)">.+?</a><br>(.+?)</li>')
        match2=p.findall(code)
        for url,name in match2:
                res.append((url,name))
        return res

def getBestFamilyEps(url,name):
        res=[]
        res2=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        code=re.sub('<br />',' ',a)
        p=re.compile('<a class="nsat" title=".+?".+?href=".+?(.+?)&amp;G=.+?&amp;DF=.+?">.+?.+?.+?.+?.+?</a><br>(.+?)</li>\r\n')
        p=re.compile('title=".+?".+?href=".+?vodcrid=(.+?)&amp;G=.+?">.+?</a><br>(.+?)</li>')
        match=p.findall(code)
        for url,name in match:
                res.append((url,name))
        #Get Another version
        p=re.compile('<a class="playVideo" title="Play" href=".+?vodcrid=(.+?)&amp;DF=.+?"><img src=".+?/.+?/.+?.jpg" alt=".+?"><span>.+?</span></a><.+?>(.+?)</.+?>')
        match1=p.findall(code)
        for url,name in match1:
                res.append((url,name))
        #Get Another version
        p=re.compile('title="Play".+?href=".+?vodcrid=(.+?)">.+?</a><br>(.+?)</li>')
        match2=p.findall(code)
        for url,name in match2:
                res.append((url,name))
        return res

def getBestDocumentaryEps(url,name):
        res=[]
        res2=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        code=re.sub('<br />',' ',a)
        p=re.compile('<a class="nsat" title=".+?".+?href=".+?(.+?)&amp;G=.+?&amp;DF=.+?">.+?.+?.+?.+?.+?</a><br>(.+?)</li>\r\n')
        p=re.compile('title=".+?".+?href=".+?vodcrid=(.+?)&amp;G=.+?">.+?</a><br>(.+?)</li>')
        match=p.findall(code)
        for url,name in match:
                res.append((url,name))
        #Get Another version
        p=re.compile('<a class="playVideo" title="Play" href=".+?vodcrid=(.+?)&amp;DF=.+?"><img src=".+?/.+?/.+?.jpg" alt=".+?"><span>.+?</span></a><.+?>(.+?)</.+?>')
        #p=re.compile('<a title="Play".+?href=".+?vodcrid=(.+?)&amp;DF=.+?">(.+?)</a><br></li>')#used for Miss marple
        match1=p.findall(code)
        for url,name in match1:
                res.append((url,name))
        #Get Another version
        p=re.compile('title="Play".+?href=".+?vodcrid=(.+?)">.+?</a><br>(.+?)</li>')
        match2=p.findall(code)
        for url,name in match2:
                res.append((url,name))
        return res

def getBestComedyEps(url,name):
        res=[]
        res2=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        code=re.sub('<br />',' ',a)
        p=re.compile('<a class="nsat" title=".+?".+?href=".+?(.+?)&amp;G=.+?&amp;DF=.+?">.+?.+?.+?.+?.+?</a><br>(.+?)</li>\r\n')
        p=re.compile('title=".+?".+?href=".+?vodcrid=(.+?)&amp;G=.+?">.+?</a><br>(.+?)</li>')
        match=p.findall(code)
        for url,name in match:
                res.append((url,name))
        #Get Another version
        p=re.compile('<a class="playVideo" title="Play" href=".+?vodcrid=(.+?)&amp;DF=.+?"><img src=".+?/.+?/.+?.jpg" alt=".+?"><span>.+?</span></a><.+?>(.+?)</.+?>')
        #p=re.compile('<a title="Play".+?href=".+?vodcrid=(.+?)&amp;DF=.+?">(.+?)</a><br></li>')#used for Miss marple
        match1=p.findall(code)
        for url,name in match1:
                res.append((url,name))
        #Get Another version
        p=re.compile('title="Play".+?href=".+?vodcrid=(.+?)">.+?</a><br>(.+?)</li>')
        match2=p.findall(code)
        for url,name in match2:
                res.append((url,name))
        return res

def getBestChildrensEps(url,name):
        res=[]
        res2=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        code=re.sub('<br />',' ',a)
        p=re.compile('<a class="nsat" title=".+?".+?href=".+?(.+?)&amp;G=.+?&amp;DF=.+?">.+?.+?.+?.+?.+?</a><br>(.+?)</li>\r\n')
        p=re.compile('title=".+?".+?href=".+?vodcrid=(.+?)&amp;G=.+?">.+?</a><br>(.+?)</li>')
        match=p.findall(code)
        for url,name in match:
                res.append((url,name))
        #Get Another version
        p=re.compile('<a class="playVideo" title="Play" href=".+?vodcrid=(.+?)&amp;DF=.+?"><img src=".+?/.+?/.+?.jpg" alt=".+?"><span>.+?</span></a><.+?>(.+?)</.+?>')
        #p=re.compile('<a title="Play".+?href=".+?vodcrid=(.+?)&amp;DF=.+?">(.+?)</a><br></li>')#used for Miss marple
        match1=p.findall(code)
        for url,name in match1:
                res.append((url,name))
        #Get Another version
        p=re.compile('title="Play".+?href=".+?vodcrid=(.+?)">.+?</a><br>(.+?)</li>')
        match2=p.findall(code)
        for url,name in match2:
                res.append((url,name))
        return res

def getBestSoapEps(url,name):
        res=[]
        res2=[]
        f=urllib.urlopen(url)
        a=f.read()
        f.close()
        code=re.sub('<br />',' ',a)
        p=re.compile('<a class="nsat" title=".+?".+?href=".+?(.+?)&amp;G=.+?&amp;DF=.+?">.+?.+?.+?.+?.+?</a><br>(.+?)</li>\r\n')
        p=re.compile('title=".+?".+?href=".+?vodcrid=(.+?)&amp;G=.+?">.+?</a><br>(.+?)</li>')
        match=p.findall(code)
        for url,name in match:
                res.append((url,name))
        #Get Another version
        p=re.compile('<a class="playVideo" title="Play" href=".+?vodcrid=(.+?)&amp;DF=.+?"><img src=".+?/.+?/.+?.jpg" alt=".+?"><span>.+?</span></a><.+?>(.+?)</.+?>')
        #p=re.compile('<a title="Play".+?href=".+?vodcrid=(.+?)&amp;DF=.+?">(.+?)</a><br></li>')#used for Miss marple
        match1=p.findall(code)
        for url,name in match1:
                res.append((url,name))
        #Get Another version
        p=re.compile('title="Play".+?href=".+?vodcrid=(.+?)">.+?</a><br>(.+?)</li>')
        match2=p.findall(code)
        for url,name in match2:
                res.append((url,name))
        return res
        
                

def getVideo(url):
        res=[]
        f=urllib.urlopen("http://www.itv.com/_app/video/GetMediaItem.ashx?vodcrid=crid://itv.com/"+url+"&bitrate=384&adparams=SITE=ITV/AREA=CATCHUP.VIDEO/SEG=CATCHUP.VIDEO%20HTTP/1.1")
        b=f.read()
        f.close()
        p=re.compile(r'<LicencePlaylist>(.+?) HTTP/1.1</LicencePlaylist>')
        match=p.findall(b)
        for b in match:
                code=re.sub('&amp;','&',b)
                code2=code+"%20HTTP/1.1"
                f=urllib.urlopen(code2)
                a=f.read()
                f.close()
                p=re.compile(r'<Entry><ref href="(.+?)" /><param value="true" name="Prebuffer" /><PARAM NAME="PrgPartNumber" VALUE="(.+?)" />')
                match=p.findall(a)
                for url,name in match:
                        res.append((url,name))
                return res
        

def getBestItvVideos(url):
        res=[]
        f=urllib.urlopen("http://www.itv.com/_app/video/GetMediaItem.ashx?vodcrid="+url+"&bitrate=384&adparams=SITE=ITV/AREA=CATCHUP.VIDEO/SEG=CATCHUP.VIDEO%20HTTP/1.1")
        b=f.read()
        f.close()
        p=re.compile(r'<LicencePlaylist>(.+?) HTTP/1.1</LicencePlaylist>')
        match=p.findall(b)
        for b in match:
                code=re.sub('&amp;','&',b)
                code2=code+"%20HTTP/1.1"
                f=urllib.urlopen(code2)
                a=f.read()
                f.close()
                p=re.compile(r'<Entry><ref href="(.+?)" /><param value="true" name="Prebuffer" /><PARAM NAME="PrgPartNumber" VALUE="(.+?)" />')
                match=p.findall(a)
                for url,name in match:
                        res.append((url,name))
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

      
def addLink(name,url):
        #print name
        #print url
        #print "--"
        ok=True
        thumbnail_url = url.split( "thumbnailUrl=" )[ -1 ]
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail_url)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
        
def showCats():
        cat=[("http://www.itv.com/_data/xml/CatchUpData/CatchUp360/CatchUpMenu.xml", "ITV CATCH-UP  :  A -Z")]
        for url,name in cat:
                addDir(name,url,1)
                addDir("THE BEST OF ITV","http://www.itv.com/BestofITV/default.html",4)
                
def showShows(url,name):
        shows=getShows(url,name)
        for url,name in shows:
                addDir(name,url,2)

def showEpisodes(url):
        Episodes=getEpisodes(url)
        i=0
        for url,name in Episodes:
                i=i+1
                addDir(name+"-Episode-"+str(i),url,3)
   
def showGetUrl(url):
        check=getVideo(url)
        for url,name in check:
                addLink(name,url)

def showGetBestofItvCats():
        addDir("BEST OF CRIME DRAMA","http://www.itv.com/BestofITV/crime/default.html",5)
        addDir("BEST OF PERIOD DRAMA","http://www.itv.com/BestofITV/perioddrama/default.html",6)
        addDir("BEST OF FAMILY DRAMA","http://www.itv.com/BestofITV/familydrama/default.html",7)
        addDir("BEST OF DOCUMENTARIES","http://www.itv.com/BestofITV/documentary/default.html",8)
        addDir("BEST OF COMEDY","http://www.itv.com/BestofITV/comedy/default.html",9)
        addDir("BEST OF CHILDREN'S TV","http://www.itv.com/BestofITV/kids/default.html",10)
        addDir("BEST OF ITV SOAPS","http://www.itv.com/BestofITV/soaps/default.html",11)

def showGetBestofItvCrimeShows(url,name):
        Bestshows=getBestCrimeShows(url,name)
        for url,name in Bestshows:
                addDir(name,url,12)

def showGetBestofItvPeriodShows(url,name):
        Bestshows=getBestPeriodShows(url,name)
        for url,name in Bestshows:
                addDir(name,url,13)

def showGetBestofItvFamilyShows(url,name):
        Bestshows=getBestFamilyShows(url,name)
        for url,name in Bestshows:
                addDir(name,url,14)

def showGetBestofItvDocumentaryShows(url,name):
        Bestshows=getBestDocumentaryShows(url,name)
        for url,name in Bestshows:
                addDir(name,url,15)

def showGetBestofItvComedyShows(url,name):
        Bestshows=getBestComedyShows(url,name)
        for url,name in Bestshows:
                addDir(name,url,16)

def showGetBestofItvChildrensShows(url,name):
        Bestshows=getBestChildrensShows(url,name)
        for url,name in Bestshows:
                addDir(name,url,17)

def showGetBestofItvSoapShows(url,name):
        Bestshows=getBestSoapShows(url,name)
        for url,name in Bestshows:
                addDir(name,url,18)


def showGetBestofItvCrimeEps(url,name):
        Besteps=getBestCrimeEps(url,name)
        for url,name in Besteps:
                addDir(name,url,19)

def showGetBestofItvPeriodEps(url,name):
        Besteps=getBestPeriodEps(url,name)
        for url,name in Besteps:
                addDir(name,url,19)

def showGetBestofItvFamilyEps(url,name):
        Besteps=getBestFamilyEps(url,name)
        for url,name in Besteps:
                addDir(name,url,19)

def showGetBestofItvDocumentaryEps(url,name):
        Besteps=getBestDocumentaryEps(url,name)
        for url,name in Besteps:
                addDir(name,url,19)

def showGetBestofItvComedyEps(url,name):
        Besteps=getBestComedyEps(url,name)
        for url,name in Besteps:
                addDir(name,url,19)

def showGetBestofItvChildrensEps(url,name):
        Besteps=getBestChildrensEps(url,name)
        for url,name in Besteps:
                addDir(name,url,19)

def showGetBestofItvSoapEps(url,name):
        Besteps=getBestSoapEps(url,name)
        for url,name in Besteps:
                addDir(name,url,19)
                
def showGetBestofItvVideos(url,name):
        BestVids=getBestItvVideos(url)
        for url,name in BestVids:
                addLink(name,url)


                
        



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
        print "index of : "+url
        showShows(url,name)
elif mode==2:
        print "Getting Episodes: "+url
        showEpisodes(url)
elif mode==3:
        print "Getting Videofiles: "+url
        showGetUrl(url)
elif mode==4:
        print "Get The Best of Itv: "+url
        showGetBestofItvCats()
elif mode==5:
        print "Get Best Of Itv shows: "+url
        showGetBestofItvCrimeShows(url,name)
elif mode==6:
        print "Get Best Of Itv shows: "+url
        showGetBestofItvPeriodShows(url,name)
elif mode==7:
        print "Get Best Of Itv shows: "+url
        showGetBestofItvFamilyShows(url,name)
elif mode==8:
        print "Get Best Of Itv shows: "+url
        showGetBestofItvDocumentaryShows(url,name)
elif mode==9:
        print "Get Best Of Itv shows: "+url
        showGetBestofItvComedyShows(url,name)
elif mode==10:
        print "Get Best Of Itv shows: "+url
        showGetBestofItvChildrensShows(url,name)
elif mode==11:
        print "Get Best Of Itv shows: "+url
        showGetBestofItvSoapShows(url,name)
elif mode==12:
        print "Get Best Of Itv Crime Episodes: "+url
        showGetBestofItvCrimeEps(url,name)
elif mode==13:
        print "Get Best Of Itv Period drama Videos: "+url
        showGetBestofItvPeriodEps(url,name)
elif mode==14:
        print "Get Best Of Itv Family Drama: "+url
        showGetBestofItvFamilyEps(url,name)
elif mode==15:
        print "Get Best Of Itv Documentaries Episodes: "+url
        showGetBestofItvDocumentaryEps(url,name)
elif mode==16:
        print "Get Best Of Itv Comedy: "+url
        showGetBestofItvComedyEps(url,name)
elif mode==17:
        print "Get Best Of Itv Children`s: "+url
        showGetBestofItvChildrensEps(url,name)
elif mode==18:
        print "Get Best Of Itv Soaps: "+url
        showGetBestofItvSoapEps(url,name)
elif mode==19:
        print "Get Best Of Itv VideoLinks: "+url
        showGetBestofItvVideos(url,name)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
