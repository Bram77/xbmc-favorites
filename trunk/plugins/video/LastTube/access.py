import urllib,urllib2,re,sys

site='http://api.tv.timbormans.com'
#http://api.tv.timbormans.com/user/por/topartists.xml

def getSite():
    return site

#thanks voinage
def getFlv(url):
    p=re.compile('http://www.youtube.com/watch\?v=(.*)')
    match=p.findall(url)
    for code in match:
        print 'code='+code
        req = urllib2.Request('http://www.youtube.com/watch?v='+code)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        p=re.compile('"t": "(.+?)"')
        match=p.findall(link)
        for blah in match:
            linkage="http://www.youtube.com/get_video?video_id="+code+"&t="+blah+"&fmt=18"
            return linkage
        
def getUrl(xml):
    p=re.compile('<url>(.*)</url>')
    match=p.findall(xml)
    for url in match:
        print 'url='+url
        flv=getFlv(url)
        return flv

def getArtist(xml):
    p=re.compile('\">(.*)</artist>(.*)')
    match=p.findall(xml)
    for artist in match:
        return artist[0]

def getTrack(xml):
    p=re.compile('\">(.*)</track>')
    match=p.findall(xml)
    for track in match:
        return track

def getThumb(xml):
    p=re.compile('<thumbnail>(.*)</thumbnail>')
    match=p.findall(xml)
    for thumb in match:
        return thumb

def getVideoInfo(mode):
    req = urllib2.Request(site+mode)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    print link
    url=getUrl(link)
    artist=getArtist(link)
    track=getTrack(link)
    thumb=getThumb(link)
    info=[url,artist,track,thumb]
    print info
    return info
