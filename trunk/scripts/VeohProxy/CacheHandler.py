import traceback
class CacheHandler:
	def getFromCache(self,name):
		return None
	def saveToCache(self,name, toSave):
		return 0

class FileCacheHandler(CacheHandler):
	def __init__(self):
		self.cache={}
		self.path=sys.path[0]

	def getFileName(self, name):
		import os
		import sys
		return os.path.join(self.path,name) +".vp"
		
	def saveToCache(self, name, toSave):
		try:
			import pickle
			fh=open(self.getFileName(name), "w")
			pickle.dump(toSave, fh)
			fh.close()
		except:
			try:
				fh.close()
			except:
				pass
			return None
			
	def getFromCache(self,name):
		try:
			import pickle
			fh=open(self.getFileName(name), "r")
			a=pickle.load(fh)
			fh.close()
			return a
		except:
			try:
				fh.close()
			except:
				pass
			return None

class MemoryCacheHandler(CacheHandler):
	def __init__(self):
		self.cache={}
		
	def saveToCache(self,name, toSave):
		self.cache[name]=toSave
		
	def getFromCache(self, name):
		try:
			return self.cache[name]
		except:
			return None
	
