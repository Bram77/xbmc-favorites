#Live Music Archive (archive.org) default.py
#by rwparris2

import urllib,urllib2,re
import xbmcplugin,xbmcgui
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup

xbmcplugin.setContent(int(sys.argv[1]), 'songs')
xbmcplugin.addSortMethod(int(sys.argv[1]), 7)
xbmcplugin.addSortMethod(int(sys.argv[1]), 9)


def getLink(site):
    req = urllib2.Request(site)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link

def addDir(name,url,mode):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name)
    liz.setInfo( type="Music", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def addLink(name,url,artist,album,track):
    ok=True
    liz=xbmcgui.ListItem(name)
    liz.setInfo( type="Music", infoLabels={"Title": name,"Album":album,"Artist":artist, "Track":track } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok

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

######################################################################
def getBandList(link):
    bandList=[]
    p=re.compile('<li><a href="(.+?)">(.+?)</a>')
    match=p.findall(link)
    for band in match:
        bandList.append(band)
    return bandList

def alphList(bandList,letter):
    alphList=[]
    if letter=='0':
        num='.0123456789'
        for n in range(0,10):
            for i in range(len(bandList)):
                if bandList[i][1][0]==num[n]:
                    alphList.append(bandList[i])
    else:
        for i in range(len(bandList)):
            if bandList[i][1][0]==letter:
                alphList.append(bandList[i])
    return alphList

def showBandList(bandList):
    i=0
    while(i<len(bandList)):
        addDir(bandList[i][1],bandList[i][0],4)
        i+=1
    return bandList

def getShowList(link):
    tree=BeautifulSoup(link)
    d=tree.findAll('a', 'titleLink')
    showList=[]
    for i in range(len(d)):
        p=re.compile('href="(.+?)">.*</span> (Live at.+?)</a>')
        match=p.findall(str(d[i]))
        for show in match:
            showList.append(show)
    for n in range(len(showList)):
        s=re.compile('<span class="searchTerm">|</span>')
        tmp=str(showList[n][1])
        tmp=s.sub('',str(showList[n][1]))
        addDir(str(n)+'. '+tmp,showList[n][0],6)

def getPageNumber(link):
    p=re.compile('&nbsp; <a href=".*page=(.+?)">Last</a>')
    match=p.findall(link)
    for pageNumber in match:
        return pageNumber

def getFileTypes(url):
    #list filetypes
    p=re.compile('/details/(.*)')
    match=p.findall(url)
    for name in match:
        temp= 'http://www.archive.org/download/'+name+'/'+name+'_files.xml'
    link=getLink(temp)
    tree=BeautifulStoneSoup(link)

    shn=tree.findAll('file', attrs= {"name" : re.compile('(.+?\.shn$)')})
    m3u=tree.findAll('file', attrs= {"name" : re.compile('(.+?\.m3u$)')})
    flac=tree.findAll('file', attrs= {"name" : re.compile('(.+?\.flac$)')})
    mp3=tree.findAll('file', attrs= {"name" : re.compile('(.+?64kb\.mp3$)')})
    vbr=tree.findAll('file', attrs= {"name" : re.compile('(.+?vbr\.mp3$)')})

    if len(m3u)>0:
        addDir('.m3u Playlists',temp,7)
    if len(flac)>0:
        addDir('1. Flac Files',temp,7)
    if len(mp3)>0:
        addDir('2. VBR mp3',temp,7)
    if len(vbr)>0:
        addDir('3. 64kB mp3',temp,7)
    if len(shn)>0:
        addDir('1. Shorten Files',temp,7)

def getTracks(url,rx):
    p=re.compile('(http://www.archive.org/download.*)/.*')
    match=p.findall(url)
    for name in match:
        temp=name
    link=getLink(url)
    tree=BeautifulStoneSoup(link)
    trackList=tree.findAll('file', attrs= {"name" : re.compile(rx)})
    for i in range(len(trackList)):
        url=temp+'/'+trackList[i]['name']
        name=trackList[i].title.contents[0]
        artist=trackList[i].creator.contents[0]
        album=trackList[i].album.contents[0]
        track=trackList[i].track.contents[0]
        addLink(name,url,artist,album,track)
    

######################################################################

site='http://www.archive.org/browse.php?collection=etree&field=%2Fmetadata%2Fcreator'
#site='file:///C:/Program Files/XBMC/plugins/music/archive.org_del.later/artistList.php.html'
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

if mode==None or url==None or len(url)<1:
    addDir('Artists A-Z',site,0)
    addDir('Browse all Artists',site,1)

if mode==0:
    addDir('0-9, et al.','0',3)
    bet='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for i in range(0,26):
        addDir(bet[i],bet[i],3)
if mode==1:
    link=getLink(site)
    bandList=getBandList(link)
    showBandList(bandList)
if mode==2:
    print 'search'
if mode==3:
    link=getLink(site)
    bandList=getBandList(link)
    bandList=alphList(bandList,url)
    showBandList(bandList)
if mode==4:
    link=getLink('http://www.archive.org'+url)
    pageNumber=getPageNumber(link)
    if pageNumber==None:
        getShowList(link)
    else:
        for i in range(1,int(pageNumber)+1):
            addDir('Page '+str(i),url+'&page='+str(i),5)    
if mode==5:
    link=getLink('http://www.archive.org'+url)
    getShowList(link)
if mode==6:
    getFileTypes(url)
if mode==7:
    if name=='.m3u Playlists':
        p=re.compile('(http://www.archive.org/download.*)/.*')
        match=p.findall(url)
        for name in match:
            temp=name
        link=getLink(url)
        tree=BeautifulStoneSoup(link)
        m3u=tree.findAll('file', attrs= {"name" : re.compile('(.+?\.m3u$)')})
        for i in range(len(m3u)):
            addLink(m3u[i].format.contents[0].string,temp+'/'+m3u[i]['name'],"","")
    elif name=='1. Flac Files':
        getTracks(url,'(.+?\.flac$)')
    elif name=='1. Shorten Files':
        getTracks(url,'(.+?\.shn$)')
    elif name=='2. VBR mp3':
        getTracks(url,'(.+?vbr\.mp3$)')
    elif name=='3. 64kB mp3':
        getTracks(url,'(.+?64kb\.mp3$)')
'''if mode==8:
    p=re.compile('(http://www.archive.org/download.*)/.*')
    match=p.findall(url)
    for name in match:
        temp=name
    link=getLink(url)
    tree=BeautifulStoneSoup(link)
    flac=tree.findAll('file', attrs= {"name" : re.compile('(.+?\.flac$)')})
    for i in range(len(flac)):
        url=temp+'/'+flac[i]['name']
        name=flac[i].track.contents[0]+'. '+flac[i].title.contents[0]
        addLink(name,url)'''



xbmcplugin.endOfDirectory(int(sys.argv[1]))
