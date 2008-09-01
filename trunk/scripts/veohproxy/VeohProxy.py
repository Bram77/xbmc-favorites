import base64
import re
import time
import urllib,urllib2
import sys
import pickle
import traceback
import md5
import socket
from urllib import FancyURLopener
from CacheHandler import *
from SocketServer import ThreadingMixIn
from MightyHTTP import HTTPRangeHandler
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class HeadURL(FancyURLopener):
    version = 'veoh-3.9.5 service (NT 5.1; IE 6.0.2900.2096; en-US Windows)'

class MyHandler(BaseHTTPRequestHandler):
        """
        Serves a HEAD request
        """
        def do_HEAD(s):
                # Only send the head
                print time.asctime(), "Serving HEAD request..."
                s.answer_request(0)

        """
        Serves a GET request.
        """
        def do_GET(s):
                print time.asctime(), "Serving GET request..."
                # Send head and video
                s.answer_request(1)

        """
        Analyzes a request to the proxy and decides if it's a video on veoh, ninjavideo.net or streamplug. Calls
        the appropriate function. If sendData is true, we serve a GET request and send all the data. Otherwise it is
        a HEAD request, so we only send headers.
        """
        def answer_request(s, sendData):
                try:
                        request_path=s.path[1:]
                        request_path=re.sub(r"\?.*","",request_path)
                        requestedRange=s.headers.getheader("Range")
                        if request_path=="stop":
                                sys.exit()
                        elif request_path[0:11]=="streamplug/":
                                s.serveStreamplug(request_path[11:], sendData)
                        elif request_path[0]!='v' or len(request_path)<10 and re.match('[0-9]*$', requested_path)!=None:
                                s.serveNinjaVideo(request_path, requestedRange, sendData)
                        elif request_path[0]=='v':
                                s.serveVeohVideo(request_path, requestedRange, sendData)
                        elif request_path[0]=='e':
                                s.serveVeohVideo(request_path, requestedRange, sendData)
                except:
                                traceback.print_exc()
                                s.wfile.close()
                                return
                s.wfile.close()
        
        def getFromCache(self, request):
                global cachehandler
                try:
                        a=cachehandler.getFromCache(request)
                        return a
                except:
                        return None
        
        def saveToCache(self, request, what):
                global cachehandler
                try:
                        cachehandler.saveToCache(request, what)
                except:
                        pass
                        
        """
        Serves a video residing on Veoh. request_path has to be a veoh id. Range is the first byte to be served. First grabs
        the infos about the part-files from veoh, then sends data using sendVeoh().
        """
        def serveVeohVideo(s, request_path, range, sendData):
                cached=s.getFromCache(request_path)
                if cached:
                        (myFileHash,myFileSize,myFileName,myParthHashFile,myUrlRoot,hashes)=cached
                else:
                        (myFileHash,myFileSize,myFileName,myParthHashFile,myUrlRoot,hashes)=s.getVeohParams(request_path)
                        s.saveToCache(request_path, (myFileHash,myFileSize,myFileName,myParthHashFile,myUrlRoot,hashes))
                range=s.headers.getheader("Range")
                (hrange, crange)=s.getRangeRequest(range, myFileSize)
                mtype="application/x-msvideo"
                # Do we have to send a normal response or a range response?
                if range!=None:
                        s.send_response(206)
                        s.send_header("Content-Range",crange)
                else:
                        s.send_response(200)
                contentsize=int(myFileSize)-hrange
                etag=s.generateETag(request_path)
                s.sendHeaders(myFileName, mtype, contentsize , etag)
                if (sendData):
                        s.sendVeoh(s.wfile, hashes,myUrlRoot,myFileHash,hrange)
                
        """
        Serves a request of a ninjavideo.net url.
        """             
        def serveNinjaVideo(s, request_path, range, sendData):
                cached=s.getFromCache(request_path)
                if cached:
                        (myFileHash,myFileSize,myFileName,myParthHashFile,myUrlRoot,hashes)=cached
                else:
                        (myFileHash,myFileSize,myFileName,myParthHashFile,myUrlRoot,hashes)=s.getNinja(request_path)
                        s.saveToCache(request_path, (myFileHash,myFileSize,myFileName,myParthHashFile,myUrlRoot,hashes))
                range=s.headers.getheader("Range")
                (hrange, crange)=s.getRangeRequest(range, myFileSize);
                mtype="application/x-msvideo"
                # Do we have to send a normal response or a range response?
                if range!=None:
                        s.send_response(206)
                        s.send_header("Content-Range",crange)
                else:
                        s.send_response(200)
                contentsize=int(myFileSize)-hrange
                etag=s.generateETag(request_path)
                s.sendHeaders(myFileName, mtype, contentsize , etag)
                if (sendData):
                        s.sendVeoh(s.wfile, hashes,myUrlRoot,myFileHash,hrange)
                        
        """
        returns info about a video file
        """
        def get_info(s, vid,data):
                ct=re.compile(r'veoh.?ct=(.+?)"\r\n\t\t').findall(data)
                perma=re.compile('permalinkId="(.+?)"').findall(data)
                filehash=re.compile('fileHash="(.+?)"').findall(data)
                size=re.compile('size="(.+?)"').findall(data)
                title=re.compile('title="(.+?)"').findall(data)
                extension=re.compile('extension="(.+?)"').findall(data)
                bit = HeadURL();filein=bit.open('http://content.veoh.com/pveoh/'+perma[0]+'/'+filehash[0]+'.veoh'+'?ct='+ct[0])
                link=filein.read();filein.close()
                print time.asctime(), "Getting information about file pieces from Veoh..."
                pieces=re.compile("<piece id='(.+?)' />").findall(link)
                return (filehash[0],size[0],title[0]+extension[0],'http://content.veoh.com/pveoh/'+perma[0]+'/'+filehash[0]+'.veoh'+'?ct='+ct[0],"http://p-cache.veoh.com/cache",pieces)

        """
        Sends the requested streamplug movie. RequestedURL is base64-encoded string carrying the url.
        """
        def serveStreamplug(s, requestedURL, sendData):
                        (steamplugURL,filename)=s.decodeB64URL(requestedURL)
                        range=s.headers.getheader("Range")
                        contentsize=s.getHTTPFileSize(steamplugURL, [])
                        (hrange, crange)=s.getRangeRequest(range, contentsize);
                        contenttype="video/x-msvideo"
                        if range!=None:
                                s.send_response(206)
                                s.send_header("Content-Range",crange)
                        else:
                                s.send_response(200)
                        contentsize=int(contentsize)-hrange
                        etag=s.generateETag(requestedURL)
                        s.sendHeaders(filename, contenttype, contentsize , etag)
                        if (sendData):
                                fileout=s.wfile
                                try:
                                        s.sendStreamplug(fileout,steamplugURL,hrange)
                                except:
                                        traceback.print_exc()
                                        s.wfile.close()
                                        return
                        s.wfile.close()
        
                        
        def getVeohParams(self, veohID):
                print time.asctime(), "Getting information about file from Veoh..."
                url = 'http://www.veoh.com/rest/v2/execute.xml?method=veoh.search.video&permalink='+veohID+'&apiKey=08344E97-13CE-E0BE-28AA-B8F7D686DD07'
                response = self.getHTTPFile(url, [('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'),( "Content-Type","application/xml")],data=None)
                return self.get_info(veohID,response)

        def sendStreamplug(self,fileout,veohID,hrange):
                print time.asctime(), "Sending streamplug stream for URL: ",veohID
                url=veohID
                opener = HTTPRangeHandler(proxies=PROXIES)
                opener.addheaders=[('Range','bytes='+str(hrange)+"-")]
                response = opener.open(veohID)
                buf="INIT"
                print time.asctime(), "Sending data..."
                try:
                        while (buf!=None and len(buf)>0):
                                buf=response.read(8*1024)
                                fileout.write(buf)
                                fileout.flush()
                        response.close()
                        fileout.close()
                        print time.asctime(),"Closing connection"
                except socket.error, e:
                        print time.asctime(),"Client Closed the connection."
                        try:
                                response.close()
                                fileout.close()
                        except Exception, e:
                                return
                except Exception,e:
                        traceback.print_exc(file=sys.stdout)
                        response.close()
                        fileout.close()

        def getNinja(self,id):
                print time.asctime(), "Getting infos from NinjaVideo.net for Video ID ",id,"..."
                url="http://www.ninjavideo.net/server.php?request="+str(id)
                the_page= self.getHTTPFile(url, [( "User-Agent","NinjaVideo Helper/0.2.4")])
                pardata=the_page.split("\r\n")
                params={}
                for s in pardata:
                        try:
                                t=s.split(": ")
                                params[t[0]]=t[1]
                        except:
                                pass
                if params["Method"]!="ninjaveoh":
                        print time.asctime(), "Could not obtain NinjaVideo information - Unknown Method."
                        return
                data=the_page
                size=re.search(r"<file\ .+?size\=\'(.+?)\'", data).group(1)
                resp=re.search(r"<file\ .+?>(.+?)</file>",data,re.DOTALL).group(0)
                pieces=re.findall(r"<piece\ id\=\'(.+?)\'", resp)
                return (params["Data"],size,params["Name"]+".avi",url,"http://p-cache.veoh.com/cache",pieces)
            
        def getRangeRequest(self, hrange, filesize):
                if hrange==None:        
                        hrange=0
                        crange=None
                else:
                        try:
                                #Get the byte value from the request string.
                                hrange=str(hrange)
                                hrange=int(hrange.split("=")[1].split("-")[0])
                                #Build range string
                                # Is the -1 correct? It looks plausible to me.
                                crange="bytes "+str(hrange)+"-" +str(int(filesize)-1)+"/"+str(filesize)
                        except:
                                # Failure to build range string? Create a 0- range.
                                hrange=0
                                crange="bytes 0-"
                return (hrange, crange)

        def decodeB64URL(self, b64):
                url=base64.b64decode(b64)
                myFileName=url.split('/')[-1]
                return (url, myFileName )

        def getHTTPFileSize(self, url, headers):
                response=self.openURL(url, headers)
                myFileSize=response.headers["Content-Length"]
                response.close()
                return myFileSize

        def openURL(self, url, headers, data=None):
                opener = HTTPRangeHandler(proxies=PROXIES)
                opener.addheaders=headers
                response = opener.open(url, data)
                return response
        
        def getHTTPFile(self, url, headers, data=None):
                response = self.openURL(url, headers, data)
                data = response.read()
                response.close()
                return data

        def generateETag(self, url):
                md=md5.new()
                md.update(url)
                return md.hexdigest()

        def sendHeaders(s, filename, contenttype, contentsize , etag):
                print time.asctime(), "Sending headers..."
                # causes utf-8 decode problems for certain filenames with odd characters
                try:
                    s.send_header("Content-Disposition", "inline; filename=\""+filename.encode('iso-8859-1', 'replace')+"\"")
                except: pass
                s.send_header("Content-type", contenttype)
                s.send_header("Last-Modified","Thu, 1 Jan 1970 00:00:00 GMT")
                #needed for streamplug & veoh mp4 files
                s.send_header("ETag",etag)
                s.send_header("Accept-Ranges","bytes")
                s.send_header("Cache-Control","public, must-revalidate")
                s.send_header("Cache-Control","no-cache")
                s.send_header("Pragma","no-cache")
                #s.send_header("features","seekable,stridable")
                s.send_header("client-id","12345")
                s.send_header("Content-Length", str(contentsize))
                s.end_headers()
                

        def sendVeoh(self,fileout,hashes,urlroot,filehash,start):
                piece=0
                print time.asctime(), "Starting download at byte ",start
                # One full chunk is 256*1024 bytes long
                myResumeCount = start/(256*1024)
                myResumeRest = start%(256*1024)
                for id in hashes:
                        if piece>=myResumeCount:
                                piece=piece+1
                                happy=0
                                trycount=0
                                while not happy and trycount<20:
                                        try:
                                                trycount=trycount+1
                                                bit = HeadURL()
                                                filein=bit.open(urlroot+"/get.jsp?fileHash="+filehash+"&pieceHash="+id)
                                                buf=filein.read(768*1024)
                                                if (piece<len(hashes)-1) and len(buf)<256*1024:
                                                        raise Exception(-1,"Error: Content too short.")
                                                happy=1
                                        except:
                                                try:
                                                        filein.close()
                                                except:
                                                        pass
                                                print time.asctime(),"Could not read from URL...reopening..."
                                try:
                                        if (myResumeRest>0):
                                                buf=buf[myResumeRest:]
                                                myResumeRest=0
                                        fileout.write(buf)
                                        fileout.flush()
                                        filein.close()
                                        del buf
                                except socket.error, e:
                                                try:
                                                        filein.close()
                                                        fileout.close()
                                                except Exception, e:
                                                        pass
                                                print "Client Closed the connection."
                                                return
                                except Exception, inst:
                                                print time.asctime(), "Some weird error happened."
                                                traceback.print_exc()
                                                try:
                                                        filein.close()
                                                except Exception, e:
                                                        pass
                                                raise inst
                                try:
                                        filein.close()
                                except:
                                        pass
                        else:
                                piece=piece+1


class Server(HTTPServer):
    """HTTPServer class with timeout."""

    def get_request(self):
        """Get the request and client address from the socket."""
        # 10 second timeout
        self.socket.settimeout(4.0)
        result = None
        while result is None:
            try:
                result = self.socket.accept()
            except socket.timeout:
                pass
        # Reset timeout on the new socket
        result[0].settimeout(1000)
        return result

class ThreadedHTTPServer(ThreadingMixIn, Server):
        """Handle requests in a separate thread."""


global cachehandler

PROXIES=None
HOST_NAME = '127.0.0.1' # The IP Adress to listen on
PORT_NUMBER = 64653 # The port of the NinjaVideo.net helper
cachehandler=MemoryCacheHandler()

if __name__ == '__main__':      
        socket.setdefaulttimeout(7.0)
        server_class = ThreadedHTTPServer
        httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
        print time.asctime(), "VeohProxy Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
        while(True):
                httpd.handle_request()
        httpd.server_close()
        print time.asctime(), "VeohProxy Stops %s:%s" % (HOST_NAME, PORT_NUMBER)
