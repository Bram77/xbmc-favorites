"""
    Videos module: fetches a list of playable streams for a specific category
"""

# main imports
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin

import urllib2
import urllib
import traceback
import re


from threading import Thread

try:
  from xml.etree import cElementTree as ElementTree
except ImportError:
  try:
    import cElementTree as ElementTree
  except ImportError:
    from elementtree import ElementTree

_ = sys.modules[ "__main__" ].__language__


class Query(dict):
	def __init__(self, feed=None, text_query=None, params=None, categories=None):
    		self.feed = feed
    		self.categories = []
    		if text_query:
      			self.text_query = text_query
    		if isinstance(params, dict):
      			for param in params:
        			self[param] = params[param]
    		if isinstance(categories, list):
      			for category in categories:
        			self.categories.append(category)
  	
	def ToUri(self):
    		q_feed = self.feed or ''
    	        category_string = '/'.join(
			[urllib.quote_plus(c) for c in self.categories])
   		 # Add categories to the feed if there are any.
    		if len(self.categories) > 0:
      			q_feed = q_feed + '/-/' + category_string
   		return self.BuildUri(q_feed, self)

   	#Converts a uri string and a collection of parameters into a URI.
    	def BuildUri(self,uri, url_params=None, escape_params=True):
  		parameter_list = self.DictionaryToParamList(url_params, escape_params)
		if parameter_list:
    			if uri.find('?') != -1:
      				full_uri = '&'.join([uri] + parameter_list)
   			else:
				full_uri = '%s%s' % (uri, '?%s' % ('&'.join([] + parameter_list)))  
  		else:
    			full_uri = uri
        
  		return full_uri
    
    	#Convert a dictionary of URL arguments into a URL parameter string.	
    	def DictionaryToParamList(self,url_parameters, escape_params=True):	
		transform_op = [str, urllib.quote_plus][bool(escape_params)]
		parameter_tuples = [(transform_op(param), transform_op(value))
        	for param, value in (url_parameters or {}).items()]
		return ['='.join(x) for x in parameter_tuples]	 	


class threadDownloadURL(Thread):
	def __init__ (self, url):
		Thread.__init__(self)
		self.url = url
		BASE_CACHE_PATH = os.path.join( "P:\\", "Thumbnails", "Video" )	
		filename = xbmc.getCacheThumbName(self.url )
		self.filepath = xbmc.translatePath( os.path.join( BASE_CACHE_PATH, filename[ 0 ], filename ) )

	def run(self):
        	try:
	   		urllib.urlretrieve( self.url, self.filepath)
        	except:
               		if ( os.path.isfile( filepath ) ):
               	     		os.remove(filepath )
		
