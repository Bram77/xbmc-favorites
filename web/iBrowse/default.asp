<html>
<head>
<title>XBMC Music Browser</title>


<link rel="stylesheet" href="css/ajax.css" type="text/css" media="screen" />
<script type="text/javascript" src="js/stringUtils.js"></script>
<script type="text/javascript" src="js/prototype.js" ></script>
<script type="text/javascript" src="js/scriptaculous.js" ></script>
<script type="text/javascript" src="js/layout.js"></script>
<script type="text/javscript" src="js/effects2.js"></script>
<script type="text/javscript" src="js/md5.js"></script>

<script type="text/javascript" src="lightbox/ibox.js"></script>
<link rel="stylesheet" href="lightbox/ibox.css" type="text/css"  media="screen"/>


<script type="text/javascript" src="windows_js/javascripts/prototype.js" ></script>
<script type="text/javascript" src="windows_js/javascripts/effects.js"> </script>
<script type="text/javascript" src="windows_js/javascripts/window.js"> </script>
<script type="text/javascript" src="windows_js/javascripts/debug.js"> </script>
	<link href="windows_js/themes/default.css" rel="stylesheet" type="text/css"/>
	<link href="windows_js/themes/alert.css" rel="stylesheet" type="text/css"/>
	<link href="windows_js/themes/alphacube.css" rel="stylesheet" type="text/css"/>

<script>


//This is used to control reciever volume via control system - has nothing to do with xbmc
var custom = false;
var customIP = "10.0.0.42";
var maxItems = "50";
//var playlistLocation = "smb://MEDIAONE/media/Playlists/";
var playlistLocation = "q:\\UserData\\playlists\\music\\";

<%
    navigatorstate = xbmcCommand("navigatorstate");

    if (navigatorstate == "pictures"){
		write('var currentPlaylist = "0";')
		write('var currentMediaType = "pictures";')
    } else if (navigatorstate == "music") {
		write('var currentPlaylist = "0";')
		write('var currentMediaType = "music";')
    } else if (navigatorstate == "videos") {
		write('var currentPlaylist = "3";')
		write('var currentMediaType = "videos";')
    } else {
		write('var currentPlaylist = "0";')
		write('var currentMediaType = "music";')
	}



xbmcAPI("SetResponseFormat", "webfooter;");
xbmcAPI("SetResponseFormat", "webheader;");
xbmcAPI("SetResponseFormat", "closetag;<li>");
xbmcAPI("SetResponseFormat", "opentag;");
xbmcAPI("SetResponseFormat", "closefinaltag;");



%>

function resize(){

	var iWidth = (window.innerWidth) ? window.innerWidth : document.body.offsetWidth;
 	var iHeight = (window.innerHeight) ? window.innerHeight : document.body.offsetHeight;
	var contentHeight = iHeight - 112;

	$('musiclibraryHolder').style.height = contentHeight;
}

</script>
</head><body onresize="resize()">

<table width="100%" background="images/topbarbg.gif" cellpadding=0 cellspacing=0><tr><td width="15" bgcolor="white"><img src="images/leftcorner.gif"></td><td width="60">
			<a href="javascript:xbmcCmds('playPrev');GetCurrentlyPlaying();">
			<IMG SRC="images/transport_prev.png" ALT="" border="0"></a>
</td><td width="60">
			<a href="javascript:GetCurrentlyPlaying();swapPlayTransport()">
			<div id="mainTransport">
			<a href="javascript:xbmcCmds('pause');GetCurrentlyPlaying();">
			<IMG SRC="images/transport_pause.png" ALT="" border="0"></a>
			</div></a>
</td><td width="60">
			<a href="javascript:xbmcCmds('playNext');GetCurrentlyPlaying();">
			<IMG SRC="images/transport_next.png" ALT="" border="0"></a>
</td>
<td width="10"></td>


<td width="66">
<a href="javascript:getContent('home');setupMenubars('browser')"><img src="images/browseBtn.gif" border=0></a>

</td>


<td width="10"></td>
<td>

<table cellpadding=0 cellspacing=0 width="100%"><tr>
<td width="14" background="images/infoleft.gif">&nbsp;</td>
<td>

<table height="70" width="100%" cellpadding=0 cellspacing=0><tr><td background="images/infoBG.gif">


<%
myval = xbmcAPI("getvolume", "");
 %>

<input id="currentVolume" type="hidden" value="<%write(myval);%>">

<font color="black" style="font-size:11px"><center><b>Currently Playing:</b></center>
<div id="currentlyPlayingText"><br><br>
</div>
</font>

</td></tr></table>

</td>
<td width="14" background="images/inforight.gif">&nbsp;</td>
</tr></table></td>


<td width="10"></td>

<td>
<span id='albumArt2'></span>
</td>



<td width="66">
<a href="javascript:SetCurrentPlaylist(currentPlaylist);getPlaylistContents(currentPlaylist);setupMenubars('playlist');"><img src="images/playlistsBtn.gif" border=0></a>

</td>



<td width="66">
<script>
muteDIV = '<img src="images/muteBtn.gif" onclick="javascript:document.getElementById(\'muteWidget\').innerHTML = unmuteDIV;" border=0>';
unmuteDIV = '<img src="images/unmute.gif" onclick="javascript:document.getElementById(\'muteWidget\').innerHTML = muteDIV;" border=0>';
</script>
<%
vollevel = xbmcAPI("GetSystemInfo", "32");
if (vollevel == "-60.0 dB"){
	write('<a href="javascript:ExecBuiltIn(\'XBMC.Mute()\');"><div id="muteWidget"><img src="images/unmute.gif"  onclick="javascript:document.getElementById(\'muteWidget\').innerHTML = muteDIV;" border=0></div></a>');
} else {
	write('<a href="javascript:ExecBuiltIn(\'XBMC.Mute()\');"><div id="muteWidget"><img src="images/muteBtn.gif" onclick="javascript:document.getElementById(\'muteWidget\').innerHTML = unmuteDIV;" border=0></div></a>');
}
%>

</td>

<td width="66">

<a href="javascript:volumeCtrl('up')"><img src="images/volup.gif" border=0><br>
<a href="javascript:volumeCtrl('down')"><img src="images/voldown.gif" border=0></a>


</td>
<td width="60">
<a href="javascript:getContent('config')"><img src="images/x_quit.png"></a>

</td>
<td width="15"  bgcolor="white"><img src="images/rightcorner.gif"></td>
</tr></table>



<div style="width:100%;">

<table style="width:100%;height:35px;" background="images/menubarbg.gif"><tr>
<td width="45%">
<div id="titlebuttons_browser" style="display:none"></div>
<div id="titlebuttons_playlist" style="display:none"><a href="javascript:SetCurrentPlaylist(currentPlaylist);xbmcCmds('setplaylistsong&parameter=0');GetCurrentlyPlaying();"><img src="images/playBtn.gif" border="0"></a>
<a href="javascript:showKeyboard()"><img src="images/saveBtn.gif" border="0"></a>

<a href="javascript:getDirectory(playlistLocation);"><img src="images/loadBtn.gif" border="0"></a>

