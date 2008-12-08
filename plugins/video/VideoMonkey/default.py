from string import *
import xbmcplugin
import sys, os.path
import urllib,urllib2
import re, random, string
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import shutil, codecs
import cookielib, htmlentitydefs
import socket, base64

__plugin__ = 'VideoMonkey'
__author__ = 'sfaxman'
__url__ = 'http://code.google.com/p/xbmc-addons/'
__svn_url__ = 'http://xbmc-addons.googlecode.com/svn/trunk/plugins/video/VideoMonkey/'
__credits__ = 'sfaxman'
__version__ = '1.7' # of this file

rootDir = os.getcwd()
if rootDir[-1] == ';':rootDir = rootDir[0:-1]
cacheDir = os.path.join(rootDir, 'cache')
resDir = os.path.join(rootDir, 'resources')
imgDir = os.path.join(resDir, 'images')
libDir = os.path.join(resDir, 'libs')
sys.path.append(libDir)
#socket.setdefaulttimeout(20)

urlopen = urllib2.urlopen
cj = cookielib.LWPCookieJar()
Request = urllib2.Request

if cj != None:
    if os.path.isfile(os.path.join(resDir, 'cookies.lwp')):
        cj.load(os.path.join(resDir, 'cookies.lwp'))
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

entitydefs = {
    'AElig':    u'\u00C6', # latin capital letter AE = latin capital ligature AE, U+00C6 ISOlat1'
    'Aacute':   u'\u00C1', # latin capital letter A with acute, U+00C1 ISOlat1'
    'Acirc':    u'\u00C2', # latin capital letter A with circumflex, U+00C2 ISOlat1'
    'Agrave':   u'\u00C0', # latin capital letter A with grave = latin capital letter A grave, U+00C0 ISOlat1'
    'Alpha':    u'\u0391', # greek capital letter alpha, U+0391'
    'Aring':    u'\u00C5', # latin capital letter A with ring above = latin capital letter A ring, U+00C5 ISOlat1'
    'Atilde':   u'\u00C3', # latin capital letter A with tilde, U+00C3 ISOlat1'
    'Auml':     u'\u00C4', # latin capital letter A with diaeresis, U+00C4 ISOlat1'
    'Beta':     u'\u0392', # greek capital letter beta, U+0392'
    'Ccedil':   u'\u00C7', # latin capital letter C with cedilla, U+00C7 ISOlat1'
    'Chi':      u'\u03A7', # greek capital letter chi, U+03A7'
    'Dagger':   u'\u2021', # double dagger, U+2021 ISOpub'
    'Delta':    u'\u0394', # greek capital letter delta, U+0394 ISOgrk3'
    'ETH':      u'\u00D0', # latin capital letter ETH, U+00D0 ISOlat1'
    'Eacute':   u'\u00C9', # latin capital letter E with acute, U+00C9 ISOlat1'
    'Ecirc':    u'\u00CA', # latin capital letter E with circumflex, U+00CA ISOlat1'
    'Egrave':   u'\u00C8', # latin capital letter E with grave, U+00C8 ISOlat1'
    'Epsilon':  u'\u0395', # grek capital letter epsilon, U+0395'
    'Eta':      u'\u0397', # greek capital letter eta, U+0397'
    'Euml':     u'\u00CB', # latin capital letter E with diaeresis, U+00CB ISOlat1'
    'Gamma':    u'\u0393', # greek capital letter gamma, U+0393 ISOgrk3'
    'Iacute':   u'\u00CD', # latin capital letter I with acute, U+00CD ISOlat1'
    'Icirc':    u'\u00CE', # latin capital letter I with circumflex, U+00CE ISOlat1'
    'Igrave':   u'\u00CC', # latin capital letter I with grave, U+00CC ISOlat1'
    'Iota':     u'\u0399', # greek capital letter iota, U+0399'
    'Iuml':     u'\u00CF', # latin capital letter I with diaeresis, U+00CF ISOlat1'
    'Kappa':    u'\u039A', # greek capital letter kappa, U+039A'
    'Lambda':   u'\u039B', # greek capital letter lambda, U+039B ISOgrk3'
    'Mu':       u'\u039C', # greek capital letter mu, U+039C'
    'Ntilde':   u'\u00D1', # latin capital letter N with tilde, U+00D1 ISOlat1'
    'Nu':       u'\u039D', # greek capital letter nu, U+039D'
    'OElig':    u'\u0152', # latin capital ligature OE, U+0152 ISOlat2'
    'Oacute':   u'\u00D3', # latin capital letter O with acute, U+00D3 ISOlat1'
    'Ocirc':    u'\u00D4', # latin capital letter O with circumflex, U+00D4 ISOlat1'
    'Ograve':   u'\u00D2', # latin capital letter O with grave, U+00D2 ISOlat1'
    'Omega':    u'\u03A9', # greek capital letter omega, U+03A9 ISOgrk3'
    'Omicron':  u'\u039F', # greek capital letter omicron, U+039F'
    'Oslash':   u'\u00D8', # latin capital letter O with stroke = latin capital letter O slash, U+00D8 ISOlat1'
    'Otilde':   u'\u00D5', # latin capital letter O with tilde, U+00D5 ISOlat1'
    'Ouml':     u'\u00D6', # latin capital letter O with diaeresis, U+00D6 ISOlat1'
    'Phi':      u'\u03A6', # greek capital letter phi, U+03A6 ISOgrk3'
    'Pi':       u'\u03A0', # greek capital letter pi, U+03A0 ISOgrk3'
    'Prime':    u'\u2033', # double prime = seconds = inches, U+2033 ISOtech'
    'Psi':      u'\u03A8', # greek capital letter psi, U+03A8 ISOgrk3'
    'Rho':      u'\u03A1', # greek capital letter rho, U+03A1'
    'Scaron':   u'\u0160', # latin capital letter S with caron, U+0160 ISOlat2'
    'Sigma':    u'\u03A3', # greek capital letter sigma, U+03A3 ISOgrk3'
    'THORN':    u'\u00DE', # latin capital letter THORN, U+00DE ISOlat1'
    'Tau':      u'\u03A4', # greek capital letter tau, U+03A4'
    'Theta':    u'\u0398', # greek capital letter theta, U+0398 ISOgrk3'
    'Uacute':   u'\u00DA', # latin capital letter U with acute, U+00DA ISOlat1'
    'Ucirc':    u'\u00DB', # latin capital letter U with circumflex, U+00DB ISOlat1'
    'Ugrave':   u'\u00D9', # latin capital letter U with grave, U+00D9 ISOlat1'
    'Upsilon':  u'\u03A5', # greek capital letter upsilon, U+03A5 ISOgrk3'
    'Uuml':     u'\u00DC', # latin capital letter U with diaeresis, U+00DC ISOlat1'
    'Xi':       u'\u039E', # greek capital letter xi, U+039E ISOgrk3'
    'Yacute':   u'\u00DD', # latin capital letter Y with acute, U+00DD ISOlat1'
    'Yuml':     u'\u0178', # latin capital letter Y with diaeresis, U+0178 ISOlat2'
    'Zeta':     u'\u0396', # greek capital letter zeta, U+0396'
    'aacute':   u'\u00E1', # latin small letter a with acute, U+00E1 ISOlat1'
    'acirc':    u'\u00E2', # latin small letter a with circumflex, U+00E2 ISOlat1'
    'acute':    u'\u00B4', # acute accent = spacing acute, U+00B4 ISOdia'
    'aelig':    u'\u00E6', # latin small letter ae = latin small ligature ae, U+00E6 ISOlat1'
    'agrave':   u'\u00E0', # latin small letter a with grave = latin small letter a grave, U+00E0 ISOlat1'
    'alefsym':  u'\u2135', # alef symbol = first transfinite cardinal, U+2135 NEW'
    'alpha':    u'\u03B1', # greek small letter alpha, U+03B1 ISOgrk3'
    'amp':      u'\u0026', # ampersand, U+0026 ISOnum'
    'and':      u'\u2227', # logical and = wedge, U+2227 ISOtech'
    'ang':      u'\u2220', # angle, U+2220 ISOamso'
    'aring':    u'\u00E5', # latin small letter a with ring above = latin small letter a ring, U+00E5 ISOlat1'
    'asymp':    u'\u2248', # almost equal to = asymptotic to, U+2248 ISOamsr'
    'atilde':   u'\u00E3', # latin small letter a with tilde, U+00E3 ISOlat1'
    'auml':     u'\u00E4', # latin small letter a with diaeresis, U+00E4 ISOlat1'
    'bdquo':    u'\u201E', # double low-9 quotation mark, U+201E NEW'
    'beta':     u'\u03B2', # greek small letter beta, U+03B2 ISOgrk3'
    'brvbar':   u'\u00A6', # broken bar = broken vertical bar, U+00A6 ISOnum'
    'bull':     u'\u2022', # bullet = black small circle, U+2022 ISOpub'
    'cap':      u'\u2229', # intersection = cap, U+2229 ISOtech'
    'ccedil':   u'\u00E7', # latin small letter c with cedilla, U+00E7 ISOlat1'
    'cedil':    u'\u00B8', # cedilla = spacing cedilla, U+00B8 ISOdia'
    'cent':     u'\u00A2', # cent sign, U+00A2 ISOnum'
    'chi':      u'\u03C7', # greek small letter chi, U+03C7 ISOgrk3'
    'circ':     u'\u02C6', # modifier letter circumflex accent, U+02C6 ISOpub'
    'clubs':    u'\u2663', # black club suit = shamrock, U+2663 ISOpub'
    'cong':     u'\u2245', # approximately equal to, U+2245 ISOtech'
    'copy':     u'\u00A9', # copyright sign, U+00A9 ISOnum'
    'crarr':    u'\u21B5', # downwards arrow with corner leftwards = carriage return, U+21B5 NEW'
    'cup':      u'\u222A', # union = cup, U+222A ISOtech'
    'curren':   u'\u00A4', # currency sign, U+00A4 ISOnum'
    'dArr':     u'\u21D3', # downwards double arrow, U+21D3 ISOamsa'
    'dagger':   u'\u2020', # dagger, U+2020 ISOpub'
    'darr':     u'\u2193', # downwards arrow, U+2193 ISOnum'
    'deg':      u'\u00B0', # degree sign, U+00B0 ISOnum'
    'delta':    u'\u03B4', # greek small letter delta, U+03B4 ISOgrk3'
    'diams':    u'\u2666', # black diamond suit, U+2666 ISOpub'
    'divide':   u'\u00F7', # division sign, U+00F7 ISOnum'
    'eacute':   u'\u00E9', # latin small letter e with acute, U+00E9 ISOlat1'
    'ecirc':    u'\u00EA', # latin small letter e with circumflex, U+00EA ISOlat1'
    'egrave':   u'\u00E8', # latin small letter e with grave, U+00E8 ISOlat1'
    'empty':    u'\u2205', # empty set = null set = diameter, U+2205 ISOamso'
    'emsp':     u'\u2003', # em space, U+2003 ISOpub'
    'ensp':     u'\u2002', # en space, U+2002 ISOpub'
    'epsilon':  u'\u03B5', # greek small letter epsilon, U+03B5 ISOgrk3'
    'equiv':    u'\u2261', # identical to, U+2261 ISOtech'
    'eta':      u'\u03B7', # greek small letter eta, U+03B7 ISOgrk3'
    'eth':      u'\u00F0', # latin small letter eth, U+00F0 ISOlat1'
    'euml':     u'\u00EB', # latin small letter e with diaeresis, U+00EB ISOlat1'
    'euro':     u'\u20AC', # euro sign, U+20AC NEW'
    'exist':    u'\u2203', # there exists, U+2203 ISOtech'
    'fnof':     u'\u0192', # latin small f with hook = function = florin, U+0192 ISOtech'
    'forall':   u'\u2200', # for all, U+2200 ISOtech'
    'frac12':   u'\u00BD', # vulgar fraction one half = fraction one half, U+00BD ISOnum'
    'frac14':   u'\u00BC', # vulgar fraction one quarter = fraction one quarter, U+00BC ISOnum'
    'frac34':   u'\u00BE', # vulgar fraction three quarters = fraction three quarters, U+00BE ISOnum'
    'frasl':    u'\u2044', # fraction slash, U+2044 NEW'
    'gamma':    u'\u03B3', # greek small letter gamma, U+03B3 ISOgrk3'
    'ge':       u'\u2265', # greater-than or equal to, U+2265 ISOtech'
    'gt':       u'\u003E', # greater-than sign, U+003E ISOnum'
    'hArr':     u'\u21D4', # left right double arrow, U+21D4 ISOamsa'
    'harr':     u'\u2194', # left right arrow, U+2194 ISOamsa'
    'hearts':   u'\u2665', # black heart suit = valentine, U+2665 ISOpub'
    'hellip':   u'\u2026', # horizontal ellipsis = three dot leader, U+2026 ISOpub'
    'iacute':   u'\u00ED', # latin small letter i with acute, U+00ED ISOlat1'
    'icirc':    u'\u00EE', # latin small letter i with circumflex, U+00EE ISOlat1'
    'iexcl':    u'\u00A1', # inverted exclamation mark, U+00A1 ISOnum'
    'igrave':   u'\u00EC', # latin small letter i with grave, U+00EC ISOlat1'
    'image':    u'\u2111', # blackletter capital I = imaginary part, U+2111 ISOamso'
    'infin':    u'\u221E', # infinity, U+221E ISOtech'
    'int':      u'\u222B', # integral, U+222B ISOtech'
    'iota':     u'\u03B9', # greek small letter iota, U+03B9 ISOgrk3'
    'iquest':   u'\u00BF', # inverted question mark = turned question mark, U+00BF ISOnum'
    'isin':     u'\u2208', # element of, U+2208 ISOtech'
    'iuml':     u'\u00EF', # latin small letter i with diaeresis, U+00EF ISOlat1'
    'kappa':    u'\u03BA', # greek small letter kappa, U+03BA ISOgrk3'
    'lArr':     u'\u21D0', # leftwards double arrow, U+21D0 ISOtech'
    'lambda':   u'\u03BB', # greek small letter lambda, U+03BB ISOgrk3'
    'lang':     u'\u2329', # left-pointing angle bracket = bra, U+2329 ISOtech'
    'laquo':    u'\u00AB', # left-pointing double angle quotation mark = left pointing guillemet, U+00AB ISOnum'
    'larr':     u'\u2190', # leftwards arrow, U+2190 ISOnum'
    'lceil':    u'\u2308', # left ceiling = apl upstile, U+2308 ISOamsc'
    'ldquo':    u'\u201C', # left double quotation mark, U+201C ISOnum'
    'le':       u'\u2264', # less-than or equal to, U+2264 ISOtech'
    'lfloor':   u'\u230A', # left floor = apl downstile, U+230A ISOamsc'
    'lowast':   u'\u2217', # asterisk operator, U+2217 ISOtech'
    'loz':      u'\u25CA', # lozenge, U+25CA ISOpub'
    'lrm':      u'\u200E', # left-to-right mark, U+200E NEW RFC 2070'
    'lsaquo':   u'\u2039', # single left-pointing angle quotation mark, U+2039 ISO proposed'
    'lsquo':    u'\u2018', # left single quotation mark, U+2018 ISOnum'
    'lt':       u'\u003C', # less-than sign, U+003C ISOnum'
    'macr':     u'\u00AF', # macron = spacing macron = overline = APL overbar, U+00AF ISOdia'
    'mdash':    u'\u2014', # em dash, U+2014 ISOpub'
    'micro':    u'\u00B5', # micro sign, U+00B5 ISOnum'
    'middot':   u'\u00B7', # middle dot = Georgian comma = Greek middle dot, U+00B7 ISOnum'
    'minus':    u'\u2212', # minus sign, U+2212 ISOtech'
    'mu':       u'\u03BC', # greek small letter mu, U+03BC ISOgrk3'
    'nabla':    u'\u2207', # nabla = backward difference, U+2207 ISOtech'
    'nbsp':     u'\u00A0', # no-break space = non-breaking space, U+00A0 ISOnum'
    'ndash':    u'\u2013', # en dash, U+2013 ISOpub'
    'ne':       u'\u2260', # not equal to, U+2260 ISOtech'
    'ni':       u'\u220B', # contains as member, U+220B ISOtech'
    'not':      u'\u00AC', # not sign, U+00AC ISOnum'
    'notin':    u'\u2209', # not an element of, U+2209 ISOtech'
    'nsub':     u'\u2284', # not a subset of, U+2284 ISOamsn'
    'ntilde':   u'\u00F1', # latin small letter n with tilde, U+00F1 ISOlat1'
    'nu':       u'\u03BD', # greek small letter nu, U+03BD ISOgrk3'
    'oacute':   u'\u00F3', # latin small letter o with acute, U+00F3 ISOlat1'
    'ocirc':    u'\u00F4', # latin small letter o with circumflex, U+00F4 ISOlat1'
    'oelig':    u'\u0153', # latin small ligature oe, U+0153 ISOlat2'
    'ograve':   u'\u00F2', # latin small letter o with grave, U+00F2 ISOlat1'
    'oline':    u'\u203E', # overline = spacing overscore, U+203E NEW'
    'omega':    u'\u03C9', # greek small letter omega, U+03C9 ISOgrk3'
    'omicron':  u'\u03BF', # greek small letter omicron, U+03BF NEW'
    'oplus':    u'\u2295', # circled plus = direct sum, U+2295 ISOamsb'
    'or':       u'\u2228', # logical or = vee, U+2228 ISOtech'
    'ordf':     u'\u00AA', # feminine ordinal indicator, U+00AA ISOnum'
    'ordm':     u'\u00BA', # masculine ordinal indicator, U+00BA ISOnum'
    'oslash':   u'\u00F8', # latin small letter o with stroke, = latin small letter o slash, U+00F8 ISOlat1'
    'otilde':   u'\u00F5', # latin small letter o with tilde, U+00F5 ISOlat1'
    'otimes':   u'\u2297', # circled times = vector product, U+2297 ISOamsb'
    'ouml':     u'\u00F6', # latin small letter o with diaeresis, U+00F6 ISOlat1'
    'para':     u'\u00B6', # pilcrow sign = paragraph sign, U+00B6 ISOnum'
    'part':     u'\u2202', # partial differential, U+2202 ISOtech'
    'permil':   u'\u2030', # per mille sign, U+2030 ISOtech'
    'perp':     u'\u22A5', # up tack = orthogonal to = perpendicular, U+22A5 ISOtech'
    'phi':      u'\u03C6', # greek small letter phi, U+03C6 ISOgrk3'
    'pi':       u'\u03C0', # greek small letter pi, U+03C0 ISOgrk3'
    'piv':      u'\u03D6', # greek pi symbol, U+03D6 ISOgrk3'
    'plusmn':   u'\u00B1', # plus-minus sign = plus-or-minus sign, U+00B1 ISOnum'
    'pound':    u'\u00A3', # pound sign, U+00A3 ISOnum'
    'prime':    u'\u2032', # prime = minutes = feet, U+2032 ISOtech'
    'prod':     u'\u220F', # n-ary product = product sign, U+220F ISOamsb'
    'prop':     u'\u221D', # proportional to, U+221D ISOtech'
    'psi':      u'\u03C8', # greek small letter psi, U+03C8 ISOgrk3'
    'quot':     u'\u0022', # quotation mark = APL quote, U+0022 ISOnum'
    'rArr':     u'\u21D2', # rightwards double arrow, U+21D2 ISOtech'
    'radic':    u'\u221A', # square root = radical sign, U+221A ISOtech'
    'rang':     u'\u232A', # right-pointing angle bracket = ket, U+232A ISOtech'
    'raquo':    u'\u00BB', # right-pointing double angle quotation mark = right pointing guillemet, U+00BB ISOnum'
    'rarr':     u'\u2192', # rightwards arrow, U+2192 ISOnum'
    'rceil':    u'\u2309', # right ceiling, U+2309 ISOamsc'
    'rdquo':    u'\u201D', # right double quotation mark, U+201D ISOnum'
    'real':     u'\u211C', # blackletter capital R = real part symbol, U+211C ISOamso'
    'reg':      u'\u00AE', # registered sign = registered trade mark sign, U+00AE ISOnum'
    'rfloor':   u'\u230B', # right floor, U+230B ISOamsc'
    'rho':      u'\u03C1', # greek small letter rho, U+03C1 ISOgrk3'
    'rlm':      u'\u200F', # right-to-left mark, U+200F NEW RFC 2070'
    'rsaquo':   u'\u203A', # single right-pointing angle quotation mark, U+203A ISO proposed'
    'rsquo':    u'\u2019', # right single quotation mark, U+2019 ISOnum'
    'sbquo':    u'\u201A', # single low-9 quotation mark, U+201A NEW'
    'scaron':   u'\u0161', # latin small letter s with caron, U+0161 ISOlat2'
    'sdot':     u'\u22C5', # dot operator, U+22C5 ISOamsb'
    'sect':     u'\u00A7', # section sign, U+00A7 ISOnum'
    'shy':      u'\u00AD', # soft hyphen = discretionary hyphen, U+00AD ISOnum'
    'sigma':    u'\u03C3', # greek small letter sigma, U+03C3 ISOgrk3'
    'sigmaf':   u'\u03C2', # greek small letter final sigma, U+03C2 ISOgrk3'
    'sim':      u'\u223C', # tilde operator = varies with = similar to, U+223C ISOtech'
    'spades':   u'\u2660', # black spade suit, U+2660 ISOpub'
    'sub':      u'\u2282', # subset of, U+2282 ISOtech'
    'sube':     u'\u2286', # subset of or equal to, U+2286 ISOtech'
    'sum':      u'\u2211', # n-ary sumation, U+2211 ISOamsb'
    'sup':      u'\u2283', # superset of, U+2283 ISOtech'
    'sup1':     u'\u00B9', # superscript one = superscript digit one, U+00B9 ISOnum'
    'sup2':     u'\u00B2', # superscript two = superscript digit two = squared, U+00B2 ISOnum'
    'sup3':     u'\u00B3', # superscript three = superscript digit three = cubed, U+00B3 ISOnum'
    'supe':     u'\u2287', # superset of or equal to, U+2287 ISOtech'
    'szlig':    u'\u00DF', # latin small letter sharp s = ess-zed, U+00DF ISOlat1'
    'tau':      u'\u03C4', # greek small letter tau, U+03C4 ISOgrk3'
    'there4':   u'\u2234', # therefore, U+2234 ISOtech'
    'theta':    u'\u03B8', # greek small letter theta, U+03B8 ISOgrk3'
    'thetasym': u'\u03D1', # greek small letter theta symbol, U+03D1 NEW'
    'thinsp':   u'\u2009', # thin space, U+2009 ISOpub'
    'thorn':    u'\u00FE', # latin small letter thorn with, U+00FE ISOlat1'
    'tilde':    u'\u02DC', # small tilde, U+02DC ISOdia'
    'times':    u'\u00D7', # multiplication sign, U+00D7 ISOnum'
    'trade':    u'\u2122', # trade mark sign, U+2122 ISOnum'
    'uArr':     u'\u21D1', # upwards double arrow, U+21D1 ISOamsa'
    'uacute':   u'\u00FA', # latin small letter u with acute, U+00FA ISOlat1'
    'uarr':     u'\u2191', # upwards arrow, U+2191 ISOnum'
    'ucirc':    u'\u00FB', # latin small letter u with circumflex, U+00FB ISOlat1'
    'ugrave':   u'\u00F9', # latin small letter u with grave, U+00F9 ISOlat1'
    'uml':      u'\u00A8', # diaeresis = spacing diaeresis, U+00A8 ISOdia'
    'upsih':    u'\u03D2', # greek upsilon with hook symbol, U+03D2 NEW'
    'upsilon':  u'\u03C5', # greek small letter upsilon, U+03C5 ISOgrk3'
    'uuml':     u'\u00FC', # latin small letter u with diaeresis, U+00FC ISOlat1'
    'weierp':   u'\u2118', # script capital P = power set = Weierstrass p, U+2118 ISOamso'
    'xi':       u'\u03BE', # greek small letter xi, U+03BE ISOgrk3'
    'yacute':   u'\u00FD', # latin small letter y with acute, U+00FD ISOlat1'
    'yen':      u'\u00A5', # yen sign = yuan sign, U+00A5 ISOnum'
    'yuml':     u'\u00FF', # latin small letter y with diaeresis, U+00FF ISOlat1'
    'zeta':     u'\u03B6', # greek small letter zeta, U+03B6 ISOgrk3'
    'zwj':      u'\u200D', # zero width joiner, U+200D NEW RFC 2070'
    'zwnj':     u'\u200C'  # zero width non-joiner, U+200C NEW RFC 2070'
}

