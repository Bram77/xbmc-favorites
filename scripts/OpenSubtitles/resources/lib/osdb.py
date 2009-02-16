import sys
import os
import xmlrpclib
import urllib, urllib2
import unzip
import globals
import RecursiveParser

from utilities import *

_ = sys.modules[ "__main__" ].__language__

BASE_URL_XMLRPC_DEV = u"http://dev.opensubtitles.org/xml-rpc"
BASE_URL_XMLRPC = u"http://www.opensubtitles.org/xml-rpc"

class OSDBServer:
    def Create(self):
	self.subtitles_list = []
	self.languages_list = []
	self.folderfilesinfo_list = []
	self.osdb_token = ""
	self.connected = False
	self.smbfile = False

    def connect( self, osdb_server, username, password ):
	LOG( LOG_INFO, "Connecting to server " + osdb_server + "..." )
	try:
		if osdb_server:
			self.server = xmlrpclib.Server(osdb_server)
			info = self.server.ServerInfo()
			if username:
				LOG( LOG_INFO, "Logging in " + username + "..." )
				login = self.server.LogIn(username, password, "en", "xbmc")
			else:
				LOG( LOG_INFO, "Logging in anonymously..." )
				login = self.server.LogIn("", "", "en", "xbmc")
			if (login["status"].find("200") > -1):
				self.connected = True
				self.osdb_token = login["token"]
				LOG( LOG_INFO, "Connected" )
				return True, ""
			else:
				self.connected = False
				error = login["status"]
				LOG( LOG_ERROR, error )
				return False, error
		else:
			self.connected = False
			error = _( 730 )
			LOG( LOG_ERROR, error )
			return False, error
	except Exception, e:
		error = _( 731 ) % ( _( 732 ), str ( e ) )
		LOG( LOG_ERROR, error )
		return False, error


    def disconnect( self ):
	try:
		if ( self.osdb_token ) and ( self.connected ):
			LOG( LOG_INFO, "Disconnecting from server..." )
			logout = self.server.LogOut(self.osdb_token)
			self.connected = False
			LOG( LOG_DEBUG, logout )
			LOG( LOG_INFO, "Disconnected" )
			return True, ""
		else:
			error = _( 737 )
			LOG( LOG_ERROR, error )
			return False, error
	except Exception, e:
		error = _( 731 ) % ( _( 733 ), str ( e ) )
		LOG( LOG_ERROR, error )
		return False, error


    def getlanguages( self ):
	try:
		if self.connected:
			LOG( LOG_INFO, "Retrieve subtitle languages..." )
			languages = self.server.GetSubLanguages()
			LOG( LOG_INFO, "Retrieved subtitle languages" )      
			self.languages_list = []
			if languages["data"]:
				for item in languages["data"]:
					self.languages_list.append({"language_name":item["LanguageName"], "language":item["SubLanguageID"], "flag_image":"flags/" + item["ISO639"] + ".gif"})
			return True, ""
		else:
			error = _( 737 )
			LOG( LOG_ERROR, error )
			return False, error
	except Exception, e:
		error = _( 731 ) % ( _( 734 ), str ( e ) )
		LOG( LOG_ERROR, error )
		return False, error

    def getfolderfilesinfo( self, folder ):
	recursivefiles = []
	hashedfiles_list = []
	hashes_list = []
	self.folderfilesinfo_list = []
	try:
		if ( self.connected ) and ( os.path.isdir( folder ) ):
			parser = RecursiveParser.RecursiveParser()
			recursivefiles = parser.getRecursiveFileList(folder, globals.videos_ext)
			for item in recursivefiles:
				filename = globals.EncodeLocale(os.path.basename(item))
				filenameurl = (item) #Corrects the accent characters.
				if not os.path.exists(item):
					error = _( 738 ) % ( item, )
					LOG( LOG_ERROR, error )
					return False, error
				else:
					hash = globals.hashFile(item)
					if hash == "IOError" or hash == "SizeError":
						error = _( 739 ) % ( item, hash, )
						LOG( LOG_ERROR, error )
						return False, errors
					else:
						hashedfiles_list.append( {'filename':item, 'hash':hash} )
						hashes_list.append( hash )
			if hashedfiles_list:
				hashes = self.server.CheckMovieHash(self.osdb_token, hashes_list)
				for item in hashes_list:
					for file in hashedfiles_list:
						if file["hash"] == item:
							f = file["filename"]				
					if hashes["data"][item]:
						movie = hashes["data"][item]
						self.folderfilesinfo_list.append( {'filename':f, 'moviename':movie['MovieName'], 'imdbid':movie['MovieImdbID']} )
						
	except Exception, e:
		error = _( 731 ) % ( _( 735 ), str ( e ) ) 
		LOG( LOG_ERROR, error )
		return False, error
		

    def searchsubtitles( self, file ):
	self.subtitles_list = []
        self.allow_exception = False
	
	try:
		if ( self.osdb_token ) and ( self.connected ):
			LOG( LOG_INFO, "Searching subtitles for " + file )
			
			#We try and check if the file is from an smb share
			if file.find( "//" ) == 0:
				error = _( 740 )
				LOG( LOG_ERROR, error )
				return False, error

			filename = globals.EncodeLocale( os.path.basename( file ) )
			filenameurl = ( filename ) #Corrects the accent characters.
			
			if not os.path.exists( file ):
				error = _( 738 ) % ( file, )
				LOG( LOG_ERROR, error )
				return False, error
			else:
				hash = globals.hashFile( file )
				if hash == "IOError" or hash== "SizeError":
					error = _( 739 ) % ( file, hash, )
					LOG( LOG_ERROR, error )
					return False, error		
				#We keep going if there was no error.
				videofilesize = os.path.getsize( file )
				linkhtml_index =  "search/moviebytesize-"+str( videofilesize )+"/moviehash-"+hash
				videofilename = filename
				pathvideofilename = file
				videohash = hash
				hashresult = {"hash":hash, "filename":filename, "pathvideofilename":file, "filesize":str( videofilesize )
						, "linkhtml_index":linkhtml_index}
				searchlist = []
				searchlist.append({'sublanguageid':"all",'moviehash':hashresult["hash"],'moviebytesize':str( hashresult["filesize"] ) })
				search = self.server.SearchSubtitles( self.osdb_token, searchlist )
				if search["data"]:
					for item in search["data"]:
						flag_image = ""
						for flag in self.languages_list:
							if flag["language"] == item["SubLanguageID"]:
								flag_image = flag["flag_image"]
								lang_name = flag["language_name"]
								break		
						if flag_image == "":
							flag_image = "-.gif"
							lang_name = ""
						self.subtitles_list.append({'filename':item["SubFileName"],'link':item["ZipDownloadLink"],"language_name":lang_name,"language_flag":flag_image})

					message = _( 742 ) % ( str( len ( self.subtitles_list ) ), )
					LOG( LOG_INFO, message )
					return True, message
				else: 
					message = _( 741 )
					LOG( LOG_INFO, message )
					return True, message
	except Exception, e:
		error = _( 731 ) % ( _( 736 ), str ( e ) ) 
		LOG( LOG_ERROR, error )
		return False, error