<a href="javascript:xbmcCmds('clearplaylist');GetCurrentlyPlaying();getPlaylistContents(currentPlaylist);"><img src="images/clearBtn.gif" border="0"></a>
</div>
</td>
<td width="55%"><b><span id="titlebox">Media Library</span></b></td></tr></table>




<div id='musiclibraryHolder' style="width:100%;">
	<ul class="musiclibrary" align="left"  id="musiclibrary">

	 </ul>
</div>






<div align="center" id="onscreenkeyboard" style="display:none;left:0px;top:100px;z-index:1000;width:100%;float:left;position:absolute;">
<table bgcolor="#EfEfEf"><tr><td bgcolor="black">
<table width="100%"><tr><td><h3>Save File As...</h3></td><td width="15"><h3><a onclick="javascript:closeKeyboard();">X</a></h3></td></tr></table>
</td></tr>
<tr><td>
<div align="center">


<script>

function addslashes(str) {
str=str.replace(/\'/g,'\\\'');
str=str.replace(/\"/g,'\\"');
str=str.replace(/\\/g,'\\\\');
str=str.replace(/\0/g,'\\0');
return str;
}
function stripslashes(str) {
str=str.replace(/\\'/g,'\'');
str=str.replace(/\\"/g,'"');
str=str.replace(/\\\\/g,'\\');
str=str.replace(/\\0/g,'\0');
return str;
}

function pausecomp(millis)
{
var date = new Date();
var curDate = null;

do { curDate = new Date(); }
while(curDate-date < millis);
}

var disableKeys = false;

function showKeyboard(){
$('enterButton').innerHTML = "Save";
document.getElementById('onscreenkeyboard').style.display='block';
}

function closeKeyboard(){
document.getElementById('onscreenkeyboard').style.display='none';
}

function keyPressed(keyToSend){

if(!disableKeys){

if(keyToSend == "BACKSPACE"){
$('textEntered').value = $('textEntered').value.substr(0, $('textEntered').value.length-1 );
}else if(keyToSend == "ENTER"){
disableKeys = true;
$('enterButton').innerHTML = "Saving";
GeneratePlaylistM3U($('textEntered').value + '.m3u');

}else if(keyToSend == "SHIFT"){

//switch to caps

}else{

$('textEntered').value += keyToSend;

}

}
}
</script>


<table><tr><td><input type="text" value="" id="textEntered" size="30"></td><td><ul class="menu6" id="topbuttons"><li><a href="javascript:keyPressed('ENTER')"><div id="enterButton">ENTER</div></a></ul></td></tr></table>


<ul class="menu5" id="topbuttons">
<li><a href="javascript:keyPressed('1')">1</a>
<li><a href="javascript:keyPressed('2')">2</a>
<li><a href="javascript:keyPressed('3')">3</a>
<li><a href="javascript:keyPressed('4')">4</a>
<li><a href="javascript:keyPressed('5')">5</a>
<li><a href="javascript:keyPressed('6')">6</a>
<li><a href="javascript:keyPressed('7')">7</a>

<li><a href="javascript:keyPressed('8')">8</a>
<li><a href="javascript:keyPressed('9')">9</a>
<li><a href="javascript:keyPressed('0')">0</a>
</ul>
<ul class="menu6" id="topbuttons">
<li><a href="javascript:keyPressed('BACKSPACE')">< BKSP</a>
</ul>
</div>
</td></tr>
<tr><td>
<div align="center">
<ul class="menu5" id="topbuttons">
<li><a href="javascript:keyPressed('q')">q</a>

<li><a href="javascript:keyPressed('w')">w</a>
<li><a href="javascript:keyPressed('e')">e</a>
<li><a href="javascript:keyPressed('r')">r</a>
<li><a href="javascript:keyPressed('t')">t</a>
<li><a href="javascript:keyPressed('y')">y</a>
<li><a href="javascript:keyPressed('u')">u</a>
<li><a href="javascript:keyPressed('i')">i</a>
<li><a href="javascript:keyPressed('o')">o</a>
<li><a href="javascript:keyPressed('p')">p</a>

</ul>
</div>
</td></tr>
<tr><td>
<div align="center">
<ul class="menu5" id="topbuttons">
<li><a href="javascript:keyPressed('a')">a</a>
<li><a href="javascript:keyPressed('s')">s</a>
<li><a href="javascript:keyPressed('d')">d</a>
<li><a href="javascript:keyPressed('f')">f</a>
<li><a href="javascript:keyPressed('g')">g</a>
<li><a href="javascript:keyPressed('h')">h</a>

<li><a href="javascript:keyPressed('j')">j</a>
<li><a href="javascript:keyPressed('k')">k</a>
<li><a href="javascript:keyPressed('l')">l</a>
</ul>
<ul class="menu6" id="topbuttons">
<li><a href="javascript:keyPressed('ENTER')">ENTER</a>
</ul>
</div>
</td></tr>
<tr><td>
<div align="center">
<ul class="menu6" id="topbuttons">
<li><a href="javascript:keyPressed('SHIFT')">SHIFT</a>

</ul>
<ul class="menu5" id="topbuttons">
<li><a href="javascript:keyPressed('z')">z</a>
<li><a href="javascript:keyPressed('x')">x</a>
<li><a href="javascript:keyPressed('c')">c</a>
<li><a href="javascript:keyPressed('v')">v</a>
<li><a href="javascript:keyPressed('b')">b</a>
<li><a href="javascript:keyPressed('n')">n</a>
<li><a href="javascript:keyPressed('m')">m</a>
</ul>

<ul class="menu6" id="topbuttons">
<li><a href="javascript:keyPressed('SHIFT')">SHIFT</a>
</ul>
</div>
</td></tr>
<tr><td>
<div align="center">
<ul class="menu6" id="topbuttons">
<li><a href="javascript:keyPressed(' ')">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;SPACEBAR&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</a>
</ul>
</div>
</td></tr>
</table>
</div>





<div align="center" id="guiControl" style="display:none;left:0px;top:50px;z-index:1001;width:100%;float:left;position:absolute;filter:alpha(opacity=50);-moz-opacity:50%;">
<table bgcolor="#EfEfEf"><tr><td bgcolor="black">
<table width="100%"><tr><td><h3>Control Media Center GUI...</h3></td><td width="15"><h3><a onclick="javascript:closeScreen();">X</a></h3></td></tr></table>
</td></tr>
<tr><td>
<div align="center">


<script>

function showScreen(){
document.getElementById('guiControl').style.display='block';
}

function closeScreen(){
document.getElementById('guiControl').style.display='none';
}

function keyPressed(keyToSend){


SendKey(keyToSend);
showLargeScreenshot();

}
</script>

<table><tr><td width="640">
<div id="largeScreenshot"></div>
</td><td>

<map name="FPMap0">
<area href="javascript:keyPressed('m')" shape="rect" coords="0, 294, 53, 479">
<area href="javascript:keyPressed('258')" shape="circle" coords="103, 344, 44">
<area href="javascript:keyPressed('256')" shape="circle" coords="191, 319, 42">
<area href="javascript:keyPressed('257')" shape="circle" coords="198, 403, 43">
<area href="javascript:keyPressed('274')" shape="rect" coords="9, 227, 88, 279">
<area href="javascript:keyPressed('275')" shape="rect" coords="93, 225, 169, 275">
<area href="javascript:keyPressed('256')" shape="rect" coords="109, 86, 189, 138">
<area href="javascript:keyPressed('270')" shape="polygon" coords="71, 36, 111, 76, 178, 76, 220, 32, 145, 3">
<area href="javascript:keyPressed('273')" shape="polygon" coords="187, 81, 223, 42, 250, 101, 250, 123, 223, 178, 190, 148, 202, 111, 193, 74, 193, 73, 193, 75, 193, 69, 196, 69, 197, 72">
<area href="javascript:keyPressed('271')" shape="polygon" coords="111, 153, 145, 164, 183, 150, 218, 185, 162, 211, 135, 211, 80, 186">
<area href="javascript:keyPressed('272')" shape="polygon" coords="105, 78, 72, 44, 47, 89, 45, 116, 68, 175, 105, 144, 92, 111">
<area href="javascript:keyPressed('256')" shape="circle" coords="101, 438, 42">
<area href="javascript:keyPressed('261')" shape="rect" coords="177, 223, 227, 267">
<area href="javascript:keyPressed('260')" shape="rect" coords="238, 222, 294, 268">
</map>
<img border="0" src="images/controllerPanel.png" width="300" height="480"  usemap="#FPMap0">
</td></tr></table>


</td></tr>
</table>
</div>







 <script type="text/javascript">

//////////////////////////////////
//// XBMC Commands
//////////////////////////////////
var lastPlaylistLocation = "";
var currentPlaylistLocation = "";
var lastPlaylistColor = "";
var currentSection = ""

function GetPlaylistSong(){

if(currentSection == "playlist"){ //only show current track stuff if we're on the playlist page

var url7 = '/xbmcCmds/xbmcHttp?command=GetPlaylistSong&rand='+Math.random(50);
var setup7 = new Ajax.Request(url7, {method:'get',onSuccess:function(obj){
var currentPlaylistLocation = obj.responseText;
//alert("current list: "+currentPlaylistLocation);

if(currentPlaylistLocation != lastPlaylistLocation){

	if(lastPlaylistLocation != ""){
		document.getElementById('musiclibrary'+lastPlaylistLocation).className=lastPlaylistColor;
	}

	lastPlaylistLocation = currentPlaylistLocation;
	lastPlaylistColor = document.getElementById('musiclibrary'+currentPlaylistLocation).className;
	document.getElementById('musiclibrary'+currentPlaylistLocation).className="rowcurrent";


}

}});
}
}


function SetCurrentPlaylist(playlistId){
currentPlaylist = playlistId;
var url6 = '/xbmcCmds/xbmcHttp?command=SetCurrentPlaylist&parameter='+playlistId+'&rand='+Math.random(50);
var setup6 = new Ajax.Request(url6, {method:'get'});
}


function addItemToPlaylistDiv(i, infoArray){
if(infoArray=="[Empty]"){

	locationPath ='<li nowrap id=playlist0';
	locationPath += "<a href='#'><center><br><br><br><b>The playlist is Empty</b><br><br></center></a></li>";

}else{
	displayTitle = infoArray.split("/");

i = i-1;

	locationPath ='<li id=musiclibrary'+i+' class="row'+ i%2 + '"';
	locationPath += "><span onclick='javascript:PlayMedia("+ i + ");' >";


locationPath += '<span style="position: absolute; left: 0px; top: 0px; width: 100px; vertical-align: top;"  align="left" id="musiclibArt'+ i +'">'


locationPath += '<img border="0" onclick="javascript:xbmcCmds(\'setplaylistsong&parameter='+ i + '\')" src="images/play.png" />';

locationPath += '<img border="0" onclick="javascript:xbmcCmds(\'removefromplaylist&parameter='+ i + '\');" src="images/delete.png"  />';


locationPath += '</span><div style="overflow: hidden;position: absolute; left: 100px; top: 0px; " id="musiclibSongInfo'+ i +'">'+ displayTitle[displayTitle.length-1] +'</div></span>';

locationPath += "</div></li>";

}

	new Insertion.Bottom('musiclibrary', locationPath);
}

function getPlaylistSuccess(t){

	$('musiclibrary').innerHTML = "";

	responseArr = t.responseText.split("<li>");




	for (var i=0;i<responseArr.length;i++){

	if((responseArr[i]!="") && (escape(responseArr[i]) != "%0A")){

		mediapath = responseArr[i];



	if(responseArr[i] != "html>"){

	addItemToPlaylistDiv(i,responseArr[i]);

	}
	}
	}
	refreshDraggables();
}

function getPlaylistFailure(t){

//	alert('failure t:'+t);
getPlaylistContents(1);

}


function getPlaylistContents(playlistNum){
	if(playlistNum == undefined){
	playlistNum = 0; //Playlist 0 is the default
	}
     var url = '/xbmcCmds/xbmcHttp?command=GetPlaylistContents&parameter='+playlistNum+'&rand='+Math.random(50);
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){getPlaylistSuccess(t)}, onFailure:getPlaylistFailure});

	$('musiclibrary').innerHTML = "<div id='loadingWidget'><br><br><center><img src='images/indicator.gif'> Loading</center><br><br></div>";


}



