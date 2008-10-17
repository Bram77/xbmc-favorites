import urllib,urllib2,re,sys,socket,xbmcplugin,xbmcgui

def CATS():
        addDir("ITV CATCH-UP  :  A -Z","http://www.itv.com/_data/xml/CatchUpData/CatchUp360/CatchUpMenu.xml",1,'http://itv-images.adbureau.net/itv/catch-up_Sponsor%20button_1x1_Apr08.jpg')
        addDir("THE BEST OF ITV - CRIME","http://www.itv.com/ClassicTVshows/crime/default.html",4,'http://www.itv.com/img/470x113/TV-Classics-Crime-c7d9e02e-a48e-4e8d-8842-46250b5af367.jpg')
        addDir("THE BEST OF ITV - PERIOD DRAMA","http://www.itv.com/ClassicTVshows/perioddrama/default.html",4,'http://www.itv.com/img/470x113/TV-Classics-Period-Drama-4a332b58-a8b0-44bc-a444-635b7d6358df.jpg')
        addDir("THE BEST OF ITV - FAMILY DRAMA","http://www.itv.com/ClassicTVshows/familydrama/default.html",4,'http://www.itv.com/img/470x113/TV-Classics-Family-Drama-768a59ff-2ab2-432d-9d2f-ffe20cec0632.jpg')
        addDir("THE BEST OF ITV - DOCUMENTARY","http://www.itv.com/ClassicTVshows/documentary/default.html",4,'http://www.itv.com/img/470x113/0891a94b-79ef-4649-8ccf-1ad33f2c7c93.jpg')
        addDir("THE BEST OF ITV - COMEDY","http://www.itv.com/ClassicTVshows/comedy/default.html",4,'http://www.itv.com/img/470x113/TV-Classics-Comedy-8685d32f-eace-490b-8004-d1d44d4a8b9b.jpg')
        addDir("THE BEST OF ITV - KIDS","http://www.itv.com/ClassicTVshows/kids/default.html",4,'http://www.itv.com/img/470x113/04741e4a-ba5e-48ee-ae32-50fe7bde69d1.jpg')
        addDir("THE BEST OF ITV - SOAPS","http://www.itv.com/ClassicTVshows/soaps/default.html",4,'http://www.itv.com/img/470x113/66fb8a0f-db7d-4094-8dcc-119f2c669eaa.jpg')
        addDir('ITV 1-4 LIVE STREAMS','http://minglefrogletpigletdog.com',6,'http://cdn-ll-73.viddler.com/e2/thumbnail_1_d6938e73.jpg')

def STREAMS():
        streams=[]
        req = urllib2.Request('http://www.itv.com/_app/dynamic/AsxHandler.ashx?getkey=please HTTP/1.1')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        key = urllib2.urlopen(req).read()
        for channel in range(1,5):
                req = urllib2.Request('http://www.itv.com/_app/dynamic/AsxHandler.ashx?key='+key+'&simid=sim'+str(channel)+'&itvsite=ITV&itvarea=SIMULCAST.SIM'+str(channel)+'&pageid=4567756521')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                streaminfo = urllib2.urlopen(req).read()
                stream=re.compile('<TITLE>(.+?)</TITLE><REF href="(.+?)" />').findall(streaminfo)
                streams.append(stream[1])
        for name,url in streams:
                addLink(name,url)

def BESTOF(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req).read()
        eps=re.compile('<li><a href="(.+?)"><img src=".+?" alt="(.+?)"></a><h4>').findall(response)
        for url,name in eps:
                addDir(name,url,5,'')
                
def BESTOFEPS(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req).read()
        eps=re.compile('<a title="Play" href=".+?vodcrid=crid://itv.com/(.+?)&amp;DF=0">(.+?)</a><br>').findall(response)
        for url,name in eps:
                addDir(name,url,3,'')
        
def SHOWS(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req).read()
        code=re.sub('&amp;','&',response)
        match=re.compile('<ProgrammeId>(.+?)</ProgrammeId>\r\n      <ProgrammeTitle>(.+?)</ProgrammeTitle>\r\n').findall(code)
        for url,name in match:
                addDir(name,url,2,'')

def EPS(url):
        req = urllib2.Request("http://www.itv.com/_app/Dynamic/CatchUpData.ashx?ViewType=1&Filter="+url+"&moduleID=115107")
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req).read()
        match=re.compile(r'<h3><a href=".+?.html?.+?=.+?&amp;Filter=(.+?)">(.+?)</a></h3>\r\n        <p class="date">.+?</p>\r\n        <p class="progDesc">.+?</p>\r\n').findall(response);i=0
        for url,name in match:
                i=i+1
                addDir(name+"-Episode-"+str(i),url,3,'')

def VIDEO(url):
        req = urllib2.Request("http://www.itv.com/_app/video/GetMediaItem.ashx?vodcrid=crid://itv.com/"+url+"&bitrate=384&adparams=SITE=ITV/AREA=CATCHUP.VIDEO/SEG=CATCHUP.VIDEO%20HTTP/1.1")
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req).read()
        match=re.compile(r'<LicencePlaylist>(.+?) HTTP/1.1</LicencePlaylist>').findall(response)
        for b in match:
                code=re.sub('&amp;','&',b)
                code2=code+"%20HTTP/1.1"
                req = urllib2.Request(code2)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                response = urllib2.urlopen(req).read()
                match=re.compile(r'<Entry><ref href="(.+?)" /><param value="true" name="Prebuffer" /><PARAM NAME="PrgPartNumber" VALUE="(.+?)" />').findall(response)
                for url,name in match:
                        addLink(name,url)
                       

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
        thumbnail_url = url.split( "thumbnailUrl=" )[ -1 ]
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail_url)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name,iconImage="DefaultVideo.png", thumbnailImage=iconimage)
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
        CATS()
elif mode==1:
        print "index of : "+url
        SHOWS(url)
elif mode==2:
        print "Getting Episodes: "+url
        EPS(url)
elif mode==3:
        print "Getting Videofiles: "+url
        VIDEO(url)
elif mode==4:
        print "Getting Videofiles: "+url
        BESTOF(url)
elif mode==5:
        print "Getting Videofiles: "+url
        BESTOFEPS(url)
elif mode==6:
        print "Getting Videofiles: "+url
        STREAMS()



xbmcplugin.endOfDirectory(int(sys.argv[1]))
