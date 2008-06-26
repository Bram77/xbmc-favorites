

import sys
import os
import xbmcgui
import xbmcplugin

_ = sys.modules[ "__main__" ].__language__

class Main:

    CATEGORY_GROUP_START = 10002
    CATEGORY_GROUP_END   = 10010
    def __init__( self ):
	self._get_settings()	
	self.get_categories()
    

    def get_categories( self ):
        try:	   ok = True
           for cat_id in range( self.CATEGORY_GROUP_START, self. CATEGORY_GROUP_END + 1 ):
	       url = "%s?id=%d&index=%d" % ( sys.argv[ 0 ], cat_id,self.settings[ "start_index"]) 
	       url = "%s?id=%s&index=%s" % ( sys.argv[ 0 ],  cat_id, self.settings[ "start_index"]) 			
               listitem=xbmcgui.ListItem( _(cat_id))
	       ok = xbmcplugin.addDirectoryItem( handle=int(sys.argv[ 1 ]), url=url, listitem=listitem, isFolder=True, )
               if ( not ok ): raise
        except:
            print sys.exc_info()[ 1 ]
            ok = False
       # if ( ok ):
   
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )
   

	
    #plugin settings        	
    def _get_settings( self ):
        self.settings = {}
	try:        
		self.settings[ "start_index"]   =  int(xbmcplugin.getSetting("start_index")  )
 
        except:
                traceback.print_exc(file=sys.stdout)
                pass

       