function RemoveFromPlaylist(playlistId){

	 var url = '/xbmcCmds/xbmcHttp?command=RemoveFromPlaylist&parameter='+playlistId+'&rand='+Math.random(50);
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){

getPlaylistContents(currentPlaylist);

}});

}


function GetCurrentlyPlaying(){

	GetPlaylistSong();

     var url = '/xbmcCmds/xbmcHttp?command=GetCurrentlyPlaying&rand='+Math.random(50);
     myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){

	responseArr = t.responseText.split("<li>");
	//	$('currentlyPlayingText').innerHTML = t.responseText;

	for (var i=0;i<responseArr.length;i++){

		responseArr2 = responseArr[i].split(":");

		if(responseArr2.length > 2){
			elementName = responseArr2[0];
			responseArr2 = responseArr2.slice(1);
			elementValue = responseArr2.join(":");
			//alert(elementName+'='+elementValue);

			$('currentlyPlayingText')[elementName] = elementValue;

		}else{
			//alert(responseArr2[0]+'='+responseArr2[1]);

		    $('currentlyPlayingText')[responseArr2[0]] = responseArr2[1];
		}
	}
	//
	//This is where the Now Playing Gets Formated
	/*
	Vars you have access to here:
	$('currentlyPlayingText').Filename	Filename
	$('currentlyPlayingText').SongNo	7
	$('currentlyPlayingText').Type	Audio
	$('currentlyPlayingText').Title	Sleeping Awake
	$('currentlyPlayingText').Artist	P.O.D.
	$('currentlyPlayingText').Album	Matrix Reloaded
	$('currentlyPlayingText').Genre	Soundtrack
	$('currentlyPlayingText').Year	2003
	$('currentlyPlayingText').Bitrate	192
	$('currentlyPlayingText').Samplerate	44
	$('currentlyPlayingText').Paused	False
	$('currentlyPlayingText').Playing	True
	$('currentlyPlayingText').Time	Time
	$('currentlyPlayingText').Duration	Duration
	$('currentlyPlayingText').Percentage	46
	$('currentlyPlayingText').File size	4879643
	*/


	if($('currentlyPlayingText').Title != undefined){


//	$('currentlyPlayingHeaderText').innerHTML = $('currentlyPlayingText').Title;


if($('currentlyPlayingText').Album == undefined){
$('currentlyPlayingText').Album = "";
}



	$('currentlyPlayingText').innerHTML = "<center><b>"+$('currentlyPlayingText').Title+"</b> by "+$('currentlyPlayingText').Artist+"<br> "+$('currentlyPlayingText').Album+"<br></center>";

//+$('currentlyPlayingText').Time+" / "+$('currentlyPlayingText').Duration+"</div>";

//s.setValue($('currentlyPlayingText').Percentage);
//s.setMinimum(0);
//s.setMaximum(100);

//$('currentlyPlayingText').SeekPercentage


	justFilePath = $('currentlyPlayingText').Filename.split("/");
	justFilePath = justFilePath.slice(0,-1);
	justFilePath = justFilePath.join("/");


	//Only download image once
	if($('currentlyPlayingText').Title != lastTitle){
	//getThumbnail(justFilePath, "albumArt");
	}
	lastTitle = $('currentlyPlayingText').Title;

	}else if(lastTitle=="screenshot"){


	}else{
	$('currentlyPlayingText').innerHTML = "<center>Nothing Playing</center>";
	//showScreenshot();
	lastTitle = "screenshot";
	}


	if($('currentlyPlayingText').Filename == "[Nothing Playing]"){

		$('currentlyPlayingText').innerHTML = "Nothing Playing";
		$('albumArt').innerHTML = '<img src="images/defaultAlbumCover.png"  align=left hspace=5 >';

	}


	pollInProgress = false;
		}});
	}


