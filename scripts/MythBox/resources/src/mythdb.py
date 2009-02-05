#
#  MythBox for XBMC - http://mythbox.googlecode.com
#  Copyright (C) 2009 analogue@yahoo.com
# 
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

import logging
import domain
import MySQLdb
import sre
import string
import util
        
from util import timed
        
log = logging.getLogger('mythtv.core')
mlog = logging.getLogger('mythtv.method')

# =============================================================================
class MythDatabase(object):

    def __init__(self, settings, translator):
        self.settings = settings
        self.translator = translator
        self.initialise()
    
    @timed        
    def initialise(self):
        log.debug("Initializing myth database connection")
        self.conn = MySQLdb.connect(
            host = self.settings.get("mysql_host"), 
            db = self.settings.get("mysql_database"),
            user = self.settings.get("mysql_user"),
            passwd = self.settings.get("mysql_password"),
            port = int(self.settings.get("mysql_port")),
            connect_timeout = 30)
        
    def close(self):
        if self.conn:
            self.conn.close()
            del self.conn

    @timed
    def getChannels(self):
        """Return viewable channels across all tuners as a list of Channels"""
        sql = \
            """
            SELECT
                ch.chanid, 
                ch.channum, 
                ch.callsign, 
                ch.name, 
                ch.icon, 
                ci.cardid
            FROM 
                channel ch,
                cardinput ci 
            WHERE 
                ch.channum IS NOT NULL
                AND ch.channum != ""
                AND ch.visible = 1
                AND ch.sourceid = ci.sourceid
            ORDER BY ch.chanid
            """
            
        channels = []
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for r in rows:
                channels.append(domain.ChannelFromQuery(r))
        finally:
            cursor.close()
        return channels
    
    @timed            
    def getRecordingGroups(self):
        """Returns [[recording group name, # recordings],]"""
        sql = \
            """
            SELECT DISTINCT 
                recgroup, 
                count(recgroup) as cnt 
            FROM 
                recorded 
            GROUP BY 
                recgroup ASC
            """
        recgroups = []
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute(sql)
            recgroups.append(["All Groups", 0])
            grpcnt = 0
            for row in cursor.fetchall():
                thisRow = ["",0]
                for k in row.keys():
                    if k.find("cnt") >= 0:
                        grpcnt += int(row[k])
                        thisRow[1] = int(row[k])
                    else:
                        thisRow[0] = str(row[k])
                recgroups.append(thisRow)
            recgroups[0][1] = grpcnt
        finally:
            cursor.close()
        return recgroups
          
    @timed            
    def getRecordingTitles(self, recgroup):
        """
        Returns list[list[title, # recordings] for the given string recording group
        ['All Shows', total # of shows] is always the first index of the returned
        list regardless of the recording group.
        """

        sql = \
          """
          SELECT DISTINCT 
              recorded.title, 
              COUNT(recorded.title) AS cnt 
          FROM 
              recorded
          """
        if string.upper(recgroup) != "ALL GROUPS":
            sql += "\nWHERE recorded.recgroup=\"%s\"" % str(recgroup)
        
        sql += " GROUP BY recorded.title ASC"

        titlegroups = []
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute(sql)
            titlegroups.append(["All Shows", 0])
            grpcnt = 0
            for row in cursor.fetchall():
                thisRow = ["",0]
                for k in row.keys():
                    if k.find("cnt") >= 0:
                        grpcnt += int(row[k])
                        thisRow[1] = int(row[k])
                    else:
                        thisRow[0] = str(row[k])
                titlegroups.append(thisRow)
            titlegroups[0][1] = grpcnt
        finally:
            cursor.close()
        return titlegroups

    @timed
    def getTuners(self):
        """ Returns list of Tuners """
        # TODO: Consider caching after first invocation - data is static
        sql = \
            """
            select 
                cardid, 
                hostname, 
                signal_timeout, 
                channel_timeout, 
                cardtype
            from   
                capturecard
            order by 
                cardid
            """
        tuners = []
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute(sql)
            for row in cursor.fetchall():
                tuners.append(domain.Tuner(
                    int(row['cardid']),
                    row['hostname'],
                    int(row['signal_timeout']),
                    int(row['channel_timeout']),
                    row['cardtype']))
        finally:
            cursor.close()
        return tuners

    @timed
    def getProgramListings(self, startTime, endTime, startChanId=None, endChanId=None):
        """
        Get tv listings for given time period and channel range.
        
        in  datetime.datetime startTime
        in  datetime.datetime endTime 
        in  int startChanId
        in  int endChanId
        out ProgramFromQuery[]
        
        TODO: Rename to getTVListings() or getProgramGuideListings() ?
        """
        mlog.debug("> " + util.currentMethod())
        strStartTime = startTime.strftime("%Y%m%d%H%M%S")
        strEndTime = endTime.strftime("%Y%m%d%H%M%S")
        
        sql = """
            select
                channel.chanid,
                channel.channum,
                channel.callsign,
                program.starttime,
                program.endtime,
                program.title,
                program.subtitle,
                program.description,
                program.showtype,
                program.originalairdate,
                program.category,
                program.seriesid,
                program.programid,
                channel.icon,
                channel.name as channame,
                0 as isduplicate
            from 
                channel,
                program
            where
                channel.visible = 1
                and channel.chanid = program.chanid
                and program.starttime != program.endtime
                and
                (
                    (
                        program.endtime > %s
                        and program.endtime <= %s
                    ) or
                    (
                        program.starttime >= %s
                        and program.starttime < %s
                    ) or
                    (
                        program.starttime < %s
                        and program.endtime > %s
                    ) or
                    (
                        program.starttime = %s
                        and program.endtime = %s
                    )
                )
        """ % (strStartTime, strEndTime,
               strStartTime, strEndTime,
               strStartTime, strEndTime,
               strStartTime, strEndTime)
        
        if startChanId and endChanId:
            sql += """
                and channel.chanid >= '%d'
                and channel.chanid <= '%d'
                """%(startChanId, endChanId)
        sql += " order by channel.chanid, program.starttime"

        programs = []
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute(sql)
            for row in cursor.fetchall():
                #log.debug(str(type(row)) + " " + str(row))
                programs.append(domain.ProgramFromQuery(row, self.settings, self.translator))
        finally:
            cursor.close()
        mlog.debug('< ' + util.currentMethod())
        return programs

    @timed
    def getMythSetting(self, key, hostname=None):
        """Returns the value from the Settings Table for the given key and hostname, None otherwise"""
        sql = """
            SELECT
                data
            FROM
                settings 
            WHERE
                value = "%s"
            """%(str(key))
            
        if hostname is not None:
            sql += ' AND hostname = "%s"' % hostname
                   
        result = None
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute(sql)
            for row in cursor.fetchall():
                result = str(row["data"])
        finally:
            cursor.close()
        log.debug("<= mythsettings['%s', %s] = %s"%(key, hostname, result))
        return result
    
    @timed
    def getRecordingSchedules(self, chanId="",recordId=-1):
        """
        Returns all recording schedules unless a specific channel or recording
        schedule ID is specified.
        
        Return Type: ScheduleFromQuery[]
        """
        log.debug("getting schedule for recordId = %s"%recordId)
        sql = """
            SELECT
                r.recordid,
                r.type,
                r.chanid,
                r.starttime,
                r.startdate,
                r.endtime,
                r.enddate,
                r.title,
                r.subtitle,
                r.description,
                r.category,
                r.profile,
                r.recpriority,
                r.autoexpire,
                r.maxepisodes,
                r.maxnewest,
                r.startoffset,
                r.endoffset,
                r.recgroup,
                r.dupmethod,
                r.dupin,
                r.station,
                r.seriesid,
                r.programid,
                r.search,
                r.autotranscode,
                r.autocommflag,
                r.autouserjob1,
                r.autouserjob2,
                r.autouserjob3,
                r.autouserjob4,
                r.findday,
                r.findtime,
                r.findid,
                r.inactive,
                r.parentid,
                c.channum,
                c.callsign,
                c.name as channame,
                c.icon
            FROM
                record r
            LEFT JOIN channel c ON r.chanid = c.chanid
            """
            
        if chanId != "":
            sql += "WHERE r.chanid = '%s' "%chanId
            
        if recordId != -1:
            if chanId == "":
                sql+="WHERE "
            else:
                sql +="AND "
            sql += "r.recordid = %d "%recordId
            
        sql += """
            ORDER BY
                r.recordid
                DESC
            """
        schedules = []
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute(sql)
            for row in cursor.fetchall():
                #log.debug(row)
                schedules.append(domain.ScheduleFromQuery(row, self.translator))
        finally:
            cursor.close()
        return schedules


    def setRecordingAutoexpire(self, program, shouldExpire):
        """
        Set the autoexpire setting for a recorded program.
        
        @param param: RecordedProgram
        @param shouldExpire: boolean
         
        chanid, starttime, shouldExpire = 0
        """
        raise NotImplementedError("TODO setRecordingAutoexpire")
        # TODO: Convert impl to mysql native client
        #sql = """
        #    update recorded set
        #        autoexpire = "%d",
        #        starttime = '%s'
        #    where
        #        chanid = '%s'
        #        and starttime = '%s'
        #"""%(shouldExpire, starttime, chanid, starttime)
        #
        #log.debug("sql = %s"%sql)
        #
        #rc = self.conn.executeSQL(sql)
        #if rc != 1:
        #    raise ClientException, self.conn.getErrorMsg()
        #
        #mlog.debug("< mythtv.Database.setRecordedAutoexpire()")