class Main:
    	
    users_feed    = "http://gdata.youtube.com/feeds/users"
    std_feeds     = "http://gdata.youtube.com/feeds/standardfeeds"
    video_feed    = "http://gdata.youtube.com/feeds/videos"

    google_search = "http://video.google.com/videosearch"
    yahoo_search  = "http://search.yahooapis.com/VideoSearchService/V1/videoSearch"		
		
    video_name_re = re.compile('[&]t=(.+?)[&].*\';')
    pDialog = xbmcgui.DialogProgress()	
	
    def __init__( self ):		
	self. _get_settings()	
	self.get_contents() 

    
    #plugin settings        	
    def _get_settings( self ):
        self.settings = {}
	try:        
		self.settings[ "download" ]     =  xbmcplugin.getSetting( "download" )
		self.settings[ "download_Path"] =  xbmcplugin.getSetting("download_path")
		self.settings[ "time" ]         =  int( xbmcplugin.getSetting( "time" ) )
		self.settings[ "max_result"]    =  xbmcplugin.getSetting("max_result")
		self.settings[ "orderby" ]      =  int( xbmcplugin.getSetting( "orderby" ) )
		self.settings[ "start_index"]   =  xbmcplugin.getSetting("start_index")  
		self.settings[ "categories"]    =  int(xbmcplugin.getSetting("categories"))
		self.settings[ "username"  ]    =  xbmcplugin.getSetting("user_id") 
		self.settings[ "user_feeds"]    =  int(xbmcplugin.getSetting("user_feeds")) 
		self.settings[ "player_type"]   =  int(xbmcplugin.getSetting("player_type")) 
		self.settings[ "channel"]       =  int(xbmcplugin.getSetting("channel"))
		self.settings[ "sites"  ]       =  xbmcplugin.getSetting("sites") 
        except:
                traceback.print_exc(file=sys.stdout)
                pass
		
	  		
    def get_contents( self ):
	param =sys.argv[ 2 ][ 1 : ].split('&')
	self.id =param[0].replace("id=","")
	self.index = param[1].replace("index=","")
	self.search=""
	if   self.id=='10002': self.addVideoList(self.getFeed("top_rated"         ,True  ), _(int(self.id)))
	elif self.id=='10003': self.addVideoList(self.getFeed("top_favorites"     ,True  ), _(int(self.id)))
	elif self.id=='10004': self.addVideoList(self.getFeed("most_viewed"       ,True  ), _(int(self.id)))
	elif self.id=='10005': self.addVideoList(self.getFeed("most_discussed"    ,True  ), _(int(self.id)))
	elif self.id=='10006': self.addVideoList(self.getFeed("most_linked"       ,False ), _(int(self.id)))
	elif self.id=='10007': self.addVideoList(self.getFeed("most_responded"    ,True  ), _(int(self.id)))
	elif self.id=='10008': self.addVideoList(self.getFeed("recently_featured" ,False ), _(int(self.id)))
	elif self.id=='10009': 
			       self.search= self.getSearchPhrase(param)
			       self.addVideoList(self.getSearchFeed(),self.search)	
			  
	elif self.id=='10010': self.addVideoList(self.getUserFeed())		
	else                 : self.playMovie()
	 
    	
    def addVideoList( self,videoList,topic=""):       
	try:
	    ok = True
	    for video in videoList:	
		ok = self.addVideo(video,videoList)	
		if ( not ok ): raise	
        except:
               traceback.print_exc(file=sys.stdout)
               pass
		
	if(ok):	
		#add next page  
		if (len(videoList) > 0):
				self.addForwadLink(topic)
				
		xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="movies" )
		xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
		xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DURATION)
		xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING)	
	        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE)				
	xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )
    
    def addForwadLink(self,topic=""):
	fIndex= int(self.index)+int(self.settings["max_result"])
	label=  _(50000) + topic + _(50001)
	icon = "DefaultVideo.png"
	thumbnail = os.path.join(os.getcwd()[0:-1],"resources","skin", xbmc.getSkinDir(),"DefaultNextFoldeBig.png")
	listitem=xbmcgui.ListItem( label,"",icon,thumbnail)
	url = "%s?id=%s&index=%s&search=%s" % ( sys.argv[ 0 ],  self.id, fIndex, self.search) 
	xbmcplugin.addDirectoryItem( handle=int(sys.argv[ 1 ]), url=url, listitem=listitem, isFolder=True, )	

	
    def addVideo(self,video,videoList):     
	ok =True	
	icon = "DefaultVideo.png"
	listitem=xbmcgui.ListItem(video['title'], iconImage=icon, thumbnailImage=video['thumb'])	
	playUrl = "%s?id=%d&title=%s&url=%s" % (sys.argv[ 0 ],10011,video['title'],video['url'])
	listitem.setInfo( "video", { "Title"        : video['title'], 
				     "Size"         : int(video['size']), 
			             "Plot"         : video['plot'], 
				     "Rating"       : float(video['rating']) , 
				     "Genre"        : video['genre'], 
				     "Duration"     : video['duration'], 				     
				     "Date"         : video['date'] ,
				     "Writer"       : video['writer'],
				     "Tagline"      : video['tagline'],
				     "Plotoutline"  : video['poutline'],	
				     "Studio"       : video['studio'], 		
				     "Year"         : int(video['year'])})        
	ok = xbmcplugin.addDirectoryItem( handle=int(sys.argv[ 1 ]), url=playUrl, listitem=listitem,isFolder=False, totalItems=len( videoList ))	
        return ok

   # Build up the Video List	
    def getVideoList(self, url,type = 0):
	VideoList=[]	
	doc = urllib2.urlopen(url)
        data = doc.read()	
	tree = ElementTree.XML(data)
	DownloadList = []

	if(type==0):
		feed ="{http://www.w3.org/2005/Atom}entry"
		
	elif(type==1):   
		feed ='channel/item'
	else:
		feed ="{urn:yahoo:srchmv}Result"	

	for node in tree.findall(feed):	
		info={}		
		info["date"]        = "00:00:00"
		info["duration"]    = ""
		info["genre"]       = ""
		info["poutline"]    = ""
		info["plot"]        = ""
		info["rating"]      = "0.0"
		info["size"]	    = "0"	
		info["studio"]      = ""
		info["tagline"]     = ""		
		info["year"]        = "0"
		info["thumb"]       ="Default.png"
		info["url"]         ="www.google.com"
		info["writer"]      =""
		info['studio']      =""
		duration            = 0
		

		if(type==0):			
			info["plot"]     = node.find("{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}description").text
			info["poutline"] = (info["plot"].splitlines())[0]			
			duration    = int(node.find("{http://search.yahoo.com/mrss/}group/{http://gdata.youtube.com/schemas/2007}duration").get("seconds"))
			category    = node.find("{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}category")				
			keywords    = node.find("{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}keywords")
			ratings     = node.find(".//{http://schemas.google.com/g/2005}rating")
			viewcount   = node.find(".//{http://gdata.youtube.com/schemas/2007}statistics")
			link        = node.find("{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}player")
			
			info["genre"]    = category.get('label')			
			info["tagline"]  = keywords.text
			info["thumb"]    = self.get_largest_thumbnail(node)
			info["studio"]   = "www.youtube.com"
			info["url"]      = link.get('url')
			
			if(ratings  != None):	
				info["rating"]= ratings.get('average')
			if(viewcount!= None):
				info["size"]  = viewcount.get('viewCount')
			
			info["title"]    = node.find("{http://www.w3.org/2005/Atom}title").text
			info["writer"]   = node.find("{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name").text

			
			date = (node.find("{http://www.w3.org/2005/Atom}published").text.split("T"))[0].split("-")
			info["date"]          = "%s:%s:%s" % (date[2],date[1],date[0])
			info["year"]          =  date[0]
		
		elif(type==1):
			info["plot"]     = node.find("{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}description").text
			info["poutline"] = (info["plot"].splitlines())[0]			
			duration = int(node.find("{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}content").get("duration"))
			info["thumb"]= node.find("{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}thumbnail").get("url")
			info["title"]= node.find("{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}title").text
			info["url"]  = node.find("guid").text
			info["studio"] = (info["url"].replace("http://","").split("/"))[0]
			date = node.find("pubDate").text
			if(date !=None):
				pdate = date.split(" ")
				month = pdate[2]
				month_param = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06",
				               "Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}[pdate[2]]	
				info["date"] = "%s/%s/%s" % (pdate[1],month_param,pdate[3])
				info["year"]          =  pdate[3]
			writer= node.find("author").text
			if(writer!=None):
				info["writer"] = writer
		
		else:
						
			t = node.find("{urn:yahoo:srchmv}Duration").text			
			if(t !=None):
				duration = int(t)
			description = node.find("{urn:yahoo:srchmv}Summary").text
			if(description != None):
				info["plot"]     = description
				info["poutline"] = (info["plot"].splitlines())[0]
			info["title"]= node.find("{urn:yahoo:srchmv}Title").text
			info["size"] = node.find("{urn:yahoo:srchmv}FileSize").text
			info["url"] = node.find("{urn:yahoo:srchmv}Url").text
			
			
			# Start parallel downloads of thumbnails
			dl = threadDownloadURL(node.find("{urn:yahoo:srchmv}Thumbnail/{urn:yahoo:srchmv}Url").text )
			info["thumb"] = dl.filepath
			DownloadList.append(dl)
			dl.start()			

		hours                = duration / 60 / 60
		minutes              = ( duration - ( hours * 60 * 60 ) ) / 60
		seconds 	     = ( duration - ( hours * 60 * 60 ) ) % 60
		info["duration"]     = "%02d:%02d:%02d" % ( hours, minutes, seconds )	
		VideoList.append(info)
	
			
	# Ensure that the required thumbnail has been downloaded
	
	if(type==2):
		i=0		
		for video in VideoList:
			DownloadList[i].join()
			i+=1
			
	return VideoList
    
    def googleRequest(self,feed):
	 query = Query()
	 orderby = {0:"2",1:"0",2:"3",3:"1",4:"4"}[self.settings[ "orderby" ]]
	 query['so']= orderby
	 max_result = int(self.settings["max_result"])
	 query['start']  = self.index
	 query['num'] = self.settings["max_result"]
	 if(self.settings[ "sites" ]):	
		sites = self.settings["sites"].split("||")
	 	query['q'] = "%s" % (urllib.quote_plus(self.search) + " site:"+sites[0])
	 query.feed   =self.google_search
	 query['output'] = "rss"	
	 return self.getVideoList(query.ToUri(),1)

    def yahooRequest(self,feed):
	 query = Query()
	 query_string =""
	 query['appid']=self.settings[ "username"]
	 max_result = int(self.settings["max_result"])
	 query['start']  = self.index
	 query['results'] = self.settings["max_result"]
	 query['query'] = "%s" % urllib.quote_plus(self.search)
	 query.feed     = self.yahoo_search
	 query_string = query.ToUri()
	 if(self.settings[ "sites" ]):
		sites = self.settings["sites"].replace("||","&site=")
		query_string =query_string+"&site="+sites
		print query_string	
	 return self.getVideoList(query_string,2)
 	 		 	
    def _request(self, feed, time=False, search=False):     
	query = Query() 
	orderby = {0:"default",1:"relevance",2:"rating",3:"updated",4:"viewCount"}[self.settings[ "orderby" ]]	  

	if time:
		time_param = {0:"today",1:"this_week",2:"this_month",3:"all_time"}[self.settings[ "time" ]]		
		query['time'] = time_param    
	 	
	if search:
		
		tag  = int(xbmcplugin.getSetting("categories"))
		cat  = {0:"all",1:"Autos",2:"Comedy",
			3:"Education",4:"Entertainment",5:"Film",
			6:"Games",7:"Howto",8:"Music",
			9:"News",10:"Nonprofit",11:"People",
			12:"Animals",13:"Tech","14":"Sports",
			15:"Travel"}[self.settings[ "categories"]]
		if self.settings[ "categories"] > 0:
			query.categories.append("%s" % cat)
			query.categories.append(urllib.quote_plus(self.search)) 		
		else:
			query['vq'] = "%s" % urllib.quote_plus(self.search)
		
	if(self.settings[ "orderby" ] > 0):
		query['orderby'] = orderby
	
	max_result = int(self.settings["max_result"])
	if(max_result > 0 and max_result < 51):
		query['max-results'] = self.settings["max_result"]
			
	query['start-index'] = "%s"  % (int(self.index)+1)	
	query.feed = feed
	print query.ToUri()
	return self.getVideoList(query.ToUri())
	
    
    #standard feeds 
    def getFeed(self,feed,inc):
	feed_url = "%s/%s" % (self.std_feeds,feed)
	return self._request("%s" % feed_url,inc,False)	
    
    #user feeds 	
    def getUserFeed(self):  	
	userfeeds  =  {0:"favorites",1:"uploads"}[self.settings[ "user_feeds"]]	
	feed_url   = "%s/%s/%s" % (self.users_feed,self.settings[ "username"  ],userfeeds) 
	return self._request("%s" % feed_url,False,False) 	
   
     #search feeds	
    def getSearchPhrase(self,params):
	if(len(params) > 2):
		search_phrase = params[2].replace("search=","")	
	else:
		search_phrase = self.getKeyboard()
		xbmc.sleep(10)
	return search_phrase

    def getSearchFeed(self,type=0):
	videos = []	
	if self.search:
		type = self.settings[ "channel"]	
		if(type == 0):
	     		videos = self._request("%s" % self.video_feed,False,True)
		elif(type == 1):
			videos = self.googleRequest("%s" % self.video_feed)
		else:
			videos = self.yahooRequest("%s" % self.video_feed)
	return videos
			
		 		
    def getKeyboard( self, default="", heading="", hidden=False ):
        kboard = xbmc.Keyboard( default, heading, hidden )
        kboard.doModal()
        if ( kboard.isConfirmed() ):
            return kboard.getText()
        return default
        
    def get_thumbnails(self, node):
        urls = {}
        for c in node.findall(".//{http://search.yahoo.com/mrss/}group"):
            for cc in c.findall("{http://search.yahoo.com/mrss/}thumbnail"):
                width = int(cc.get("width"))
                height = int(cc.get("height"))
                size = (width, height)
                url = cc.get("url")
                if size not in urls:
                    urls[size] = [url,]
                else:
                    urls[size].append(url)
        return urls

    def get_largest_thumbnail(self, node):
        thumbnails = self.get_thumbnails(node)
        sizes = thumbnails.keys()
        #sizes.sort()
        return thumbnails[sizes[-1]][0]


    def playMovie(self):
	params =sys.argv[ 2 ].split("&title=")
	videoParam= params[1].split("url=")
	fileUrl = videoParam[1]	
	title =  videoParam[0].replace("&","");	

	status = _(2031)
	if(self.settings[ "download" ] == "true"):	
		status  = _(2030)
	self.pDialog.create( "YouTube", status)
	icon = "DefaultVideo.png"
	listitem = xbmcgui.ListItem(title,iconImage=icon)
	listitem.setInfo( "video", { "Title": title})

	flv_file = self.get_flv_video_url(fileUrl)
	if(self.settings[ "download" ] == "true"):
		flv_file = self.downloadMovie(flv_file)
	self.pDialog.close()	
	if ( flv_file ):		
		#set the player core		
		palyer_type= {0:xbmc.PLAYER_CORE_DVDPLAYER,1:xbmc.PLAYER_CORE_MPLAYER}[self.settings[ "player_type"]]	
		xbmc.Player(palyer_type).play( flv_file, listitem )
		
	        #d= SelectionDialog()
		#d.create()

    def downloadMovie(self,url):
	filename = xbmc.getCacheThumbName( url )
	filepath  = xbmc.translatePath( os.path.join(self.settings[ "download_Path"], filename ))	
        filepath = filepath.replace(".tbn",".flv")
        try:
	   self.msg = _(2030) 	
	   urllib.urlretrieve( url, filepath, self._report_hook )
        except:
               if ( os.path.isfile( filepath ) ):
               	     os.remove(filepath )
	return filepath 

    def downloadImage(self,url):
	BASE_CACHE_PATH = os.path.join( "P:\\", "Thumbnails", "Video" )	
	filename = xbmc.getCacheThumbName( url )
	filepath = xbmc.translatePath( os.path.join( BASE_CACHE_PATH, filename[ 0 ], filename ) )	
        try:
	   urllib.urlretrieve( url, filepath)
        except:
               if ( os.path.isfile( filepath ) ):
               	     os.remove(filepath )
	return filepath 	
    
    def get_flv_video_url(self, url):
        flv_url = ''
        doc = urllib2.urlopen(url)
        data = doc.read()

        # extract video name
        match = self.video_name_re.search(data)
        if match is not None:
            video_name = match.group(1)

            # extract video id
            url_splited = url.split("watch?v=")
            video_id = url_splited[1]     

            flv_url = "http://www.youtube.com/get_video?video_id=%s&t=%s&fmt=18"
            flv_url = flv_url % (video_id, video_name)
        return flv_url	
    

    def _report_hook( self, count, blocksize, totalsize ):
        percent = int( float( count * blocksize * 100) / totalsize )
        self.pDialog.update( percent, self.msg )
        if ( self.pDialog.iscanceled() ): raise
 