var lastTitle = "";


function SetCurrentPlaylist(playlistId){
currentPlaylist = playlistId;
var url6 = '/xbmcCmds/xbmcHttp?command=SetCurrentPlaylist&parameter='+playlistId+'&rand='+Math.random(50);
var setup6 = new Ajax.Request(url6, {method:'get'});
}

function AddIdToPlayList(songId){
     var url = '/xbmcCmds/xbmcForm?command=catalog&parameter=que,'+songId+'&rand='+Math.random(50);
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){

myeffect = new Effect.Highlight('musiclibrary'+songId, {startcolor:'#94BBF1', endcolor:'#999999'})
}});
}


function PlayMedia(mediapath){

	 var url = '/xbmcCmds/xbmcHttp?command=playfile&parameter='+mediapath+'&rand='+Math.random(50);
	 var myAjax = new Ajax.Request(url, {method:'get'});

}


function PlayMediaCRC(mediapath){

	 var url = 'playcrc.spy?crc='+mediapath+'&rand='+Math.random(50);
	 var myAjax = new Ajax.Request(url, {method:'get'});

}

function AddMediaCRC(mediapath){

	 var url = 'addcrc.spy?crc='+mediapath+'&rand='+Math.random(50);
	 var myAjax = new Ajax.Request(url, {method:'get'});

}

function playAlbum(idAlbum){

	 var url = 'playalbum.spy?idAlbum='+idAlbum+'&rand='+Math.random(50);
	 var myAjax = new Ajax.Request(url, {method:'get'});

}

function getDirectorySuccess(t, mediapath){

	responseArrD = t.responseText.split("<li>");
	data = '';
	for (i=0;i<responseArrD.length;i++){


//alert(responseArrD[i]);

if(responseArrD[i] != ""){
	strippedPath = responseArrD[i].replace(mediapath, '');
	strippedPath = strippedPath.replace('.m3u', '');


	fixed	 = addslashes(responseArrD[i]); // fixes encoding


    data = data + ' <li class="row0" mediapath="'+ i + '" id="musiclibrary'+ i + '" >  <span onclick="javascript:PlayMedia(\''+ fixed + '\');" >';
    data = data + '<span valign="center" align="left" id="musiclibArt'+ i +'"><img hspace="20" align="left" onclick="javascript:PlayMedia('+ fixed + ');getPlaylistContents(currentPlaylist);setupMenubars(\'playlist\');" src="images/music.png"/></span><div style="overflow: hidden; width: 60%;" id="musiclibSongInfo'+ i +'">'+ strippedPath +'</div>';
    data = data + "</span>";
    data = data + '<div style="position: absolute; right: 0pt; top: 0px; width: 100px; vertical-align: top;" id="itemControls'+ i +'">';
    data = data + '<img border="0" onclick="javascript:PlayMedia(\''+ fixed + '\');getPlaylistContents(currentPlaylist);setupMenubars(\'playlist\');" src="images/play.png"  />';

    data = data + "</div>";
	data = data + "</li>";
}
	}

	data = data +' ';
	document.getElementById('musiclibrary').innerHTML =  data;



}

function connectionFailure(t){

//	alert('failure t:'+t);

}


function getDirectory(mediapath){
     var url = '/xbmcCmds/xbmcHttp?command=GetDirectory&parameter='+mediapath+'&rand='+Math.random(50);
     var myAjaxP = new Ajax.Request(url, {method:'get', onSuccess:function(obj){getDirectorySuccess(obj,mediapath);}, onFailure:connectionFailure});
	}


function getPLDirectorySuccess(t, mediapath){

	responseArr = t.responseText.split("<li>");



	data = '';
	for (i=0;i<responseArr.length;i++){


//	alert(responseArr[i]);



if(responseArr[i] != ""){
	strippedPath = responseArr[i].replace(mediapath, '');
	strippedPath = strippedPath.replace('.m3u', '');

//alert(responseArr[i]);


//	strippedPath = strippedPath.replace('.m3u', '');

    data = data + ' <li class="row0" mediapath="'+ i + '" id="musiclibrary'+ i + '" >  <span onclick="javascript:RunPlaylist(\''+ responseArr[i] + '\');" >';
    data = data + '<span valign="center" align="left" id="musiclibArt'+ i +'"><img hspace="20" align="left" onclick="javascript:RunPlaylist('+ responseArr[i] + ');getPlaylistContents(currentPlaylist);setupMenubars(\'playlist\');" src="images/music.png"/></span><div style="overflow: hidden; width: 60%;" id="musiclibSongInfo'+ i +'">'+ strippedPath +'</div>';
    data = data + "</span>";
    data = data + '<div style="position: absolute; right: 0pt; top: 0px; width: 100px; vertical-align: top;" id="itemControls'+ i +'">';
    data = data + '<img border="0" onclick="javascript:RunPlaylist(\''+ responseArr[i] + '\');getPlaylistContents(currentPlaylist);setupMenubars(\'playlist\');" src="images/play.png"  />';

    data = data + "</div>";
	data = data + "</li>";
}
	}

	data = data +' ';
	document.getElementById('musiclibrary').innerHTML =  data;



}

function getPLDirectory(mediapath){
     var url = '/xbmcCmds/xbmcHttp?command=GetDirectory&parameter='+mediapath+'&PLrand='+Math.random(50);
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(obj){getPLDirectorySuccess(obj,mediapath);}, onFailure:connectionFailure});
	}

