# VideoMonkey by sfaxman

from string import *
import xbmcplugin
import sys, os.path
import urllib,urllib2
import re, random, string
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import shutil
import codecs
import cookielib
import htmlentitydefs

rootDir = os.getcwd()
if rootDir[-1] == ';':rootDir = rootDir[0:-1]
cacheDir = os.path.join(rootDir, 'cache')
resDir = os.path.join(rootDir, 'resources')
imgDir = os.path.join(resDir, 'images')
libDir = os.path.join(resDir, 'libs')
sys.path.append(libDir)

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
    'Epsilon':  u'\u0395', # greek capital letter epsilon, U+0395'
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

#entitydefs2 = {
#    '$':    '%24',
#    '&':    '%26',
#    '+':    '%2B',
#    ',':    '%2C',
#    '/':    '%2F',
#    ':':    '%3A',
#    ';':    '%3B',
#    '=':    '%3D',
#    '?':    '%3F',
#    '@':    '%40',
#    ' ':    '%20',
#    '"':    '%22',
#    '<':    '%3C',
#    '>':    '%3E',
#    '#':    '%23',
#    '%':    '%25',
#    '{':    '%7B',
#    '}':    '%7D',
#    '|':    '%7C',
#    '\\':   '%5C',
#    '^':    '%5E',
#    '~':    '%7E',
#    '[':    '%5B',
#    ']':    '%5D',
#    '`':    '%60'
#}

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

def clean4(s): # remove multiple '?'
    idx = s.rfind('?')
    if idx != -1:
        if s[:idx].rfind('?') != -1:
            s[idx] = '&'
            s = clean4(s)
    return s

def decode(s):
    if not s:
        return ''
    try:
        dic=htmlentitydefs.name2codepoint
        for key in dic.keys():
            entity='&' + key + ';'
            s=s.replace(entity, unichr(dic[key]))
    except:
        traceback.print_exc(file = sys.stdout)
    return s

#def XXXXXX(s): # XXXXXX
#    if not s:
#        return ''
#    for key, value in entitydefs2.iteritems():
#        s = s.replace(key, value)
#    return s;

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

def clean_name(s):
    if not s:
        return ''
    try:
        s = clean1(clean2(clean3(smart_unicode(s)))).replace('\r\n', '').replace('\n', '')
    except:
        traceback.print_exc(file = sys.stdout)
    return s

def clean_url(s):
    if not s:
        return ''
    try:
        s = clean4(s)
    except:
        traceback.print_exc(file = sys.stdout)
    return s

class CListItem:
    def __init__(self):
        self.name = ''
        self.type = ''
        self.thumb = os.path.join(imgDir, 'video.png')
        self.url = ''
        # to-do: date, duration, size...

class CVideoItem:
    def __init__(self):
        self.url_img_title = ''
        self.order = ''
        self.img = ''
        self.img_build = '%s'
        self.title = ''
        self.url_build = '%s'

class CNextItem:
    def __init__(self):
        self.url = ''
        self.url_build = '%s'
        self.thumb = os.path.join(imgDir, 'next.png')

