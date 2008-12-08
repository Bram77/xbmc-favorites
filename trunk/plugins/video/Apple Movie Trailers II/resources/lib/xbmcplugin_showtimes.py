"""
Showtimes module

Nuka1195
"""

import sys
import os

import xbmc
import xbmcgui
import xbmcplugin

from urllib import unquote_plus


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class GUI( xbmcgui.WindowXMLDialog ):
    ACTION_CANCEL_DIALOG = ( 9, 10, )

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        #xbmcgui.lock()
        self._parse_argv()
        self._get_settings()
        self._get_scraper()
        #xbmcgui.unlock()
        self.doModal()

    def onInit( self ):
        self._show_dialog()
        self._get_showtimes()

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( unquote_plus( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ) ), )

    def _show_dialog( self ):
        self.getControl( 20 ).setLabel( self.args.title )
        self.getControl( 30 ).setLabel( "%s: %s" % ( xbmc.getLocalizedString( 30603 ), self.settings[ "local" ] ), )
        self.getControl( 40 ).setLabel( "%s:" % ( xbmc.getLocalizedString(30602 ), ) )
        self.getControl( 50 ).setLabel( "" )
        self.getControl( 100 ).reset()
        self.getControl( 100 ).addItem( xbmc.getLocalizedString( 30601 ) )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "local" ] = xbmcplugin.getSetting( "local" )
        self.settings[ "scraper" ] = xbmcplugin.getSetting( "scraper" )
        self.settings[ "day" ] = int( xbmcplugin.getSetting( "day" ) )

    def _get_scraper( self ):
        exec "import resources.scrapers.%s.showtimesScraper as showtimesScraper" % ( self.settings[ "scraper" ], )
        self.ShowtimesFetcher = showtimesScraper.ShowtimesFetcher()

    def _get_showtimes( self ):
        date, self.movie_showtimes = self.ShowtimesFetcher.get_showtimes( self.args.title, self.settings[ "local" ] )
        if ( date is None ): date = xbmc.getLocalizedString( 30600 )
        else: date = "%s: %s" % ( xbmc.getLocalizedString( 30602 ), date, )
        self.getControl( 40 ).setLabel( date )
        self._fill_list()

    def _get_selection( self, choice ):
        self.getControl( 20 ).setLabel( choice )
        self.getControl( 30 ).setLabel( self.movie_showtimes[ choice ][ 0 ] )
        self.getControl( 40 ).setLabel( "%s:" % ( xbmc.getLocalizedString( 30602 ), ) )
        self.getControl( 50 ).setLabel( self.movie_showtimes[ choice ][ 2 ] )
        self.getControl( 100 ).reset()
        self.getControl( 100 ).addItem( xbmc.getLocalizedString( 30601 ) )
        date, self.movie_showtimes = self.ShowtimesFetcher.get_selection( self.movie_showtimes[ choice ][ 3 ] )
        self.getControl( 40 ).setLabel( "%s: %s" % ( xbmc.getLocalizedString( 30602 ), date, ) )
        self._fill_list()

    def _fill_list( self ):
        self.getControl( 100 ).reset()
        if ( self.movie_showtimes ):
            self.theaters = self.movie_showtimes.keys()
            self.theaters.sort()
            for theater in self.theaters:
                list_item = xbmcgui.ListItem( theater, self.movie_showtimes[ theater ][ 1 ], self.movie_showtimes[ theater ][ 0 ], self.movie_showtimes[ theater ][ 2 ] )
                self.getControl( 100 ).addItem( list_item )
        else:
            self.getControl( 100 ).addItem( xbmc.getLocalizedString( 30600 ) )

    def _close_dialog( self ):
        self.close()

    def onClick( self, controlId ):
        self._get_selection( self.theaters[ self.getControl( controlId ).getSelectedPosition() ] )

    def onFocus( self, controlId ):
        pass

    def onAction( self, action ):
        try:
            if ( action in self.ACTION_CANCEL_DIALOG ):
                self._close_dialog()
        except: pass
