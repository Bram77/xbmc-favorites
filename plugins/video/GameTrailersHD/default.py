'''
	GameTrailers v0.6
		A boxee/xbmc plugin for www.gametrailers.com
'''

__plugin__ = "GameTrailers"
__author__ = "riegersn"
__url__ = "http://code.google.com/p/boxee-plugins"
__svn__ = "svn/trunk/plugins/video/GameTrailersHD/"
__version__ = "0.6"

import urllib, urllib2, re
import string, os, time, datetime
import xbmc, xbmcgui, xbmcplugin
from BeautifulSoup import *


#grab to root directory and assign the image forlder a var
rootDir = os.getcwd()
if rootDir[-1] == ';':rootDir = rootDir[0:-1]
imageDir = os.path.join(rootDir, 'resources', 'thumbnails') + '/'

#setup default platforms to pull video from
platforms = [
	{'type':'xb360', 'name':'Xbox 360'},
	{'type':'xbla', 'name':'Xbox Live Arcade'},
	{'type':'ps3', 'name':'PlayStation 3'},
	{'type':'psp', 'name':'PSP'},
	{'type':'wii', 'name':'Nintendo Wii'},
	{'type':'ds', 'name':'Nintendo DS'},
	{'type':'pc', 'name':'PC'}]


def catsInitial():
	addDir('Podcasts','http://www.gametrailers.com/podcasts.php', 3 , imageDir + 'logo_gt_rss.png')
	addDir('Game Trailers','http://www.gametrailers.com/gthd.php', 3 , imageDir + 'logo_gt_hd.png')

def catsHDRSS(url):
	if 'gthd.php' in url:
		addDir('Game Trailers','%s%s' % (url,'?p={platform}&show=Trailers'), 4 , imageDir + 'trailers.png')
		addDir('Game Reviews','%s%s' % (url,'?p={platform}&show=Reviews'), 4 , imageDir + 'reviews.png')
		addDir('Gameplay Video','%s%s' % (url,'?p={platform}&show=Gameplay'), 4 , imageDir + 'gameplay.png')
		addDir('Developer Interviews','%s%s' % (url,'?p={platform}&show=Interview'), 4 , imageDir + 'interviews.png')
	else:
		for feed in getRssCats(url):
			addDir(feed['title'],feed['rss'], 5, feed['image'], feed['plot'])

def getRssCats(url):
	print 'DEF:: getRssCats()'
	links = []; data = []; titles = []; desc = []
	html = getHTML(url, '<div class="basicinfo_text">', '<div class="rightthin_content">')
	soup = BeautifulSoup(html)
	href = soup.findAll('a')
	thumbs = soup.findAll('img')
	info = soup.findAll(attrs={'class':'gen_text'})
	for i in info:
		titles.append(i.findAll('b')[0].string.strip())
		desc.append(str(i).split('<br />')[1].strip())
	for i in href:
		if 'direct link' in str(i).lower():
			links.append(i['href'])
	for index, i in enumerate(links):
		data.append( { 'title':titles[index], 'rss':links[index], 'image':thumbs[index]['src'], 'plot':desc[index] } )
	return data

def catsPodcasts(url):
	print 'DEF:: catsPodcasts()'
	xml = BeautifulStoneSoup(getHTML('http://www.gametrailers.com/'+url))
	links = re.compile('<enclosure url="(.+?)"').findall(str(xml))
	dates = re.compile('<pubDate>(.+?)</pubDate>').findall(str(xml))
	titles = xml.findAll('title')[1:]
	desc = xml.findAll('itunes:subtitle')[1:]
	print dates
	for index, i in enumerate(links):
		info = ['',desc[index].string.strip(),'']
		addLink(titles[index].string.strip(),i,info)


def catsPlatforms(url):
	for i in platforms:
		addDir(i['name'],url.replace('{platform}', i['type']), 1 , imageDir + 'icon_' + i['type'] + '.png')
		print imageDir + 'icon_' + i['type'] + '.png'

