import urllib,urllib2,re,xbmcplugin,xbmcgui
#NINJAVIDEO PLUGIN FOR XBMC 2008.#

def indexcats():
        addDirSpecial("1. ANIME","http://www.ninjavideo.net/anime",1,"http://mediaicons.org/Services/GetIcon.ashx?key=57097&format=2&style=0&type=med")
        addDirSpecial( "2. MOVIES","http://www.ninjavideo.net/movies",5,"http://mediaicons.org/Services/GetIcon.ashx?key=59368&format=2&style=0&type=med")
        addDirSpecial( "3. TV SHOWS","http://www.ninjavideo.net/tvshows",1,"http://mediaicons.org/Services/GetIcon.ashx?key=17875&format=2&style=0&type=med")
        addDirSpecial("6. DOCUMENTARIES","http://www.ninjavideo.net/docus",6,"http://www.planetrapido.com/images/shwpnl.4.scr.jpg")
        addDirSpecial( "5. CARTOONS","http://www.ninjavideo.net/cartoons",1,"http://mediaicons.org/Services/GetIcon.ashx?key=87684&format=2&style=0&type=med")
        addDirSpecial( "7. SPORTS","http://www.ninjavideo.net/sports",9,"http://mediaicons.org/Services/GetIcon.ashx?key=57089&format=2&style=0&type=med")
        addDirSpecial( "8. MUSIC","http://www.ninjavideo.net/music",8,"http://mediaicons.org/Services/GetIcon.ashx?key=56724&format=2&style=0&type=med")
        addDirSpecial( "4. COMEDY","http://www.ninjavideo.net/comedy",7,"http://mediaicons.org/Services/GetIcon.ashx?key=7527&format=2&style=0&type=med")

def indexmoviecats():
        addDirSpecial("NEW RELEASES","http://www.ninjavideo.net/cat/25",3,"http://mediaicons.org/Services/GetIcon.ashx?key=66965&format=2&style=0&type=med")
        addDirSpecial("STAFF FAVORITES","http://www.ninjavideo.net/cat/26",3,"http://www.iconarchive.com/icons/icons-land/vista-elements/Favorites-256x256.png")

def indexcomedycats():
        addDirSpecial("CHAPPELLES' SHOW","http://www.ninjavideo.net/cat/419",2,"http://sharetv.org/images/chappelles_show-show.jpg")
        addDirSpecial("STAND UP","http://www.ninjavideo.net/cat/369",3,"http://mediaicons.org/Services/GetIcon.ashx?key=53241&format=2&style=0&type=med")
        addDirSpecial("ALI G","http://www.ninjavideo.net/cat/543",2,"http://www.people.cornell.edu/pages/agp9/ali%20g.jpg")
        addDirSpecial("LAST COMIC STANDING","http://www.ninjavideo.net/cat/701",2,"http://farm1.static.flickr.com/60/175613128_c2c344968f.jpg")
        addDirSpecial("MIND OF MENCIA","http://www.ninjavideo.net/cat/562",2,"http://image.com.com/tv/images/genie_images/story/DVDimages/mindofmencia_3_DVD.jpg")
def indexdocucats():
        addDirSpecial("1. ACADEMY AWARD WINNING","http://www.ninjavideo.net/cat/211",3,"http://ninjavideo.net/images/external/docus/academyawardwinning.png")
        addDirSpecial("2. ADVENTURE","http://www.ninjavideo.net/cat/241",3,"http://ninjavideo.net/images/external/docus/adventure.png")
        addDirSpecial("3. ARCHAEOLOGY / ANTHROPOLOGY","http://www.ninjavideo.net/cat/263",3,"http://ninjavideo.net/images/external/docus/archaeologyandanthropology.png")
        addDirSpecial("4. BIOGRAPHIES","http://www.ninjavideo.net/cat/212",3,"http://ninjavideo.net/images/external/docus/biographies.png")
        addDirSpecial("5. COUNTER CULTURE / DRUGS","http://www.ninjavideo.net/cat/307",3,"http://ninjavideo.net/images/external/docus/counterculture.png")
        addDirSpecial("6. CRIME","http://www.ninjavideo.net/cat/463",3,"http://ninjavideo.net/images/external/docus/crime.png")
        addDirSpecial("7. DISASTER","http://www.ninjavideo.net/cat/217",3,"http://ninjavideo.net/images/external/docus/disasters.png")
        addDirSpecial("8. ENGINEERING","http://www.ninjavideo.net/cat/223",3,"http://ninjavideo.net/images/external/docus/engineering.png")
        addDirSpecial("9. HISTORY","http://www.ninjavideo.net/cat/202",3,"http://mediaicons.org/Services/GetIcon.ashx?key=1354&format=2&style=2&type=med")
        addDirSpecial("10. IMAX","http://www.ninjavideo.net/cat/214",3,"http://ninjavideo.net/images/external/docus/imax.png")
        addDirSpecial("11. MILITARY / WARFARE","http://www.ninjavideo.net/cat/331",3,"http://ninjavideo.net/images/external/docus/military.png")
        addDirSpecial("12. MUSIC","http://www.ninjavideo.net/cat/275",3,"http://ninjavideo.net/images/external/docus/music.png")
        addDirSpecial("13. LOCOMOTIVE TECHNOLOGY","http://www.ninjavideo.net/cat/221",3,"http://ninjavideo.net/images/external/docus/technology.png")
        addDirSpecial("14. SCIENCE","http://www.ninjavideo.net/cat/254",3,"http://ninjavideo.net/images/external/docus/science.png")
        addDirSpecial("15. SPACE ","http://www.ninjavideo.net/cat/200",3,"http://ninjavideo.net/images/external/docus/space.png")
        addDirSpecial("16. AL-JAZEERA","http://www.ninjavideo.net/cat/850",3,"http://www2.fanscape.com/betamasters/images/aljazeera.jpg")