entitydefs2 = {
    '$':    '%24',
    '&':    '%26',
    '+':    '%2B',
    ',':    '%2C',
    '/':    '%2F',
    ':':    '%3A',
    ';':    '%3B',
    '=':    '%3D',
    '?':    '%3F',
    '@':    '%40',
    ' ':    '%20',
    '"':    '%22',
    '<':    '%3C',
    '>':    '%3E',
    '#':    '%23',
    '%':    '%25',
    '{':    '%7B',
    '}':    '%7D',
    '|':    '%7C',
    '\\':   '%5C',
    '^':    '%5E',
    '~':    '%7E',
    '[':    '%5B',
    ']':    '%5D',
    '`':    '%60'
}

def clean1(s): # remove &XXX;
    if not s:
        return ''
    for name, value in entitydefs.iteritems():
        if u'&' in s:
            s = s.replace(u'&' + name + u';', value)
    return s;

def clean2(s): # remove \\uXXX
    pat = re.compile(r'\\u(....)')
    def sub(mo):
        return unichr(int(mo.group(1), 16))
    return pat.sub(sub, smart_unicode(s))

def clean3(s): # remove &#XXX;
    pat = re.compile(r'&#(\d+);')
    def sub(mo):
        return unichr(int(mo.group(1)))
    return decode(pat.sub(sub, smart_unicode(s)))

