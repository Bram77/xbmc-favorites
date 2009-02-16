import sys
import os
import xbmc
import xbmcgui
import threading
import osdb
from osdb import OSDBServer
from utilities import *
import urllib
import unzip

try: current_dlg_id = xbmcgui.getCurrentWindowDialogId()
except: current_dlg_id = 0
current_win_id = xbmcgui.getCurrentWindowId()

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__


class GUI( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        pass

    def set_filepath( self, path ):
        LOG( LOG_INFO, "set_filepath" )
        self.filepath = path[path.find("/"):len(path)]
        
    def onInit( self ):
        LOG( LOG_INFO, "onInit" )

        self.setup_all()
        
        if self.settings["username"]:
                self.getControl( 100 ).setLabel( _( 637 ) % ( self.settings["username"], ) )
                ok,msg = self.osdb_server.connect( self.settings["osdb_server"], self.settings["username"], self.settings["password"] )
        else:
                self.getControl( 100 ).setLabel( _( 636 ) )
                ok,msg = self.osdb_server.connect( self.settings["osdb_server"], "", "" )
        
        if not ok:
                self.getControl( 100 ).setLabel( _( 634 ) % ( msg, ) )
        else:
                self.getControl( 100 ).setLabel( _( 635 ) )

        self.osdb_server.getlanguages()
        if self.filepath:
                self.search_subtitles()
        else:
                self.setFocus( self.getControl( 111 ) )
                
    def setup_all( self ):
        self.setup_variables()
        self.get_settings()

    def get_settings( self ):
        self.settings = Settings().get_settings()
        
    def setup_variables( self ):
        self.controlId = -1
        self.allow_exception = False
        self.osdb_server = OSDBServer()
        self.osdb_server.Create()
        if xbmc.Player().isPlayingVideo():
                self.set_filepath( xbmc.Player().getPlayingFile() )


    def search_subtitles( self ):
                self.getControl( 100 ).setLabel( _( 642 ) % ( os.path.basename( self.filepath ), ) )
                ok,msg = self.osdb_server.searchsubtitles( self.filepath )
                if not ok:
                        self.getControl( 100 ).setLabel( _( 634 ) % ( msg, ) )
                        self.setFocus( self.getControl( 111 ) )
                elif self.osdb_server.subtitles_list:
                        for item in self.osdb_server.subtitles_list:
                                self.getControl( 120 ).addItem( xbmcgui.ListItem( item["filename"], item["language_name"], thumbnailImage = item["language_flag"] ) )
                        self.getControl( 120 ).selectItem( 0 )
                        self.getControl( 100 ).setLabel( msg )
                        self.setFocus( self.getControl( 120 ) )
                elif msg:
                        self.getControl( 100 ).setLabel( msg )
                        self.setFocus( self.getControl( 111 ) )

    def show_control( self, controlId ):
        self.getControl( 100 ).setVisible( controlId == 100 )
        self.getControl( 120 ).setVisible( controlId == 120 )
        page_control = ( controlId == 100 )
        try: self.setFocus( self.getControl( controlId + page_control ) )
        except: self.setFocus( self.getControl( controlId ) )



    def file_download(self, url, dest):
        dp = xbmcgui.DialogProgress()
        dp.create( __scriptname__, _( 633 ), os.path.basename(dest) )
        urllib.urlretrieve( url, dest, lambda nb, bs, fs, url=url: self._pbhook( nb, bs, fs, url, dp ) )
 
    def _pbhook(self, numblocks, blocksize, filesize, url=None, dp=None):
        try:
            percent = min( ( numblocks*blocksize*100 ) / filesize, 100 )
            print percent
            dp.update(percent)
        except:
            percent = 100
            dp.update( percent )
        if dp.iscanceled(): 
            print "Subtitle download cancelled" # need to get this part working
            dp.close()
                

    def downloadsubtitle(self, pos):
        if self.osdb_server.subtitles_list:
            filename = self.osdb_server.subtitles_list[pos]["filename"]
            filename = filename[0:filename.rfind(".")] + ".zip"
            remote_path = os.path.dirname( self.filepath )
            local_path = os.path.dirname( self.settings["subtitles_path"] )

            url = self.osdb_server.subtitles_list[pos]["link"]

            self.getControl( 100 ).setLabel( _( 632 ) % ( filename, ) )
            self.file_download( url, os.path.join( local_path, filename ) )

            if os.path.exists( os.path.join( local_path, filename ) ):
                un = unzip.unzip()
                self.getControl( 100 ).setLabel( _( 631 ) % ( filename, os.path.dirname( local_path ) ) )

                un.extract( os.path.join( local_path, filename ), local_path )
                if self.settings["save_to_videofile_path"]:

                        self.getControl( 100 ).setLabel( _( 631 ) % ( filename, os.path.dirname( remote_path ), ) )
                        un.extract( os.path.join( local_path, filename ), remote_path )
                self.getControl( 100 ).setLabel( _( 630 ) )


    def reset_controls( self ):
        self.getControl( 100 ).setLabel( "" )
        self.getControl( 120 ).reset()
        
    def search_dialog( self ):
        self.reset_controls()
        dialog = xbmcgui.Dialog()
        self.filepath = dialog.browse(1, _( 640 ), 'video')
        self.search_subtitles()

    def change_settings( self ):
        self.getControl( 100 ).setVisible( False )
        self.getControl( 110 ).setVisible( False )
        self.getControl( 120 ).setVisible( False )
        import settings
        settings = settings.GUI( "script-%s-settings.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(), "Default" )
        settings.doModal()
        ok = False
        if ( settings.changed ):
            self.get_settings()
            if ( settings.restart ):
                ok = xbmcgui.Dialog().yesno( __scriptname__, _( 240 ), "", _( 241 ) % ( __scriptname__, ), _( 256 ), _( 255 ) )
            if ok:
                self.exit_script( True )
        del settings
        self.getControl( 100 ).setVisible( True )
        self.getControl( 110 ).setVisible( True )
        self.getControl( 120 ).setVisible( True )

    def exit_script( self, restart=False ):
        self.close()
        if ( restart ): xbmc.executebuiltin( "XBMC.RunScript(%s)" % ( os.path.join( os.getcwd().replace( ";", "" ), "default.py" ), ) )

    def onClick( self, controlId ):
        if ( self.controlId == 112 ):
            self.change_settings()
        elif ( self.controlId == 111 ):
            self.search_dialog()
        elif ( self.controlId == 120 ):
            self.downloadsubtitle( self.getControl( 120 ).getSelectedPosition() )

    def onFocus( self, controlId ):
        self.controlId = controlId

    def onAction( self, action ):
        if ( action.getButtonCode() in EXIT_SCRIPT ):
            self.exit_script()

