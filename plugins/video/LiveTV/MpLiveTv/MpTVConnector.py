import urllib
import socket

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
        self.mysend("TVServerXBMC:0-1\n")

        # make sure that what we receive is correct
        data = self.myreceive()

        if(data.find("Protocol-Accept:1") == -1):
            raise RuntimeError, "not the right protocol : " + data
        else:
            print "Connection made"


    # return a list of the group names, list<string>
    def getGroups( self ):
        self.mysend("ListGroups:\n")
        groupsLine = self.myreceive().rstrip()

        # we need to split by ,
        groups = groupsLine.split(",")


        # unescape
        for index, item in enumerate(groups):
            groups[index] = urllib.unquote(item)
        
        return groups
    
    # returns a list of pairs. pair = (id, name)
    def getChannels( self, group ):
        self.mysend("ListChannels:" + urllib.quote(group) + "\n")
        channelsLine = self.myreceive().rstrip()

        # we need to split by ,
        channels = channelsLine.split(",")

        # unescape
        for index, item in enumerate(channels):
            channels[index] = urllib.unquote(item)
            
            # we have to break up ID;name into a tuple
            channelParts = channels[index].split(';')
            channels[index] = (channelParts[0], channelParts[1])
        
        return channels

    def startTimeshift( self, chanId ):
        self.mysend("TimeshiftChannel:" + str(chanId) + "\n")
        result = self.myreceive().rstrip()

        return result

    def stopTimeshift ( self ):
        self.mysend("StopTimeshift:\n")
        result = self.myreceive().rstrip()

    def __del__(self):
        # destructor will kill the connection
        self.mysend("CloseConnection:\n")
        self.sock.close()


