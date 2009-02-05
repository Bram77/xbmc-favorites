"""
A MySQL client library written entirely in python.

$Id: mysql.py,v 1.5 2006/07/25 07:54:22 frooby Exp $

A pure python implementation of an interface to the MySQL database.  This
module is written entirely in python and does not require linking to any
dyanmic libraries or compiling of C driver code to connect to a MySQL
database.  This is handy for systems that have a python port but do not have
the MySQL database/libraries/dlls ported yet (e.g. Xbox Media Center).

There are no plans to implement additional features in this module.  It does
what I need it to do and that's as far as I have taken it.  If you would
like to contribute additional functionality to this, feel free to send me
any additions/changes/bug reports.

This python module is based on a pure perl implementation of an interface to
MySQL written by Hiroyuki Oyama.

Here are some simple examples of how to use this module:

import mysql

conn = mysql.Connection(
    host="myhost",
    database="mydb",
    user="myuser",
    password="mypass",
    timeout=30,
    port=3306)

if conn.executeSQL( "select * from db where hostname like '%myhost%'" ):
    iter = conn.dictRowIterator()
    for row in iter:
        for k in row.keys():
            v = row[k]
            if not v:
                print k + "=>[(null)]",
            else:
                print k + "=>[" + v + "]",
        print
    print str(iter.getRowCount()) + " rows retrieved"
else:
    print "ERROR " + str(conn.getErrorCode()) + ": " + conn.getErrorMsg()

if conn.executeSQL(
    "insert into person (id, first, last) values (null, 'Tom','Warkentin')" ):
    print "insert succeeded: id=" + str(conn.getInsertId())
else:
    print "ERROR " + str(conn.getErrorCode()) + ": " + conn.getErrorMsg()

if conn.executeSQL(
    "update settings set data = 'my new value' where value = 'my data value'" ):
    print "update succeeded"
else:
    print "ERROR " + str(conn.getErrorCode()) + ": " + conn.getErrorMsg()

if conn.executeSQL( "delete from db where hostname = 'myhost'" ):
    print "delete succeeded"
else:
    print "ERROR " + str(conn.getErrorCode()) + ": " + conn.getErrorMsg()

if conn.createDatabase( "mydb" ):
    print "database created"
else:
    print "ERROR " + str(conn.getErrorCode()) + ": " + conn.getErrorMsg()

if conn.dropDatabase( "mydb" ):
    print "database dropped"
else:
    print "ERROR " + str(conn.getErrorCode()) + ": " + conn.getErrorMsg()

conn.close()


Copyright (C) 2004 Tom Warkentin <tom@ixionstudios.com>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
or at the website: http://www.gnu.org

"""
import re
import sha
import socket
import string
import struct
import sys
import logging

log = logging.getLogger('mythtv.mysql')
wlog = logging.getLogger('mythtv.mysql.wire')

SUPPORT_41_AUTH = False

if SUPPORT_41_AUTH:
    CLIENT_LONG_PASSWORD = 1
    CLIENT_FOUND_ROWS = 1 << 1
    CLIENT_LONG_FLAG = 1 << 2
    CLIENT_CONNECT_WITH_DB = 1 << 3
    CLIENT_NO_SCHEMA = 1 << 4
    CLIENT_COMPRESS = 1 << 5
    CLIENT_ODBC = 1 << 6
    CLIENT_LOCAL_FILES = 1 << 7
    CLIENT_IGNORE_SPACE = 1 << 8
    CLIENT_PROTOCOL_41 = 1 << 9
    CLIENT_INTERACTIVE = 1 << 10
    CLIENT_SSL = 1 << 11
    CLIENT_IGNORE_SIGPIPE = 1 << 12
    CLIENT_TRANSACTIONS  = 1 << 13
    CLIENT_SECURE_CONNECTION = 1 << 15
    CLIENT_MULTI_STATEMENTS = 1 << 16
    CLIENT_MULTI_RESULTS = 1 << 17
    CLIENT_CAPABILITIES = CLIENT_LONG_FLAG | CLIENT_LONG_PASSWORD | CLIENT_PROTOCOL_41 | CLIENT_SECURE_CONNECTION | CLIENT_TRANSACTIONS 
    #CLIENT_LONG_PASSWORD|CLIENT_LONG_FLAG|CLIENT_TRANSACTIONS| \
    #                        CLIENT_PROTOCOL_41|CLIENT_SECURE_CONNECTION
                                
