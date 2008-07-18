////
//helper functions///
///

function URLEncode(plaintext)
{
	// The Javascript escape and unescape functions do not correspond
	// with what browsers actually do...
	var SAFECHARS = "0123456789" +					// Numeric
					"ABCDEFGHIJKLMNOPQRSTUVWXYZ" +	// Alphabetic
					"abcdefghijklmnopqrstuvwxyz" +
					"-_.!~*'()";					// RFC2396 Mark characters
	var HEX = "0123456789ABCDEF";

	var encoded = "";
	for (var i = 0; i < plaintext.length; i++ ) {
		var ch = plaintext.charAt(i);
	    if (ch == " ") {
		    encoded += "+";				// x-www-urlencoded, rather than %20
		} else if (SAFECHARS.indexOf(ch) != -1) {
		    encoded += ch;
		} else {
		    var charCode = ch.charCodeAt(0);
			if (charCode > 255) {
			    alert( "Unicode Character '" 
                        + ch 
                        + "' cannot be encoded using standard URL encoding.\n" +
				          "(URL encoding only supports 8-bit characters.)\n" +
						  "A space (+) will be substituted." );
				encoded += "+";
			} else {
				encoded += "%";
				encoded += HEX.charAt((charCode >> 4) & 0xF);
				encoded += HEX.charAt(charCode & 0xF);
			}
		}
	} // for
	return encoded;
};

function URLDecode(encoded)
{
   // Replace + with ' '
   // Replace %xx with equivalent character
   // Put [ERROR] in output if %xx is invalid.
   var HEXCHARS = "0123456789ABCDEFabcdef"; 
   var plaintext = "";
   var i = 0;
   while (i < encoded.length) {
       var ch = encoded.charAt(i);
	   if (ch == "+") {
	       plaintext += " ";
		   i++;
	   } else if (ch == "%") {
			if (i < (encoded.length-2) 
					&& HEXCHARS.indexOf(encoded.charAt(i+1)) != -1 
					&& HEXCHARS.indexOf(encoded.charAt(i+2)) != -1 ) {
				plaintext += unescape( encoded.substr(i,3) );
				i += 3;
			} else {
				alert( 'Bad escape combination near ...' + encoded.substr(i) );
				plaintext += "%[ERROR]";
				i++;
			}
		} else {
		   plaintext += ch;
		   i++;
		}
	} // while
   return plaintext;
};

///


function RemoveEmbeddedSpaces(s)
{
   var i = s.indexOf(' ',0);
   while(i > -1)
   {
      s = s.substring(0,i) + s.substring((i + 1),s.length);
      i = s.indexOf(' ',0);
   }
   return s;
}

function RemoveDots(s)
{
   var i = s.indexOf('.',0);
   while(i > -1)
   {
      s = s.substring(0,i) + s.substring((i + 1),s.length);
      i = s.indexOf('.',0);
   }
   return s;
}


