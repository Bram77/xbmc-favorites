import urllib,urllib2,re,sys,xbmcplugin,xbmcgui

#Podaudio/Librivox Plugin - By Voinage 2008.

def MAINCATS():
        addDir("POD-AUDIO","http://podiobooks.com/",1,"")
        addDir("LIBRIVOX","http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=0",4,"")

def ALPHABET():
        addDir('A','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=0',4,'')
        addDir('B','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=120',4,'')
        addDir('C','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=280',4,'')
        addDir('D','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=360',4,'')
        addDir('E','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=440',4,'')
        addDir('F','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=480',4,'')
        addDir('G','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=480',4,'')
        addDir('H','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=560',4,'')
        addDir('I','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=640',4,'')
        addDir('J','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=640',4,'')
        addDir('K','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=680',4,'')
        addDir('L','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=720',4,'')
        addDir('M','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=800',4,'')
        addDir('N','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=920',4,'')
        addDir('O','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=960',4,'')
        addDir('P','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=960',4,'')
        addDir('Q','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=1000',4,'')
        addDir('R','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=1000',4,'')
        addDir('S','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=1040',4,'')
        addDir('T','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=1160',4,'')
        addDir('U','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=1200',4,'')
        addDir('V','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=1240',4,'')
        addDir('W','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=1440',4,'')
        addDir('X','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=1520',4,'')
        addDir('Y','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=1520',4,'')
        addDir('Z','http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=1520',4,'')

        
def INDEX(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()        
        p=re.compile('<option label="(.+?)" value="(.+?)">.+?</option>')
        match=p.findall(link)
        for name,ident in match:
                main="http://podiobooks.com/podiobooks/search.php?category="+ident
                thumbnail="http://www.podiobooks.com/images/podiobooks300x300.jpg"
                addDir(name,main,2,thumbnail)

def INDEX2(url):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()        
        p=re.compile('<a href="(.+?)"><img vspace=".+?" hspace=".+?" align="left" src="(.+?)" alt="(.+?)"  border=0 /></a></td>')
        match=p.findall(link)
        for url2,thumbnail,name in match:
                main="http://podiobooks.com/"+url2+"/feed"
                thumbnail="http://podiobooks.com/"+thumbnail
                res.append((name,main,thumbnail))
        for name,url,thumbnail in res:
                addDir(name,url,3,thumbnail)

def AUDIO(url):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('<itunes:image href="(.+?)"/>\n\t')
        thumb=p.findall(link)
        p=re.compile('<title>(.+?)</title>\n\t\t\t<link>.+?</link>\n\t\t\t<comments>.+?</comments>\n\t\t\t<description>.+?</description>\n\t\t\t<category>.+?</category>\n\t\t\t<category>.+?</category>\n\t\t\t<category>.+?</category>\n\t\t\t<guid isPermaLink="false">.+?</guid>\n\t\t\t<pubDate>.+?</pubDate>\n\t\t\t<author>.+?</author>\n\t\t\t<enclosure url="(.+?)"')
        match=p.findall(link)
        i=0
        for name,mp3 in match:
                i=i+1
                #mp3=re.sub('.mp3','',mp3)
                thumbnail=thumb[0]
                addLink(str(i)+". "+ name,mp3,thumbnail)

def LIBRIVOX(url):
        res=[]
        url=url+"&"
        req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('<li><a href="(.+?)">.+?"(.+?)"</a>')
        match=p.findall(link)
        for uri,name in match:
                addDir(name,uri,5,"")        
        p=re.compile('http://librivox.org/newcatalog/search.+?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset=(.+?)&')
        next=p.findall(url)
        for page in next:
                nextpage='http://librivox.org/newcatalog/search.php?reader=&mc=&bc=&cat=&genre=&language=&type=&author=&title=&status=complete&reader_exact=&mc_exact=&bc_exact=&date=&offset='+str(int(page)+40)
                addDir(" NEXT PAGE",nextpage,4,"")
                
def LIBRIVOXAUDIO(url):
        res=[]
        req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('<em>(.+?)</em> .+? <br />\nSource: <a href=".+?">.+?</a><br />\n.+?<a href="(.+?)">(.+?)</a>.+?<br />\n.+?<a href="(.+?)">(.+?)</a>.+?<br />\n.+?<a href="(.+?)">(.+?)</a>.+?\n</li>\n')
        match=p.findall(link)
        for mainname,lowmp3,lowname,medmp3,medname,highogg,highoggname in match:
                addLink(mainname+" "+lowname,lowmp3,'')
                addLink(mainname+" "+medname,medmp3,'')
                addLink(mainname+" "+highoggname,highogg,'')
                
        p=re.compile('<em>(.+?)</em> .+? <br />\n.+?<a href="(.+?)">(.+?)</a>.+?<br />\n.+?<a href="(.+?)">(.+?)</a>.+?<br />\n.+?<a href="(.+?)">(.+?)</a>.+?<br />')
        match2=p.findall(link)
        for mainname,lowmp3,lowname,medmp3,medname,highogg,highoggname in match2:
                addLink(mainname+" "+lowname,lowmp3,'')
                addLink(mainname+" "+medname,medmp3,'')
                addLink(mainname+" "+highoggname,highogg,'')                        
        
        
                                
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
        print "categories"
        MAINCATS()
elif mode==1:
        print "index of : "+url
        INDEX(url)
elif mode==2:
        print "index of : "+url
        INDEX2(url)
elif mode==3:
        print "index of : "+url
        AUDIO(url)
elif mode==4:
        print "index of : "+url
        LIBRIVOX(url)
elif mode==5:
        print "index of : "+url
        LIBRIVOXAUDIO(url)
elif mode==6:
        print "index of : "+url
        ALPHABET()

        
xbmcplugin.endOfDirectory(int(sys.argv[1]))
