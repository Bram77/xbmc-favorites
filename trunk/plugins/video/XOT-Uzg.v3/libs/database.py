import os, sys

sys.path.append(os.path.join(os.getcwd().replace(";",""),'libs'))
from pysqlite2 import dbapi2 as sqlite
import config
import common

logFile = sys.modules['__main__'].globalLogFile

#===============================================================================
# Database Handler class
#===============================================================================
class DatabaseHandler:
    def __init__(self):
        """
            initialize the DB connection
        """
        self.xotDatabase = sqlite.connect(config.xotDbFile)
        self.CheckDatabaseExistence()
        pass
    
    #============================================================================== 
    def CheckDatabaseExistence(self):
        """
            Checks if the database exists, if not, it will be created.
        """
        sql = "PRAGMA table_info('favorites')"
        result = self.ExecuteQuery(sql)
        if len(result) < 1:
            self.CreateDatabase()
                    
    #============================================================================== 
    def CreateDatabase(self):
        """
            Creates a functional database
        """
        logFile.info("Creating Database")
        sql = 'PRAGMA encoding = "UTF-16"'
        self.ExecuteNonQuery(sql, True)
        sql = "CREATE TABLE favorites (channel string, name string, url string)"
        self.ExecuteNonQuery(sql)
        sql = "CREATE TABLE settings (setting string, value string)"
        self.ExecuteNonQuery(sql)
    
    #==============================================================================
    def AddFavorite(self, name, url, channelName):
        logFile.debug("Adding favorite '%s' for channel '%s' and url '%s'", name, channelName, url)
        sql = u"INSERT INTO favorites (channel, name, url) VALUES(?, ?, ?)"
        params = (channelName, name, url)
        logFile.debug(params)
        self.ExecuteNonQuery(sql, params=params)
    
    #==============================================================================
    def LoadFavorites(self, channelName):
        logFile.debug("Loading favorites")
        items = []
        
        sql = "SELECT name, url FROM favorites WHERE channel='%s'" % (channelName)
        rows = self.ExecuteQuery(sql)
        
        for row in rows:            
            item = common.clistItem(row[0], row[1])
            items.append(item)
        
        return items
    
    #============================================================================== 
    def DeleteFavorites(self, name, url):
        logFile.debug("Deleting favorite %s (%s)", name, url)
        query = "DELETE FROM favorites WHERE name=? AND url=?"
        self.ExecuteNonQuery(query, commit=True, params=(name, url))
        return
    
    #===============================================================================
    # Query Methods 
    #===============================================================================
    def ExecuteNonQuery(self, query, commit=True, params = []):
        """
            Executes and commits (if true) a sql statement to the database.
            Returns nothing, as it does not expect any results
        """
        
        # decode to unicode
        uParams = []
        for param in params:
            uParams.append(param.decode('iso-8859-1'))
        
        cursor = self.xotDatabase.cursor()
        if len(params) > 0:
            cursor.execute(query, uParams)
        else:
            cursor.execute(query)
        
        if commit:
            self.xotDatabase.commit()
    
    def ExecuteQuery(self, query, commit=False, params = []):
        """
            Executs and commits (if true) a sql statement to the database.
            Returns a row-set
        """
        
        # decode to unicode
        uParams = []
        for param in params:
            uParams.append(param.decode('iso-8859-1'))
        
        cursor = self.xotDatabase.cursor()
        if len(params) > 0:
            cursor.execute(query, uParams)
        else:
            cursor.execute(query)        
        
        if commit:
            self.xotDatabase.commit()
        
        return cursor.fetchall()