function connectionFailure(t){

//	alert('failure t:'+t);

}

function RunPlaylist(mediapath){
	 var url = '/xbmcCmds/xbmcForm?command=catalog&parameter=select,'+mediapath+'&rand='+Math.random(50);
	 var myAjax = new Ajax.Request(url, {method:'get'});

}


function PlayId(mediapath){
	 var url = '/xbmcCmds/xbmcForm?command=catalog&parameter=select,'+mediapath+'&rand='+Math.random(50);
	 var myAjax = new Ajax.Request(url, {method:'get'});

}


function pushMediaList(t){

$('musiclibraryHolder').innerHTML = t.responseText;

}

var beforeVolCache = "";
function getVolumeCtrls(){

setupMenubars('volume');


flashVolCtrl ='<OBJECT classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=5,0,0,0" WIDTH="100%" HEIGHT="100%" id="stage" align="top"> ';
flashVolCtrl +='<param name="movie" value="http://'+customIP+'/ajax_popup.swf" /> ';
flashVolCtrl +='<PARAM NAME=menu VALUE=false><PARAM NAME=salign VALUE=LT><param name="quality" value="high" /><param name="scale" value="exactfit" /> ';

flashVolCtrl +='<EMBED src="http://'+customIP+'/ajax_popup.swf" quality="high" menu="false" salign=LT  WIDTH="100%" HEIGHT="100%" bgcolor="#FFFFFF" TYPE="application/x-shockwave-flash" wmode="transparent" PLUGINSPAGE="http://www.macromedia.com/shockwave/download/index.cgi?P1_Prod_Version=ShockwaveFlash" NAME="stage" scale=exactfit ALIGN="top"></EMBED> ';
flashVolCtrl +='</OBJECT> ';


beforeVolCache = $('musiclibrary').innerHTML;
document.getElementById('musiclibrary').innerHTML = flashVolCtrl;

}


function hideVolCtrls(){
	$('musiclibrary').innerHTML = beforeVolCache;
	beforeVolCache = "";
}

function navigateToLocation(locationId){
	pollInProgress = true;
	$('musiclibrary').innerHTML = "<div id='loadingWidget'><br><br><center><img src='images/indicator.gif' alt=''> Loading</center><br><br></div>";
if(locationId != ""){
     var url = 'musicList.asp?command=select&item='+locationId+'&nocache='+Math.random()*5;
}else{
     var url = 'musicList.asp?nocache='+Math.random()*5;
}
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(obj){pushMediaList(obj,locationId);}});

}



function setMediaType(mediaType){


	$('musiclibrary').innerHTML = "<div id='loadingWidget'><br><br><center><img src='images/indicator.gif' alt=''> Loading</center><br><br></div>";
	currentMediaType = mediaType;

	var url = 'musicList.asp?Action='+mediaType+'&nocache='+Math.random()*5;
    var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(obj){pushMediaList(obj);}});

if(mediaType == "videos"){
currentPlaylist	 = "2";
}else{
currentPlaylist	 = "0";
}

SetCurrentPlaylist(currentPlaylist);

}

function getThumbnail(filePath, returnDiv){

thumburl = '/xbmcCmds/xbmcHttp?command=GetThumbFilename&parameter='+filePath+";";
thumbAjax = new Ajax.Request(thumburl, {method:'get', onSuccess:function(t){
	tempLocation = t.responseText.split("<li>");
	tempLocation2 = tempLocation[1].split("\\");

			thumburl2 = '/xbmcCmds/xbmcHttp?command=filedownload&parameter='+escape(tempLocation);
   			thumbAjax2 = new Ajax.Request(thumburl2, {method:'get', onSuccess:function(y){

				tempLocation3 = y.responseText.split("<li>");
				imageData = tempLocation3[0];

		if(imageData.length > 1){
				$(returnDiv).innerHTML = '<img src="data:image/jpg;base64,'+ imageData + '"  align=left hspace=5 >';
		}else{
				$(returnDiv).innerHTML = '<img src="images/defaultAlbumCover.png"  align=left hspace=5 >';
		}


			}, onFailure:connectionFailure});


	}});

}



function GeneratePlaylistM3U(playlistName){

	playlistContents="";
	playlistNum = currentPlaylist; //Playlist currentPlaylist is the default

     var url = '/xbmcCmds/xbmcHttp?command=GetPlaylistContents&parameter='+playlistNum+'&rand='+Math.random(50);
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){



	responseArr = t.responseText.split("<li>");




	for (var i=0;i<responseArr.length;i++){

	if((responseArr[i]!="") && (escape(responseArr[i]) != "%0A")){

		mediapath = responseArr[i];


	if(responseArr[i] != "html>"){

playlistContents += responseArr[i] + "\n\r";



	}
	}
	}


SavePlaylist(playlistName, playlistContents);



}});

}

function SavePlaylist(playlistName, playlistContents){


//alert("saving playlist string:"+playlistName+"----"+playlistContents);

playlistContents64 = encodeBase64(playlistContents)

//alert("base64 string:"+playlistContents64);

     var url = '/xbmcCmds/xbmcHttp?command=FileUpload&parameter='+playlistLocation+playlistName+';'+playlistContents64+'&rand='+Math.random(50);
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){

	//	responseArr = t.responseText.split(":");
	//	$(currentlyPlayingText).innerHTML = responseArr[1];


	disableKeys = false;
	closeKeyboard();
	getMediaLocation(playlistLocation);

		}});

}

function listPlaylists(){
	var url = 'viewPlaylist.asp?path='+playlistLocation+'&rand='+Math.random(50);
    var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(obj){pushMediaList(obj);}});


}

function AddToPlayList(mediapath){
     var url = '/xbmcCmds/xbmcHttp?command=AddToPlayList&parameter='+mediapath;
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){getPlaylistContents()}, onFailure:connectionFailure});

}

function xbmcCmds(command, callbackFunction){

     var url = '/xbmcCmds/xbmcHttp?command='+command+'&rand='+Math.random(50);
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){
    	callbackFunction(t.responseText);
		}});

}

function ExecBuiltIn(command){

     var url = '/xbmcCmds/xbmcHttp?command=ExecBuiltIn&parameter='+command+'&rand='+Math.random(50);
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){
    	//callbackFunction(t.responseText);
		}});

}

var mainPlayTransport = false; //isCurrentlyPlaying?

function swapPlayTransport(){


if(!mainPlayTransport){ //start playback and change icon
document.getElementById("mainTransport").innerHTML = '<IMG SRC="images/transport_pause.png" ALT="" border="0">';
SetCurrentPlaylist(currentPlaylist);
//xbmcCmds('setplaylistsong&parameter=0');
xbmcCmds('pause');
mainPlayTransport = !mainPlayTransport;

}else{ //pause playback and change icon
document.getElementById("mainTransport").innerHTML = '<IMG SRC="images/transport_play2.png" ALT="" border="0">';
xbmcCmds('pause');
mainPlayTransport = !mainPlayTransport;
}


}