def indexmusiccats():
        addDirSpecial("1. CLASSIC ROCK","http://www.ninjavideo.net/cat/249",3,"http://ninjavideo.net/images/external/music/classicrock.png")
        addDirSpecial("2. CLASSICAL","http://www.ninjavideo.net/cat/245",3,"http://ninjavideo.net/images/external/music/classical.png")
        addDirSpecial("3. CLUB / TECHNO","http://www.ninjavideo.net/cat/253",3,"http://ninjavideo.net/images/external/music/club.png")
        addDirSpecial("4. COUNTRY","http://www.ninjavideo.net/cat/248",3,"http://ninjavideo.net/images/external/music/country.png")
        addDirSpecial("5. HIP HOP","http://www.ninjavideo.net/cat/246",3,"http://ninjavideo.net/images/external/music/hiphop.png")
        addDirSpecial("6. POP","http://www.ninjavideo.net/cat/252",3,"http://ninjavideo.net/images/external/music/pop.png")
        addDirSpecial("7. PUNK / SKA","http://www.ninjavideo.net/cat/247",3,"http://ninjavideo.net/images/external/music/punk.png")
        addDirSpecial("8. RNB / SOUL","http://www.ninjavideo.net/cat/250",3,"http://ninjavideo.net/images/external/music/rnb.png")
        addDirSpecial("9. ROCK / METAL","http://www.ninjavideo.net/cat/243",3,"http://ninjavideo.net/images/external/music/rockmetal.png")
        addDirSpecial("10. WORLD","http://www.ninjavideo.net/cat/251",3,"http://ninjavideo.net/images/external/music/world.png")

def indexsportcats():
        addDirSpecial("1. BASKETBALL","http://www.ninjavideo.net/cat/462",3,"http://ninjavideo.net/images/external/sports/basketball.png")
        addDirSpecial("2. CYCLING","http://www.ninjavideo.net/cat/466",3,"http://z.about.com/d/renotahoe/1/0/P/-/-/-/tourdenez1.jpg")
        addDirSpecial("3. BOXING","http://www.ninjavideo.net/cat/161",3,"http://ninjavideo.net/images/external/sports/delahoyavsforbes.png")
        addDirSpecial("4. CIRQUE DU SOLEIL","http://www.ninjavideo.net/cat/376",3,"http://ninjavideo.net/images/external/sports/cirque.png")
        addDirSpecial("5. ULTIMATE FIGHTING","http://www.ninjavideo.net/cat/193",3,"http://ninjavideo.net/images/external/sports/ultimatefighter.png")
        addDirSpecial("6. WRESTLING","http://www.ninjavideo.net/cat/445",3,"http://ninjavideo.net/images/external/sports/tna.png")
        
      
def shows(url,name):
        res=[]
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
        
def seasons(url,name):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        clean=re.sub('&amp;','&',link)
        clean1=re.sub("\xe2\x80\x99","'",clean)
        clean2=re.sub('\xc5\xab','u',clean1)
        response.close()
        p=re.compile(' <a href="(.+?)">(.+?)</a>')
        match=p.findall(clean2)
        for url,name in match:
                res.append((url,name))
        p=re.compile('\n<a href="(.+?)">(.+?)</a> ')
        match=p.findall(clean2)
        for url,name in match:
                res.append((url,name))
        p=re.compile('\n<a href="(.+?)">.+?</a></p>')
        match=p.findall(link)
        for url in match:
                res.append((url,"MISC SEASON"))
        for url,name in res:
                addDir(name,url,3)
        if len(match)<1:
                p=re.compile('\n<a href="(.+?)">(.+?)</a>\n<br />')
                match=p.findall(link)
                for url,name in match:
                        addDir(name,url,3)
        
def episodes(url,name):
        res=[]
        req = urllib2.Request(url)
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

def vidlinks(url):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        clean=re.sub('&amp;','&',link)
        clean1=re.sub("\xe2\x80\x99","'",clean)
        clean2=re.sub('\xc5\xab','u',clean1)
        response.close()
        p=re.compile('<param name="src" value="(.+?)" />\n<param name=".+?" value="(.+?)" />')
        match=p.findall(clean2)
        for url,name in match:
                addLink(name,url+"?.avi")
  
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
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png")
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addLinkSpecial(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
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

def addDirSpecial(name,url,mode,iconimage):
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
        print "main category index : "
        indexcats()
elif mode==1:
        print "index of shows : "+url
        shows(url,name)
elif mode==2:
        print "index of seasons : "+url
        seasons(url,name)
elif mode==3:
        print "index of episodes : "+url
        episodes(url,name)
elif mode==4:
        print "index of videolinks : "+url
        vidlinks(url)
elif mode==5:
        print "index of moviecats : "+url
        indexmoviecats()
elif mode==6:
        print "index of Docucats : "+url
        indexdocucats()
elif mode==7:
        print "index of Comedycats : "+url
        indexcomedycats()
elif mode==8:
        print "index of Musicats : "+url
        indexmusiccats()
elif mode==9:
        print "index of Sportcats : "+url
        indexsportcats()


xbmcplugin.endOfDirectory(int(sys.argv[1]))
