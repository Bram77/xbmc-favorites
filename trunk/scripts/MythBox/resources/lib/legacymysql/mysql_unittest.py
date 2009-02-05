import logging
import logging.config
import socket
import traceback
import unittest
from mysql import Connection, ServerException

log = logging.getLogger('mythtv.unittest')

dbhost = 'change_me'
dbname = 'mythconverg'
dbuser = 'mythtv'
dbpassword = 'change_me'

class ConnectionTest(unittest.TestCase):

    def testLoginMySQLServer41Passes(self):
        conn = Connection(dbhost, dbname, dbuser, dbpassword, 3306, 60.0)
        self.assertTrue(conn, 'connection null')
        conn.close()

    def testLoginPasses(self):
        conn = Connection(dbhost, dbname, dbuser, dbpassword, 3306, 60.0)
        self.assertTrue(conn, 'connection null')
        conn.close()
        
    def testLoginFailsWhenMySQLNotListeningOnPort(self):
        try:
            conn = Connection(dbhost, dbname, dbuser, dbpassword, 9999, 60.0)
            fail('expected failure')
        except socket.error, ex:
            log.debug('Exception = %s:%s' % (type(ex), ex))
            self.assertTrue(str(ex).find('refused'), 'Error msg didnt match')

    def testLoginFailsWithInvalidPassword(self):
        try:
            conn = Connection(dbhost, dbname, dbuser, 'xxx', 3306, 60.0)
            self.fail('expected ServerException')
        except ServerException, ex:
            log.debug('Exception = %s:%s' % (type(ex), ex))
            self.assertTrue(str(ex).find('password'))

    def testLoginFailsWithInvalidUser(self):
        try:
            conn = Connection(dbhost, dbname, 'xxx', dbpassword, 3306, 60.0)
            fail('expected ServerException')
        except ServerException, e:
            errorMessage = str(e)
            log.debug('Exception = %s:%s' % (type(e), errorMessage))
            self.assertTrue(errorMessage.find('denied'))
            self.assertTrue(errorMessage.find('user'))

    def testLoginFailsWhenConnectingToNonExistantHostname(self):
        try:
            conn = Connection('1.1.1.1', dbname, dbuser, dbpassword, 3306, 1)
            fail('expected ServerException')
        except Exception, e:
            #except socket.timeout, e:
            errorMessage = str(e)
            log.debug('Exception = %s:%s' % (type(e), errorMessage))
            #self.assertTrue(errorMessage.find('timeout'))

    def testCloseSucceeds(self):
        conn = Connection(dbhost, dbname, dbuser, dbpassword, 3306, 60.0)
        conn.close()
        self.assertFalse(conn.isConnected)

    def testSuccessiveCallsToCloseHaveNoAdverseEffects(self):
        conn = Connection(dbhost, dbname, dbuser, dbpassword, 3306, 60.0)
        conn.close()
        conn.close()
        conn.close()
        self.assertFalse(conn.isConnected)

    def testGetErrorCodeIsNoneWhenNothingDone(self):
        conn = Connection(dbhost, dbname, dbuser, dbpassword, 3306, 60.0)
        errorCode = conn.getErrorCode()
        self.assertTrue(errorCode is None)

    def testGetErrorMessageIsEmptyWhenNothingDone(self):
        conn = Connection(dbhost, dbname, dbuser, dbpassword, 3306, 60.0)
        errorMessage = conn.getErrorMsg()
        self.assertEquals(0, len(errorMessage))

class SelectQueryTestCase(unittest.TestCase):

    def setUp(self):
        self.host = dbhost
        self.dbName = dbname
        self.username = dbuser
        self.password = dbpassword
        self.conn = Connection(self.host, self.dbName, self.username, self.password, 3306, 10)

    def tearDown(self):
        if self.conn:
            self.conn.close()
            
    def testSelectStatementWithNoRowsReturned(self):
        result = self.conn.executeSQL('select * from channel where chanid = 999')    
        if result:
            log.debug(self.conn.getFormattedSQLResultsFromIterator())
        else:
            log.debug(str(result))

        log.debug('Result = %s' % result)
        self.assertEquals(1, result, 'successfull sql select should return 1')
        self.assertTrue(self.conn.getErrorCode() is None, 'expected None error code') 
        self.assertEquals('', self.conn.getErrorMsg(), 'expected empty error msg')
        itr = self.conn.dictRowIterator()
        self.assertTrue(itr is None, 'expected null iterator')

    def testSelectStatementWithOneRowReturned(self):
        if self.conn.executeSQL( "select chanid, visible, xmltvid, freqid, sourceid, callsign, name, channum from channel where chanid=1021" ):
            log.debug('\n' + self.conn.getFormattedSQLResultsFromIterator())
        else:
            log.debug('ERROR ' + str(self.conn.getErrorCode()) + ': ' + self.conn.getErrorMsg())

    def testSelectStatementWithManyRowsReturned(self):
        if self.conn.executeSQL( "select chanid, visible, xmltvid, freqid, sourceid, callsign, name, channum from channel order by chanid" ):
            log.debug('\n' + self.conn.getFormattedSQLResultsFromIterator())
        else:
            log.debug("ERROR " + str(self.conn.getErrorCode()) + ": " + self.conn.getErrorMsg())

if __name__ == "__main__":
    logging.config.fileConfig('mythbox_log.ini')
    unittest.main()
    