# =============================================================================
#class Database(object):
#
#    def __init__(self, settings, translator):
#        """Constructor with injected dependencies"""
#        mlog.debug("> mythtv.Database.__init__()")
#        
#        self.settings = settings
#        self.translator = translator
#
#        if not 'isConnected' in self.__dict__:
#            self.isConnected = 0
#
#        if self.isConnected == 0:
#            self.initialise()
#        mlog.debug("< mythtv.Database.__init__()")
#
#    def initialise(self):
#        log.debug("initializing database connection")
#        host = str(self.settings.get("mysql_host"))
#        
#        try:
#            self.conn = mysql.Connection(
#                host, 
#                str(self.settings.get( "mysql_database")),
#                str(self.settings.get( "mysql_user")),
#                str(self.settings.get( "mysql_password")),
#                int(self.settings.get( "mysql_port")))
#            self.isConnected = 1
#        except:
#            self.isConnected = 0
#            raise
#
#        # change default encoding
#        try:
#            self.conn.executeSQL(
#                "set names %s"%str(
#                    self.settings.get("mysql_encoding_override")))
#        except Exception, ex:
#            log.warn('Changing default encoding: %s'%ex)
#            pass
#        
#    def close(self):
#        mlog.debug("Database.close()")
#
#        if self.isConnected:
#            self.conn.close()
#            del self.conn
#            self.isConnected = 0
#
#    def __del__( self ):
#        mlog.debug("Database.__del__()")
#        self.close()
#        
#    ## New LiveTV Queries
#    def clearChainFiles(self, chainid):
#        """ Deletes all tvchain records for TVChain """
#        try:
#            sql = "DELETE FROM tvchain WHERE tvchain.chainid = '%s'" % str(chainid)
#            
#            if not self.conn.executeSQL( sql ):
#                raise Exception, "Error Deleting TVChains: %s" % self.conn.getErrorMsg()
#                return False
#            return True
#        except:
#            # TODO: Raise instead?
#            log.exception('clearChainFiles')
#            return False
#    
#    def getChainFiles(self, chainid, chanid, lastChainPos, limit="1", tryOnce=False):
#        """ 
#        Returns an Array for all the Files Associated with a TV Chain or ChanID 
#        """
#        mlog.debug("> mythtv.Database.getChainFiles(%s,%s,%s,%s)" % (chainid, chanid, lastChainPos, limit))
#        tvChains = []
#        lastFile = ""
#        lastChain = lastChainPos
#       
#        sql = """
#            SELECT
#                recorded.basename,
#                tvchain.chainpos,
#                tvchain.chainid,
#                tvchain.channame
#            FROM
#                tvchain
#            LEFT JOIN recorded ON
#                recorded.chanid = tvchain.chanid
#            AND recorded.starttime = tvchain.starttime
#            WHERE tvchain.chainpos > %s """ % str(lastChainPos)
#        
#        if chanid != None:
#            sql += " AND tvchain.channame = '%s'" % str(chanid)
#        if chainid != None:
#            sql += " AND tvchain.chainid = '%s'" % str(chainid)
#        sql += " ORDER BY tvchain.chainpos DESC LIMIT %s" % str(limit)
#
#        log.debug("SQL: %s" % sql)
#
#        if not self.conn.executeSQL(sql):
#            raise Exception, "Error Retrieving TV Chains: %s" % self.conn.getErrorMsg()
#
#        rowIter = self.conn.dictRowIterator()
#        for row in rowIter:
#            log.debug("basename: %s" % row["recorded.basename"])
#
#            if chainid == None:
#                chainid = str(row["tvchain.chainid"])
#                globals()["chainid"] = chainid
#                
#            lastChain = row["tvchain.chainpos"]
#            #if self.waitForBigFile(row["recorded.basename"]):
#            sleepTime = self.settings.get("mythtv_tunewait")
#            log.debug("Time to Sleep: %s" % sleepTime)
#            time.sleep(int(sleepTime))
#            tvChains.append(row)
#
#        if len(tvChains) == 0 and not tryOnce:
#            log.debug(" PAUSING FOR 2 SECOND TO GET MORE CHAINS")
#            time.sleep(1)
#            globals()["chainCnt"] += 1
#            if globals()["chainCnt"] > 10:
#                globals()["chainCnt"] = 0
#                return tvChains
#            return self.getChainFiles( chainid, chanid, lastChain, 1)
#        return tvChains
#
#    def waitForBigFile(self, basename):
#        log.debug("waitForBigFile(%s)" % basename)
#        try:
#            ## If we can't get the XBMC Cache for some reason then fall back to xbmcmythtv cache setting
#            minBufSize = self.settings.getXBMCCache()
#            if minBufSize == "":
#                minBufSize = int(self.settings.get("mythtv_minlivebufsize"))
#            else:
#                minBufSize = ( int(minBufSize) * 1024 ) + ( 512 * 1024 )
#            curSize = -1
#            zeroCnt = 0
#            lastSize = 0
#            cnt = 0
#            while curSize < minBufSize:
#                time.sleep(1)
#                sql = "SELECT recorded.filesize FROM recorded WHERE recorded.basename = '%s' LIMIT 1" % str(basename)
#                log.debug(sql)
#                if not self.conn.executeSQL(sql):
#                    raise Exception, "Error Retrieving Filesize: %s" % self.conn.getErrorMsg()
#
#                rowIter = self.conn.dictRowIterator()
#                for row in rowIter:
#                    curSize = int(row["recorded.filesize"])
#                    
#                if lastSize == curSize:
#                    if curSize == 0 and zeroCnt <= 5:
#                        zeroCnt += 1
#                    else:
#                        zeroCnt = 0
#                        log.debug ("*** Current Size of %s is %s, wanted %s" % (basename, curSize, minBufSize))
#                        return False
#
#                lastSize = curSize
#                if curSize < minBufSize:
#                    time.sleep(1)
#                cnt += 1
#                log.debug("*** [%s] waitForBigFile: Current Size of %s is %s, waiting for %s" % (cnt, basename, curSize, minBufSize))
#        except Exception, ex:
#            log.exception("Error while waiting for big file: %s" % str(ex) )
#        log.debug("< waitForBigFile [%s,%s]" % (basename, curSize))
#        return True
#
#    def setMythSettingRow(self, value, data): 
#        """
#        Sets a Value in the Settings table for All Hosts
#        """
#        sql = """
#            UPDATE
#                settings
#            SET
#                settings.data="%s"
#            WHERE
#                settings.value="%s"
#            """ % (str(data), str(value))
#        if not self.conn.executeSQL(sql):
#            return False
#        return True
#
#    def delMythSetting (self, value, host): 
#        """
#        Deletes a Value in the Settings table for Host
#        """
#        sql = """
#            DELETE
#            FROM
#                settings 
#            WHERE
#                settings.hostname = "%s"
#                AND settings.value = "%s"
#        """ % (str(host), str(value))
#        
#        if not self.conn.executeSQL(sql):
#            return False
#        return True
#
#    def setMythSetting(self, value, host, data): 
#        """
#        Sets a Value in the Settings table for Host
#        """
#        sql = """
#            SELECT
#                settings.data
#            FROM
#                settings 
#            WHERE
#                settings.hostname = "%s"
#                AND settings.value = "%s"
#        """ % (str(host), str(value))
#        
#        if not self.conn.executeSQL(sql):
#            raise Exception, "Error setting value: %s" % self.conn.getErrorMsg()
#
#        # retrieve the current setting
#        curValue = "--NO VALUE--"
#        
#        rowIter = self.conn.dictRowIterator()
#        for row in rowIter:
#            curValue = str(row["settings.data"])
#            break
#
#        if  str(curValue) == str(data):
#            return True
#        
#        if curValue == "--NO VALUE--":
#            sql = """
#                INSERT INTO
#                    settings
#                    (
#                        settings.value,
#                        settings.hostname,
#                        settings.data
#                    )
#                    VALUES
#                    (
#                        "%s",
#                        "%s",
#                        "%s"
#                    )
#                    """ % (str(value), str(host), str(data))
#        else:
#            sql = """
#                UPDATE
#                    settings
#                SET
#                    settings.data="%s"
#                WHERE
#                    settings.value="%s" AND
#                    settings.hostname="%s"
#                """ % (str(data), str(value), str(host))
#        if not self.conn.executeSQL(sql):
#            return False
#        return True
#
#    def getMythSettingRow(self, val):
#        """
#        Returns the Value from the Settings Table for Host
#        """
#        sql = """
#            SELECT
#                settings.data,
#                settings.hostname
#            FROM
#                settings 
#            WHERE
#                settings.value = "%s"
#        """ % (str(val))
#        
#        if not self.conn.executeSQL(sql):
#            raise Exception, "Error retrieving setting: %s" % self.conn.getErrorMsg()
#
#        # retrieve the setting
#        rowIter = self.conn.dictRowIterator()
#        return rowIter
#
#    def getMythSetting(self, val, hst=None, retryCnt = 0):
#        """
#        Returns the Value from the Settings Table for Host
#        """
#        log.debug("getMythSetting(%s,%s)"%(val, hst))
#        sql = """
#            SELECT
#                settings.data
#            FROM
#                settings 
#            WHERE
#            """
#        if hst != None:
#            sql += """
#                    settings.hostname = "%s"
#                    AND settings.value = "%s"
#                   """ % (str(hst), str(val))
#        else:
#            sql += """
#                    settings.value = "%s"
#                   """ % (str(val))
#        
#        result = -1
#        try:
#            if not self.conn.executeSQL(sql):
#                raise Exception, "Error retrieving setting: %s" % self.conn.getErrorMsg()
#
#            # retrieve the setting
#            rowIter = self.conn.dictRowIterator()
#            for row in rowIter:
#                result = str(row["settings.data"])
#
#        except Exception, ex:
#            # TODO: Re-evaluate even attempting retry logic
#            if retryCnt < 5:
#                log.error('***ERROR GETSETTING*** %s - Retry %s' %(ex, retryCnt))
#                time.sleep(0.5)
#                result = self.getMythSetting(val, hst, retryCnt + 1)
#            else:
#                retryCnt = 0
#                log.exception('***ERROR GETSETTING*** %s'%ex)
#                
#        log.debug("getMythSetting returned %s"%result)
#        return result
#    
#    def getTunerHost(self, cardid):
#        """
#        TODO: Remove me once refs deleted
#        """
#        sql = """
#            select capturecard.hostname
#            from   capturecard
#            where  capturecard.cardid = '%s'
#        """ % (str(cardid))
#        
#        if not self.conn.executeSQL(sql):
#            raise Exception, "Error getting tuner host: %s" % self.conn.getErrorMsg()
#
#        rowIter = self.conn.dictRowIterator()
#        for row in rowIter:
#            return(str(row["capturecard.hostname"]))
#
#        return -1
#
#    def getChanCallsign(self, channum):
#        sql = "SELECT channel.callsign FROM channel WHERE channel.channum='%s' LIMIT 1" % str(channum)
#
#        if not self.conn.executeSQL(sql):
#            raise Exception, "Error getting Callsign: %s" % self.conn.getErrorMsg()
#
#        rowIter = self.conn.dictRowIterator()
#        for row in rowIter:
#            return str(row["channel.callsign"])
#
#    def getChanID(self, channum):
#        sql = "SELECT channel.chanid FROM channel WHERE channel.channum='%s' LIMIT 1" % str(channum)
#
#        if not self.conn.executeSQL(sql):
#            raise Exception, "Error getting channel id from channel number: %s" % self.conn.getErrorMsg()
#
#        rowIter = self.conn.dictRowIterator()
#        for row in rowIter:
#            return str(row["channel.chanid"])
#
#    def getTuners(self):
#        """Returns a list of the Tuners"""
#        tuners = []
#
#        sql = """
#        select 
#            cardid, 
#            hostname, 
#            signal_timeout, 
#            channel_timeout, 
#            cardtype
#        from   
#            capturecard
#        order by 
#            cardid
#        """
#
#        log.debug(sql)
#        
#        if not self.conn.executeSQL(sql):
#            raise Exception, "Error getting tuners: %s" % self.conn.getErrorMsg()
#        
#        rowIter = self.conn.dictRowIterator()
#        
#        for row in rowIter:
#            tuners.append(domain.Tuner(
#                int(row['capturecard.cardid']),
#                row['capturecard.hostname'],
#                int(row['capturecard.signal_timeout']),
#                int(row['capturecard.channel_timeout']),
#                row['capturecard.cardtype']))
#        return tuners
#
#    def getClientStatus(self, hst):
#        # TODO: Fix sql stmt - 'BEGINS' is not valid sql
#        sql = """
#            SELECT
#                settings.data
#            FROM
#                settings
#            WHERE
#                settings.value BEGINS "%s" AND
#                setting.hostname = "%s" AND
#                settings.data = "1"
#        """ %("XBMCClientStatus", str(hst))
#        
#        if not self.conn.executeSQL(sql):
#            raise Exception, "Error getting client status: %s" % self.conn.getErrorMsg()
#
#        rowIter = self.conn.dictRowIterator()
#        if len(rowIter) == 0:
#            isOn = False
#        else:
#            isOn = True
#        return isOn
#
#    def getLastShow(self):
#        sql = "SELECT program.endtime FROM program ORDER BY endtime DESC LIMIT 1"
#        ## sql = "SELECT max(endtime) FROM program"
#        log.debug("sql=%s"%sql)
#        if not self.conn.executeSQL(sql):
#            raise ServerException, "Error retrieving last show time: %s" % self.conn.getErrorMsg()
#        rowIter = self.conn.dictRowIterator()
#        for row in rowIter:
#            log.debug("LAST SHOW ROW: %s" % row)
#            endtime = row["program.endtime"]
#            if str(endtime[4:5]) == "-":
#                return datetime.datetime(int(endtime[0:4]), int(endtime[5:7]), int(endtime[8:10]), int(endtime[11:13]), int(endtime[14:16]))
#            else: 
#                return datetime.datetime(int(endtime[0:4]), int(endtime[4:6]), int(endtime[6:8]), int(endtime[8:10]), int(endtime[10:12]))
#
#        return None
#
#    def getRecordingGroups(self):
#        """
#        Returns list[list[recording group name, # recordings]]
#        """
#
#        sql = """
#          SELECT DISTINCT 
#              recorded.recgroup, 
#              count(recorded.recgroup) as cnt 
#          FROM recorded 
#          GROUP BY recorded.recgroup ASC
#          """
#
#        log.debug("sql=%s"%sql)
#
#        if not self.conn.executeSQL(sql):
#            log.error("Error retrieving recording groups: %s" % self.conn.getErrorMsg())
#            raise ServerException, "Error retrieving recording groups: %s" % self.conn.getErrorMsg()
#    
#        recgroups = []
#        rowIter = self.conn.dictRowIterator()
#        recgroups.append(["All Groups", 0])
#        grpcnt = 0
#        for row in rowIter:
#            thisRow = ["",0]
#            for k in row.keys():
#                if k.find("cnt") >= 0:
#                    grpcnt += int(row[k])
#                    thisRow[1] = int(row[k])
#                else:
#                    thisRow[0] = str(row[k])
#            recgroups.append(thisRow)
#        recgroups[0][1] = grpcnt
#        return recgroups
#
#    def getRecordingTitles(self, recgroup):
#        """
#        Returns list[list[title, # recordings] for the given string recording group
#        ['All Shows', total # of shows] is always the first index of the returned
#        list regardless of the recording group.
#        """
#
#        sql = """
#          SELECT DISTINCT 
#              recorded.title, 
#              COUNT(recorded.title) AS cnt 
#          FROM recorded
#        """
#
#        if string.upper(recgroup) != "ALL GROUPS":
#            sql += "\nWHERE recorded.recgroup=\"%s\"" % str(recgroup)
#        
#        sql += " GROUP BY recorded.title ASC"
#        
#        log.debug("sql=%s"%sql)
#
#        if not self.conn.executeSQL(sql):
#            raise ServerException, "Error retrieving recording titles: %s" % self.conn.getErrorMsg()
#    
#        titlegroups = []
#        rowIter = self.conn.dictRowIterator()
#
#        titlegroups.append(["All Shows", 0])
#        grpcnt = 0
#        for row in rowIter:
#            thisRow = ["",0]
#            for k in row.keys():
#                if k.find("cnt") >= 0:
#                    grpcnt += int(row[k])
#                    thisRow[1] = int(row[k])
#                else:
#                    thisRow[0] = str(row[k])
#            titlegroups.append(thisRow)
#
#        titlegroups[0][1] = grpcnt
#        return titlegroups
#
#    def getRecordListings(
#            self,
#            startTime, endTime,
#            startChanId=None, endChanId=None):
#        mlog.debug('> mythtv.getRecordListings')
#        strStartTime = startTime.strftime( "%Y%m%d%H%M%S" )
#        strEndTime = endTime.strftime( "%Y%m%d%H%M%S" )
#        sql = """
#            select
#                channel.chanid,
#                channel.channum,
#                channel.callsign,
#                program.starttime,
#                program.endtime,
#                program.title,
#                program.subtitle,
#                program.description,
#                program.showtype,
#                program.originalairdate,
#                program.category,
#                record.startoffset,
#                record.endoffset,
#                0 as isduplicate
#            from 
#                channel,
#                program, 
#                recordmatch,
#                record
#            where
#                channel.visible = 1
#                and channel.chanid = program.chanid
#                and recordmatch.chanid = channel.chanid
#                and program.starttime != program.endtime
#                and
#                (
#                    (
#                        program.endtime > %s
#                        and program.endtime <= %s
#                    ) or
#                    (
#                        program.starttime >= %s
#                        and program.starttime < %s
#                    ) or
#                    (
#                        program.starttime < %s
#                        and program.endtime > %s
#                    ) or
#                    (
#                        program.starttime = %s
#                        and program.endtime = %s
#                    )
#                )
#                and recordmatch.starttime = program.starttime
#                and record.recordid = recordmatch.recordid
#                and record.type != 0
#        """ % (strStartTime, strEndTime,
#        strStartTime, strEndTime,
#        strStartTime, strEndTime,
#        strStartTime, strEndTime)
#        
#        if startChanId and endChanId:
#            sql += """
#                and channel.chanid >= '%d'
#                and channel.chanid <= '%d'
#                """%(startChanId, endChanId)
#        #sql += " order by channel.chanid, program.starttime"
#
#        log.debug("sql=%s"%sql)
#        if not self.conn.executeSQL(sql):
#            raise ServerException, "Error retrieving recording listings: %s" % self.conn.getErrorMsg()
#        
#        recprograms = []
#        rowIter = self.conn.dictRowIterator()
#        
#        for row in rowIter:
#            recprogram = domain.ProgramFromQuery( 
#                stripSQLTablePrefix(row), self.settings, self.translator)
#            recprograms.append(recprogram)
#        mlog.debug('< mythtv.getRecordListings')
#        return recprograms
#
#    def deleteProgram(self, recordId):
#        """
#        Deletes the program created when a manual schedule is created
#        """
#        mlog.debug("> deletePrograms '%d'"%recordId)
#        sql = """
#            DELETE FROM program
#            WHERE manualid=%d
#            """%recordId
#        log.debug(sql)
#        if not self.conn.executeSQL(sql):
#            log.error("Error deleting manual program %d: %s"%(recordId, self.conn.getErrorMsg()))
#            return 0
#        else:
#            return 1
#
#    def deleteSchedule(self, schedule):
#        """
#        Deletes the specified recording schedule. Returns 1 on success.
#        Raises ServerException on error.
#        """
#        recordId = int(schedule.recordid())
#        mlog.debug("> deleteSchedule '%d'"%recordId)
#        sql = """
#            DELETE FROM record
#            WHERE recordid = %d
#            """%recordId
#        log.debug(sql)
#
#        if not self.conn.executeSQL(sql):
#            log.error("Error deleting recording schedule %d: %s"%(recordId, self.conn.getErrorMsg()))
#            return 0
#        else:
#            return 1
#        
#    def getChannels(self):
#        """
#        Returns a list of all the currently enabled channels as a list[ChannelFromQuery]
#        """
#        mlog.debug('> mythtv.getChannels')        
#        sql = """
#            SELECT
#                c.chanid as chanid,
#                c.channum as channum,
#                c.callsign as callsign,
#                c.name as name, 
#                c.icon as icon
#            FROM
#                channel c
#            WHERE
#                c.channum IS NOT NULL
#                AND c.channum != ""
#                AND c.visible = 1
#            ORDER BY
#                c.chanid
#        """
#
#        if not self.conn.executeSQL(sql):
#            raise Exception, "Error retrieving channels: %s" % self.conn.getErrorMsg()
#
#        # retrieve all recorded shows and store them in an array
#        rowIter = self.conn.dictRowIterator()
#        channelInfo = []
#        for row in rowIter:
#            channelInfo.append(domain.ChannelFromQuery(stripSQLTablePrefix(row)))
#        
#        mlog.debug('< mythtv.getChannels')
#        return channelInfo
#
#    def getProgramListings(
#            self,
#            startTime, endTime,
#            startChanId=None, endChanId=None):
#        
#        mlog.debug('> mythtv.getProgramListings')
#        strStartTime = startTime.strftime("%Y%m%d%H%M%S")
#        strEndTime = endTime.strftime("%Y%m%d%H%M%S")
#        
#        sql = """
#            select
#                channel.chanid,
#                channel.channum,
#                channel.callsign,
#                program.starttime,
#                program.endtime,
#                program.title,
#                program.subtitle,
#                program.description,
#                program.showtype,
#                program.originalairdate,
#                program.category,
#                program.seriesid,
#                program.programid,
#                channel.icon,
#                channel.name as channame,
#                0 as isduplicate
#            from 
#                channel,
#                program
#            where
#                channel.visible = 1
#                and channel.chanid = program.chanid
#                and program.starttime != program.endtime
#                and
#                (
#                    (
#                        program.endtime > %s
#                        and program.endtime <= %s
#                    ) or
#                    (
#                        program.starttime >= %s
#                        and program.starttime < %s
#                    ) or
#                    (
#                        program.starttime < %s
#                        and program.endtime > %s
#                    ) or
#                    (
#                        program.starttime = %s
#                        and program.endtime = %s
#                    )
#                )
#        """ % (strStartTime, strEndTime,
#               strStartTime, strEndTime,
#               strStartTime, strEndTime,
#               strStartTime, strEndTime )
#        
#        if startChanId and endChanId:
#            sql += """
#                and channel.chanid >= '%d'
#                and channel.chanid <= '%d'
#                """%(startChanId, endChanId)
#        sql += " order by channel.chanid, program.starttime"
#
#        # log.debug( "sql=[%s]"%sql )
#        if not self.conn.executeSQL(sql):
#            raise ServerException, "Error retrieving program listing: %s" % self.conn.getErrorMsg()
#        
#        programs = []
#        rowIter = self.conn.dictRowIterator()
#        
#        for row in rowIter:
#            log.debug(row)
#            program = domain.ProgramFromQuery(stripSQLTablePrefix(row ), self.settings, self.translator)
#            programs.append(program)
#        mlog.debug('< mythtv.getProgramListings')
#        return programs
#
#    def getRecordingSchedules(self, chanId="",recordId=-1):
#        """
#        Returns ScheduleFromQuery[] .  If recordId is specified,
#        only the matching schedule is returned.  Otherwise, all schedules are
#        returned.
#        """
#        log.debug("getting schedule for recordId = %s"%recordId)
#        sql = """
#            SELECT
#                r.recordid,
#                r.type,
#                r.chanid,
#                r.starttime,
#                r.startdate,
#                r.endtime,
#                r.enddate,
#                r.title,
#                r.subtitle,
#                r.description,
#                r.category,
#                r.profile,
#                r.recpriority,
#                r.autoexpire,
#                r.maxepisodes,
#                r.maxnewest,
#                r.startoffset,
#                r.endoffset,
#                r.recgroup,
#                r.dupmethod,
#                r.dupin,
#                r.station,
#                r.seriesid,
#                r.programid,
#                r.search,
#                r.autotranscode,
#                r.autocommflag,
#                r.autouserjob1,
#                r.autouserjob2,
#                r.autouserjob3,
#                r.autouserjob4,
#                r.findday,
#                r.findtime,
#                r.findid,
#                r.inactive,
#                r.parentid,
#                c.channum,
#                c.callsign,
#                c.name as channame,
#                c.icon
#            FROM
#                record r
#            LEFT JOIN channel c ON r.chanid = c.chanid
#            """
#            
#        if chanId != "":
#            sql += "WHERE r.chanid = '%s' "%chanId
#            
#        if recordId != -1:
#            if chanId == "":
#                sql+="WHERE "
#            else:
#                sql +="AND "
#            sql += "r.recordid = %d "%recordId
#            
#        sql += """
#            ORDER BY
#                r.recordid
#                DESC
#            """
#
#        log.debug(sql)
#        
#        if not self.conn.executeSQL(sql):
#            raise ServerException, "Error retrieving recording schedule: %s" % self.conn.getErrorMsg()
#        
#        schedules = []
#        rowIter = self.conn.dictRowIterator()
#        
#        for row in rowIter:
#            sched = domain.ScheduleFromQuery(stripSQLTablePrefix(row), self.translator)
#            schedules.append(sched)
#        mlog.debug("< getSchedule")
#        return schedules
#
#    def getCurrentSchedule(self, chanid, endtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())):
#        """
#        Returns an array of recording schedules for the chanid and time.
#        """
#        log.debug("getting current schedule for chanid = %s   endtime = %s)"%(chanid, endtime))
#        sql = """
#            SELECT
#                r.starttime,
#                r.endtime,
#                r.title,
#                r.subtitle,
#                r.description,
#                r.category,
#                r.chanid,
#                r.hostname,
#                r.basename,
#                c.channum,
#                r.originalairdate,
#                c.callsign,
#                r.seriesid,
#                r.programid,
#                c.icon,
#                c.name as channame,
#                r.duplicate,
#                r.recordid,
#                m.manualid
#            FROM
#                recorded r
#            LEFT JOIN channel c ON r.chanid = c.chanid
#            LEFT JOIN recordmatch m ON r.recordid = m.recordid
#            INNER JOIN record s ON s.recordid = r.recordid
#            """
#        curtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#        curdate = time.strftime("%Y-%m-%d", time.localtime())
#        # first just get all schedules that started before now
#        sql += "WHERE "
#        if chanid != None:
#            sql += "c.channum='%s' AND "%chanid
#        sql += "r.starttime<='%s' AND r.endtime>='%s'"%(endtime,curtime)
#        
#        sql += """
#            ORDER BY
#                m.manualid
#            """
#        log.debug(sql)
#        if not self.conn.executeSQL(sql):
#            raise ServerException, "Error retrieving current schedule: " + self.conn.getErrorMsg()
#        
#        schedules = []
#        rowIter = self.conn.dictRowIterator()
#        
#        for row in rowIter:
#            sched = domain.ProgramFromQuery(stripSQLTablePrefix(row), self.settings, self.translator)
#            schedules.append(sched)
#        mlog.debug("< getCurrentSchedule")
#        return schedules
#
#    def notifyChange(self):
#        """
#        Method to notify the mythbackend of a change to a record.
#
#        This is how mythweb notifies the backend after changes to schedules,
#        deleting a recorded program, etc..
#        """
#        mlog.debug("> mythtv.Database.notifyChange()")
#
#        rc = self.conn.executeSQL("""
#            update settings set data='yes' where value='RecordChanged'
#            """ )
#        if not rc:
#            raise ClientException, self.conn.getErrorMsg()
#
#        return 0
#        mlog.debug("< mythtv.Database.notifyChange()")
#
#    def saveSchedule(self, s):
#        """
#        Method to save a schedule to the database. If recordid() is None in
#        passed schedule, then it will be populated with id returned from
#        database (i.e. a new one will be created).
#
#        Returns:
#            0 on success
#            ClientException on error
#
#        Note:
#
#        Connection.rescheduleNotify() must be called after scheduling changes
#        have been made so that the backend will apply the changes.
#        """
#        programid = s.programid()
#        if not programid:
#            programid = ""
#        seriesid = s.seriesid()
#        if not seriesid:
#            seriesid = ""
#        sql = """
#            REPLACE INTO
#                record
#            (   recordid, type,
#                chanid, starttime,
#                startdate, endtime,
#                enddate, title,
#                subtitle, description,
#                category, profile,
#                recpriority, autoexpire,
#                maxepisodes, maxnewest,
#                startoffset, endoffset,
#                recgroup, dupmethod,
#                dupin, station,
#                seriesid, programid,
#                search, autotranscode,
#                autocommflag, autouserjob1,
#                autouserjob2, autouserjob3,
#                autouserjob4, findday,
#                findtime, findid,
#                inactive, parentid
#            ) VALUES (
#                %s, %s,
#                %s, %s,
#                %s, %s,
#                %s, %s,
#                %s, %s,
#                %s, %s,
#                %s, %s,
#                %s, %s,
#                %s, %s,
#                %s, %s,
#                %s, %s,
#                %s, %s,
#                %s, %s,
#                %s, %s,
#                %s, %s,
#                %s, %s,
#                %s, %s,
#                %s, %s
#            )
#            """ % (
#                mysql.escape(s.recordid()), mysql.escape(s.type()),
#                mysql.escape(s.chanid()), mysql.escape(s.starttime()),
#                mysql.escape(s.startdate()), mysql.escape(s.endtime()),
#                #
#                # NOTE:
#                #
#                # s.title(), s.subtitle(), and s.description() were not
#                # used because they return the data in GUI encoding whereas
#                # the database is in UTF-8.  This may need to be rethought to
#                # make things cleaner but for now this was the easiest. TODO
#                #
#                mysql.escape(s.enddate()), mysql.escape(s.data()['title']),
#                mysql.escape(s.data()['subtitle']),
#                mysql.escape(s.data()['description']),
#                mysql.escape(s.category()), mysql.escape(s.profile()),
#                mysql.escape(s.recpriority()), mysql.escape(int(s.autoexpire())),
#                mysql.escape(s.maxepisodes()), mysql.escape(s.maxnewest()),
#                mysql.escape(s.startoffset()), mysql.escape(s.endoffset()),
#                mysql.escape(s.recgroup()), mysql.escape( s.dupmethod()),
#                mysql.escape(s.dupin()), mysql.escape( s.station()),
#                mysql.escape(seriesid), mysql.escape(programid),
#                mysql.escape(s.search()), mysql.escape(int(s.autotranscode())),
#                mysql.escape(int(s.autocommflag())), mysql.escape(int(s.autouserjob1())),
#                mysql.escape(int(s.autouserjob2())), mysql.escape(int(s.autouserjob3())),
#                mysql.escape(int(s.autouserjob4())), mysql.escape(s.findday()),
#                mysql.escape(s.findtime()), mysql.escape(s.findid()),
#                mysql.escape(int(s.inactive())), mysql.escape(s.parentid()))
#            
#        log.debug("sql = %s"%sql)
#        rc = self.conn.executeSQL(sql)
#        if rc < 1:
#            raise ClientException, self.conn.getErrorMsg()
#        if not s.recordid():
#            s.data()['recordid'] = self.conn.getInsertId()
#        return s.recordid()
#
#    def testActive(self):
#        active = 0
#        try:
#            self.conn.executeSQL("select sysdate()")
#            active = 1
#        except:
#            self.isConnected = 0
#            del self.conn
#            self.conn = None
#        return active

