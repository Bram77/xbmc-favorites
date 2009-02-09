# XBMC Video Plugin
# National Geographic
# Date: 02/07/09
# Author: stacked < http://xbmc.org/forum/member.php?u=26908 >
# Changelog & More Info: http://xbmc.org/forum/showthread.php?t=45132

import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback

def sectionlist():
	url='http://video.nationalgeographic.com/video/player/data/xml/sectionlist.xml'
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6')
	f=urllib2.urlopen(req)
	a=f.read()
	f.close()
	data=re.compile('<section id="(.+?)">(.+?)</section>').findall(a)
	cell=0
	for info in data:
		sectionid=data[cell][0]
		name=data[cell][1]
		name=clean(name)
		url='http://video.nationalgeographic.com/video/player/data/xml/section_'+sectionid+'.xml'
		li=xbmcgui.ListItem(name)
		u=sys.argv[0]+"?mode=1&name="+urllib.quote_plus(name)+"&url="+urllib.quote_plus(url)
		xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,li,True)
		cell=cell+1

def section(url, name):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6')
	f=urllib2.urlopen(req)
	a=f.read()
	f.close()
	data=re.compile('<children>(.+?)</children>', re.DOTALL).findall(a)
	catdata=re.compile('<category id="(.+?)" >').findall(data[0])
	title=re.compile('<name>(.+?)</name>').findall(data[0])
	check=re.compile('<hasVideo>(.+?)</hasVideo>').findall(data[0])
	cell=0
	for info in catdata:
		categoryid=catdata[cell]
		name=title[cell]
		name=clean(name)
		if (check[cell]=='true'):
			url='http://video.nationalgeographic.com/video/player/data/xml/category_assets_'+categoryid+'.xml'
			u=sys.argv[0]+"?mode=3&name="+urllib.quote_plus(name)+"&url="+urllib.quote_plus(url)
		else:
			url='http://video.nationalgeographic.com/video/player/data/xml/category_'+categoryid+'.xml'
			u=sys.argv[0]+"?mode=2&name="+urllib.quote_plus(name)+"&url="+urllib.quote_plus(url)
		thumb='http://video.nationalgeographic.com/video/player/media/featured_categories/'+categoryid+'_102x68.jpg'
		li=xbmcgui.ListItem(name)
		xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,li,True)
		cell=cell+1

def category(url, name):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6')
	f=urllib2.urlopen(req)
	a=f.read()
	f.close()
	data=re.compile('<children>(.+?)</children>', re.DOTALL).findall(a)
	catdata=re.compile('<category id="(.+?)" >').findall(data[0])
	title=re.compile('<name>(.+?)</name>').findall(data[0])
	cell=0
	for info in catdata:
		categoryid=catdata[cell]
		name=title[cell]
		name=clean(name)
		url='http://video.nationalgeographic.com/video/player/data/xml/category_assets_'+categoryid+'.xml'
		thumb='http://video.nationalgeographic.com/video/player/media/'+categoryid+'/'+categoryid+'_150x100.jpg'
		li=xbmcgui.ListItem(name)
		u=sys.argv[0]+"?mode=3&name="+urllib.quote_plus(name)+"&url="+urllib.quote_plus(url)
		xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,li,True)
		cell=cell+1

def category_assets(url, name):
	thisurl=url
	new=url[:-4]
	if (page != 0):
		req = urllib2.Request(new+'_'+str(int(page))+'.xml')
	else:
		req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6')
	f=urllib2.urlopen(req)
	a=f.read()
	f.close()
	data=re.compile('<videoasset refid="(.+?)">').findall(a)
	data2=re.compile('<title>(.+?)</title>').findall(a)
	data3=re.compile('<assetlist total="(.+?)" totalpages="(.+?)" page="(.+?)" pagesize="(.+?)">').findall(a)
	cell=0
	for info in data:
		refid=data[cell]
		name=data2[cell]
		name1=clean(name)
		name = str((cell+1)+(page*10)-(1*page))+'. '+name1
		url='http://video.nationalgeographic.com/video/cgi-bin/cdn-auth/cdn_tokenized_url.pl?slug='+refid+'&siteid=popupmain'
		thumb='http://video.nationalgeographic.com/video/player/media/'+refid+'/'+refid+'_480x360.jpg'
		li=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
		u=sys.argv[0]+"?mode=4&name="+urllib.quote_plus(name1)+"&url="+urllib.quote_plus(url)
		xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,li)
		cell=cell+1
	if (data3[0][1] != data3[0][2]):
		li=xbmcgui.ListItem("Next Page")
		u=sys.argv[0]+"?mode=3&name="+urllib.quote_plus(name)+"&url="+urllib.quote_plus(thisurl)+"&page="+str(int(page)+1)
		xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,li,True)

def clean(name):
	remove=[('&amp;','&'),('&quot;','"'),('&#233;','e'),('&#8212;',' - '),('&#39;','\''),('&#46;','.'),('&#58;',':')]
	for trash, crap in remove:
		name=name.replace(trash,crap)
	return name
		
def playVideo(url, name):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6')
	f=urllib2.urlopen(req)
	a=f.read()
	f.close()
	data=re.compile('<tokenizedURL>(.+?)</tokenizedURL>').findall(a)
	url=data[0]
	url=url.replace('amp;','')
	badchars = '\\/:*?\"<>|'
	for c in badchars:
		name = name.replace(c, '')
	name=name+'.flv'
	def Download(url,dest):
			dp = xbmcgui.DialogProgress()
			dp.create('Downloading','',name)
			urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
	def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
			try:
					percent = min((numblocks*blocksize*100)/filesize, 100)
					dp.update(percent)
			except:
					percent = 100
					dp.update(percent)
			if dp.iscanceled():
					dp.close()
	flv_file = None
	stream = 'false'
	if (xbmcplugin.getSetting('download') == 'true'):
			flv_file = xbmc.translatePath(os.path.join(xbmcplugin.getSetting('download_Path'), name))
			Download(url,flv_file)
	elif (xbmcplugin.getSetting('download') == 'false' and xbmcplugin.getSetting('download_ask') == 'true'):
		dia = xbmcgui.Dialog()
		ret = dia.select('What do you want to do?', ['Download & Play', 'Stream', 'Exit'])
		if (ret == 0):
			flv_file = xbmc.translatePath(os.path.join(xbmcplugin.getSetting('download_Path'), name))
			Download(url,flv_file)
		elif (ret == 1):
			stream = 'true'
		else:
			pass
	elif (xbmcplugin.getSetting('download') == 'false' and xbmcplugin.getSetting('download_ask') == 'false'):
		stream = 'true'
	if xbmcplugin.getSetting("dvdplayer") == "true":
		player_type = xbmc.PLAYER_CORE_DVDPLAYER
	else:
		player_type = xbmc.PLAYER_CORE_MPLAYER
	if (flv_file != None and os.path.isfile(flv_file)):
		xbmc.Player(player_type).play(str(flv_file))
	elif (stream == 'true'):
		xbmc.Player(player_type).play(str(url))
	xbmc.sleep(200)

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

params=get_params()
mode=None
name=None
url=None
page=0
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
try:
        page=int(params["page"])
except:
        pass

if mode==None:
	sectionlist()
elif mode==1:
	section(url, name)
elif mode==2:
	category(url, name)
elif mode==3:
	category_assets(url, name)
elif mode==4:
	playVideo(url, name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))

    