def decode(s):
    if not s:
        return ''
    try:
        dic=htmlentitydefs.name2codepoint
        for key in dic.keys():
            entity = '&' + key + ';'
            s = s.replace(entity, unichr(dic[key]))
    except:
        traceback.print_exc(file = sys.stdout)
    return s

def unquote_safe(s): # unquote
    if not s:
        return ''
    try:
        for key, value in entitydefs2.iteritems():
            s = s.replace(value, key)
    except:
        traceback.print_exc(file = sys.stdout)
    return s;

def quote_safe(s): # quote
    if not s:
        return ''
    try:
        for key, value in entitydefs2.iteritems():
            s = s.replace(key, value)
    except:
        traceback.print_exc(file = sys.stdout)
    return s;

def smart_unicode(s):
    if not s:
        return ''
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'UTF-8')
        elif not isinstance(s, unicode):
            s = unicode(s, 'UTF-8')
    except:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'ISO-8859-1')
        elif not isinstance(s, unicode):
            s = unicode(s, 'ISO-8859-1')
    return s

def clean_title(s):
    if not s:
        return ''
    try:
        s = clean1(clean2(clean3(smart_unicode(s)))).replace('\r\n', '').replace('\n', '')
    except:
        traceback.print_exc(file = sys.stdout)
    return s

class CListItem:
    def __init__(self):
        self.infos_names = []
        self.infos_values = []

class CSourceItem:
    def __init__(self):
        self.rule = ''
        self.extension = ''
        self.quality = 'standard'
        self.url = ''

class CVideoInfoItem:
    def __init__(self):
        self.name = ''
        self.src = ''
        self.rule = ''
        self.build = '%s'

class CVideoItem:
    def __init__(self):
        self.infos = ''
        self.order = ''
        self.view = ''
        self.url_action = ''
        self.info_list = []
        self.url_build = '%s'
        self.thumb = os.path.join(imgDir, 'video.png')

class CDirItem:
    def __init__(self):
        self.view = ''
        self.infos_names = []
        self.infos_values = []
        self.title = ''
        self.url = ''
        self.url_action = ''
        self.url_build = '%s'
        self.curr_url = ''
        self.img = ''
        self.img_build = '%s'
        self.curr_img = ''
        self.curr_img_build = '%s'
        self.thumb = ''

