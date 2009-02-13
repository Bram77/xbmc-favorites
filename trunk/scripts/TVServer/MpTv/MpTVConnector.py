import urllib
import socket
import re
import xbmcgui

class MpTVConnector:
   '''demonstration class only 
     - coded for clarity, not efficiency'''


   def __init__(self, sock=None):
      if sock is None:
         self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
      else:
         self.sock = sock


   def mysend(self, msg):
      totalsent = 0
      while totalsent < len(msg):
         sent = self.sock.send(msg[totalsent:])
         if sent == 0:
            raise RuntimeError, "socket connection broken"
         totalsent = totalsent + sent


   def myreceive(self):
      fs = self.sock.makefile()
      return fs.readline()


   def connect(self, host, port):
      self.sock.connect((host, port))

      # connect and send the protocol
      self.mysend("TVServerXBMC:0-2\n")

      # make sure that what we receive is correct
      data = self.myreceive().rstrip()

      if(re.compile("^Protocol-Accept;0-[2-9][^0-9]$").search(data)):
         raise RuntimeError, "not the right protocol : " + data
      else:
         print "Connection made"
   

   def getArguments( self, line ):
      list = line.split(";")
      for i in range(0, len(list)):
         list[i] = urllib.unquote(list[i])
      
      return list


   def getArgumentsList( self, line ):
      list = line.split(",")
      for i in range(0, len(list)):
         list[i] = self.getArguments(urllib.unquote(list[i]))
      
      return list


   # return a list of the group names, list<string>
   def getGroups( self ):
      self.mysend("ListGroups:\n")
      groupsLine = self.myreceive().rstrip()

      groups = self.getArgumentsList(groupsLine)
      for i in range(0, len(groups)):
         groups[i] = groups[i][0]

      return groups

   
   # returns a list of pairs. pair = (id, name)
   def getChannels( self, group ):
      self.mysend("ListChannels:" + urllib.quote(group) + "\n")
      channelsLine = self.myreceive().rstrip()
      channels = self.getArgumentsList(channelsLine)

      return channels


   def startTimeshift( self, chanId ):
      self.mysend("TimeshiftChannel:" + str(chanId) + "\n")
      result = self.myreceive().rstrip()

      return result


   def stopTimeshift ( self ):
      self.mysend("StopTimeshift:\n")
      result = self.myreceive().rstrip()


   def isTimeshifting ( self ):
      self.mysend("IsTimeshifting:\n")
      result = self.myreceive().rstrip()
      timeshiftInfo = self.getArgumentsList(result)[0];
      return timeshiftInfo


   # return a list of the show names, list<string>
   def getShows( self ):
      self.mysend("ListRecordedTV:\n")
      showsLine = self.myreceive().rstrip()
      shows = self.getArgumentsList(showsLine)

      return shows

   # delete a given show
   def deleteShow( self, recId ):
      self.mysend("DeleteRecordedTv:" + str(recId) + "\n")
      result = self.myreceive().rstrip()

      return result


   def __del__(self):
      # destructor will kill the connection
      self.mysend("CloseConnection:\n")
      self.sock.close()