class CDirItem:
    def __init__(self):
        self.name = ''
        self.type = ''
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
        self.version = '0'
        self.title = ''
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
        self.catcher_data = ''
        self.catcher_reference = ''
        self.catcher_content = ''
        self.catcher_url_build = '%s'
        self.search_url_build = '%s'
        self.search_thumb = ''
        self.list = []
        self.video_list = []
        self.dir_list = []
        self.next_list = []

    def getKeyboard(self, default = "", heading = "", hidden = False):
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

    def random_filename(self, dir = cacheDir, chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', length = 8, prefix = '', suffix = '', attempts = 1000):
        for attempt in range(attempts):
            filename = ''.join([random.choice(chars) for i in range(length)])
            filename = prefix + filename + suffix
            if not os.path.exists(os.path.join(dir, filename)):
                return filename

    def loadCatcher(self, name):
        f = codecs.open(os.path.join(resDir, 'catcher.list'), 'r', 'utf-8')
        data = f.read()
        data = data.replace('\r\n', '\n')
        data = data.split('\n')
        f.close()

        catcher_found = False
        for m in data:
            if m and m[0] != '#':
                index = m.find('=')
                if index != -1:
                    key = m[:index]
                    value = m[index+1:]
                    if key == 'version':
                        if value != '1':
                            return -1
                    elif key == 'name':
                        if name == value:
                            catcher_found = True
                    elif key == 'data' and catcher_found == True:
                        self.catcher_data = value
                    elif key == 'header' and catcher_found == True:
                        index = value.find('|')
                        self.catcher_reference = value[:index]
                        self.catcher_content = value[index+1:]
                    elif key == 'url' and catcher_found == True:
                        self.catcher_url_build = value
                    elif key == 'target' and catcher_found == True:
                        self.target_url = value
                        return 0
        return -1

    def loadLocal(self, filename, recursive = True):
        try:
            f = codecs.open(os.path.join(resDir, filename.replace('|', '%')), 'r', 'utf-8')
            data = f.read()
            data = data.replace('\r\n', '\n')
            data = data.split('\n')
            f.close()
        except:
            try:
                f = codecs.open(os.path.join(cacheDir, filename.replace('|', '%')), 'r', 'utf-8')
                data = f.read()
                data = data.replace('\r\n', '\n')
                data = data.split('\n')
                f.close()
            except:
                traceback.print_exc(file = sys.stdout)
                return -2

        self.cfg_name = filename
        del self.list[:]
        for m in data:
            if m and m[0] != '#':
                index = m.find('=')
                if index != -1:
                    key = m[:index]
                    value = m[index+1:]
                    if key == 'version':
                        self.version = value
                        if self.version != '1':
                            return -1
                    elif key == 'title':
                        self.title = value
                    elif key == 'start_url':
                        self.start_url = value
                    elif key == 'force_player':
                        self.force_player = value
                    elif key == 'sort_method':
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
                                    return self.loadLocal(forward_cfg, recursive)
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
                                return ret
                        except:
                            traceback.print_exc(file = sys.stdout)
                            return -2
                    elif key == 'user':
                        self.user = value
                    elif key == 'password':
                        self.password = value
                    elif key == 'video_action':
                        self.video_action = value
                    elif key == 'header':
                        index = value.find('|')
                        self.reference = value[:index]
                        self.content = value[index+1:]
                    elif key == 'video_url_img_title':
                        video_tmp = CVideoItem()
                        video_tmp.url_img_title = value
                    elif key == 'video_order':
                        video_tmp.order = value
                    elif key == 'video_img':
                        video_tmp.img = value
                    elif key == 'video_img_build':
                        video_tmp.img_build = value
                    elif key == 'video_title':
                        video_tmp.title = value
                    elif key == 'video_url_build':
                        video_tmp.url_build = value
                        self.video_list.append(video_tmp)
                    elif key == 'next_url':
                        next_tmp = CNextItem()
                        next_tmp.url = value
                    elif key == 'next_url_build':
                        next_tmp.url_build = value
                    elif key == 'next_thumb':
                        next_tmp.thumb = value
                        index = value.find('|')
                        if value[:index] == 'video.monkey.image':
                            next_tmp.thumb = os.path.join(imgDir, value[index+1:])
                        self.next_list.append(next_tmp)
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
                    elif key == 'search_url_build':
                        self.search_url_build = value
                    elif key == 'search_thumb':
                        self.search_thumb = value
                        index = value.find('|')
                        if value[:index] == 'video.monkey.image':
                            self.search_thumb = os.path.join(imgDir, value[index+1:])
                    elif key == 'dir_name':
                        dir_tmp = CDirItem()
                        dir_tmp.name = value
                        index = value.find('|')
                        if value[:index] == 'video.monkey.locale':
                            dir_tmp.name = xbmc.getLocalizedString(int(value[index+1:]))
                    elif key == 'dir_url':
                        dir_tmp.url = value
                    elif key == 'dir_type':
                        dir_tmp.type = value
                    elif key == 'dir_url_action':
                        dir_tmp.url_action = value
                    elif key == 'dir_url_build':
                        dir_tmp.url_build = value
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
                        self.dir_list.append(dir_tmp)
                    elif key == 'name':
                        tmp = CListItem()
                        tmp.name = value
                        index = value.find('|')
                        if value[:index] == 'video.monkey.locale':
                            tmp.name = ' ' + xbmc.getLocalizedString(int(value[index+1:])) + ' '
                    elif key == 'type':
                        tmp.type = value
                        if (recursive and tmp.type == 'once'):
                            tmp.type = 'rss'
                    elif key == 'thumb':
                        tmp.thumb = value
                        index = value.find('|')
                        if value[:index] == 'video.monkey.image':
                            tmp.thumb = os.path.join(imgDir, value[index+1:])
                    elif key == 'url':
                        tmp.url = value
                        self.list.append(tmp)

        if (recursive and self.start_url != ''):
            result = self.loadRemote(self.start_url, False)
        if (self.search_url_build != '%s'):
            tmp = CListItem()
            tmp.name = ' ' + xbmc.getLocalizedString(30102) + ' '
            tmp.type = 'rss'
            tmp.thumb = self.search_thumb
            tmp.url = filename + '|search'
            self.list.append(tmp)
        return 0

    def loadRemote(self, filename, recursive = True):
        try:
            curr_url = filename
            if (recursive):
                splitvalues = filename.split('|')
                if ((len(splitvalues)) > 1):
                    ext = self.getFileExtension(splitvalues[0])
                    if (ext == 'cfg'):
                        self.loadLocal(splitvalues[0], False)
                        self.cfg_name = splitvalues[0]
                        curr_url = splitvalues[1]
                    if (splitvalues[1] == 'search'):
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
                        curr_url = self.search_url_build % (search_phrase)
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
            return -2

        # Find video items
        for video in self.video_list:
            if (video.url_img_title != ''):
                revid = re.compile(video.url_img_title, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                for pot_url, pot_img, pot_name in revid.findall(data):
                    if (video.order != ''):
                        u_index = video.order.find('U')
                        i_index = video.order.find('I')
                        if (u_index == 0):
                            url = pot_url
                            if (i_index == 1):
                                img = pot_img
                                name = pot_name
                            else:
                                img = pot_name
                                name = pot_img
                        elif (u_index == 1):
                            url = pot_img
                            if (i_index == 0):
                                img = pot_url
                                name = pot_name
                            else:
                                img = pot_name
                                name = pot_url
                        else:
                            url = pot_name
                            if (i_index == 0):
                                img = pot_url
                                name = pot_img
                            else:
                                img = pot_img
                                name = pot_url
                    else:
                        url = pot_url
                        img = pot_img
                        name = pot_name
                    url = decode(url)
                    img = decode(img)
                    name = clean_name(name)
                    tmp = CListItem()
                    tmp.type = 'video'
                    img = video.img_build % (img)
                    if (img == ''):
                        img = os.path.join(imgDir, 'video.png')
                    try:
                        tmp.url = smart_unicode(self.cfg_name + '|' + (video.url_build % (url)))
                    except:
                        tmp.url = smart_unicode(self.cfg_name + '|' + (video.url_build % (smart_unicode(url))))
                    if (video.img != ''):
                        try:
                            img_catcher = video.img % (url)
                        except:
                            img_catcher = video.img
                        reimg = re.compile(img_catcher, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                        imgsearch = reimg.search(data)
                        try:
                            img = video.img_build % (decode(imgsearch.group(1)))
                        except:
                            traceback.print_exc(file = sys.stdout)
                            img = os.path.join(imgDir, 'video.png')
                    tmp.thumb = img
                    if (video.title != ''):
                        try:
                            title_catcher = video.title % (url)
                        except:
                            title_catcher = video.title
                        retitle = re.compile(title_catcher, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                        titlesearch = retitle.search(data)
                        try:
                            name = titlesearch.group(1)
                        except:
                            traceback.print_exc(file = sys.stdout)
                            name = self.random_filename(prefix = 'noname_')
                    tmp.name = name.lstrip().rstrip()
                    if (len(tmp.name) == 0):
                        tmp.name = self.random_filename(prefix = 'noname_')
                    self.list.append(tmp)
        # Find category items
        for dir in self.dir_list:
            oneFound = False
            catfilename = self.random_filename(prefix=(self.cfg_name + '%'), suffix = '.list')
            f = None
            if (dir.url != ''):
                recat = re.compile(dir.url, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                for url, name in recat.findall(data):
                    url = decode(url)
                    name = clean_name(name.lstrip().rstrip())
                    if (dir.img != ''):
                        img_catcher = dir.img % (url)
                        reimg = re.compile(img_catcher, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                        imgsearch = reimg.search(data)
                        try:
                            dir.thumb = dir.img_build % (decode(imgsearch.group(1)))
                        except:
                            traceback.print_exc(file = sys.stdout)
                    try:
                        url = dir.url_build % (url)
                    except:
                        url = dir.url_build % (smart_unicode(url))
                    if dir.url_action.find('append') != -1:
                        if curr_url[len(curr_url) - 1] == '?':
                            url = curr_url + url
                        else:
                            url = curr_url + '&' + url
                    if dir.type.find('flat') != -1:
                        tmp = CListItem()
                        if dir.type.find('space') != -1:
                            tmp.name = ' ' + name + ' '
                        else:
                            tmp.name = name
                        if (len(tmp.name) == 0):
                            tmp.name = self.random_filename(prefix = 'noname_')
                        tmp.type = 'rss'
                        tmp.thumb = dir.thumb
                        tmp.url = self.cfg_name + '|' + url
                        self.list.append(tmp)
                    else:
                        if f == None:
                            f = codecs.open(os.path.join(cacheDir, catfilename), 'w', 'utf-8')
                        f.write('name= ' + smart_unicode(name) + ' \n')
                        f.write('type=rss\n')
                        f.write('thumb=' + smart_unicode(dir.thumb) + '\n')
                        f.write('url=' + smart_unicode(self.cfg_name) + '|' + smart_unicode(url) + '\n')
                    oneFound = True
            if (dir.curr_url != ''):
                recat = re.compile(dir.curr_url, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                for name in recat.findall(data):
                    name = clean_name(name.lstrip().rstrip())
                    if (dir.img != ''):
                        img_catcher = dir.curr_img % (name)
                        reimg = re.compile(img_catcher, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                        imgsearch = reimg.search(data)
                        try:
                            dir.thumb = dir.curr_img_build % (decode(imgsearch.group(1)))
                        except:
                            traceback.print_exc(file = sys.stdout)
                    if dir.type.find('flat') != -1:
                        tmp = CListItem()
                        if dir.type.find('space') != -1:
                            tmp.name = ' ' + name + ' '
                        else:
                            tmp.name = name
                        if (len(tmp.name) == 0):
                            tmp.name = self.random_filename(prefix = 'noname_')
                        tmp.type = 'rss'
                        tmp.thumb = dir.thumb
                        tmp.url = self.cfg_name + '|' + curr_url
                        self.list.append(tmp)
                    else:
                        if f == None:
                            f = codecs.open(os.path.join(cacheDir, catfilename), 'w', 'utf-8')
                        f.write('name= ' + smart_unicode(name) + ' (' + xbmc.getLocalizedString(30106) +') \n')
                        f.write('type=rss\n')
                        f.write('thumb=' + smart_unicode(dir.thumb) + '\n')
                        f.write('url=' + smart_unicode(self.cfg_name + '|' + curr_url) + '\n')
                    OneFound = True
            if (oneFound and (dir.type.find('flat') == -1)):
                tmp = CListItem()
                tmp.name = ' ' + dir.name + ' '
                tmp.type = 'rss'
                tmp.thumb = dir.thumb
                tmp.url = catfilename
                self.list.append(tmp)
            if f != None:
                f.close()
        # Find next page item
        found = False
        for next in self.next_list:
            if (not found):
                renext = re.compile(next.url, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                for url in renext.findall(data):
                    url = decode(url)
                    if (not found):
                        tmp = CListItem()
                        tmp.name = ' ' + xbmc.getLocalizedString(30103) + ' '
                        tmp.type = 'rss'
                        tmp.thumb = next.thumb
                        try:
                            tmp.url = smart_unicode(self.cfg_name + '|' + (next.url_build % (url)))
                        except:
                            tmp.url = smart_unicode(self.cfg_name + '|' + (next.url_build % (smart_unicode(url))))
                        self.list.append(tmp)
                        found = True
        return 0

class Main:
    def __init__(self):
        self.pDialog = None
        self.currentlist = CCurrentList()

    def getDirectLink(self, orig_url):
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
                return urlsearch.group(1)
            except:
                traceback.print_exc(file = sys.stdout)
                return ''
        elif (self.currentlist.catcher_url_build != '%s'):
            return self.currentlist.catcher_url_build % (orig_url.replace('\r\n', '').replace('\n', ''))
        else:
            return orig_url

    def playVideo(self, url):
        cfg_pos = url.find('|')
        cfg_file = url[:cfg_pos]
        self.currentlist.loadLocal(cfg_file, False)
        sep_pos = url.rfind('|')
        icon = url[sep_pos + 1:len(url) - 12]
        url = url[cfg_pos+1:sep_pos]
        sep_pos = url.rfind('|')
        title = url[sep_pos + 1:]
        vidURL = self.getDirectLink(url[:sep_pos])
        if vidURL == '':
            return
        vidURL = clean_url(self.siteSpecificUrlTarget(vidURL, cfg_file))
        title = clean_url(self.siteSpecificName(title, cfg_file))
        try:
            urllib.urlretrieve(icon, os.path.join(cacheDir, 'thumb.tbn'))
            icon = os.path.join(cacheDir, 'thumb.tbn')
        except:
            traceback.print_exc(file = sys.stdout)
            icon = os.path.join(imgDir, 'video.png')
        flv_file = vidURL
        listitem = xbmcgui.ListItem(title, title, icon, icon)
        listitem.setInfo("video", {"Title":title})
        if self.currentlist.video_action.find('nodownload') == -1:
            if (xbmcplugin.getSetting("download") == "true"):
                self.pDialog = xbmcgui.DialogProgress()
                self.pDialog.create("VideoMonkey", xbmc.getLocalizedString(30050), xbmc.getLocalizedString(30051))
                flv_file = self.downloadMovie(vidURL, title)
                self.pDialog.close()
                if (flv_file == None):
                    dialog = xbmcgui.Dialog()
                    dialog.ok("VideoMonkey Info", xbmc.getLocalizedString(30053))
            elif (xbmcplugin.getSetting("download") == "false" and xbmcplugin.getSetting("download_ask") == "true"):
                dia = xbmcgui.Dialog()
                if dia.yesno('', xbmc.getLocalizedString(30052)):
                    self.pDialog = xbmcgui.DialogProgress()
                    self.pDialog.create("VideoMonkey", xbmc.getLocalizedString(30050), xbmc.getLocalizedString(30051))
                    flv_file = self.downloadMovie(vidURL, title)
                    self.pDialog.close()
                    if (flv_file == None):
                        dialog = xbmcgui.Dialog()
                        dialog.ok("VideoMonkey Info", xbmc.getLocalizedString(30053))
        else:
            flv_file = None

        player_type = {0:xbmc.PLAYER_CORE_AUTO, 1:xbmc.PLAYER_CORE_MPLAYER, 2:xbmc.PLAYER_CORE_DVDPLAYER}[int(xbmcplugin.getSetting("player_type"))]
        if (self.currentlist.force_player == 'auto'):
            player_type = xbmc.PLAYER_CORE_AUTO
        elif (self.currentlist.force_player == 'mplayer'):
            player_type = xbmc.PLAYER_CORE_MPLAYER
        elif (self.currentlist.force_player == 'dvdplayer'):
            player_type = xbmc.PLAYER_CORE_DVDPLAYER

        if (flv_file != None and os.path.isfile(flv_file)):
            xbmc.Player(player_type).play(vidURL, listitem)
        else:
            xbmc.Player(player_type).play(vidURL, listitem)
        xbmc.sleep(200)

    def downloadMovie(self, url, title):
        filepath = xbmc.translatePath(os.path.join(xbmcplugin.getSetting("download_Path"), title + '.flv'))
        try:
            urllib.urlretrieve(url, filepath, self._report_hook)
        except:
            traceback.print_exc(file = sys.stdout)
            if (os.path.isfile(filepath)):
                try:
                    os.remove(filepath)
                except:
                    traceback.print_exc(file = sys.stdout)
            filepath = xbmc.translatePath(os.path.join(xbmcplugin.getSetting("download_Path"), self.currentlist.random_filename(dir = xbmcplugin.getSetting("download_Path"), suffix = '.flv')))
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

    def siteSpecificUrlTarget(self, url, cfg_file): # Site specific target url handling
        if cfg_file == 'metacafe.com.cfg' or cfg_file == 'metacafe.adult.com.cfg': # Metacafe
            return url.replace('[', '%5B').replace(']', '%5D').replace(' ', '%20')
        elif cfg_file == 'tu.tv.cfg': # TUtv
            return urllib.unquote(urllib.unquote(url))
        if cfg_file == 'zdf.de.cfg': # ZDF mediathek
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
        elif cfg_file == 'arteplus7.cfg' or cfg_file == 'arteplus7.de.cfg'or cfg_file == 'arteplus7.fr.cfg': # arte+7
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

    def siteSpecificName(self, name, cfg_file): # Site specific name handling
        if cfg_file == 'arteplus7.cfg' or cfg_file == 'arteplus7.de.cfg'or cfg_file == 'arteplus7.fr.cfg': # arte+7
            return name.replace('</index>', ' - ').replace('        <bigTitle>', '').replace('\n', '')
        return name

    def parseView(self, url):
        ext = self.currentlist.getFileExtension(url)
        if ext == 'cfg' or ext == 'list':
            result = self.currentlist.loadLocal(url)
        elif ext == 'videomonkey':
            result = self.playVideo(url)
            return
        else:
            result = self.currentlist.loadRemote(url)

        if result == -1:
            dialog = xbmcgui.Dialog()
            dialog.ok("Error", "Invalid directory version.")
        elif result == -2:
            dialog = xbmcgui.Dialog()
            dialog.ok("Error", "Directory could not be opened.")

        if self.currentlist.sort_method == 'label':
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_LABEL)
        elif self.currentlist.sort_method == 'size':
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_SIZE)
        elif self.currentlist.sort_method == 'duration':
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_DURATION)
        elif self.currentlist.sort_method == 'genre':
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_GENRE)
        elif self.currentlist.sort_method == 'rating':
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_VIDEO_RATING)
        elif self.currentlist.sort_method == 'date':
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_DATE)
        else:
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = xbmcplugin.SORT_METHOD_LABEL)

        if self.currentlist.video_action.find('play') != -1 and len(self.currentlist.list) == 1 and self.currentlist.list[0].type == u'video':
            result = self.parseView(self.currentlist.list[0].url + '|' + self.currentlist.list[0].name + '|' + self.currentlist.list[0].thumb + '.videomonkey')
        elif self.currentlist.video_action.find('play') != -1 and self.currentlist.search_url_build != '' and len(self.currentlist.list) == 2 and self.currentlist.list[1].type == u'video':
            result = self.parseView(self.currentlist.list[1].url + '|' + self.currentlist.list[1].name + '|' + self.currentlist.list[1].thumb + '.videomonkey')
        else:
            for m in self.currentlist.list:
                if (m.type == u'rss') or (m.type == u'adult_rss' and xbmcplugin.getSetting("no_adult") == 'false'):
                    self.addDir(self.siteSpecificName(m.name, self.currentlist.cfg_name), clean_url(m.url), m.thumb, len(self.currentlist.list))
                elif (m.type == u'live') or (m.type == u'adult_live' and xbmcplugin.getSetting("no_adult") == 'false'):
                    self.addLink(m.name, m.url, m.thumb, len(self.currentlist.list))
                elif (m.type == u'video') or (m.type == u'adult_video' and xbmcplugin.getSetting("no_adult") == 'false'):
                    self.addDir(self.siteSpecificName(m.name, self.currentlist.cfg_name), clean_url(m.url) + '|' + m.name + '|' + m.thumb + '.videomonkey', m.thumb, len(self.currentlist.list))
        return result

    def addLink(self, name, url, icon = None, totalItems = None):
        if (icon == None or icon == ''):
            liz = xbmcgui.ListItem(name)
        else:
            liz = xbmcgui.ListItem(name, name, icon, icon)
        liz.setInfo( type = "Video", infoLabels = {"Title":name})
        if totalItems == None:
            ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = url, listitem = liz)
        else:
            ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = url, listitem = liz, totalItems = totalItems)

    def addDir(self, name, url, icon = None, totalItems = None):
        u = sys.argv[0] + "?url=" + urllib.quote_plus(url)
        if (icon == None or icon == ''):
            liz = xbmcgui.ListItem(name)
        else:
            liz = xbmcgui.ListItem(name, name, icon, icon)
        if totalItems == None:
            ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = True)
        else:
            ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = True, totalItems = totalItems)

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
                self.purgeCache()
                if self.parseView('sites.list') == 0:
                    xbmcplugin.endOfDirectory(int(sys.argv[1]))
            else:
                params = sys.argv[2]
                cleanedparams = params.replace('?', '')
                if (params[len(params)-1] == '/'):
                    params = params[0:len(params)-2]
                pairsofparams = cleanedparams.split('&')
                param = {}
                for i in range(len(pairsofparams)):
                    splitparams = {}
                    splitparams = pairsofparams[i].split('=')
                    if (len(splitparams)) == 2:
                        param[splitparams[0]] = splitparams[1]
                currentView = urllib.unquote_plus(param['url'])
                if self.parseView(currentView) == 0:
                    xbmcplugin.endOfDirectory(int(sys.argv[1]))
        except Exception, e:
            traceback.print_exc(file = sys.stdout)
            dialog = xbmcgui.Dialog()
            dialog.ok("VideoMonkey Error", "Error running VideoMonkey.\n\nReason:\n" + str(e))

win = Main()
win.run()
