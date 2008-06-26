import urllib
from urllib import *

proxy_bypass=urllib.proxy_bypass
addinfourl=urllib.addinfourl

class HTTPRangeHandler(urllib.FancyURLopener):
	"""
	# Modified by Torben Gerkensmeyer. Bloody hacks. Don't use this.
	# This class is part of urlgrabber, a high-level cross-protocol url-grabber
	# Copyright 2002-2004 Michael D. Stenner, Ryan Tomayko
	"""
	def http_error_206(self, req, fp, code, msg, hdrs):
		# 206 Partial Content Response
		r = urllib.addinfourl(fp, hdrs, req)
		r.code = code
		r.msg = msg
		return r

	def http_error_416(self, req, fp, code, msg, hdrs):
		# HTTP's Range Not Satisfiable error
		raise RangeError('Requested Range Not Satisfiable')

	def open_http(self, url, data=None):
		"""Use HTTP protocol."""
		import httplib
		user_passwd = None
		proxy_passwd= None
		if isinstance(url, str):
		    host, selector = splithost(url)
		    if host:
		        user_passwd, host = splituser(host)
		        host = urllib.unquote(host)
		    realhost = host
		else:
		    host, selector = url
		    # check whether the proxy contains authorization information
		    proxy_passwd, host = splituser(host)
		    # now we proceed with the url we want to obtain
		    urltype, rest = splittype(selector)
		    url = rest
		    user_passwd = None
		    if urltype.lower() != 'http':
		        realhost = None
		    else:
		        realhost, rest = splithost(rest)
		        if realhost:
		            user_passwd, realhost = splituser(realhost)
		        if user_passwd:
		            selector = "%s://%s%s" % (urltype, realhost, rest)
		        if proxy_bypass(realhost):
		            host = realhost

		    #print "proxy via http:", host, selector
		if not host: raise IOError, ('http error', 'no host given')

		if proxy_passwd:
		    import base64
		    proxy_auth = base64.b64encode(proxy_passwd).strip()
		else:
		    proxy_auth = None

		if user_passwd:
		    import base64
		    auth = base64.b64encode(user_passwd).strip()
		else:
		    auth = None
		h = httplib.HTTP(host)
		if data is not None:
		    h.putrequest('POST', selector)
		    h.putheader('Content-Length', '%d' % len(data))
		else:
		    h.putrequest('GET', selector)
		if proxy_auth: h.putheader('Proxy-Authorization', 'Basic %s' % proxy_auth)
		if auth: h.putheader('Authorization', 'Basic %s' % auth)
		if realhost: h.putheader('Host', realhost)
		for args in self.addheaders: h.putheader(*args)
		h.endheaders()
		if data is not None:
		    h.send(data)
		errcode, errmsg, headers = h.getreply()
		if errcode == -1:
		    # something went wrong with the HTTP status line
		    raise IOError, ('http protocol error', 0,
		                    'got a bad status line', None)
		fp = h.getfile()
		if errcode == 200:
		    return urllib.addinfourl(fp, headers, "http:" + url)
		else:
		    if data is None:
		        return self.http_error(url, fp, errcode, errmsg, headers)
		    else:
		        return self.http_error(url, fp, errcode, errmsg, headers, data)


class HTTPSRangeHandler(HTTPRangeHandler):
	""" Range Header support for HTTPS. """
	def https_error_206(self, req, fp, code, msg, hdrs):
		return self.http_error_206(req, fp, code, msg, hdrs)

	def https_error_416(self, req, fp, code, msg, hdrs):
		self.https_error_416(req, fp, code, msg, hdrs)