function setupMenubars(sectionId){
	if(sectionId=="browser"){
	$('titlebox').innerHTML = "Media Library";
	document.getElementById('titlebuttons_browser').style.display='block';
	document.getElementById('titlebuttons_playlist').style.display='none';
//	document.getElementById('musiclibraryHolder').style.overflow='scroll';
	}else if(sectionId=="volume"){
	$('titlebox').innerHTML = "Volume Controls";
	document.getElementById('titlebuttons_browser').style.display='none';
	document.getElementById('titlebuttons_playlist').style.display='none';
//	document.getElementById('musiclibraryHolder').style.overflow='';
	}else if(sectionId=="playlist"){
	$('titlebox').innerHTML = "Playlist";
	document.getElementById('titlebuttons_browser').style.display='none';
	document.getElementById('titlebuttons_playlist').style.display='block';
	}
		currentSection = sectionId;
}

function pullScript(fileName)
{
var oHead = document.getElementsByTagName("HEAD")[0];
var oScript = document.createElement('script');
oScript.setAttribute('src',fileName);
oScript.setAttribute('type','text/javascript');
oHead.appendChild(oScript);
}

function GetVolume(){
     var url = '/xbmcCmds/xbmcHttp?command=GetVolume';
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){

	//	responseArr = t.responseText.split("<li>");

	//	alert(t.responseText);

		document.getElementById('currentVolume').value=t.responseText;


		}, onFailure:getPlaylistFailure});
}


function volumeCtrl(direction){
if(direction == "up"){

	if(!custom){
	     var url = '/xbmcCmds/xbmcHttp?command=SetVolume&parameter='+(parseInt(document.getElementById('currentVolume').value)+5);
	     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:GetVolume, onFailure:getPlaylistFailure});
	}else{
		pullScript("http://10.0.0.40/pullJS.asp?direction=up");
	}

}else{

	if(!custom){
	     var url = '/xbmcCmds/xbmcHttp?command=SetVolume&parameter='+(parseInt(document.getElementById('currentVolume').value)-5);
	     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:GetVolume, onFailure:getPlaylistFailure});
	}else{
		pullScript("http://10.0.0.40/pullJS.asp?direction=down");
	}




}
}


function createRequestObject() {
    var ro;
    var browser = navigator.appName;
    if(browser == "Microsoft Internet Explorer"){
        ro = new ActiveXObject("Microsoft.XMLHTTP");
    }else{
        ro = new XMLHttpRequest();
    }
    return ro;
}

var http = createRequestObject();



function getContent(options){

	if(options == "covers"){
		showAlbumArt();
	}else if(options == "home"){



		resultsHTML = "<div align='center'><font size=6>Browse</font>";

		resultsHTML += "<table><tr><td><div class=menu3><ul><li><a href='javascript:getContent(\"covers\")'>By CoverArt</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:getContent(\"artist\")'>By Artist</a></li></ul></div>";
		resultsHTML += "</td><td><div class=menu3><ul><li><a href='javascript:getContent(\"playlist\")'>By Playlist</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:getContent(\"home\")'>By --</a></li></ul></div>";
		resultsHTML += "</td><td><div class=menu3><ul><li><a href='javascript:getContent(\"album\")'>By Album</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:getContent(\"folder\")'>By Folder</a></li></ul></div></td></tr></table><br>";


	resultsHTML += 'Search by Artist:<br><input id="artistsearchbox" type="text" value=""><input value="Search" type="button" onclick="searchArtist(\'\'+$(\'artistsearchbox\').value+\'%\')"><br><br>';

	resultsHTML += 'Search by Song Name:<br><input id="songsearchbox" type="text" value=""><input value="Search" type="button" onclick="searchSongs(\'%%\'+document.getElementById(\'songsearchbox\').value+\'%%\')"><br>';

	resultsHTML += '</div>';

		document.getElementById("musiclibrary").innerHTML = resultsHTML;

	}else if(options == "folder"){
		navigateToLocation("");
	}else if(options == "playlist"){
		//navigateToLocation("playlists://");
		getDirectory(playlistLocation);


	}else if(options == "config"){
		document.getElementById("musiclibrary").innerHTML = "<iframe src='config.asp?DisplayConfiguration=true&page=bookmarks' width=99% height=100%></iframe>";

	}else if(options == "artist"){
	//searchArtist	("B");

		resultsHTML = "<SPAN ALIGN='CENTER'><div class=menu3><ul><li><a href='javascript:searchArtist(\"A%\")'>A</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"B%\")'>B</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"C%\")'>C</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"D%\")'>D</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"E%\")'>E</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"F%\")'>F</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"G%\")'>G</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"H%\")'>H</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"I%\")'>I</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"J%\")'>J</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"K%\")'>K</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"L%\")'>L</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"M%\")'>M</a></li></ul></div><br><br><br><br><br>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"N%\")'>N</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"O%\")'>O</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"P%\")'>P</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"Q%\")'>Q</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"R%\")'>R</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"S%\")'>S</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"T%\")'>T</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"U%\")'>U</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"V%\")'>V</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"W%\")'>W</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"X%\")'>X</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"Y%\")'>Y</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchArtist(\"Z%\")'>Z</a></li></ul></div></SPAN>";


		document.getElementById("musiclibrary").innerHTML = resultsHTML;
//resize div
resize();

	}else if(options == "album"){

		resultsHTML = "<SPAN ALIGN='CENTER'><div class=menu3><ul><li><a href='javascript:searchAlbum(\"A%\")'>A</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"B%\")'>B</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"C%\")'>C</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"D%\")'>D</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"E%\")'>E</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"F%\")'>F</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"G%\")'>G</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"H%\")'>H</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"I%\")'>I</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"J%\")'>J</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"K%\")'>K</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"L%\")'>L</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"M%\")'>M</a></li></ul></div><br><br><br><br><br>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"N%\")'>N</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"O%\")'>O</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"P%\")'>P</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"Q%\")'>Q</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"R%\")'>R</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"S%\")'>S</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"T%\")'>T</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"U%\")'>U</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"V%\")'>V</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"W%\")'>W</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"X%\")'>X</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"Y%\")'>Y</a></li></ul></div>";
		resultsHTML += "<div class=menu3><ul><li><a href='javascript:searchAlbum(\"Z%\")'>Z</a></li></ul></div></SPAN>";


		document.getElementById("musiclibrary").innerHTML = resultsHTML;

	}else if(options == "w"){

	}else if(options == "e"){




	}


}


numofCoverArtItems = 0;


function countCoverArt(){


var sqlquery = "select count(*) from albumview WHERE strThumb != 'NONE' ;";

     var url = "/xbmcCmds/xbmcHttp?command=QueryMusicDatabase&parameter="+sqlquery+'&rand='+Math.random(50);

     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){
			responseArr = t.responseText.split("<li>");

	//Number of covers
	//alert(responseArr[1]);

	numofCoverArtItems = responseArr[1];

document.getElementById("nextX").style.display = "block";
if(parseInt(numofCoverArtItems)> parseInt(startAt) + 50){
	document.getElementById("nextX").style.display = "block";
}
if(parseInt(startAt) >= maxItems){
	document.getElementById("prevX").style.display = "block";
}

		}});

}