# ===========  GRAVEYARD ==================================
#
#    NOT REFERENCED ANYWHERE     
#
#    def programInfo(self, startTime, endTime, channelID):
#        try:
#            strStartTime = startTime.strftime( "%Y%m%d%H%M%S" )
#            strEndTime = endTime.strftime( "%Y%m%d%H%M%S" )
#            sql = """
#                select
#                    channel.chanid,
#                    channel.channum,
#                    channel.callsign,
#                    program.starttime,
#                    program.endtime,
#                    program.title,
#                    program.subtitle,
#                    program.description,
#                    program.showtype,
#                    program.originalairdate,
#                    program.category,
#                    0 as isduplicate
#                from 
#                    channel,
#                    program
#                where
#                    channel.visible = 1
#                    and channel.channum = '%s'
#                    and program.chanid = channel.chanid
#                    and program.starttime != program.endtime
#                    and
#                    (
#                        (
#                            program.endtime > %s
#                            and program.endtime <= %s
#                        ) or
#                        (
#                            program.starttime >= %s
#                            and program.starttime < %s
#                        ) or
#                        (
#                            program.starttime < %s
#                            and program.endtime > %s
#                        ) or
#                        (
#                            program.starttime = %s
#                            and program.endtime = %s
#                        )
#                    )
#            """%(   str(channelID),
#                    strStartTime,strEndTime,
#                    strStartTime,strEndTime,
#                    strStartTime,strEndTime,
#                    strStartTime,strEndTime )
#            sql += " order by channel.chanid"
#            log.debug(sql)
#            if not self.conn.executeSQL(sql):
#                raise ServerException, "Error retrieving program info: %s" % self.conn.getErrorMsg()
#            rowIter = self.conn.dictRowIterator()
#            for row in rowIter:
#                return row
#        except:
#            log.exception('programInfo')
#
#
#
#    def sql2MythTime( str ):
#        return \
#            str[0:4] + '-' + str[4:6] + '-' + str[6:8] + 'T' + \
#            str[8:10] + ':' + str[10:12] + ':' + str[12:14]
#