String.prototype.sprintf = function () {
  var fstring = this.toString();

  var pad = function(str,ch,len) { var ps='';
      for(var i=0; i<Math.abs(len); i++) {
		  ps+=ch;
	  }
      return len>0?str+ps:ps+str;
  };
  var processFlags = function(flags,width,rs,arg) { 
      var pn = function(flags,arg,rs) {
          if(arg>=0) { 
              if(flags.indexOf(' ')>=0) {
				  rs = ' ' + rs;
			  } else if(flags.indexOf('+')>=0) {
				  rs = '+' + rs;
			  }
          } else {
              rs = '-' + rs;
		  }
          return rs;
      };
      var iWidth = parseInt(width,10);
      if(width.charAt(0) == '0') {
          var ec=0;
          if(flags.indexOf(' ')>=0 || flags.indexOf('+')>=0) {
			  ec++;
		  }
          if(rs.length<(iWidth-ec)) {
			  rs = pad(rs,'0',rs.length-(iWidth-ec));
		  }
          return pn(flags,arg,rs);
      }
      rs = pn(flags,arg,rs);
      if(rs.length<iWidth) {
          if(flags.indexOf('-')<0) {
			  rs = pad(rs,' ',rs.length-iWidth);
		  } else {
			  rs = pad(rs,' ',iWidth - rs.length);
		  }
      }    
      return rs;
  };
  var converters = [];
  converters.c = function(flags,width,precision,arg) { 
      if (typeof(arg) == 'number') {
		  return String.fromCharCode(arg);
	  } else if (typeof(arg) == 'string') {
		  return arg.charAt(0);
	  } else {
		  return '';
	  }
  };
  converters.d = function(flags,width,precision,arg) { 
      return converters.i(flags,width,precision,arg); 
  };
  converters.u = function(flags,width,precision,arg) { 
      return converters.i(flags,width,precision,Math.abs(arg)); 
  };
  converters.i =  function(flags,width,precision,arg) {
      var iPrecision=parseInt(precision, 10);
      var rs = ((Math.abs(arg)).toString().split('.'))[0];
      if(rs.length<iPrecision) {
		  rs=pad(rs,' ',iPrecision - rs.length);
	  }
      return processFlags(flags,width,rs,arg); 
  };
  converters.E = function(flags,width,precision,arg) {
      return (converters.e(flags,width,precision,arg)).toUpperCase();
  };
  converters.e = function(flags,width,precision,arg) {
      iPrecision = parseInt(precision, 10);
      if(isNaN(iPrecision)) {
		  iPrecision = 6;
	  }
      rs = (Math.abs(arg)).toExponential(iPrecision);
      if(rs.indexOf('.')<0 && flags.indexOf('#')>=0) {
		  rs = rs.replace(/^(.*)(e.*)$/,'$1.$2');
	  }
      return processFlags(flags,width,rs,arg);        
  };
  converters.f = function(flags,width,precision,arg) { 
      iPrecision = parseInt(precision, 10);
      if(isNaN(iPrecision)) {
		  iPrecision = 6;
	  }
      rs = (Math.abs(arg)).toFixed(iPrecision);
      if(rs.indexOf('.')<0 && flags.indexOf('#')>=0) {
		  rs = rs + '.';
	  }
      return processFlags(flags,width,rs,arg);
  };
  converters.G = function(flags,width,precision,arg) { 
      return (converters.g(flags,width,precision,arg)).toUpperCase();
  };
  converters.g = function(flags,width,precision,arg) {
      iPrecision = parseInt(precision, 10);
      absArg = Math.abs(arg);
      rse = absArg.toExponential();
      rsf = absArg.toFixed(6);
      if(!isNaN(iPrecision)) { 
          rsep = absArg.toExponential(iPrecision);
          rse = rsep.length < rse.length ? rsep : rse;
          rsfp = absArg.toFixed(iPrecision);
          rsf = rsfp.length < rsf.length ? rsfp : rsf;
      }
      if(rse.indexOf('.')<0 && flags.indexOf('#')>=0) {
		  rse = rse.replace(/^(.*)(e.*)$/,'$1.$2');
	  }
      if(rsf.indexOf('.')<0 && flags.indexOf('#')>=0) {
		  rsf = rsf + '.';
	  }
      rs = rse.length<rsf.length ? rse : rsf;
      return processFlags(flags,width,rs,arg);        
  };  
  converters.o = function(flags,width,precision,arg) { 
      var iPrecision=parseInt(precision, 10);
      var rs = Math.round(Math.abs(arg)).toString(8);
      if(rs.length<iPrecision) {
		  rs=pad(rs,' ',iPrecision - rs.length);
	  }
      if(flags.indexOf('#')>=0) {
		  rs='0'+rs;
	  }
      return processFlags(flags,width,rs,arg); 
  };
  converters.X = function(flags,width,precision,arg) { 
      return (converters.x(flags,width,precision,arg)).toUpperCase();
  };
  converters.x = function(flags,width,precision,arg) { 
      var iPrecision=parseInt(precision, 10);
      arg = Math.abs(arg);
      var rs = Math.round(arg).toString(16);
      if(rs.length<iPrecision) {
		  rs=pad(rs,' ',iPrecision - rs.length);
	  }
      if(flags.indexOf('#')>=0) {
		  rs='0x'+rs;
	  }
      return processFlags(flags,width,rs,arg); 
  };
  converters.s = function(flags,width,precision,arg) { 
      var iPrecision=parseInt(precision, 10);
      var rs = arg;
      if(rs.length > iPrecision) {
		  rs = rs.substring(0,iPrecision);
	  }
      return processFlags(flags,width,rs,0);
  };

  farr = fstring.split('%');
  retstr = farr[0];
  fpRE = /^([-+ #]*)(?:(\d*)\$|)(\d*)\.?(\d*)([cdieEfFgGosuxX])(.*)$/;
  for(var i = 1; i<farr.length; i++) { 
      fps=fpRE.exec(farr[i]);
      if(!fps) {
		  continue;
	  }
	  var my_i = fps[2] ? fps[2] : i;
      if(arguments[my_i-1]) {
          retstr+=converters[fps[5]](fps[1],fps[3],fps[4],arguments[my_i-1]);
      }
      retstr += fps[6];
  }
  return retstr;
};


//Some functions for converting data on the playlists
//encodeBase64(PLAYLIST FILE STRING ONE PER LINE);


function urlDecode(str){
    str=str.replace(new RegExp('\\+','g'),' ');
    return unescape(str);
}
function urlEncode(str){
    str=escape(str);
    str=str.replace(new RegExp('\\+','g'),'%2B');
    return str.replace(new RegExp('%20','g'),'+');
}

var END_OF_INPUT = -1;

var base64Chars = new Array(
    'A','B','C','D','E','F','G','H',
    'I','J','K','L','M','N','O','P',
    'Q','R','S','T','U','V','W','X',
    'Y','Z','a','b','c','d','e','f',
    'g','h','i','j','k','l','m','n',
    'o','p','q','r','s','t','u','v',
    'w','x','y','z','0','1','2','3',
    '4','5','6','7','8','9','+','/'
);

var reverseBase64Chars = new Array();
for (var i=0; i < base64Chars.length; i++){
    reverseBase64Chars[base64Chars[i]] = i;
}

var base64Str;
var base64Count;
function setBase64Str(str){
    base64Str = str;
    base64Count = 0;
}
function readBase64(){    
    if (!base64Str) return END_OF_INPUT;
    if (base64Count >= base64Str.length) return END_OF_INPUT;
    var c = base64Str.charCodeAt(base64Count) & 0xff;
    base64Count++;
    return c;
}
function encodeBase64(str){
    setBase64Str(str);
    var result = '';
    var inBuffer = new Array(3);
    var lineCount = 0;
    var done = false;
    while (!done && (inBuffer[0] = readBase64()) != END_OF_INPUT){
        inBuffer[1] = readBase64();
        inBuffer[2] = readBase64();
        result += (base64Chars[ inBuffer[0] >> 2 ]);
        if (inBuffer[1] != END_OF_INPUT){
            result += (base64Chars [(( inBuffer[0] << 4 ) & 0x30) | (inBuffer[1] >> 4) ]);
            if (inBuffer[2] != END_OF_INPUT){
                result += (base64Chars [((inBuffer[1] << 2) & 0x3c) | (inBuffer[2] >> 6) ]);
                result += (base64Chars [inBuffer[2] & 0x3F]);
            } else {
                result += (base64Chars [((inBuffer[1] << 2) & 0x3c)]);
                result += ('=');
                done = true;
            }
        } else {
            result += (base64Chars [(( inBuffer[0] << 4 ) & 0x30)]);
            result += ('=');
            result += ('=');
            done = true;
        }
        lineCount += 4;
        if (lineCount >= 76){
            result += ('\n');
            lineCount = 0;
        }
    }
    return result;
}
function readReverseBase64(){   
    if (!base64Str) return END_OF_INPUT;
    while (true){      
        if (base64Count >= base64Str.length) return END_OF_INPUT;
        var nextCharacter = base64Str.charAt(base64Count);
        base64Count++;
        if (reverseBase64Chars[nextCharacter]){
            return reverseBase64Chars[nextCharacter];
        }
        if (nextCharacter == 'A') return 0;
    }
    return END_OF_INPUT;
}

function ntos(n){
    n=n.toString(16);
    if (n.length == 1) n="0"+n;
    n="%"+n;
    return unescape(n);
}

function decodeBase64(str){
    setBase64Str(str);
    var result = "";
    var inBuffer = new Array(4);
    var done = false;
    while (!done && (inBuffer[0] = readReverseBase64()) != END_OF_INPUT
        && (inBuffer[1] = readReverseBase64()) != END_OF_INPUT){
        inBuffer[2] = readReverseBase64();
        inBuffer[3] = readReverseBase64();
        result += ntos((((inBuffer[0] << 2) & 0xff)| inBuffer[1] >> 4));
        if (inBuffer[2] != END_OF_INPUT){
            result +=  ntos((((inBuffer[1] << 4) & 0xff)| inBuffer[2] >> 2));
            if (inBuffer[3] != END_OF_INPUT){
                result +=  ntos((((inBuffer[2] << 6)  & 0xff) | inBuffer[3]));
            } else {
                done = true;
            }
        } else {
            done = true;
        }
    }
    return result;
}

var digitArray = new Array('0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f');
function toHex(n){
    var result = ''
    var start = true;
    for (var i=32; i>0;){
        i-=4;
        var digit = (n>>i) & 0xf;
        if (!start || digit != 0){
            start = false;
            result += digitArray[digit];
        }
    }
    return (result==''?'0':result);
}

function pad(str, len, pad){
    var result = str;
    for (var i=str.length; i<len; i++){
        result = pad + result;
    }
    return result;
}

function encodeHex(str){
    var result = "";
    for (var i=0; i<str.length; i++){
        result += pad(toHex(str.charCodeAt(i)&0xff),2,'0');
    }
    return result;
}

function decodeHex(str){
    str = str.replace(new RegExp("s/[^0-9a-zA-Z]//g"));
    var result = "";
    var nextchar = "";
    for (var i=0; i<str.length; i++){
        nextchar += str.charAt(i);
        if (nextchar.length == 2){
            result += ntos(eval('0x'+nextchar));
            nextchar = "";
        }
    }
    return result;
    
}