class CCurrentList:
    def __init__(self):
        self.start_url = ''
        self.force_player = ''
        self.sort_method = 'label'
        self.cfg_name = ''
        self.action = ''
        self.video_action = ''
        self.user = ''
        self.password = ''
        self.reference = ''
        self.content = ''
        self.target_url = ''
        self.target_extension = ''
        self.ext_target_url = ''
        self.catcher_data = ''
        self.catcher_reference = ''
        self.catcher_content = ''
        self.catcher_url_build = '%s'
        self.search_url_build = '%s'
        self.search_thumb = ''
        self.list = []
        self.video_list = []
        self.source_list = []
        self.dir_list = []

    def getKeyboard(self, default = '', heading = '', hidden = False):
        kboard = xbmc.Keyboard(default, heading, hidden)
        kboard.doModal()
        if (kboard.isConfirmed()):
            return urllib.quote_plus(kboard.getText())
        return default

    def getFileExtension(self, filename):
        ext_pos = filename.rfind('.')
        if ext_pos != -1:
            return filename[ext_pos+1:]
        else:
            return ''

    def randomFilename(self, dir = cacheDir, chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', length = 8, prefix = '', suffix = '', attempts = 1000):
        for attempt in range(attempts):
            filename = ''.join([random.choice(chars) for i in range(length)])
            filename = prefix + filename + suffix
            if not os.path.exists(os.path.join(dir, filename)):
                return filename

    def videoCount(self):
        count = 0
        for item in self.list:
            if item.infos_values[item.infos_names.index('type')] == 'video':
                count = count +1
        return count

    def getVideo(self):
        for item in self.list:
            if item.infos_values[item.infos_names.index('type')] == 'video':
                return item

    def getItemFromList(self, listname, name):
        self.loadLocal(listname, False)
        for item in self.list:
            if item.infos_values[item.infos_names.index('url')] == name:
                return item
        return None

    def itemInLocalList(self, name):
        for item in self.list:
            if item.infos_values[item.infos_names.index('url')] == name:
                return True
        return False

    def getItem(self, name):
        item = None
        for root, dirs, files in os.walk(resDir):
            for listname in files:
                if self.getFileExtension(listname) == 'list':
                    item = self.getItemFromList(listname, name)
                if item != None:
                    return item
        return None

    def addItem(self, name):
        item = self.getItem(name)
        del self.list[:]
        try:
            self.loadLocal('entry.list', False)
        except:
            del self.list[:]
        if self.itemInLocalList(name) == False and item != None:
            self.list.append(item)
            self.saveList()
        return

    def removeItem(self, name):
        item = self.getItemFromList('entry.list', name)
        if item != None:
            self.list.remove(item)
            self.saveList()
        return

    def saveList(self):
        f = codecs.open(os.path.join(resDir, 'entry.list'), 'w', 'utf-8')
        f.write('########################################################\n')
        f.write('# Added sites and live streams\n')
        f.write('########################################################\n')
        f.write('action=remove\n')
        f.write('########################################################\n')
        for item in self.list:
            f.write('title=' + item.infos_values[item.infos_names.index('title')] + '\n')
            for info_name in item.infos_names:
                if info_name != 'url' and info_name != 'title':
                    f.write(info_name + '=' + item.infos_values[item.infos_names.index(info_name)] + '\n')
            f.write('url=' + item.infos_values[item.infos_names.index('url')] + '\n')
            f.write('########################################################\n')
        f.close()
        return

    def codeUrl(self, videoItem, suffix = ''):
        url_idx = videoItem.infos_names.index('url')
        info_idx = 0
        firstInfo = True
        for info_name in videoItem.infos_names:
            if info_idx != url_idx:
                if firstInfo:
                    firstInfo = False
                    try:
                        videoUrl = videoItem.infos_names[info_idx] + ':' + videoItem.infos_values[info_idx]
                    except:
                        videoUrl = videoItem.infos_names[info_idx] + ':' + smart_unicode(videoItem.infos_values[info_idx])
                else:
                    try:
                        videoUrl = videoUrl + '|' + videoItem.infos_names[info_idx] + ':' + videoItem.infos_values[info_idx]
                    except:
                        videoUrl = videoUrl + '|' + videoItem.infos_names[info_idx] + ':' + smart_unicode(videoItem.infos_values[info_idx])
            info_idx = info_idx + 1
        videoUrl = videoUrl + '|' + videoItem.infos_names[url_idx] + ':' + videoItem.infos_values[url_idx]
        if len(suffix) > 0:
            videoUrl = videoUrl + '.' + suffix
        return videoUrl

    def decodeUrl(self, videoUrl, type = 'rss'):
        videoItem = CListItem()
        if videoUrl.find('|') == -1:
            videoItem.infos_names.append('url')
            videoItem.infos_values.append(videoUrl)
            videoItem.infos_names.append('type')
            videoItem.infos_values.append(type)
            return videoItem
        video_infos_names_values = videoUrl.split('|')
        for video_info_name_value in video_infos_names_values:
            sep_index = video_info_name_value.find(':')
            if sep_index != -1:
                videoItem.infos_names.append(video_info_name_value[:sep_index])
                if video_info_name_value[:sep_index] == 'title':
                    videoItem.infos_values.append(clean_title(video_info_name_value[sep_index+1:]))
                else:
                    videoItem.infos_values.append(video_info_name_value[sep_index+1:])
        try:
            type_idx = videoItem.infos_names.index('type')
        except:
            videoItem.infos_names.append('type')
            videoItem.infos_values.append(type)
        return videoItem

    def loadCatcher(self, title):
        f = codecs.open(os.path.join(resDir, 'catcher.list'), 'r', 'utf-8')
        data = f.read()
        data = data.replace('\r\n', '\n')
        data = data.split('\n')
        f.close()

        del self.source_list[:]
        catcher_found = False
        for m in data:
            if m and m[0] != '#':
                index = m.find('=')
                if index != -1:
                    key = lower(m[:index])
                    value = m[index+1:]
                    if key == 'title':
                        if title == value:
                            catcher_found = True
                    elif key == 'data' and catcher_found == True:
                        self.catcher_data = value
                    elif key == 'header' and catcher_found == True:
                        index = value.find('|')
                        self.catcher_reference = value[:index]
                        self.catcher_content = value[index+1:]
                    elif key == 'url' and catcher_found == True:
                        self.catcher_url_build = value
                    elif key == 'source':
                        source_tmp = CSourceItem()
                        source_tmp.rule = value
                    elif key == 'source_extension':
                        source_tmp.extension = value
                    elif key == 'source_quality':
                        source_tmp.quality = value
                        self.source_list.append(source_tmp)
                    elif key == 'ext_target' and catcher_found == True:
                        self.ext_target_url = value
                    elif key == 'extension' and catcher_found == True:
                        self.target_extension = value
                    elif key == 'target' and catcher_found == True:
                        self.target_url = value
                        return 0
        return -1

    def loadLocal(self, filename, recursive = True, lItem = None):
        print(filename)
        try:
            f = codecs.open(os.path.join(resDir, filename), 'r', 'utf-8')
            data = f.read()
            data = data.replace('\r\n', '\n')
            data = data.split('\n')
            f.close()
        except:
            try:
                f = codecs.open(os.path.join(cacheDir, filename), 'r', 'utf-8')
                data = f.read()
                data = data.replace('\r\n', '\n')
                data = data.split('\n')
                f.close()
            except:
                try:
                    f = codecs.open(filename, 'r', 'utf-8')
                    data = f.read()
                    data = data.replace('\r\n', '\n')
                    data = data.split('\n')
                    f.close()
                except:
                    #traceback.print_exc(file = sys.stdout)
                    return -1

        self.cfg_name = filename
        if self.getFileExtension(self.cfg_name) == 'cfg' and lItem != None:
            try:
                lItem.infos_values[lItem.infos_names.index(strin)] = self.cfg_name
            except:
                lItem.infos_names.append('cfg')
                lItem.infos_values.append(self.cfg_name)
        del self.list[:]
        tmp = None
        for m in data:
            if m and m[0] != '#':
                index = m.find('=')
                if index != -1:
                    key = lower(m[:index])
                    value = m[index+1:]
                    if key == 'start_url':
                        self.start_url = value
                    elif key == 'force_player':
                        self.force_player = value
                    elif key == 'fort_method':
                        self.sort_method = value
                    elif key == 'action':
                        self.action = value
                        action_file = filename[:filename.find('.')] + '.lnk'
                        if self.action.find('redirect') != -1:
                            try:
                                f = open(os.path.join(resDir, action_file), 'r')
                                forward_cfg = f.read()
                                f.close()
                                if (forward_cfg != self.cfg_name):
                                    return self.loadLocal(forward_cfg, recursive, lItem)
                                return 0
                            except:
                                pass
                        elif self.action.find('store') != -1:
                            f = open(os.path.join(resDir, action_file), 'w')
                            f.write(self.cfg_name)
                            f.close()
                    elif key == 'catcher':
                        try:
                            ret = self.loadCatcher(value)
                            if ret != 0:
                                print('Error while loding catcher!')
                                return ret
                        except:
                            traceback.print_exc(file = sys.stdout)
                            return -1
                    elif key == 'video_action':
                        self.video_action = value
                    elif key == 'header':
                        index = value.find('|')
                        self.reference = value[:index]
                        self.content = value[index+1:]
                    elif key == 'item_infos':
                        video_tmp = CVideoItem()
                        video_tmp.infos = value
                    elif key == 'item_order':
                        video_tmp.order = value
                    elif key == 'item_view':
                        video_tmp.view = value
                    elif key == 'item_info_name':
                        video_info_tmp = CVideoInfoItem()
                        video_info_tmp.name = value
                    elif key == 'item_info_from':
                        video_info_tmp.src = value
                    elif key == 'item_info':
                        video_info_tmp.rule = value
                    elif key == 'item_info_build':
                        index = value.find('|')
                        if value[:index] == 'video.monkey.locale':
                            value = xbmc.getLocalizedString(int(value[index+1:]))
                        elif value[:index] == 'video.monkey.image':
                            value = os.path.join(imgDir, value[index+1:])
                        video_info_tmp.build = value
                        video_tmp.info_list.append(video_info_tmp)
                    elif key == 'item_thumb':
                        video_tmp.thumb = value
                        index = value.find('|')
                        if value[:index] == 'video.monkey.image':
                            video_tmp.thumb = os.path.join(imgDir, value[index+1:])
                    elif key == 'item_url_build':
                        video_tmp.url_build = value
                        self.video_list.append(video_tmp)
                    elif key == 'ext_target_url':
                        self.ext_target_url = value
                    elif key == 'target_extension':
                        self.target_extension = value
                    elif key == 'target_url':
                        self.target_url = value
                    elif key == 'catcher_data':
                        self.catcher_data = value
                    elif key == 'catcher_header':
                        index = value.find('|')
                        self.catcher_reference = value[:index]
                        self.catcher_content = value[index+1:]
                    elif key == 'catcher_url_build':
                        self.catcher_url_build = value
                    elif key == 'catcher_source':
                        source_tmp = CSourceItem()
                        source_tmp.rule = value
                    elif key == 'catcher_source_extension':
                        source_tmp.extension = value
                    elif key == 'catcher_source_quality':
                        source_tmp.quality = value
                        self.source_list.append(source_tmp)
                    elif key == 'dir_title':
                        dir_tmp = CDirItem()
                        dir_tmp.title = value
                        index = value.find('|')
                        if value[:index] == 'video.monkey.locale':
                            dir_tmp.title = xbmc.getLocalizedString(int(value[index+1:]))
                    elif key == 'dir_url':
                        dir_tmp.url = value
                    elif key == 'dir_view':
                        dir_tmp.view = value
                    elif key == 'dir_url_action':
                        dir_tmp.url_action = value
                    elif key == 'dir_curr_url':
                        dir_tmp.curr_url = value
                    elif key == 'dir_curr_img':
                        dir_tmp.curr_img = value
                    elif key == 'dir_curr_img_build':
                        dir_tmp.curr_img_build = value
                    elif key == 'dir_img':
                        dir_tmp.img = value
                    elif key == 'dir_img_build':
                        dir_tmp.img_build = value
                    elif key == 'dir_thumb':
                        dir_tmp.thumb = value
                        index = value.find('|')
                        if value[:index] == 'video.monkey.image':
                            dir_tmp.thumb = os.path.join(imgDir, value[index+1:])
                    elif key == 'dir_url_build':
                        dir_tmp.url_build = value
                        self.dir_list.append(dir_tmp)
                    elif key == 'title':
                        tmp = CListItem()
                        tmp.infos_names.append('title')
                        index = value.find('|')
                        if value[:index] == 'video.monkey.locale':
                            value = ' ' + xbmc.getLocalizedString(int(value[index+1:])) + ' '
                        tmp.infos_values.append(value)
                    elif key == 'type':
                        tmp.infos_names.append('type')
                        vType = value
                        if (recursive and value == 'once'):
                            vType = 'rss'
                        tmp.infos_values.append(vType)
                    elif key == 'icon':
                        tmp.infos_names.append('icon')
                        index = value.find('|')
                        if value[:index] == 'video.monkey.image':
                            value = os.path.join(imgDir, value[index+1:])
                        tmp.infos_values.append(value)
                    elif key == 'url':
                        tmp.infos_names.append('url')
                        tmp.infos_values.append(value)
                        if lItem != None:
                            for info_name in lItem.infos_names:
                                try:
                                    info_idx = tmp.infos_names.index(info_name)
                                except:
                                    tmp.infos_names.append(info_name)
                                    tmp.infos_values.append(lItem.infos_values[lItem.infos_names.index(info_name)])
                        self.list.append(tmp)
                        tmp = None
                    elif tmp != None:
                        tmp.infos_names.append(key)
                        index = value.find('|')
                        if value[:index] == 'video.monkey.locale':
                            value = ' ' + xbmc.getLocalizedString(int(value[index+1:])) + ' '
                        elif value[:index] == 'video.monkey.image':
                            value = os.path.join(imgDir, value[index+1:])
                        tmp.infos_values.append(value)

        if (recursive and self.start_url != ''):
            if lItem == None:
                self.loadRemote(self.start_url, False)
            else:
                if self.getFileExtension(lItem.infos_values[lItem.infos_names.index('url')]) == 'cfg':
                    lItem.infos_values[lItem.infos_names.index('url')] = self.start_url
                    self.loadRemote(self.start_url, False, lItem)
                else:
                    self.loadRemote(lItem.infos_values[lItem.infos_names.index('url')], False, lItem)
        return 0

    def infoFormatter(self, info_name, info_value, cfg_file): # Site specific info handling
        if (info_name == 'title'):
            try:
                info_value = clean_title(info_value)
            except:
                info_value = 'No title'
            if (len(info_value) == 0):
                info_value = 'No title'
            if cfg_file == 'arteplus7.cfg' or cfg_file == 'arteplus7.de.cfg'or cfg_file == 'arteplus7.fr.cfg': # arte+7
                info_value = info_value.replace('</index>', ' - ').replace('        <bigTitle>', '').replace('\n', '')
        elif (info_name == 'icon'):
            info_value = decode(unquote_safe(info_value)).replace(' ', '%20')
            if (info_value == ''):
                info_value = os.path.join(imgDir, 'video.png')
        elif (info_name == 'Related'):
            if (info_value != ''):
                info_value = cfg_file + '|' + info_value
        return info_value

    def loadRemote(self, remote_url, recursive = True, lItem = None):
        print(remote_url)
        if lItem == None:
            lItem = self.decodeUrl(curr_url)
        try:
            curr_url = remote_url
            if (recursive):
                try:
                    if self.loadLocal(lItem.infos_values[lItem.infos_names.index('cfg')], False, lItem) != 0:
                        return -1
                except:
                    pass
                try:
                    if lItem.infos_values[lItem.infos_names.index('type')] == u'search':
                        try:
                            f = open(os.path.join(cacheDir, 'search'), 'r')
                            curr_phrase = urllib.unquote_plus(f.read())
                            f.close()
                        except:
                            curr_phrase = ''
                        search_phrase = self.getKeyboard(default = curr_phrase, heading = xbmc.getLocalizedString(30102))
                        xbmc.sleep(10)
                        f = open(os.path.join(cacheDir, 'search'), 'w')
                        f.write(search_phrase)
                        f.close()
                        curr_url = curr_url % (search_phrase)
                        lItem.infos_values[lItem.infos_names.index('url')] = curr_url
                        lItem.infos_values[lItem.infos_names.index('type')] = u'rss'
                except:
                    pass
            if (self.reference == ''):
                txheaders = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14', 'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}
            else:
                txheaders = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14', 'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7', self.reference:self.content}
            #f = open(os.path.join(cacheDir, 'page.html'), 'w')
            #f.write('<Titel>'+ curr_url + '</Title>\n\n')
            req = Request(curr_url, None, txheaders)
            try:
                handle = urlopen(req)
            except:
                traceback.print_exc(file = sys.stdout)
                return
            data = handle.read()
            #cj.save(os.path.join(resDir, 'cookies.lwp'), ignore_discard=True)
            cj.save(os.path.join(resDir, 'cookies.lwp'))
            #f.write(data)
            #f.close()
        except IOError:
            traceback.print_exc(file = sys.stdout)
            return -1

        # Find video items
        reinfos = []
        for video in self.video_list:
            if video.order.find('|') != -1:
                reinfos = []
                infos_nbr = len(video.order.split('|'))
                for idx in range(infos_nbr):
                    reinfos.append('')
            else:
                reinfos = ''
            if (video.infos != ''):
                revid = re.compile(video.infos, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                for reinfos in revid.findall(data):
                    tmp = CListItem()
                    if video.order.find('|') != -1:
                        tmp.infos_names = video.order.split('|')
                        tmp.infos_values = list(reinfos)
                    else:
                        tmp.infos_names.append(video.order)
                        tmp.infos_values.append(reinfos)
                    for info in video.info_list:
                        info_value = ''
                        try:
                            src = tmp.infos_values[tmp.infos_names.index(info.src)]
                        except:
                            src = ''
                        if info.rule != '':
                            try:
                                info_rule = info.rule % (src)
                            except:
                                try:
                                    info_rule = info.rule % (smart_unicode(src))
                                except:
                                    info_rule = info.rule
                            reinfo = re.compile(info_rule, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                            infosearch = reinfo.search(data)
                            try:
                                info_value = infosearch.group(1)
                            except:
                                info_value = ''
                        tmp.infos_names.append(info.name)
                        info_value = info_value.lstrip().rstrip()
                        try:
                            iValue = smart_unicode(info.build % (info_value))
                            tmp.infos_values.append(iValue)
                        except:
                            try:
                                iValue = smart_unicode(info.build % (smart_unicode(info_value)))
                                tmp.infos_values.append(iValue)
                            except:
                                tmp.infos_values.append(smart_unicode(info.build))
                    info_idx = tmp.infos_names.index('url')
                    if video.url_action.find('append') != -1:
                        if curr_url[len(curr_url) - 1] == '?':
                            tmp.infos_values[info_idx] = curr_url + url
                        else:
                            tmp.infos_values[info_idx] = curr_url + '&' + url
                    else:
                        try:
                            tmp.infos_values[info_idx] = smart_unicode(video.url_build % (tmp.infos_values[info_idx]))
                        except:
                            try:
                                tmp.infos_values[info_idx] = smart_unicode(video.url_build % (smart_unicode(tmp.infos_values[info_idx])))
                            except:
                                tmp.infos_values[info_idx] = video.url_build
                    info_idx = 0
                    for info_name in tmp.infos_names:
                        tmp.infos_values[info_idx] = self.infoFormatter(info_name, tmp.infos_values[info_idx], self.cfg_name)
                        info_idx = info_idx + 1
                    try:
                        title = tmp.infos_values[tmp.infos_names.index('title')]
                    except:
                        tmp.infos_names.append('title')
                        tmp.infos_values.append('No title')
                        title = tmp.infos_values[tmp.infos_names.index('title')]
                    for info_name in lItem.infos_names:
                        try:
                            info_idx = tmp.infos_names.index(info_name)
                        except:
                            tmp.infos_names.append(info_name)
                            tmp.infos_values.append(lItem.infos_values[lItem.infos_names.index(info_name)])
                    if video.view.find('space') != -1:
                        tmp.infos_values[tmp.infos_names.index('title')] = ' ' + title + ' '
                    self.list.append(tmp)
        # Find category items
        for dir in self.dir_list:
            oneFound = False
            catfilename = self.randomFilename(prefix=(self.cfg_name + '%'), suffix = '.list')
            f = None
            if (dir.url != ''):
                recat = re.compile(dir.url, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                for url, title in recat.findall(data):
                    url = decode(url)
                    title = clean_title(title.lstrip().rstrip())
                    icon = dir.thumb
                    if (dir.img != ''):
                        try:
                            img_catcher = dir.img % (url)
                        except:
                            img_catcher = dir.img
                        reimg = re.compile(img_catcher, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                        imgsearch = reimg.search(data)
                        try:
                            #icon= dir.img_build % (decode(imgsearch.group(1)).replace(' ', '%20'))
                            icon = dir.img_build % (decode(unquote_safe(imgsearch.group(1))).replace(' ', '%20'))
                        except:
                            #traceback.print_exc(file = sys.stdout)
                            pass
                    try:
                        url = dir.url_build % (url)
                    except:
                        url = dir.url_build % (smart_unicode(url))
                    if dir.url_action.find('append') != -1:
                        if curr_url[len(curr_url) - 1] == '?':
                            url = curr_url + url
                        else:
                            url = curr_url + '&' + url
                    if dir.url_action.find('recursive') != -1:
                        lItem.infos_values[lItem.infos_names.index('url')] = url
                        self.loadRemote(url, False, lItem)
                    else:
                        tmp = CListItem()
                        tmp.infos_names.append('title')
                        if dir.view.find('space') != -1:
                            tmp.infos_values.append(' ' + title + ' ')
                        else:
                            tmp.infos_values.append(title)
                        if len(tmp.infos_values[tmp.infos_names.index('title')]) == 0:
                            tmp.infos_values[tmp.infos_names.index('title')] = self.randomFilename(prefix = 'notitle_')
                        tmp.infos_names.append('icon')
                        tmp.infos_values.append(icon)
                        tmp.infos_names.append('url')
                        tmp.infos_values.append(url)
                        for info_name in lItem.infos_names:
                            try:
                                info_idx = tmp.infos_names.index(info_name)
                            except:
                                tmp.infos_names.append(info_name)
                                tmp.infos_values.append(lItem.infos_values[lItem.infos_names.index(info_name)])
                        if dir.view.find('flat') != -1:
                            self.list.append(tmp)
                        else:
                            if f == None:
                                f = codecs.open(os.path.join(cacheDir, catfilename), 'w', 'utf-8')
                            f.write('Title=' + tmp.infos_values[tmp.infos_names.index('title')] + '\n')
                            for info_name in tmp.infos_names:
                                if info_name != 'url' and info_name != 'title':
                                    f.write(info_name + '=' + tmp.infos_values[tmp.infos_names.index(info_name)] + '\n')
                            f.write('Url=' + tmp.infos_values[tmp.infos_names.index('url')] + '\n')
                        oneFound = True
            if (dir.curr_url != ''):
                recat = re.compile(dir.curr_url, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                for title in recat.findall(data):
                    title = clean_title(title.lstrip().rstrip())
                    if (dir.img != ''):
                        try:
                            img_catcher = dir.curr_img % (title)
                        except:
                            img_catcher = dir.curr_img
                        reimg = re.compile(img_catcher, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                        imgsearch = reimg.search(data)
                        try:
                            dir.thumb = dir.curr_img_build % (decode(imgsearch.group(1)).replace(' ', '%20'))
                        except:
                            traceback.print_exc(file = sys.stdout)
                    tmp = CListItem()
                    tmp.infos_names.append('title')
                    if dir.view.find('space') != -1:
                        tmp.infos_values.append(' ' + title + ' ')
                    else:
                        tmp.infos_values.append(title)
                    if len(tmp.infos_values[tmp.infos_names.index('title')]) == 0:
                        tmp.infos_values[tmp.infos_names.index('title')] = self.randomFilename(prefix = 'notitle_')
                    tmp.infos_names.append('icon')
                    tmp.infos_values.append(dir.thumb)
                    tmp.infos_names.append('url')
                    tmp.infos_values.append(curr_url)
                    if lItem != None:
                        for info_name in lItem.infos_names:
                            try:
                                info_idx = tmp.infos_names.index(info_name)
                            except:
                                tmp.infos_names.append(info_name)
                                tmp.infos_values.append(lItem.infos_values[lItem.infos_names.index(info_name)])
                    if dir.view.find('flat') != -1:
                        self.list.append(tmp)
                    else:
                        if f == None:
                            f = codecs.open(os.path.join(cacheDir, catfilename), 'w', 'utf-8')
                        tmp.infos_values[tmp.infos_names.index('title')] = smart_unicode(title) + ' (' + xbmc.getLocalizedString(30106) +') '
                        f.write('Title=' + tmp.infos_values[tmp.infos_names.index('title')] + '\n')
                        for info_name in tmp.infos_names:
                            if info_name != 'url' and info_name != 'title':
                                f.write(info_name + '=' + tmp.infos_values[tmp.infos_names.index(info_name)] + '\n')
                        f.write('Url=' + tmp.infos_values[tmp.infos_names.index('url')] + '\n')
                    oneFound = True
            if (oneFound and (dir.view.find('flat') == -1)):
                tmp = CListItem()
                tmp.infos_names.append('url')
                tmp.infos_values.append(catfilename)
                tmp.infos_names.append('title')
                tmp.infos_values.append(' ' + dir.title + ' ')
                tmp.infos_names.append('icon')
                tmp.infos_values.append(dir.thumb)
                if lItem != None:
                    for info_name in lItem.infos_names:
                        try:
                            info_idx = tmp.infos_names.index(info_name)
                        except:
                            tmp.infos_names.append(info_name)
                            tmp.infos_values.append(lItem.infos_values[lItem.infos_names.index(info_name)])
                self.list.append(tmp)
            if f != None:
                f.close()
        return 0

class Main:
    def __init__(self):
        self.pDialog = None
        self.urlList = []
        self.extensionList = []
        self.selectionList = []
        self.videoExtension = '.flv'
        self.currentlist = CCurrentList()
        try:
            self.date_format = xbmc.getRegion( 'datelong' ).replace( 'DDDD,', '' ).replace( 'MMMM', '%B' ).replace( 'D', '%d' ).replace( 'YYYY', '%Y' ).strip()
        except:
            self.date_format = '%B %d, %Y'

    def getDirectLink(self, orig_url):
        if self.currentlist.target_extension != '':
            self.videoExtension = '.' + self.currentlist.target_extension
        if (self.currentlist.catcher_url_build != '%s' and self.currentlist.target_url != ''):
            if (self.currentlist.catcher_data == ''):
                url = self.currentlist.catcher_url_build % (orig_url.replace('\r\n', '').replace('\n', ''))
                opener = urllib2.build_opener()
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                if (self.currentlist.catcher_reference != ''):
                    req.add_header(self.currentlist.catcher_reference, self.currentlist.catcher_content)
                urlfile = opener.open(req)
                fc = urlfile.read()
            else:
                data = self.currentlist.catcher_data % (orig_url.replace('\r\n', '').replace('\n', ''))
                req = urllib2.Request(self.currentlist.catcher_url_build, data)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                if (self.currentlist.catcher_reference != ''):
                    req.add_header(self.currentlist.catcher_reference, self.currentlist.catcher_content)
                response = urllib2.urlopen(req)
                fc = response.read()
            #f = open(os.path.join(cacheDir, 'catcher.html'), 'w')
            #f.write('<Titel>'+ orig_url + '</Title>\n\n')
            #f.write(fc)
            #f.close()
            resecurl = re.compile(self.currentlist.target_url, re.IGNORECASE + re.DOTALL + re.MULTILINE)
            urlsearch = resecurl.search(fc)
            try:
                match = urlsearch.group(1)
                if len(self.currentlist.source_list) > 0:
                    for source in self.currentlist.source_list:
                        resecurl = re.compile(source.rule, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                        urlsearch = resecurl.search(fc)
                        try:
                            source.url = urlsearch.group(1)
                            self.urlList.append(source.url)
                            self.extensionList.append(source.extension)
                            if source.quality == 'low':
                                self.selectionList.append(xbmc.getLocalizedString(30056) + ' (' + source.extension + ')')
                            elif source.quality == 'standard':
                                self.selectionList.append(xbmc.getLocalizedString(30057) + ' (' + source.extension + ')')
                            elif source.quality == 'high':
                                self.selectionList.append(xbmc.getLocalizedString(30058) + ' (' + source.extension + ')')
                        except:
                            source.url = ''
                    if len(self.urlList) > 0:
                        if len(self.urlList) == 1:
                            self.videoExtension = '.' + self.extensionList[0]
                            return self.urlList[0]
                        elif int(xbmcplugin.getSetting('video_type')) == 0:
                            dia = xbmcgui.Dialog()
                            selection = dia.select(xbmc.getLocalizedString(30055), self.selectionList)
                            self.videoExtension = '.' + self.extensionList[selection]
                            return self.urlList[selection]
                        elif int(xbmcplugin.getSetting('video_type')) == 1: # low
                            for source in self.currentlist.source_list:
                                if source.quality == 'low' and source.url != '':
                                    self.videoExtension = '.' + source.extension
                                    return source.url
                            for source in self.currentlist.source_list:
                                if source.quality == 'standard' and source.url != '':
                                    self.videoExtension = '.' + source.extension
                                    return source.url
                            for source in self.currentlist.source_list:
                                if source.quality == 'high' and source.url != '':
                                    self.videoExtension = '.' + source.extension
                                    return source.url
                        elif int(xbmcplugin.getSetting('video_type')) == 3: # high
                            for source in self.currentlist.source_list:
                                if source.quality == 'high' and source.url != '':
                                    self.videoExtension = '.' + source.extension
                                    return source.url
                            for source in self.currentlist.source_list:
                                if source.quality == 'standard' and source.url != '':
                                    self.videoExtension = '.' + source.extension
                                    return source.url
                            for source in self.currentlist.source_list:
                                if source.quality == 'low' and source.url != '':
                                    self.videoExtension = '.' + source.extension
                                    return source.url
                        elif int(xbmcplugin.getSetting('video_type')) == 2: # standard
                            for source in self.currentlist.source_list:
                                if source.quality == 'standard' and source.url != '':
                                    self.videoExtension = '.' + source.extension
                                    return source.url
                            for source in self.currentlist.source_list:
                                if source.quality == 'low' and source.url != '':
                                    self.videoExtension = '.' + source.extension
                                    return source.url
                            for source in self.currentlist.source_list:
                                if source.quality == 'high' and source.url != '':
                                    self.videoExtension = '.' + source.extension
                                    return source.url
                if self.currentlist.ext_target_url == '':
                    return match
            except:
                traceback.print_exc(file = sys.stdout)
                return ''
            if self.currentlist.ext_target_url == '':
                return match
            request = urllib2.Request(match)
            opener = urllib2.build_opener()
            req = urllib2.Request(match)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
            urlfile = opener.open(req)
            feed_data = urlfile.read(500)
            match = re.compile(self.currentlist.ext_target_url, re.IGNORECASE + re.DOTALL + re.MULTILINE)
            urlsearch = match.search(feed_data)
            try:
                return urlsearch.group(1)
            except:
                traceback.print_exc(file = sys.stdout)
                return ''
        elif (self.currentlist.catcher_url_build != '%s'):
            return self.currentlist.catcher_url_build % (orig_url.replace('\r\n', '').replace('\n', ''))
        else:
            return orig_url

    def playVideo(self, videoItem):
        if videoItem == None:
            return
        if videoItem.infos_values[videoItem.infos_names.index('url')] == '':
            return
        url = videoItem.infos_values[videoItem.infos_names.index('url')]
        try:
            icon = videoItem.infos_values[videoItem.infos_names.index('icon')]
        except:
            icon = os.path.join(imgDir, 'video.png')
        try:
            title = videoItem.infos_values[videoItem.infos_names.index('title')]
        except:
            title = 'No title'
        try:
            urllib.urlretrieve(icon, os.path.join(cacheDir, 'thumb.tbn'))
            icon = os.path.join(cacheDir, 'thumb.tbn')
        except:
            traceback.print_exc(file = sys.stdout)
            icon = os.path.join(imgDir, 'video.png')
        flv_file = url
        listitem = xbmcgui.ListItem(title, title, icon, icon)
        listitem.setInfo('video', {'Title':title})
        for video_info_name in videoItem.infos_names:
            try:
                listitem.setInfo(type = 'Video', infoLabels = {video_info_name: videoItem.infos_values[videoItem.infos_names.index(video_info_name)]})
            except:
                pass
        if self.currentlist.video_action.find('nodownload') == -1:
            if (xbmcplugin.getSetting('download') == 'true'):
                self.pDialog = xbmcgui.DialogProgress()
                self.pDialog.create('VideoMonkey', xbmc.getLocalizedString(30050), xbmc.getLocalizedString(30051))
                flv_file = self.downloadMovie(url, title)
                self.pDialog.close()
                if (flv_file == None):
                    dialog = xbmcgui.Dialog()
                    dialog.ok('VideoMonkey Info', xbmc.getLocalizedString(30053))
            elif (xbmcplugin.getSetting('download') == 'false' and xbmcplugin.getSetting('download_ask') == 'true'):
                dia = xbmcgui.Dialog()
                if dia.yesno('', xbmc.getLocalizedString(30052)):
                    self.pDialog = xbmcgui.DialogProgress()
                    self.pDialog.create('VideoMonkey', xbmc.getLocalizedString(30050), xbmc.getLocalizedString(30051))
                    flv_file = self.downloadMovie(url, title)
                    self.pDialog.close()
                    if (flv_file == None):
                        dialog = xbmcgui.Dialog()
                        dialog.ok('VideoMonkey Info', xbmc.getLocalizedString(30053))
        else:
            flv_file = None

        player_type = {0:xbmc.PLAYER_CORE_AUTO, 1:xbmc.PLAYER_CORE_MPLAYER, 2:xbmc.PLAYER_CORE_DVDPLAYER}[int(xbmcplugin.getSetting('player_type'))]
        if (self.currentlist.force_player == 'auto'):
            player_type = xbmc.PLAYER_CORE_AUTO
        elif (self.currentlist.force_player == 'mplayer'):
            player_type = xbmc.PLAYER_CORE_MPLAYER
        elif (self.currentlist.force_player == 'dvdplayer'):
            player_type = xbmc.PLAYER_CORE_DVDPLAYER

        if (flv_file != None and os.path.isfile(flv_file)):
            xbmc.Player(player_type).play(str(flv_file), listitem)
        else:
            xbmc.Player(player_type).play(str(url), listitem)
        xbmc.sleep(200)

    def downloadMovie(self, url, title):
        filepath = ''
        title = repr(title)
        try:
            filepath = xbmc.translatePath(os.path.join(xbmcplugin.getSetting('download_Path'), title + self.videoExtension))
            urllib.urlretrieve(url, filepath, self._report_hook)
        except:
            traceback.print_exc(file = sys.stdout)
            if (os.path.isfile(filepath)):
                try:
                    os.remove(filepath)
                except:
                    traceback.print_exc(file = sys.stdout)
            filepath = xbmc.translatePath(os.path.join(xbmcplugin.getSetting('download_Path'), self.currentlist.randomFilename(dir = xbmcplugin.getSetting('download_Path'), suffix = self.videoExtension)))
            try:
                urllib.urlretrieve(url, filepath, self._report_hook)
            except:
                traceback.print_exc(file = sys.stdout)
                if (os.path.isfile(filepath)):
                    try:
                        os.remove(filepath)
                    except:
                        traceback.print_exc(file = sys.stdout)
                return None
        return filepath

    def _report_hook(self, count, blocksize, totalsize):
        percent = int(float(count * blocksize * 100) / totalsize)
        self.pDialog.update(percent, xbmc.getLocalizedString(30050), xbmc.getLocalizedString(30051))
        if (self.pDialog.iscanceled()):raise

    def TargetFormatter(self, url, cfg_file): # Site specific target url handling
        #if cfg_file == 'metacafe.com.cfg' or cfg_file == 'metacafe.adult.com.cfg': # Metacafe
        #    return url.replace('[', '%5B').replace(']', '%5D').replace(' ', '%20')
        if cfg_file == 'myspass.de.cfg': # Myspass
            return unquote_safe(url)
        elif cfg_file == 'pornhub.com.cfg': # Pornhub
            return urllib.unquote(url)
        elif cfg_file == 'zdf.de.cfg': # ZDF mediathek
            request = urllib2.Request(url)
            opener = urllib2.build_opener()
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
            urlfile=opener.open(req)
            feed_data = urlfile.read()
            match=re.compile('href=\"([^\"]+)\"', re.IGNORECASE)
            urlsearch=match.search(feed_data)
            try:
                url=urlsearch.group(1)
            except:
                traceback.print_exc(file = sys.stdout)
                url=''
        elif cfg_file == 'arteplus7.cfg' or cfg_file == 'arteplus7.de.cfg' or cfg_file == 'arteplus7.fr.cfg': # arte+7
            freq = urllib.urlopen(url)
            feed_data = freq.read()
            freq.close()
            match = re.search(r'availableFormats\[\d]\["format"] = "WMV";\n    availableFormats\[\d]\["quality"] = "HQ";\n    availableFormats\[\d]\["url"] = "(.+?)\?obj', feed_data)
            if match:
                request = urllib2.Request(match.group(1))
                opener = urllib2.build_opener()
                req = urllib2.Request(match.group(1))
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                urlfile=opener.open(req)
                feed_data = urlfile.read(500)
                match=re.compile('href=\"([^\"]+)\"', re.IGNORECASE)
                urlsearch=match.search(feed_data)
                try:
                    url=urlsearch.group(1)
                except:
                    traceback.print_exc(file = sys.stdout)
                    url=''
            else:
                url = ''
        elif cfg_file == 'youporn.com.cfg': # YouPorn
            request = urllib2.Request(url)
            opener = urllib2.build_opener()
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
            req.add_header('Cookie','age_check=1')
            urlfile=opener.open(req)
            feed_data=urlfile.read()
            resecurl=re.compile('<p><a\ href="([^"]+)">FLV[^<]+</a>')
            urlsearch=resecurl.search(feed_data)
            try:
                url=urlsearch.group(1)
            except:
                traceback.print_exc(file = sys.stdout)
                url=''
        return url

    def parseView(self, url):
        lItem = self.currentlist.decodeUrl(url)
        url = lItem.infos_values[lItem.infos_names.index('url')]
        ext = self.currentlist.getFileExtension(url)
        if ext == 'cfg' or ext == 'list':
            result = self.currentlist.loadLocal(url, lItem = lItem)
        elif ext == 'add':
            self.currentlist.addItem(url[:len(url) - 4])
            return -2
        elif ext == 'remove':
            dia = xbmcgui.Dialog()
            if dia.yesno('', xbmc.getLocalizedString(30054)):
                self.currentlist.removeItem(url[:len(url) - 7])
                xbmc.executebuiltin('Container.Refresh')
            return -2
        elif ext == 'videomonkey' or ext == 'dwnldmonkey':
            url = url[:len(url) - 12]
            lItem.infos_values[lItem.infos_names.index('url')] = url
            cfg_file = lItem.infos_values[lItem.infos_names.index('cfg')]
            self.currentlist.loadLocal(cfg_file, False, lItem)
            lItem.infos_values[lItem.infos_names.index('url')] = self.getDirectLink(lItem.infos_values[lItem.infos_names.index('url')])
            lItem.infos_values[lItem.infos_names.index('url')] = self.TargetFormatter(lItem.infos_values[lItem.infos_names.index('url')], cfg_file)
            if ext == 'videomonkey':
                result = self.playVideo(lItem)
            else:
                self.pDialog = xbmcgui.DialogProgress()
                self.pDialog.create('VideoMonkey', xbmc.getLocalizedString(30050), xbmc.getLocalizedString(30051))
                self.downloadMovie(lItem.infos_values[lItem.infos_names.index('url')], lItem.infos_values[lItem.infos_names.index('title')])
                self.pDialog.close()
            return -2
        else:
            result = self.currentlist.loadRemote(lItem.infos_values[lItem.infos_names.index('url')], lItem = lItem)

        xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_LABEL)
        if self.currentlist.sort_method == 'label':
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_LABEL)
        if self.currentlist.sort_method == 'size':
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_SIZE)
        if self.currentlist.sort_method == 'duration':
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_DURATION)
        if self.currentlist.sort_method == 'genre':
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_GENRE)
        if self.currentlist.sort_method == 'rating':
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_VIDEO_RATING)
        if self.currentlist.sort_method == 'date':
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_DATE)

        if self.currentlist.video_action.find('play') != -1 and self.currentlist.videoCount() == 1:
            url = self.currentlist.codeUrl(self.currentlist.getVideo(), 'videomonkey')
            result = self.parseView(url)
        else:
            for m in self.currentlist.list:
                m_url = m.infos_values[m.infos_names.index('url')]
                try:
                    m_type = m.infos_values[m.infos_names.index('type')]
                except:
                    m_type = u'rss'
                m_icon = m.infos_values[m.infos_names.index('icon')]
                m_title = clean_title(m.infos_values[m.infos_names.index('title')])
                if (m_type == u'rss') or (m_type == u'search') or (m_type == u'adult_rss' and xbmcplugin.getSetting('no_adult') == 'false'):
                    self.addDir(m_title, self.currentlist.codeUrl(m), m_icon, len(self.currentlist.list), m)
                elif (m_type == u'video') or (m_type == u'adult_video' and xbmcplugin.getSetting('no_adult') == 'false'):
                    self.addDir(m_title, self.currentlist.codeUrl(m, 'videomonkey'), m_icon, len(self.currentlist.list), m)
                elif (m_type == u'live') or (m_type == u'adult_live' and xbmcplugin.getSetting('no_adult') == 'false'):
                    self.addLink(m_title, m_url, m_icon, len(self.currentlist.list), m)
        return result

    def addLink(self, title, url, icon, totalItems, lItem):
        u = sys.argv[0] + '?url=' + url
        liz = xbmcgui.ListItem(title, title, icon, icon)
        liz.setInfo(type = 'Video', infoLabels = {'Title':title})
        if self.currentlist.action.find('add') != -1:
            action = 'XBMC.RunPlugin(%s.add)' % (u)
            try:
                liz.addContextMenuItems([(xbmc.getLocalizedString(30010), action)])
            except:
                pass
        if self.currentlist.action.find('remove') != -1:
            action = 'XBMC.RunPlugin(%s.remove)' % (u)
            try:
                liz.addContextMenuItems([(xbmc.getLocalizedString(30011), action)])
            except:
                pass
        for video_info_name in lItem.infos_names:
            try:
                if video_info_name != 'url' and video_info_name != 'title' and video_info_name != 'icon' and video_info_name != 'type':
                    liz.setInfo(type = 'Video', infoLabels = {capitalize(video_info_name): lItem.infos_values[lItem.infos_names.index(video_info_name)]})
            except:
                pass
        xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = url, listitem = liz, totalItems = totalItems)

    def addDir(self, title, url, icon, totalItems, lItem):
        u = sys.argv[0] + '?url=' + url
        liz = xbmcgui.ListItem(title, title, icon, icon)
        if self.currentlist.video_action.find('nodownload') == -1:
            action = 'XBMC.RunPlugin(%s.dwnldmonkey)' % (u[:len(u)-12])
            try:
                liz.addContextMenuItems([(xbmc.getLocalizedString(30007), action)])
            except:
                pass
        try:
            if lItem.infos_values[lItem.infos_names.index('Related')] != '': # to-do: build a new item
                action = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?url=' + lItem.infos_values[lItem.infos_names.index('Related')])
                liz.addContextMenuItems([(xbmc.getLocalizedString(30117), action)])
        except:
            pass
        if self.currentlist.action.find('add') != -1:
            action = 'XBMC.RunPlugin(%s.add)' % (u)
            try:
                liz.addContextMenuItems([(xbmc.getLocalizedString(30010), action)])
            except:
                pass
        if self.currentlist.action.find('remove') != -1:
            action = 'XBMC.RunPlugin(%s.remove)' % (u)
            try:
                liz.addContextMenuItems([(xbmc.getLocalizedString(30011), action)])
            except:
                pass
        for video_info_name in lItem.infos_names:
            try:
                if video_info_name != 'url' and video_info_name != 'title' and video_info_name != 'icon' and video_info_name != 'type':
                    liz.setInfo(type = 'Video', infoLabels = {capitalize(video_info_name): lItem.infos_values[lItem.infos_names.index(video_info_name)]})
            except:
                pass
        xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = True, totalItems = totalItems)

    def purgeCache(self):
        for root, dirs, files in os.walk(cacheDir , topdown = False):
            for name in files:
                os.remove(os.path.join(root, name))

    def run(self):
        try:
            self.handle = int(sys.argv[1])
            try:
                xbmcplugin.setPluginFanart(self.handle, os.path.join(imgDir, 'fanart.png'))
            except:
                traceback.print_exc(file = sys.stdout)
            paramstring = sys.argv[2]
            if len(paramstring) <= 2:
                if not os.path.exists(cacheDir):
                    os.mkdir(cacheDir)
                if not os.path.exists(xbmcplugin.getSetting('download_Path')):
                    try:
                        os.mkdir(xbmcplugin.getSetting('download_Path'))
                    except:
                        traceback.print_exc(file = sys.stdout)
                self.purgeCache()
                result = self.parseView('sites.list')
                del self.currentlist.list[:]
                try:
                    self.parseView('entry.list')
                except:
                    pass
                try:
                    xbmcplugin.endOfDirectory(handle = int(sys.argv[1]), cacheToDisc = False)
                except:
                    xbmcplugin.endOfDirectory(handle = int(sys.argv[1]))
            else:
                params = sys.argv[2]
                currentView = params[5:]
                print(u' ==> ' + repr(currentView))
                if self.parseView(currentView) == 0:
                    xbmcplugin.endOfDirectory(int(sys.argv[1]))
        except Exception, e:
            traceback.print_exc(file = sys.stdout)
            dialog = xbmcgui.Dialog()
            dialog.ok('VideoMonkey Error', 'Error running VideoMonkey.\n\nReason:\n' + str(e))

win = Main()
win.run()
