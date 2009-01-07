'''
	66stage v0.2
		A boxee/xbmc plugin for www.66stage.com

		Currently this plugin only supports the 2 DivX categories from
		66stage.com including the ones that link out to stagevu.

		Not fond of this site nor its content layout, wont see too many
		updates to this.

'''

__plugin__ = "66stage"
__author__ = "riegersn"
__url__ = "http://code.google.com/p/boxee-plugins"
__svn__ = "svn/trunk/plugins/video/66stage/"
__version__ = "0.3"

import urllib, urllib2
import re, string
import socket
import xbmc, xbmcgui, xbmcplugin
from BeautifulSoup import BeautifulSoup


#add the initial category
def catsInitial():
	addDir('DivX','http://www.66stage.com/movies.php?pl=div',1,"")


def grabLinks(url, filter_out=[]):
	soup = BeautifulSoup(getHTML(url, 'Movies List</B>', '</table>'))
	links = soup.findAll('a')
	result = []
	for index, i in enumerate(links):
		if not listin(i['href'], filter_out):
			link = re.sub('movies.php\?pl=(.+?)&url=', '', i['href'])
			for x in result:
				if link == x['link']:
					link = ''
			if not link:
				continue
			type = ''
			if listin(link, ['tinyurl.com', '.divx', '.avi']):
				type = 'avi'
			elif (not listin(link, ['/', '.'])) and (listin(link, ['&w=', '&h='])):
				type = 'stagevu'
				link = link.split('&')[0]
			if type:
				entry = {'title':i.string, 'link':link, 'type':type}
				result.append(entry)
	return result


def INDEX(data):
	print '**INDEX()'
	if (not "http://" in data) and (';' in data):
		link=getStagevuLink(data.split(';')[1])
		name=data.split(';')[0]
		if link == '0':
			ok = xbmcgui.Dialog().ok( '66stage', 'Video has been removed!' )
		else:
			addLink(name,link,['',int('0'),'','',''])
	else:

		movies = grabLinks(data, ['ftp://'])
		movies.extend(grabLinks(data+'2', ['ftp://']))

		for index, entry in enumerate(movies):
			if entry['type'] == 'avi':
				#try:
				#	metadata = imdbScrape(entry['title'])
				#	addLink(entry['title'],entry['link'],metadata)
				#except:
				addLink(entry['title'],entry['link'],['',int('0'),'','',''])
			elif entry['type'] == 'stagevu':
				addDir(entry['title'],entry['title']+";"+entry['link'],1, '')


#grab an avi link from stagevu.com
def getStagevuLink(data):
	response = getHTML("http://stagevu.com/video/"+data)
	if "Welcome to Stagevu!" in response:
		return '0'
	temp=response.split('<embed type="video/divx" src="http://n')[1]
	temp=temp.split('.avi" width=')[0]
	return "http://n"+temp+".avi"


#add a media link to the boxee window
def addLink(name,url,info):
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=info[2])
	liz.setInfo( type="Video", infoLabels={ "Title": name, "Genre": info[0], "Year": info[1], "Plot": info[4] } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
	return ok


#add a dir link to the boxee window
def addDir(name,url,mode,iconimage):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name.replace('_', ' ') } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	print u
	return ok


#parse out pass params
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


#dirty-quick function, no python 2.5 in boxee
def listin(x, l):
	for line in l:
		if line in x:
			return True
	return False


#grab an html string for any url, break off ends if needed to shorten returned string
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
print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
if mode==None or url==None or len(url)<1:
    catsInitial()
elif mode==1:
    INDEX(url)
elif mode==2:
    VIDEO(url,name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