function showAlbumArt(startAt){

document.getElementById("musiclibrary").innerHTML = "";

if(startAt == undefined){
startAt = 0
}

var sqlquery = "SELECT idAlbum, strAlbum, strArtist, strThumb  from albumview WHERE strThumb != 'NONE' LIMIT "+ startAt +","+ maxItems +";";

     var url = "/xbmcCmds/xbmcHttp?command=QueryMusicDatabase&parameter="+sqlquery+'&rand='+Math.random(50);

resultsHTML = "";
//resultsHTML = "<b>"+unescape(sqlquery)+"</b><br><br>";


     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){


		responseArr = t.responseText.split("<li>");

	numalbums = (responseArr.length - 1) / 4;

	resultsHTML += "<table>";


			while(responseArr.length>1){


	numalbums = numalbums - 1;

			//We know that we pulled 4 columns,
			//so we can pop off 4 at a time for each song
			strThumb = responseArr.pop();
			strArtist = responseArr.pop();
			strAlbum = responseArr.pop();
			idAlbum = responseArr.pop();

			//document.write("strThumb:"+strThumb+"<br>");
			//document.write("idAlbum:"+idAlbum+"<br>");
			//document.write("strAlbum:"+strAlbum+"<br>");
			//document.write("strArtist:"+strArtist+"<br>");
			//document.write("<br><br>"+"<br>");


thumb = strThumb.split("\\");
thisthumb = thumb[thumb.length -1];
thumb = thisthumb.split(".");
thisthumb = thumb[0]+".jpg";


if(thisthumb != ""){


if(numalbums%2 == "1"){
	resultsHTML += "<tr><td width='50%'>";
}else{
	resultsHTML += "<td width='50%'>";
}



	resultsHTML += '<table><tr><td><a href="javascript:playAlbum('+idAlbum+');GetCurrentlyPlaying();getPlaylistContents(0);setupMenubars(\"playlist\");" style="text-decoration:none;">';

	resultsHTML += "<img src='musicthumbs/"+thisthumb+"' width=100 height=100 border=0></a></td><td valign=top>";
	//resultsHTML += "<a href=\"javascript:SetCurrentPlaylist(currentPlaylist);xbmcCmds('clearplaylist');pausecomp(1000);SetCurrentPlaylist(currentPlaylist);pausecomp(1000);AddToPlayList('"+urlSafeMediaPath+"/');xbmcCmds('setplaylistsong&parameter=0');setupMenubars('playlist');\"><img border=0 align='bottom' src='images/play.png'/> PLAY</a>";
	//xbmcCmds('setplaylistsong&parameter=0');setupMenubars('playlist');

	resultsHTML += "<a href=\"javascript:playAlbum("+idAlbum+");GetCurrentlyPlaying();getPlaylistContents(0);setupMenubars('playlist');\" style=\"text-decoration:none;\"><img border=0 align='bottom' src='images/play.png'/> PLAY</a>";


	resultsHTML += "<br><b>"+strAlbum+"</b><br>"+strArtist+"</td></tr></table>";

if(numalbums%2 == "0"){
	resultsHTML += "</td></tr>";
}else{
	resultsHTML += "</td>";
}




}


			}
	resultsHTML += "</table>";

	resultsHTML += "<div style='display:none' id='prevX'><a href='javascript:showAlbumArt("+ ( parseInt(startAt) - parseInt(maxItems) ) +");'>Prev "+maxItems+"</a></div>";

	resultsHTML += "<div style='display:none' id='nextX'><a href='javascript:showAlbumArt("+ (parseInt(startAt) + parseInt(maxItems)) +");'>Next "+maxItems+"</a></div>";


document.getElementById("musiclibrary").innerHTML = resultsHTML;


if(numofCoverArtItems == 0){
	countCoverArt();
}else{


if(numofCoverArtItems> parseInt(startAt) + parseInt(maxItems)){
	document.getElementById("nextX").style.display = "block";
}
if(parseInt(startAt) >= maxItems){
	document.getElementById("prevX").style.display = "block";
}

//	alert(document.getElementById("nextX").style.display);

}




		}});

}


function searchArtist(artistName, startAt){

if(startAt == undefined){
startAt = 0
}

document.getElementById("musiclibrary").innerHTML = "";

if (artistName == undefined){
	artistName = "";
}

lastStrArtist = "";

var sqlquery = "SELECT idArtist, strFilename, strTitle, strAlbum, strArtist, dwFileNameCRC, strThumb  from songview WHERE strArtist LIKE '"+artistName+"' order by strArtist DESC LIMIT "+ startAt +","+ maxItems +";";

     var url = "/xbmcCmds/xbmcHttp?command=QueryMusicDatabase&parameter="+sqlquery+'&rand='+Math.random(50);

resultsHTML = "";
//resultsHTML = "<b>"+unescape(sqlquery)+"</b><br><br>"
resultsHTML += "<span><blockquote>";

var	myUniques = [];

     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){


		responseArr = t.responseText.split("<li>");


	numalbums = (responseArr.length - 1) / 7;



			while(responseArr.length>1){

			//We know that we pulled 4 columns,
			//so we can pop off 4 at a time for each song
			strThumb = responseArr.pop();
			crc	= responseArr.pop();
			strArtist = responseArr.pop();
			strAlbum = responseArr.pop();
			strTitle = responseArr.pop();
			strFilename = responseArr.pop();
			idArtist = responseArr.pop();

			thumb = strThumb.split("\\");
			thisthumb = thumb[thumb.length -1];

			numalbums = numalbums - 1;


if(lastStrArtist != idArtist){
myUniques.push(idArtist);


	resultsHTML += "</blockquote></span>";

	resultsHTML += "<table><tr><td></td><td valign=top><a href=\"javascript:showMedia('artist"+ idArtist +"')\"><img border=0 align='bottom' src='images/music.png'/></a> "+" <b>"+strArtist+"</b></td></tr></table>";


	resultsHTML += "<span style='display:none' id='artist"+idArtist+"'><img border=0 align='bottom' src='images/music.png'/> "+" <b>"+strArtist+"</b><blockquote>";
}



//Just play buttons no playlist
//	resultsHTML += "<div onclick=\"javascript:PlayMediaCRC('"+crc+"')\"><table><tr><td></td><td valign=top><a href=\"#\"><img border=0 align='bottom' src='images/play.png'/></a> "+" <b>"+strTitle+"</b></td></tr></table></div>";

	resultsHTML += "<div><table><tr><td><a href=\"javascript:AddMediaCRC('"+crc+"')\"><img border=0 align='bottom' src='images/addtoplaylist.gif'/></a> </td><td valign=top><a href=\"javascript:PlayMediaCRC('"+crc+"')\"><img border=0 align='bottom' src='images/play.png'/></a> "+" <b>"+strTitle+"</b></td></tr></table></div>";



lastStrArtist = idArtist;

			}


	resultsHTML += "</blockquote></span>";


document.getElementById("musiclibrary").innerHTML = resultsHTML;

		}});




		}