"""
	grabLinks()
	function used to pull video links from the given page as well as next and
	previous buttons if they are available.
"""
def grabLinks(url):
	data = []
	html = getHTML(url).split('<div id="stuff">')[1]
	soup = BeautifulSoup(html.split("<!--end of second contentwrapper-->")[0].strip())

	pagelink_next = ''
	pagelink_prev = ''
	pagelink = soup.findAll(attrs={'class' : "reviewlist_barlink reviewlist_barlink_gthd"})
	if len(pagelink) > 2:
		if 'Next' in pagelink[-1].string:
			pagelink_next = pagelink[-1]['href']
		if 'Previous' in pagelink[0].string:
			pagelink_prev = pagelink[0]['href']

	titles = soup.findAll(attrs={'class':'movie_listing_item_game_url'})
	thumbs = soup.findAll(attrs={'class':'gamepage_content_row_image'})
	links = soup.findAll(attrs={'class':'movie_listing_item_title_url'})
	plots = soup.findAll(attrs={'class':'MovieDescription MovieDescription_gthd'})
	dates = soup.findAll(attrs={'class':'MovieDate'})

	for index, i in enumerate(links):
		link = getGTRLink('http://www.gametrailers.com'+i['href'])
		#GameTrailers date in string format ( Mon Day, Year ) dmy
		post_date = str(time.strftime("%d-%m-%Y", time.strptime(dates[index].string, '%b %d, %Y')))
		print 'DATE:: '+str(post_date)
		if link:
			entry = {
				'title': titles[index].string+' - '+links[index].string.strip(),
				'link':link,
				'thumb':thumbs[index]['src'],
				'plot':plots[index].string.strip(),
				'date':post_date    #"03/12/2008"
				}
			data.append(entry)

	return [data, pagelink_next, pagelink_prev]

def getHTML(url, break_one='', break_two=''):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
	lemon = urllib2.urlopen(req);
	response=lemon.read();
	lemon.close()
	if break_one:
		response = response.split(break_one)[1]
	if break_two:
		response = response.split(break_two)[0]
	return response


"""
	INDEX()
	when user makes a selection from CATS2(), the url is passed here. index()
	will query grabLinks() and use its response to show user the results.
"""
def INDEX(data):

	#this is where the fun starts, so we'll print some text here to
	#locate this section of code in the boxee debug logs.
	print '**INDEX()'

	#grab page links
	links = grabLinks(data)
	games = links[0]

	#check for next and previous links, add them if available
	if links[1]:
		addDir(':Next','http://www.gametrailers.com/gthd.php'+links[1], 1 , imageDir + 'next.png')
	if links[2]:
		addDir(':Previous','http://www.gametrailers.com/gthd.php'+links[2], 1 , imageDir + 'prev.png')

	#loop through the game videos and add each one
	for i in games:
		info = [i['date'],i['plot'],i['thumb']]
		addLink(i['title'],i['link'],info)


"""
	getGTRLink()
	the actual video page gets parsed here, from it we'll pull out the actual
	wmv/mov file. in testing, wmv seemed to play better for me so we'll try
	to grab this first if its available.
"""
def getGTRLink(url):
	html = getHTML(url).split('<div id="media_dl" class="media_dl" style="display:none;">')[1]
	soup = BeautifulSoup(html.split('Right click and Save As...')[0])
	links = soup.findAll('a')
	for i in links:
		if '.wmv' in i['href']:
			return i['href']
	for i in links:
		if '.mov' in i['href']:
			return i['href']
	return 0


"""
	addLink()
	this function simply adds a media link to boxee's current screen
"""
def addLink(name,url,info):
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=info[2])
	liz.setInfo( type="Video", infoLabels={ "Title": name, "Date": info[0], "Plot": info[1] } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
	return ok


"""
	addDir()
	this function simply adds a directory link to boxee's current screen
"""
def addDir(name,url,mode,iconimage, plot=''):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	if plot:
		liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": plot } )
	else:
		liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok


"""
	getParams()
	grab parameters passed by the available functions in this script
"""
def getParams():
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

#grab params and assign them if found
params=getParams()
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

#print params to the debug log
print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

#check $mode and execute that mode
if mode==None or url==None or len(url)<1:
    print "CATEGORY INDEX : "
    catsInitial()
elif mode==1:
    INDEX(url)
elif mode==2:
    VIDEO(url,name)
elif mode==3:
	catsHDRSS(url)
elif mode==4:
	catsPlatforms(url)
elif mode==5:
	catsPodcasts(url)

#let boxee know that this is the end of the directory structure
xbmcplugin.endOfDirectory(int(sys.argv[1]))
