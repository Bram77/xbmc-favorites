import os
import pickle
import sys
import traceback

import xbmcgui
import xbmc

import youtube

import random

import string


class YouTubeGUI(xbmcgui.WindowXML):
    
    

	# GUI States.
	STATE_MAIN = 1
	STATE_FEEDS = 2
	STATE_USERS = 4
	STATE_MOST_DISCUSSED = STATE_FEEDS | 8
	STATE_MOST_VIEWED = STATE_MOST_DISCUSSED | 16
	STATE_MOST_LINKED = STATE_MOST_VIEWED | 32
	STATE_MOST_POPULAR = STATE_MOST_LINKED | 64
	STATE_CATEGORIES = 128
	STATE_SEARCH = 256
	STATE_USERS = 512

	# Content list states
	CONTENT_STATE_NONE = 0
	CONTENT_STATE_VIDEO = 1
	CONTENT_STATE_USERS = 2
	CONTENT_STATE_FAVORITES = 4
	CONTENT_STATE_SEARCH_HISTORY = 8
	

	def onInit(self):
    	
		
		try:
			if (self.initialized == True):
												
				self.update_list_mini(self.getList())				
				pass
				
		except:
			try: 						
				self.init_button_state()
				self.initialized = True
				self.base_path = os.getcwd().replace(';','')

				self.data = []
				
				self.current_position = 0
				
				self.yt = youtube.YouTube()
				self.yt.set_filter_hook(self.confirm_content)

				self.state = YouTubeGUI.STATE_MAIN
				self.list_state = YouTubeGUI.CONTENT_STATE_NONE	

				# Get the last search term
				history = self.get_search_history()
				if history is not None and len(history) > 0:
					self.last_search_term = history[0]
				else:
					self.last_search_term = ''

				self.player = xbmc.Player(xbmc.PLAYER_CORE_MPLAYER)						
				
				self.get_feed('recently_featured?')				

			except:
				xbmc.log('Exception (init): ' + str(sys.exc_info()[0]))
				traceback.print_exc()
				self.close()  
			
		
		# Put your List Populating code/ and GUI startup stuff here
		pass 
 
 
 	def onAction(self, action):
 		"""Handle user input events."""
  
 		try: 
 			# BACK BUTTON
 			if action.getId() == 10:
 				if self.state is YouTubeGUI.STATE_MAIN:
 					self.close()
 				elif self.state & ~YouTubeGUI.STATE_FEEDS & YouTubeGUI.STATE_MOST_DISCUSSED:
 					self.set_button_state(YouTubeGUI.STATE_FEEDS)
 				else:
 					self.set_button_state(YouTubeGUI.STATE_MAIN)

			# CONTEXT MENU
 			elif action.getId() == 117:
 				if self.list_state is YouTubeGUI.CONTENT_STATE_VIDEO:
 					self.context_menu_video()
 				else:
 					self.not_implemented()
 			
 		except:
 			xbmc.log('Exception (onAction): ' + str(sys.exc_info()[0]))
 			traceback.print_exc()
 			self.close()
 
 	def onClick(self, controlID):
 		"""Handle widget events."""
 
 		ctrl = self.getControl(controlID)
 		 		
 		try:  			
 			if controlID >= 50 and controlID < 60:
 				self.on_control_list(self) 			 				
 			elif controlID == 130:
 				self.get_next()
 			elif controlID == 131:
 				self.get_prev() 				
 			elif self.state is YouTubeGUI.STATE_MAIN:
 				self.on_control_main(ctrl)
 			elif self.state is YouTubeGUI.STATE_SEARCH:
 				self.on_control_search(ctrl)
 			elif self.state is YouTubeGUI.STATE_USERS:
 				self.on_control_users(ctrl)
 			elif self.state is YouTubeGUI.STATE_FEEDS:
 				self.on_control_feeds(ctrl)
 			elif self.state is YouTubeGUI.STATE_MOST_VIEWED:
 				self.get_feed_by_time(ctrl, "most_viewed")								
 			elif self.state is YouTubeGUI.STATE_MOST_DISCUSSED:
 				self.get_feed_by_time(ctrl, "most_discussed")								
 			elif self.state is YouTubeGUI.STATE_MOST_LINKED:
 				self.get_feed_by_time(ctrl, "most_linked")	
 			elif self.state is YouTubeGUI.STATE_MOST_POPULAR:
 				self.get_feed_by_time(ctrl, "most_popular")
 				
 		except:
 			xbmc.log('Exception (onControl): ' + str(sys.exc_info()[0]))
 			traceback.print_exc()
 			self.close()
			
			
			

	def onFocus(self, controlID):

		pass
	        

	def confirm_content(self, udata):
		"""Let the user choose to watch offensive crap."""

		dlg = xbmcgui.Dialog()
		return dlg.yesno('YouTube',
		                 'This clip may contain inappropriate content.',
		                 'Do you want to watch it anyway?')

	def get_search_history(self):
		"""Return a list of old search terms."""

		history_list = []
		path = os.path.join(self.base_path, 'data', 'history.txt')

		try:
			f = open(path, 'rb')
			history_list = pickle.load(f)
			f.close()
		except IOError, e:
			# File not found, will be created upon save
			pass

		return history_list

	def add_search_history(self, term):
		"""Append a term, and trim the search history to max 50 entries."""

		history_list = self.get_search_history()

		# Filter out the term to add from the list so only one copy is stored.
		history_list = filter(lambda x: x != term, history_list)
		history_list.insert(0, term)

		if len(history_list) > 50:
			history_list = history_list[:50]

		try:
			dir = os.path.join(self.base_path, 'data')
			# Create the 'data' directory if it doesn't exist.
			if not os.path.exists(dir):
				os.mkdir(dir)
			path = os.path.join(dir, 'history.txt')
			f = open(path, 'wb')
			pickle.dump(history_list, f, protocol=pickle.HIGHEST_PROTOCOL)
			f.close()
		except IOError, e:
			print 'There was an error while saving the pickle (%s)' % e


	def show_about(self):
		"""Show an 'About' dialog."""

		dlg = xbmcgui.Dialog()
		dlg.ok('About', 'By Boris Sitsker 2008 & Daniel Svensson 2007', 'Paypal: boris@sitsker.com, dsvensson@gmail.com','Bugs: XBMC Forum - Python Script Development')


	def progress_handler(self, done, total, dlg):
		"""Update progress dialog percent and return abort status."""

		percent = int((done * 100.0) / total)

		dlg.update(percent)
		return not dlg.iscanceled()
	
	def download_data(self, arg, func, save=False):
		"""Show a progress dialog while downloading and return the data."""

		if (save):
			self.func = func
			self.arg = arg
		
		dlg = xbmcgui.DialogProgress()
		dlg.create('YouTube', 'Downloading...')

		self.yt.set_report_hook(self.progress_handler, dlg)

		try:
		
			data = func(arg)
			
		except Exception, e:
			dlg.close()
			err_dlg = xbmcgui.Dialog()
			err_dlg.ok('YouTube', 'There was an error.')			
			return None

		dlg.close()

		return data
		
	#
	# refreshes the list
	#
	def load_list(self):
		data = self.download_data(self.arg, self.func)
		if (self.update_list(data, self.getList())):
			lbl = self.getControl(5).getLabel()
			lbls = lbl.split('-')
			lbl = lbls[0] + "- Page " + self.yt.get_page()
			self.getControl(5).setLabel(lbl)	
			

	#
	# change the sort ordering for a particular result
	#
	def change_sort(self):
	
		items = self.yt.ordertypes
		result = xbmcgui.Dialog().select("Sort order:", ["Default", "Time Published", "Number of Views", "Rating"])
		if (result > -1):	
			self.yt.ordertype = result			
			self.load_list()


	#
	# next page button
	#
	def get_next(self):
	
		if (self.yt.do_next()):			
						
			self.load_list()

	#
	# prev page button
	#
	def get_prev(self):
	
		if (self.yt.do_prev()):
		
			self.load_list()
			
			
		
	
	def get_input(self, title, default="", hidden=False):
		"""Show a virtual keyboard and return the entered text."""
	
		ret = None
	
		keyboard = xbmc.Keyboard(default, title)
		keyboard.setHiddenInput(hidden)
		keyboard.doModal()
	
		if keyboard.isConfirmed():
			ret = keyboard.getText()
	
		return ret

	def get_user_videos(self, method, title, user=None):
		"""Get rss data and update the list."""

		if user is None:
			user = self.get_input("Enter User: ", '')
			
		if user is not None:
			
			self.yt.reset_page()
			
			#self.initMainView()
			
			data = self.download_data(user, method, True)
						
			if self.update_list(data, self.getList()):				
				self.list_state = YouTubeGUI.CONTENT_STATE_VIDEO
				lbl = '%s user %s' % (title, user)
				self.getControl(5).setLabel(lbl + " - Page " + self.yt.get_page())			
				
	
	def get_youtube(self, lbl, arg, func):
	
		self.yt.reset_page()
			
		data = self.download_data(arg, func, True)

		if self.update_list(data, self.getList()):			
			self.list_state = YouTubeGUI.CONTENT_STATE_VIDEO			
			
		self.getControl(5).setLabel(lbl + " - Page " + self.yt.get_page())
	
	
	def get_feed(self, feed):
		"""Get rss data and update the list."""
						
		self.yt.reset_page()
		
		data = self.download_data(feed, self.yt.get_feed, True)
		
		if self.update_list(data, self.getList()):			
			self.list_state = YouTubeGUI.CONTENT_STATE_VIDEO

			# Change 'something_bleh_bluh' to 'Something Bleh Bluh'.
			tmpfeed = feed.split('?')
			feed = tmpfeed[0]
			lbl = ' '.join(map(lambda x: x.capitalize(), feed.split('_')))
			self.getControl(5).setLabel(lbl + " - Page " + self.yt.get_page())

	def get_cat(self, cstr):
		"""Get rss data and update the list."""
						
		self.yt.reset_page()
		
		data = self.download_data(cstr, self.yt.get_category, True)
		
		if self.update_list(data, self.getList()):			
			self.list_state = YouTubeGUI.CONTENT_STATE_VIDEO

			# Change 'something_bleh_bluh' to 'Something Bleh Bluh'.
			tmpfeed = cstr
			
			lbl = ' '.join(map(lambda x: x.capitalize(), tmpfeed.split('_')))
			self.getControl(5).setLabel(lbl + " - Page " + self.yt.get_page())


		
	def search(self, term=None):
		"""Get user input and perform a search. On success update the list."""

		if term is None:
			term = self.get_input('Search', self.last_search_term)					
		
		# Only update the list if the user entered something.
		if term != None:
		
			#self.initMainView()
			
			self.yt.reset_page()
			
			self.last_search_term = term
			data = self.download_data(term, self.yt.search, True)
				
			if self.update_list(data, self.getList()):				
				self.add_search_history(term)
				self.list_state = YouTubeGUI.CONTENT_STATE_VIDEO
				lbl = 'Search: %s' % term
				self.getControl(5).setLabel(lbl + " - Page " + self.yt.get_page())
				
			else:
				dlg = xbmcgui.Dialog()
				dlg.ok('YouTube', 'No videos were found that match your query.')
				self.setFocus(self.getControl(40))
				
		
		
	def search_history(self):
		"""Get search history and update the list."""
		
		data = [x for x in self.get_search_history()]
		
		if (len(data) <= 0):		
			dlg = xbmcgui.Dialog()
			dlg.ok('YouTube', 'Search history empty.')
			return
		else:
			ret = xbmcgui.Dialog().select("Search history", data)
			if (ret >= 0 and ret < len(data)):
				self.search(data[ret])
			
	#
	# updates the list for onInit.
	#
	def update_list_mini(self, content_list):
	
		xbmcgui.lock()
		
		for listitem in self.listItems:
			content_list.addItem(listitem)
		
		content_list.setCurrentListPosition(self.current_position)		
		xbmcgui.unlock()
	
	#
	# "wrapper" function in case we use control lists, or window lists.	
	#
	def listClear(self, content_list):
	
		content_list.clearList()
	
	#
	# retrieves new data and updates the list.
	#
	def update_list(self, data, content_list):
		"""Updates the list widget with new data."""

		# Either an error dialog has been shown, or the user
		# aborted the download. Anyway, there's no new data
		# to put in the list, so lets just keep the old.
		if data == None:
			return False

		dlg = xbmcgui.DialogProgress()
		dlg.create('YouTube', 'Downloading thumbs...')
		dlg.update(0)
		
		self.data = data		
		self.listItems = []
		
		xbmcgui.lock()		
				
		self.listClear(content_list)		
		
		dir = os.path.join(self.base_path, 'data')
		files = os.listdir(dir)

		print "Deleting thumbs..."
		
		#delete old thumbs
		for file in files:
			if file == '.' or file == '..': continue
			try:
				path = dir + os.sep + file
				f = file.split(".")
				if (f[1]=="jpg"):
					os.remove(path)
			except:
				pass				
			
		
		
		print "Done."
		
		counter = 0
		totalsize = len(self.data)
		
		for desc, id in self.data:
		
			counter += 0
			
			dlg.update(int(counter/totalsize))
			
			author = ""
			out2 = ""
			out = str(desc)
			path = ""
			
			#set image													
			if (self.yt.thumbnail is not None and len(self.yt.thumbnail) > counter):
				thumbdet = self.yt.thumbnail[counter]
				try:
					thumb = self.yt.retrieve(thumbdet)
					
					pass
				except DownloadAbort, e:
					# Just fall through as a thumbnail is not required.
					pass
				except DownloadError, e:
					pass
				except:
					pass
				else:
					# Save the thumbnail to a local file so it can be used.
					
					rp = str(random.randint(100000000, 999999999))
					path = os.path.join(self.base_path, 'data', 'thumb' + str(counter) + rp + '.jpg')
					
					fp = open(path, 'wb')				
					fp.write(thumb)
					fp.close()				
											
					pass						
			
			if (self.yt.author is not None and len(self.yt.author) > counter):
				author = self.yt.author[counter]
				out2 = str(author[:15])
				out3 = out2

			if (self.yt.views is not None and len(self.yt.views) > counter):
				views = self.yt.views[counter]	
				out2 += "\n" + str(views) + " views"

			if (self.yt.rating is not None and len(self.yt.rating) > counter):
				rating = self.yt.rating[counter]					
				out2 += "\n" + str(rating) + " rating"

			if (self.yt.duration is not None and len(self.yt.duration) > counter):
				duration = self.yt.duration[counter]					
				out2 += "\n" + str(duration) + ""				

			
			item = xbmcgui.ListItem (label=out, label2=out2, thumbnailImage=path)			
			
			self.listItems.append(item)
			content_list.addItem(item)
			
						
			counter += 1
		
		xbmcgui.unlock()

		dlg.close()
		return True

	#
	# logs in?
	#
	def login(self, username=None, password=None):
		"""Get username and password from the user and try to login."""

		ret = False

		if username is None:
			username = self.get_input('Username', 'boritchka')

		if password is None:
			password = self.get_input('Password', hidden=True)

		try:
			ret = self.yt.login(username, password)
		except DownloadAbort, e:
			# Just fall through as ret defaults to False
			pass
		except DownloadError, e:
			err_dlg = xbmcgui.Dialog()
			err_dlg.ok('YouTube', 'There was an error.', e.value)

		return ret

	#
	# adds a favorite?
	#
	
	def add_favorite(self):
	
		content_list = self.getList()		
		
		pos = self.getListPosition(content_list)


		desc, id = self.data[pos]

		dlg = xbmcgui.DialogProgress()
		dlg.create('YouTube', 'Adding \'%s\' to favorites' % desc)

		self.yt.set_report_hook(self.progress_handler, dlg)

		try:
			if not self.yt.login_status() and not self.login():
				err_dlg = xbmcgui.Dialog()
				err_dlg.ok('YouTube', 'Login failed.')
			elif self.yt.user_add_favorite(id):
				added_dlg = xbmcgui.Dialog()
				added_dlg.ok('YouTube', 'Favorite added.')
		except DownloadAbort, e:
			# Just fall through as the method shouldn't return anyhting.
			pass
		except DownloadError, e:
			err_dlg = xbmcgui.Dialog()
			err_dlg.ok('YouTube', 'There was an error.', e.value)

		dlg.close()

	#
	# get list wrapper for control lists vs built in window lists.
	#
	def getList(self):
	
		return self#.getControl(500)
		



	#
	# get videos by a user from current position in list
	#
	def videos_by_user(self):
		
		pos = self.getListPosition(self)		
		user = self.yt.get_author(pos)
		
		if user is not None:			
			self.get_user_videos(self.yt.get_user_videos, 'Videos by', user)

	#
	# get videos by a user from current position in list
	#
	def related_videos(self):
		
		pos = self.getListPosition(self)				
		
		if pos is not None:			
			self.get_youtube("Related Videos", pos, self.yt.get_related)

	#
	# get videos by a user from current position in list
	#
	def response_videos(self):
		
		pos = self.getListPosition(self)				
		
		if pos is not None:			
			self.get_youtube("Video Responses", pos, self.yt.get_responses)
	
			

	def play_clip(self, id):
		"""Get the url for the id and start playback."""

		try:
			self.current_position = self.getCurrentListPosition()
			
			file = self.download_data(id, self.yt.get_video_url)
			self.player.play(str(file))
			#self.close()
			
		except youtube.PrivilegeError, e:
			dlg = xbmcgui.Dialog()
			ret = dlg.yesno('YouTube',
			                'You need to be logged in to watch this clip.',
			                'Do you want to login?')

			# If the user wants to login, and login works, then try again
			try:									
				if ret:
					if self.login():
						self.play_clip(id)
					else:
						dlg = xbmcgui.Dialog()
						dlg.ok('YouTube', 'Login failed.')
			except DownloadError, e:
				err_dlg = xbmcgui.Dialog()
				err_dlg.ok('YouTube', 'There was an error.', e.value)
			except DownloadAbort, e:
				# Just fall through as the method shouldn't return anything.
				pass
		except youtube.VideoStreamError, e:
			dlg = xbmcgui.Dialog()
			dlg.ok('YouTube', 'Unable to play the video clip.')
			
			
	#
	# context handler
	#
	def context_menu_video_handler(self, id):
		if id is 0: # 'Other Videos By User'
			self.videos_by_user()
		elif id is 1: # 'Other Videos By User'
			self.related_videos()			
		elif id is 2: # 'Other Videos By User'
			self.response_videos()	
		elif id is 3: # 'Other Videos By User'
			self.change_sort()				

	#
	# context select
	#
	def context_menu_video(self):
		items = ['Other Videos By User', 'Related Videos', 'Video Responses', 'Change Sort Order']
		         		         	
		self.context_menu_video_handler(xbmcgui.Dialog().select("Perform action:", items))


	#wrapper method in case of built in window list vs control list.	
	def getListPosition(self, ctrl):
		
		return ctrl.getCurrentListPosition()		

	def on_control_list(self, ctrl):
		"""Handle content list events."""
				
		pos = self.getListPosition(ctrl)				

		try:
			desc, id = self.data[pos]
		except IndexError, e:
			# If this happens something is terribly wrong
			print 'Index out of bounds'
			self.close()
			return

		if self.list_state is YouTubeGUI.CONTENT_STATE_VIDEO:
			self.play_clip(id)
		elif self.list_state is YouTubeGUI.CONTENT_STATE_SEARCH_HISTORY:
			self.search(desc)
		else:
			self.not_implemented()

	def on_control_main(self, ctrl):
		"""Handle main menu events."""

		if ctrl is self.getControl(10):			
			self.set_button_state(YouTubeGUI.STATE_FEEDS)
		elif ctrl is self.getControl(11):	
			self.set_button_state(YouTubeGUI.STATE_USERS)
		elif ctrl is self.getControl(14):	
			self.set_button_state(YouTubeGUI.STATE_SEARCH)
		elif ctrl is self.getControl(13):	
			self.show_about()

	def on_control_search(self, ctrl):
		"""Handle search menu events."""
		if ctrl is self.getControl(40):
			self.search()
		elif ctrl is self.getControl(41):
			self.search_history()

	def on_control_users(self, ctrl):
		if ctrl is self.getControl(90):
			self.get_user_videos(self.yt.get_user_favorites, 'Favorites of')
		elif ctrl is self.getControl(91):
			self.get_user_videos(self.yt.get_user_videos, 'Videos by')
		elif ctrl is self.getControl(92):
			self.not_implemented()

	def on_control_feeds(self, ctrl):
		"""Handle feeds menu events."""

		if ctrl is self.getControl(20):			
			self.get_feed('most_recent?')
		elif ctrl is self.getControl(21):
			self.get_feed('recently_featured?')
		elif ctrl is self.getControl(22):
			self.get_feed('top_favorites?')
		elif ctrl is self.getControl(23):
			self.get_feed('top_rated?')
		elif ctrl is self.getControl(24):
			self.set_button_state(YouTubeGUI.STATE_MOST_VIEWED)
		elif ctrl is self.getControl(25):
			self.set_button_state(YouTubeGUI.STATE_MOST_DISCUSSED)
		elif ctrl is self.getControl(26):
			self.set_button_state(YouTubeGUI.STATE_MOST_LINKED)
		elif ctrl is self.getControl(27):
			self.set_button_state(YouTubeGUI.STATE_MOST_POPULAR)			
		elif ctrl is self.getControl(28):
		
			cats = self.yt.get_categories()
			
			choice = xbmcgui.Dialog().select("Choose a category:", cats)			
			
			self.get_cat('%s' % cats[choice])




	def get_feed_by_time(self, ctrl, feedstr):
	
		if ctrl is self.getControl(30):
			self.get_feed('%s?time=today' % feedstr)
		elif ctrl is self.getControl(31):
			self.get_feed('%s?time=this_week' % feedstr)
		elif ctrl is self.getControl(32):
			self.get_feed('%s?time=this_month' % feedstr)
		elif ctrl is self.getControl(33):
			self.get_feed('%s?' % feedstr)
		


		
	def init_button_state(self):
		xbmcgui.lock()
		
		visible = True
		self.getControl(02).setVisible(visible)
		self.getControl(10).setVisible(visible)
		self.getControl(11).setVisible(visible)
		self.getControl(14).setVisible(visible)
		self.getControl(13).setVisible(visible)	
		
		visible = False
		self.getControl(6).setVisible(visible)
		self.getControl(20).setVisible(visible)
		self.getControl(21).setVisible(visible)
		self.getControl(22).setVisible(visible)
		self.getControl(23).setVisible(visible)
		self.getControl(24).setVisible(visible)
		self.getControl(25).setVisible(visible)
		self.getControl(26).setVisible(visible)
		self.getControl(27).setVisible(visible)		
		self.getControl(28).setVisible(visible)		

		self.getControl(30).setVisible(visible)
		self.getControl(31).setVisible(visible)
		self.getControl(32).setVisible(visible)
		self.getControl(33).setVisible(visible)

		self.getControl(90).setVisible(visible)
		self.getControl(91).setVisible(visible)
		self.getControl(92).setVisible(visible)
		
		self.getControl(40).setVisible(visible)
		self.getControl(41).setVisible(visible)		

		xbmcgui.unlock()
	
	def set_button_state(self, state):
		"""Update button visibility, current state and focused widget."""

		xbmcgui.lock()

		# Are we in the main menu?
		visible = bool(state & YouTubeGUI.STATE_MAIN)
		
		self.getControl(10).setVisible(visible)
		self.getControl(11).setVisible(visible)
		self.getControl(14).setVisible(visible)
		self.getControl(13).setVisible(visible)

		if visible:
			dominant = self.getControl(10)

		# Are we in the feeds menu?
		visible = bool(state & YouTubeGUI.STATE_FEEDS)		
		
		
		self.getControl(20).setVisible(visible)
		self.getControl(21).setVisible(visible)
		self.getControl(22).setVisible(visible)
		self.getControl(23).setVisible(visible)
		self.getControl(24).setVisible(visible)
		self.getControl(25).setVisible(visible)
		self.getControl(26).setVisible(visible)
		self.getControl(27).setVisible(visible)
		self.getControl(28).setVisible(visible)
		
		if visible:
			dominant = self.getControl(20)

		# Are we in the most discussed menum (or the most viewed menu)
		visible = bool(state & ~YouTubeGUI.STATE_FEEDS &
		               YouTubeGUI.STATE_MOST_DISCUSSED)

		self.getControl(30).setVisible(visible)
		self.getControl(31).setVisible(visible)
		self.getControl(32).setVisible(visible)
		self.getControl(33).setVisible(visible)

		if visible:
			dominant = self.getControl(30)

		# Are we in the users menu?
		visible = bool(state & YouTubeGUI.STATE_USERS)		

		self.getControl(90).setVisible(visible)
		self.getControl(91).setVisible(visible)
		self.getControl(92).setVisible(visible)

		if visible:
			dominant = self.getControl(90)
		
		# Are we in the search menu?
		visible = bool(state & YouTubeGUI.STATE_SEARCH)

		self.getControl(40).setVisible(visible)
		self.getControl(41).setVisible(visible)

		if visible:
			dominant = self.getControl(40)


		# Set focus to the top-most relevant button, and move
		# to that when leaving the list.
						
		self.setFocus(dominant)
		#self.getControl(50).controlLeft(dominant)
		
		self.state = state

		xbmcgui.unlock()
	        

	        


base_path = os.getcwd()		

w = YouTubeGUI("youtube.xml", base_path, "DefaultSkin")
w.doModal()
del w