function searchAlbum(albumName, startAt){

document.getElementById("musiclibrary").innerHTML = "";

if(startAt == undefined){
	startAt = 0
}

if (albumName == undefined){
	albumName = "";
}

lastStrArtist = "";

var sqlquery = "SELECT idAlbum, strFilename, strTitle, strAlbum, strArtist, dwFileNameCRC, strThumb  from songview WHERE strAlbum LIKE '"+albumName+"' order by idAlbum DESC LIMIT "+ startAt +","+ maxItems +";";

     var url = "/xbmcCmds/xbmcHttp?command=QueryMusicDatabase&parameter="+sqlquery+'&rand='+Math.random(50);

resultsHTML = "";
//resultsHTML = "<b>"+unescape(sqlquery)+"</b><br><br>"
resultsHTML += "<span><blockquote>";

var	myUniques = [];

     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){


		responseArr = t.responseText.split("<li>");


	numalbums = (responseArr.length - 1) / 7;



			while(responseArr.length>1){

			//We know that we pulled 4 columns,
			//so we can pop off 4 at a time for each song
			strThumb = responseArr.pop();
			crc	= responseArr.pop();
			strArtist = responseArr.pop();
			strAlbum = responseArr.pop();
			strTitle = responseArr.pop();
			strFilename = responseArr.pop();
			idAlbum = responseArr.pop();

			thumb = strThumb.split("\\");
			thisthumb = thumb[thumb.length -1];

			thumbname = thisthumb.split(".");
			thisthumb = thumbname[0]+".jpg"; //give it the correct filename

			numalbums = numalbums - 1;


if(lastStrArtist != idAlbum){
myUniques.push(idAlbum);


	resultsHTML += "</blockquote></span>";

	resultsHTML += "<table><tr><td></td><td valign=top><a href=\"javascript:playAlbum("+idAlbum+");GetCurrentlyPlaying();getPlaylistContents(0);setupMenubars('playlist');\" style=\"text-decoration:none;\"><img border=0 align='bottom' src='images/play.png'/></a></a>  <a href=\"javascript:showMedia('album"+ idAlbum +"')\"><img border=0 align='bottom' src='images/music.png'/></a> "+" <b>"+strAlbum+"</b></td></tr></table>";


	resultsHTML += "<span style='display:none' id='album"+idAlbum+"'>";

if(thisthumb != "NONE.jpg"){
	resultsHTML += "<img src='musicthumbs/"+ thisthumb +"' width=150 height=150 align='right'>";
}

	resultsHTML += "<img border=0 align='bottom' src='images/music.png'/> "+" <b>"+strAlbum+"</b><blockquote>";
}



//Just play buttons no playlist
//	resultsHTML += "<div onclick=\"javascript:PlayMediaCRC('"+crc+"')\"><table><tr><td></td><td valign=top><a href=\"#\"><img border=0 align='bottom' src='images/play.png'/></a> "+" <b>"+strTitle+"</b></td></tr></table></div>";

	resultsHTML += "<div><table><tr><td><a href=\"javascript:AddMediaCRC('"+crc+"')\"><img border=0 align='bottom' src='images/addtoplaylist.gif'/></a> </td><td valign=top><a href=\"javascript:PlayMediaCRC('"+crc+"')\"><img border=0 align='bottom' src='images/play.png'/></a> "+" <b>"+strTitle+"</b></td></tr></table></div>";



lastStrArtist = idAlbum;

			}


	resultsHTML += "</blockquote></span>";


document.getElementById("musiclibrary").innerHTML = resultsHTML;

		}});


	resultsHTML += "<div style='display:none' id='prevX'><a href='javascript:searchAlbum(albumName, (parseInt(startAt) - parseInt(maxItems)))'>Prev "+maxItems+"</a></div>";

	resultsHTML += "<div style='display:none' id='nextX'><a href='javascript:searchAlbum(albumName, (parseInt(startAt) + parseInt(maxItems)))'>Next "+maxItems+"</a></div>";



if(numalbums> parseInt(startAt) + parseInt(maxItems)){
	document.getElementById("nextX").style.display = "block";
}
if(parseInt(startAt) >= maxItems){
	document.getElementById("prevX").style.display = "block";
}


		}


function showMedia(clickedId){

	myContent = document.getElementById(clickedId).innerHTML;
	win = new Window(clickedId+"_win", {className: "alphacube",  width:780, height:300, resizable: true, showEffect:Element.show, hideEffect: Effect.SwitchOff, draggable:false, destroyOnClose:true})
	win.getContent().innerHTML=myContent;
	win.showCenter();

}


function searchSongs(songName, startAt){

if(startAt == undefined){
startAt = 0
}

document.getElementById("musiclibrary").innerHTML = "";

lastStrArtist = "";

var sqlquery = "SELECT idArtist, strFilename, strTitle, strAlbum, strArtist, dwFileNameCRC, strThumb  from songview WHERE strFilename LIKE '"+songName+"' order by strTitle DESC LIMIT "+ startAt +","+ maxItems +";";

     var url = "/xbmcCmds/xbmcHttp?command=QueryMusicDatabase&parameter="+sqlquery+'&rand='+Math.random(50);

resultsHTML = "";
resultsHTML = "<b>"+unescape(sqlquery)+"</b><br><br>"
resultsHTML += "<span><blockquote>";

var	myUniques = [];

     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){


		responseArr = t.responseText.split("<li>");


	numalbums = (responseArr.length - 1) / 7;



			while(responseArr.length>1){

			//We know that we pulled 4 columns,
			//so we can pop off 4 at a time for each song
			strThumb = responseArr.pop();
			crc	= responseArr.pop();
			strArtist = responseArr.pop();
			strAlbum = responseArr.pop();
			strTitle = responseArr.pop();
			strFilename = responseArr.pop();
			idArtist = responseArr.pop();

			thumb = strThumb.split("\\");
			thisthumb = thumb[thumb.length -1];

			numalbums = numalbums - 1;


if(lastStrArtist != strArtist){
//myUniques.push(idArtist);

	resultsHTML += "</blockquote></span><span id='artist"+idArtist+"'><a href=\"javascript:showMedia('artist"+ idArtist +"')\"><img border=0 align='bottom' src='images/music.png'/></a> "+" <b>"+strArtist+"</b><blockquote>";
}



//Just play buttons no playlist
//	resultsHTML += "<div onclick=\"javascript:PlayMediaCRC('"+crc+"')\"><table><tr><td></td><td valign=top><a href=\"#\"><img border=0 align='bottom' src='images/play.png'/></a> "+" <b>"+strTitle+"</b></td></tr></table></div>";

	resultsHTML += "<div><table><tr><td><a href=\"javascript:AddMediaCRC('"+crc+"')\"><img border=0 align='bottom' src='images/addtoplaylist.gif'/></a> </td><td valign=top><a href=\"javascript:PlayMediaCRC('"+crc+"')\"><img border=0 align='bottom' src='images/play.png'/></a> "+" <b>"+strTitle+"</b></td></tr></table></div>";

lastStrArtist = strArtist;

			}


	resultsHTML += "</blockquote></span>";


document.getElementById("musiclibrary").innerHTML = resultsHTML;

		}});




		}






//	navigateToLocation("");
	atimer = window.setInterval("GetCurrentlyPlaying()", 5000);

//	setupMenubars("browser");

getContent("home");
//resize div
resize();
</script>




</div>
</body>
</html>