# ugly hack for problem passing Connection object to class contructor on xbox
global db
db = None

def escape(obj):
    """
    Method to escape a string.  If the object is not defined, returns "NULL".
    This method is intended to be used to escape values sent to mysql in an
    insert or update statement.

    Example:

    s = "they're here"
    print escape( s )
    # will return: 'they\'re\ here'

    print escape( None )
    # will return: NULL
    """
    if type( obj ) is int:
        return "%d"%obj
    elif obj == None:
        return "NULL"
    elif type( obj ) is str or type( obj ) is string:
        return "'%s'"%re.escape( obj )
    else:
        return obj

# =============================================================================
class ClientException(Exception):
    pass

class ServerException(Exception):
    pass

# =============================================================================
class Connection:
    BUFFER_LENGTH   = 1024
    CMD_QUIT        = "\x01"
    CMD_QUERY       = "\x03"
    CMD_CREATE_DB   = "\x05"
    CMD_DROP_DB     = "\x06"

    def __init__(self, host, database, user, password, port=3306, timeout=60.0):
        """
        Initialize a new connection to a MySQL database.
        """
        self.isConnected = 0
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.timeout = timeout
        self.socket = None
        self.salt = None
        self.protocolVersion = None
        self.clientCapabilities = None
        
        if SUPPORT_41_AUTH:
            self.clientCapabilities = CLIENT_CAPABILITIES
            self.clientCapabilities |= CLIENT_MULTI_STATEMENTS
            if self.database:
                self.clientCapabilities |= CLIENT_CONNECT_WITH_DB

        self.__connect()
        self.__getServerInfo()
        self.__requestAuth()
        self.__resetStatus()

    #---------------------------------------------------------------------------
    # class private/protected methods
    #---------------------------------------------------------------------------
    def __andByChar( self, source, mask ):
        retVal = source & mask
        return retVal

    def __andByLong( self, source, mask=4294967295L ):  # 0xFFFFFFFF
        retVal = self.__cutOffToLong(source) & self.__cutOffToLong(mask)
        return retVal

    def __buildMsg( self, cmd, args, flags=0 ):
        """
        Function to build a message to send to the server.
        
        cmd     - Command to send to the server
        args    - Arguments associated with the cmd.  No checking is done to
                  verify that the args passed are valid for the cmd passed.
                  The caller is trusted to know what the valid args are.
        flags   - Some commands require additional flags.  I'm not too sure why
                  or what effect this has on the receiving end since I have
                  not looked at MySQL protocol source code.
        """
        body = cmd
        body += string.join( args, "\0" )

        msg = struct.pack( "<H", len( body ) )
        msg += struct.pack( "B", 0 )
        msg += struct.pack( "B", flags ) + body

        return msg

    def __connect( self ):
        """
        Method to create and connect a socket to a MySQL database server socket.
        Attempts to set the timeout but continues even if the timeout cannot
        be set.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(1)

        try:
            s.settimeout(self.timeout)
        except:
            log.warn("failed to set socket timeout to %d" % self.timeout)

        s.connect((self.host, self.port))
        log.debug("connected to mysql db: " + self.host + ":" + str(self.port))
        self.socket = s

    def __cutOffToLong( self, source ):
        while source > 4294967295L:             # 0xFFFFFFFF
            source -= (4294967295L + 1L)
        return source

    def __del__( self ):
        """Destructor for an instance of the class."""
        Connection.close( self )

    def __dumpMsg(self, data):
        """Dumps the passed message if debugging is enabled."""
        #if log.isEnabledFor('DEBUG'):
        #wlog.debug( self.__sprintMsg( msg ) )
        
        def is_ascii(data):
            if data.isalnum():
                return data
            return '.'
        
        dump = "packet length %d\n" % len(data)
        dump += "method call: %s \npacket dump\n" % sys._getframe(1).f_code.co_name
        dump += ("-" * 88) + "\n"
        dump_data = [data[i:i+16] for i in xrange(len(data)) if i%16 == 0]
        for d in dump_data:
            dump += ' '.join(map(lambda x:"%02X" % ord(x), d)) + \
                    '   ' * (16 - len(d)) + ' ' * 2 + ' '.join(map(lambda x:"%s" % is_ascii(x), d)) + "\n"
        dump += ("-" * 88) + "\n\n"
        wlog.debug(dump)

    def __executeCmd( self, cmd, args ):
        """
        Executes the specified command on the server.

        cmd     - The command to be executed.
        args    - The arguments for the command.  The caller is assumed to
                  know what the valid args are for the cmd passed.
        """
        msg = self.__buildMsg( cmd, [args] )
        self.__dumpMsg( msg )
        self.socket.send( msg )

        result = self.socket.recv( Connection.BUFFER_LENGTH )
        self.__dumpMsg( result )
        self.__resetStatus()

        if self.__isError( result ):
            return self.__setErrorByPacket( result )
        elif self.__isSelectQueryResult( result ):
            return self.__getRecordByServer( result )
        elif self.__isUpdateQueryResult( result ):
            # treat database drop as a special case - server returns 0 but we
            # return 1 to indicate success
            if cmd == Connection.CMD_DROP_DB:
                return 1
            else:
                return self.__getAffectedRowsInfoByMsg( result )
        else:
            text = "unknown response: " + self.__sprintMsg( result )
            raise ClientException, text

    def __getAffectedRowsInfoByMsg( self, msg ):
        self.affectedRowsLength = self.__getAffectedRowsLength( msg )
        log.debug( "affectedRowsLength=%d"%self.affectedRowsLength )
        self.insertId = self.__getInsertId( msg )
        log.debug( "insertId=%d"%self.insertId )
        self.serverMsg = ''
        return self.affectedRowsLength

    def __getAffectedRowsLength( self, msg ):
        return ord( msg[5] )

    def __getColumnLength( self, msg ):
        "Retrieves the number of columns in a server response."
        return ord( msg[4] )

    def __getErrorCode( self, msg ):
        """
        Retrieves the error code from the passed message. Raises an exception
        if the passed message is not an error message.
        """
        if not self.__isError( msg ):
            raise ClientException, "invalid error msg: " + self.__sprintMsg( msg )
        return struct.unpack( "<H", msg[5:7] )[0]

    def __getHash( self, password ):
        """
        Calculates a hash value based on the password passed in.
        """
        nr = 1345345333L
        add = 7L
        nr2 = 305419889L        # 0x12345671
        pwlen = len(password)
        for i in range(0,pwlen):
            c = password[i]
            if c == ' ' or c == '\t':
                continue
            tmp = ord( c )
            value = ((self.__andByChar(nr,63) + add) * tmp) + nr * 256
            nr = self.__xorByLong( nr, value )
            nr2 += self.__xorByLong( (nr2 * 256), nr )
            add += tmp
        return (int(self.__andByLong( nr, 2147483647L)),        # 0x7FFFFFFF
            int(self.__andByLong( nr2, 2147483647L )))

    def __getInsertId( self, msg ):
        if ord( msg[6] ) != 0xfc:
            return ord( msg[6] )
        else:
            return struct.unpack( "<H", msg[7:9] )[0]

    def __getRecordByServer( self, msg ):
        self.__getColumnLength( msg )
        while self.__hasNextMsg( msg ):
            nextMsg = self.socket.recv( Connection.BUFFER_LENGTH )
            self.__dumpMsg( nextMsg )
            msg += nextMsg
        self.selectedRecord = msg
        return 1

    def __getServerInfo(self):
        """Gets server info an the salt needed to authenticate"""
        msg = self.socket.recv(Connection.BUFFER_LENGTH)
        self.__dumpMsg(msg)
        if self.__isError(msg):
            raise ServerException, msg[7:]

        # get length of message
        i = 0
        msgLen = struct.unpack("<I", msg[i:4])[0]
        i += 4
        wlog.debug("msgLen is %s" % msgLen)

        # get protocol version
        self.protocolVersion = ord(msg[i])
        i += 1
        wlog.debug("protocol version is %s" % self.protocolVersion)
        if self.protocolVersion == 10:
            if SUPPORT_41_AUTH:
                self.clientCapabilities |= CLIENT_LONG_PASSWORD
            else:
                self.clientCapabilities = 1

        # get server version
        end = msg.find("\0", i)
        self.serverVersion = msg[i:end]
        wlog.debug("server version is '%s'" % self.serverVersion)
        i = end + 1

        # get server thread id
        self.serverThreadId = struct.unpack("<I", msg[i:i + 4])[0]
        wlog.debug("server thread id is %s" % self.serverThreadId)
        i += 4

        # get salt for password hashing
        self.salt = msg[i:i + 8]
        wlog.debug("salt is '%s'" % self.salt)

        # new stuff ==============================================
        if SUPPORT_41_AUTH:
            i += 9
            if len(msg) >= i + 1:
                i += 1
           
            self.serverCapabilities = struct.unpack('h', msg[i:i+2])
            wlog.debug("serverCapabilities is %s" % self.serverCapabilities)
            
            i += 1
            self.serverLanguage = ord(msg[i:i+1])
            wlog.debug('serverLanguage is %s' % self.serverLanguage)
            
            i += 16 
            if len(msg) >= i+12-1:
                rest_salt = msg[i:i+12]
                wlog.debug("additional salt is '%s'" % rest_salt)
                self.salt += rest_salt
            wlog.debug("final salt is '%s'" % self.salt)
        
    def __getServerMsg( self, msg ):
        if len( msg ) < 7:
            return ''
        return msg[7:]

    def __hasNextMsg( self, msg ):
        return msg[-1] != '\xfe'

    def __hasSelectedRecord( self ):
        return self.selectedRecord

    def __isError( self, msg ):
        if len( msg ) < 4:
            return 1
        return ord( msg[4:5] ) == 255

    def __isSelectQueryResult( self, msg ):
        if self.__isError( msg ):
            return None
        return ord(msg[4]) >= 1

    def __isUpdateQueryResult( self, msg ):
        if self.__isError( msg ):
            return None
        return ord(msg[4]) == 0

    def __requestAuth( self ):
        self.__sendLoginMsg()
        authResult = self.socket.recv( Connection.BUFFER_LENGTH )
        wlog.debug('login response:')
        self.__dumpMsg(authResult)
        
        if SUPPORT_41_AUTH:

            def _check_error(recv_data):
                field_count = ord(recv_data[4:5])
                wlog.debug('field count = %s' % field_count)
                if field_count == 255:
                    raise ServerException, recv_data[7:]
                    #raise_mysql_exception(recv_data)

#            def __isError( self, msg ):
#                if len( msg ) < 4:
#                    return 1
#                return ord( msg[4:5] ) == 255

            _check_error(authResult)
        else:
            if self.__isError(authResult):
                self.close()
                if len(authResult) < 7:
                    raise ClientException, "authentication timeout"
                raise ServerException, authResult[7:]
        
        log.debug( "connected to database successfully" )
        self.isConnected = 1

    def __resetStatus( self ):
        self.insertId = None
        self.serverMsg = ''
        self.errorCode = None
        self.selectedRecord = None

    def __scramblePassword( self, password, salt, flags ):
        if len(password) == 0:
            return ''
        hsl = len( salt )
        out = []
        hashPass = self.__getHash(password)
        hashMess = self.__getHash(salt)
        maxValue = None
        seed = None
        seed2 = None
        if flags < 1:
            maxValue = 33554431L        # 0x01FFFFFF
            seed = self.__xorByLong(hashPass[0], hashMess[0]) % maxValue
            seed2 = int(seed / 2)
        else:
            maxValue = 1073741823L      # 0x3FFFFFFF
            seed = self.__xorByLong(hashPass[0], hashMess[0]) % maxValue
            seed2 = self.__xorByLong(hashPass[1], hashMess[1]) % maxValue
        dMax = maxValue
        dRes = None
        dSeed = None

        for i in range(0,hsl):
            val = seed * 3L + seed2
            seed = int(val % maxValue)
            seed2 = int((seed + seed2 + 33) % maxValue)
            dSeed = seed
            dRes = float(dSeed) / float(dMax)
            out.append( int(dRes * 31) + 64 )

        if flags == 1:
            seed = (seed * 3L + seed2) % maxValue
            seed2 = (seed + seed2 + 33L) % maxValue
            dSeed = seed

            dRes = float(dSeed) / float(dMax)
            e = int(dRes * 31)
            for i in range(0,hsl):
                out[i] ^= e
        retVal = ''
        for i in range(0,len(out)):
            retVal += chr(out[i])
        return retVal
    
    def __scramble41(self, password, salt):
        stage1 = sha.new(password).digest()
        stage2 = sha.new(stage1).digest()
        s = sha.new()
        s.update(salt)
        s.update(stage2)
        result = s.digest()
        return self.__my_crypt41(result, stage1)
    
    def __my_crypt41(self, message1, message2):
        length = len(message1)
        result = ''
        for i in xrange(length):
            x = (struct.unpack('B', message1[i:i+1])[0] ^ struct.unpack('B', message2[i:i+1])[0])
            result += struct.pack('B', x)
        return result

    def __sendLoginMsg(self):
        """Sends a login message to the server"""
        if SUPPORT_41_AUTH:
            if self.serverVersion.startswith('5'):
                self.clientCapabilities |= CLIENT_MULTI_RESULTS
            
            msg = (struct.pack('l', self.clientCapabilities)) + "\0\0\0\x01" + \
                '\x08' + '\0'*23 + \
                self.user + "\0\x14" + self.__scramble41(self.password, self.salt)
                
            if self.database:
                msg += self.database + "\0"
                
            msg = pack_int24(len(msg)) + "\x01" + msg
                            
        else:
            msg = self.__buildMsg(
                cmd = "\x8D\x00\x00\x00\x00",
                args = [
                    self.user,
                    self.__scramblePassword(
                        self.password,
                        self.salt,
                        self.clientCapabilities),
                    self.database ],
                flags = 1 )
        
        wlog.debug('login msg:')    
        self.__dumpMsg(msg)
        self.socket.send(msg)

    def __setErrorByPacket( self, msg ):
        self.serverMsg = self.__getServerMsg( msg )
        self.errorCode = self.__getErrorCode( msg )
        return None

    def __sprintMsg( self, msg ):
        """
        """
        charsText = []
        for i in range( 0, len( msg ) ):
            charsText.append( "%02x" % ord( msg[i] ) )
        transMsg = ''
        for i in range( 0, len( msg ) ):
            if re.match('[\d \w\!-\/\:-\@\[-\`\{-\~]', msg[i]):
                transMsg += msg[i]
            else:
                transMsg += '.'
        return string.join( charsText, ' ' ) + " (" + transMsg + ")"
        
    def __xorByLong( self, source, mask=0L ):
        retVal = self.__cutOffToLong(source) ^ self.__cutOffToLong(mask)
        return retVal

    #---------------------------------------------------------------------------
    # public methods
    #---------------------------------------------------------------------------
    def close( self ):
        """
        Closes a connection to the MySQL server.  Can be safely called
        multiple times (although subsequent calls don't do anything useful).
        """
        if self.socket:
            if self.isConnected > 0:
                log.debug( "sending quit command" )
                msg = self.__buildMsg( Connection.CMD_QUIT, [] )
                self.__dumpMsg( msg )
                self.socket.send( msg )
                self.isConnected = 0
            log.debug( "closing socket" )
            self.socket.close()
            self.socket = None

    def createDatabase( self, dbName ):
        """
        Creates the database with the passed dbName.  The user must have
        sufficient priviledges to do this.
        """
        return self.__executeCmd( Connection.CMD_CREATE_DB, dbName )
        
    def dictRowIterator( self ):
        """
        Returns a dictionary row iterator for the selected data.  Returns None
        if a select statement has not been executed.  Otherwise, returns a
        RowIterator object that can be used to iterate through all the rows
        retrieved.  Each row is a dictionary where the key is of the form
        <table_name>.<column_name> and the key value is the column value
        retrieved from the database.  Null column values are returned as None.
        """
        if not self.__hasSelectedRecord():
            return None

        iter = RowIterator(self.selectedRecord, RowIterator.DICT_ROW)
        self.selectedRecord = None
        iter.parse()
        return iter

    def dropDatabase( self, dbName ):
        """
        Drops the database named by the passed dbName.  The user must have
        sufficient priviledges to do this.
        """
        return self.__executeCmd( Connection.CMD_DROP_DB, dbName )
        
    def executeSQL( self, sqlText ):
        """
        Executes the passed SQL statement on the server.  Returns None on
        error.  On a successful select, returns 1.  All other statements return
        the number of rows affected.
        """
        return self.__executeCmd( Connection.CMD_QUERY, sqlText )

    def getErrorCode( self ):
        """
        Retrieves the error code returned by the last query to the server.  If
        no error was encountered, returns None.
        """
        return self.errorCode

    def getErrorMsg( self ):
        """
        Returns the server error message returned by the last query.  If no
        error was encountered, returns an empty string.
        """
        return self.serverMsg

    def getInsertId( self ):
        """
        Returns the id of the row that was inserted if the table being
        inserted into has a unique sequence column.  The value returned is
        meaningless if this is called after executing non-insert statements
        or tables that do not have a unique sequence column.
        """
        return self.insertId

    def getFormattedSQLResultsFromIterator(self):
        iter = self.dictRowIterator()
        columnWidths = {}
        columns = []
        columnMap = {}
        result = ''
        table = []
        y = 0
        firstRow = True

        for row in iter:

            if firstRow:
                columns, columnMap = self.getColumnNames(row)
                firstRow = False
                for column in columns:
                    columnWidths[column] = len(column)

            data = []
            for k in row.keys():
                column = columnMap[k]
                v = row[k]
                if not v:
                    width = len('null')
                    data.append(['NULL',column])
                else:
                    width = len(v)
                    data.append([v,column])

                if width > columnWidths[column]:
                    columnWidths[column] = width

            table.append(data)
            
        for column in columns:
            result += ''.ljust(columnWidths[column] + 1, '=')
        result += '\n'
        
        for column in columns:
            result += column.ljust(columnWidths[column] + 1)
        result += '\n'

        for column in columns:
            result += ''.ljust(columnWidths[column] + 1, '-')
        result += '\n'

        for row in table:
            for data in row:
                v = data[0]
                column = data[1]
                result += v.ljust(columnWidths[column] + 1)
            result += '\n'

        for column in columns:
            result += ''.ljust(columnWidths[column] + 1, '-')
        result += '\n'
        result += str(iter.getRowCount()) + " rows retrieved\n"
        return result

       
    def getFormattedSQLResults(self, sqlText):
        """
        Given a sql statement, returns the results as a formatted string
        in a easy to read table format
        """
        self.executeSQL(sqlText)
        return self.getFormattedSQLResultsFromIterator()

    def getColumnNames(self, row):
        """
        Returns a list of columns and raw column name to short column name
        map for the passed in row
        """
        columns = []
        columnMap = {}
        cnt = 0
        for column in row.keys():
            tableName = column[column.find('.') + 1:]
            columns.append(tableName)
            columnMap[column] = tableName
            cnt += 1
        return columns, columnMap

# =============================================================================
class RowIterator:
    DICT_ROW                    = 0
    LIST_ROW                    = 1     # not implemented yet

    NULL_COLUMN                 = 251
    UNSIGNED_CHAR_COLUMN        = 251
    UNSIGNED_SHORT_COLUMN       = 252
    UNSIGNED_INT24_COLUMN       = 253
    UNSIGNED_INT32_COLUMN       = 254
    UNSIGNED_INT32_PAD_LENGTH   = 4

    #---------------------------------------------------------------------------
    # class private/protected methods
    #---------------------------------------------------------------------------
    def __init__(self, msg, rowType):
        self.msg = msg
        self.position = 0
        self.columns = []
        self.rowType = rowType
        self.index = 0

    def __iter__( self ):
        return self

    def __fetchRowAsDict( self ):
        if self.__isEndOfMsg():
            return None
        result = []
        for i in range(0, self.columnLength):
            if self.columns[i]['table']:
                column = self.columns[i]['table'] + "." + self.columns[i]['column']
            else:
                column = self.columns[i]['column']
            value = self.__getStringAndSeekPos()
            result.append( (column,value) )
        self.position += 4
        return dict(result)

    def __getColumnLength( self ):
        self.position += 4
        self.columnLength = ord( self.msg[self.position] )
        wlog.debug( "column length is " + str( self.columnLength ) )
        self.position += 5

    def __getColumnNames( self ):
        for i in range( 0, self.columnLength ):
            self.columns.append(
                { 'table': self.__getStringAndSeekPos(),
                'column': self.__getStringAndSeekPos() } )
            self.position += 14
        self.position += 5

        if wlog.isEnabledFor('DEBUG'):
            columns = []
            for i in self.columns:
                columns.append( str(i['table']) + "." + str(i['column']) )
            wlog.debug( string.join( columns, ", " ) )

    def __getFieldLength( self ):
        wlog.debug("pos=" + str(self.position) + " len=" + str(len(self.msg)) )
        head = ord( self.msg[self.position] )
        self.position += 1

        if head == RowIterator.NULL_COLUMN:
            return None
        if head < RowIterator.UNSIGNED_CHAR_COLUMN:
            return head
        elif head == RowIterator.UNSIGNED_SHORT_COLUMN:
            length = struct.unpack(
                "<H", self.msg[self.position:self.position+2] )[0]
            self.position += 2
            return length
        elif head == RowIterator.UNSIGNED_INT24_COLUMN:
            int24 = self.msg[self.position:self.position+3]
            length = int(struct.unpack(
                'B', int24[0] )[0]) + int(struct.unpack(
                'B', int24[1] )[0]) << 8 + int(struct.unpack(
                'B', int24[2] )[0]) << 16
            self.position += 3
            return length
        else:
            int32 = self.msg[self.position:self.position+4]
            length = int(struct.unpack(
                'B', int32[0] )[0]) + (int(struct.unpack(
                'B', int32[1] )[0]) << 8) + (int(struct.unpack(
                'B', int32[2] )[0]) << 16) + (int(struct.unpack(
                'B', int32[3] )[0]) << 32)
            self.position += 4
            self.position += RowIterator.UNSIGNED_INT32_PAD_LENGTH
            return length

    def __getStringAndSeekPos( self ):
        length = self.__getFieldLength()
        if not length:
            return None

        tmpString = self.msg[self.position:self.position+length]
        wlog.debug( "tmpString=[" + tmpString + "]" )
        self.position += length
        return tmpString

        # TODO
        #
        # Figure out a nice way to clean this HACK up so that special characters
        # are displayed correctly.  This seems to work for French but I have
        # no idea if it works for other characters.
        #
        ##retList = []
        ##i = 0
        ##while i < len(tmpString):
        ##    if ord(tmpString[i]) == ord('\xc3'):
        ##        retList.append(chr(ord(tmpString[i+1])+(ord('\xe9')-ord('\xa9'))))
        ##        i += 2
        ##    else:
        ##        retList.append(tmpString[i])
        ##        i += 1
        ##return string.join(retList, "")
        
    def __isEndOfMsg( self ):
        return len( self.msg ) <= self.position + 1

    def parse( self ):
        self.__getColumnLength()
        self.__getColumnNames()

    def getRowCount( self ):
        """
        Returns the number of rows retrieved.  This value is incremented as
        each call to next() is made.  If you want the actual number of rows
        retrieved from the database, you will have to call next() until the
        StopIteration exception is raised before calling getRowCount().
        """
        return self.index

    def next( self ):
        """
        Returns the next row retrieved from the database.  Raises the
        StopIteration exception when all rows have been retrieved.
        """
        if self.__isEndOfMsg():
            raise StopIteration
        self.index = self.index + 1
        if self.rowType == RowIterator.DICT_ROW:
            return self.__fetchRowAsDict()
        else:
            raise ClientException, "unsupported row type"
        
# =============================================================================
def pack_int24(n):
    return struct.pack('B', n%256) + struct.pack('H', n>>8)
