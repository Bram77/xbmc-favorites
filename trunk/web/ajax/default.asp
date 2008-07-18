<html>
<head>
<title>XBMC AJAX Control Interface</title>
<link rel="stylesheet" href="css/ajax.css" type="text/css" media="screen" />
<link type="text/css" rel="StyleSheet" href="css/luna/luna.css" />

<script type="text/javascript" src="js/stringUtils.js"></script>
<script type="text/javascript" src="js/layout.js"></script>
<script type="text/javascript" src="js/prototype.js" ></script>
<script type="text/javascript" src="js/scriptaculous.js" ></script>
<script type="text/javascript" src="js/effects2.js"></script>
<script type="text/javascript" src="js/range.js"></script>
<script type="text/javascript" src="js/timer.js"></script>
<script type="text/javascript" src="js/slider.js"></script>


<script>
var disableKeys = false;
var pollInProgress = false;
var musicListItem = [];
var supportedAudioExtentions = "";
var supportedVideoExtentions = "";

var lastMenuItem = 0;
var lastMenuMusicItem = 0;
var lastMusicLibItem = new Array();
var lastNavigationItem = 0;

//This is used to control reciever volume via control system - has nothing to do with xbmc
var custom = false;
var customIP = "10.0.0.40";

var effectInProgress = false;

<%
    navigatorstate = xbmcCommand("navigatorstate");

    if (navigatorstate == "pictures"){
		write('var currentPlaylist = "0";')
		write('var currentMediaType = "pictures";')
    } else if (navigatorstate == "music") {
		write('var currentPlaylist = "0";')
		write('var currentMediaType = "music";')
    } else if (navigatorstate == "videos") {
		write('var currentPlaylist = "2";')
		write('var currentMediaType = "videos";')
    } else {
		write('var currentPlaylist = "0";')
		write('var currentMediaType = "music";')
	}



%>

function connectToXbox(){

    xbmcCmds('config&parameter=getoption;musicextensions', musicExtentions);
    xbmcCmds('config&parameter=getoption;videoextensions', videoExtentions);

	navigateToLocation("");
	window.setInterval("GetCurrentlyPlaying()", 5000);
	window.setInterval("GetVolume()", 60000);

	GetVolume();
	GetCurrentlyPlaying();
	SetCurrentPlaylist(currentPlaylist);	

	resize();

}


</script>

</head>

<BODY scroll="no" bgcolor="#1E3B70" background="bckg.gif" margintop=0 marginleft=10 marginright=10 topmargin=0 leftmargin=0  onresize="resize()">

<script>
	//init calls to make httpapi easier to parse
	
	     var url4 = '/xbmcCmds/xbmcHttp?command=SetResponseFormat&parameter=webheader;';
	     var setup4 = new Ajax.Request(url4, {method:'get'});
	
	     var url5 = '/xbmcCmds/xbmcHttp?command=SetResponseFormat&parameter=webfooter;';
	     var setup5 = new Ajax.Request(url5, {method:'get'});
	
	     var url7 = '/xbmcCmds/xbmcHttp?command=setAutoGetPictureThumbs&parameter=true;';
	     var setup7 = new Ajax.Request(url7, {method:'get'});
	

	/*
	//optional init calls
	
	     var url1 = '/xbmcCmds/xbmcHttp?command=SetResponseFormat&parameter=closetag;<li>';
	     var setup1 = new Ajax.Request(url1, {method:'get'});
	
	     var url2 = '/xbmcCmds/xbmcHttp?command=SetResponseFormat&parameter=opentag;';
	     var setup2 = new Ajax.Request(url2, {method:'get'});
	
	     var url3 = '/xbmcCmds/xbmcHttp?command=SetResponseFormat&parameter=closefinaltag;';
	     var setup3 = new Ajax.Request(url3, {method:'get'});
	
	
	
	*/
</script>


<div align="center" id="onscreenkeyboard" style="display:none;left:0px;top:100px;z-index:1000;width:100%;float:left;position:absolute;">
<table bgcolor="#EfEfEf"><tr><td bgcolor="black">
<table width="100%"><tr><td><h3>Save File As...</h3></td><td width="15"><h3><a onclick="javascript:closeKeyboard();">X</a></h3></td></tr></table>
</td></tr>
<tr><td>
<div align="center">


<script>

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






<div align="center" id="guiControl" style="display:none;left:0px;top:50px;z-index:1001;width:100%;float:left;position:absolute;">
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

function XBMCkeyPressed(keyToSend){


SendKey(keyToSend);
showLargeScreenshot();

}
</script>

<table><tr><td width="640">
<div id="largeScreenshot"></div>
</td><td>

<map name="FPMap0">
<area href="javascript:XBMCkeyPressed('m')" shape="rect" coords="0, 294, 53, 479">
<area href="javascript:XBMCkeyPressed('258')" shape="circle" coords="103, 344, 44">
<area href="javascript:XBMCkeyPressed('256')" shape="circle" coords="191, 319, 42">
<area href="javascript:XBMCkeyPressed('257')" shape="circle" coords="198, 403, 43">
<area href="javascript:XBMCkeyPressed('274')" shape="rect" coords="9, 227, 88, 279">
<area href="javascript:XBMCkeyPressed('275')" shape="rect" coords="93, 225, 169, 275">
<area href="javascript:XBMCkeyPressed('256')" shape="rect" coords="109, 86, 189, 138">
<area href="javascript:XBMCkeyPressed('270')" shape="polygon" coords="71, 36, 111, 76, 178, 76, 220, 32, 145, 3">
<area href="javascript:XBMCkeyPressed('273')" shape="polygon" coords="187, 81, 223, 42, 250, 101, 250, 123, 223, 178, 190, 148, 202, 111, 193, 74, 193, 73, 193, 75, 193, 69, 196, 69, 197, 72">
<area href="javascript:XBMCkeyPressed('271')" shape="polygon" coords="111, 153, 145, 164, 183, 150, 218, 185, 162, 211, 135, 211, 80, 186">
<area href="javascript:XBMCkeyPressed('272')" shape="polygon" coords="105, 78, 72, 44, 47, 89, 45, 116, 68, 175, 105, 144, 92, 111">
<area href="javascript:XBMCkeyPressed('256')" shape="circle" coords="101, 438, 42">
<area href="javascript:XBMCkeyPressed('261')" shape="rect" coords="177, 223, 227, 267">
<area href="javascript:XBMCkeyPressed('260')" shape="rect" coords="238, 222, 294, 268">
</map>
<img border="0" src="images/controllerPanel.png" width="300" height="480"  usemap="#FPMap0">
</td></tr></table>


</td></tr>
</table>
</div>

<input id="currentVolume" type="hidden" value="50">

<div id="browserArea">





<div style="width:100%;float:left;height:170px;width:100%;">
<h3>Currently Playing</h3>

<div style="float:left;width:50%;">
<table><tr><td><span id='albumArt'><img src='images/defaultAlbumCover.png'></span></td><td valign="top">



<table><tr><td>
 <div id="currentlyPlayingText" style="float:left;color:#FFFFFF">

 </div>
</td></tr>
<tr><td>

<div class="slider" id="slider-1" tabIndex="1"><input class="slider-input" id="slider-input-1"   name="slider-input-1"/></div>


<script>
var s = new Slider(document.getElementById("slider-1"),                  document.getElementById("slider-input-1"));


</script>
</td></tr></table>


</td></tr>
</table>
</div>


<div style="position:absolute;top:30;right:5;">
<table><tr>
<td>
<a href="javascript:xbmcCmds('play');GetCurrentlyPlaying();"><img src="images/transport_play2.png" border=0 align="left"></a>
</td><td>
<a href="javascript:xbmcCmds('pause');GetCurrentlyPlaying();"><img src="images/transport_pause.png" border=0 align="left"></a>
</td><td>
<a href="javascript:xbmcCmds('stop');GetCurrentlyPlaying();"><img src="images/transport_stop.png" border=0 align="left"></a>
</td><td>
<a href="javascript:xbmcCmds('playPrev');GetCurrentlyPlaying();"><img src="images/transport_prev.png" border=0 align="left"></a>
</td><td>
<a href="javascript:xbmcCmds('playNext');GetCurrentlyPlaying();"><img src="images/transport_next.png" border=0 align="left"></a>
</td>
</tr>
<tr><td>
<a href="javascript:back();"><img src="images/home6.png" border=0 align="left"></a>
</td>
<td>
<a href="javascript:showScreen();showLargeScreenshot()"><img src="images/gui_control.png" border=0 align="left"></a>
</td>
<td></td><td>
<a href="javascript:volumeCtrl('down');"><img src="images/voldn.png" border=0 align="left"></a>
</td><td>
<a href="javascript:volumeCtrl('up');"><img src="images/volup.png" border=0 align="left"></a>
</td></tr></table>
</div>

</div>

<br><br><br>


<div style="width:50%; float:right;">
 <h3>Playlist</h3>
<ul class="menu4">
<li><a href="javascript:SetCurrentPlaylist(currentPlaylist);xbmcCmds('setplaylistsong&parameter=0');GetCurrentlyPlaying();"><img src="images/startplaylist.png" border="0"> Start Playing</a>
<li><a href="javascript:showKeyboard()"><img src="images/saveplaylist.png" border="0"> Save Playlist</a>
<li><a href="javascript:SetCurrentPlaylist(currentPlaylist);xbmcCmds('clearplaylist');GetCurrentlyPlaying();"><img src="images/clearplaylist.png" border="0"> Clear PlayList</a>
</ul>

 <div id="playlist-div" style="float:left;width:100%;height:80%;overflow:auto;z-index:10;">
<ul class="playlist" id="playlist"></ul>
</div>
</div>	  

	  
<div style="width:50%; float:left;">
<h3>Music Library</h3>
<ul class="menu4" id="topbuttons">
<li><a href='javascript:setMediaType("videos");'><img src="images/movie.png" border="0"> Videos</a>
<li><a href='javascript:setMediaType("music");'><img src="images/music.png" border="0"> Music</a>
<li><a href='javascript:setMediaType("pictures");'><img src="images/image.png" border="0"> Pictures</a>
</ul>


<div id='musiclibraryHolder' style="width:100%;height:80%;overflow:auto;float:left;">
	<ul class="musiclibrary" align="left"  id="musiclibrary"> 

	 </ul>
</div>
</div>


 <script type="text/javascript">

//////////////////////////////////
//Drag and Drop Code
//////////////////////////////////
    Droppables.add('playlist-div', {accept: 'green',onDrop: function(element, droppableElement)
           {

			//alert("Dropped    "+element.id+"   "+element.attributes.getNamedItem('mediapath').nodeValue);
			//SetCurrentPlaylist(currentPlaylist);
			AddIdToPlayList(element.attributes.getNamedItem('mediapath').nodeValue);
            }
            });


function asignDragAndDrop(idArray)
{

        var windowIdArray = idArray;
        for(i=0;i<windowIdArray.length;i++)
    {
        var windowId = windowIdArray[i];
        //set to be draggable
        new Draggable(windowId,{revert:true,ghosting:true});
    }
}


function refreshDraggables(){

	asignDragAndDrop(document.getElementsByClassName('green'));

}

function showMenu2(elementId, isFolder){
//placeholder
}


function showMenu(elementId, isFolder){
	itemControlsPath = elementId.replace('musiclibrary', 'itemControls');

			if(lastMenuItem != ""){
			lastmusiclibArtPath = lastMenuItem.replace('itemControls', 'musiclibArt');
			lastMenuMusicItem = lastMenuItem.replace('itemControls', 'musiclibrary');
			$(lastmusiclibArtPath).innerHTML = "<img src='images/folder_small.png'  align=left hspace=20 onClick='javascript:getMediaLocation(\""+$(lastMenuMusicItem).mediapath+"\");'>";
			new Effect.Scale(lastMenuMusicItem, 25, {scaleX:false, scaleY:true, scaleContent:false});
			}
		urlSafeMediaPath = $(elementId).attributes['mediapath'].value;

		justFilePath = urlSafeMediaPath.split("%2F");
		justFilePath = justFilePath.slice(0,-1);
		justFilePath = justFilePath.join("%2F");
		urlSafeMediaDirectory =justFilePath;

		if(urlSafeMediaDirectory == ""){
		
		urlSafeMediaDirectory = urlSafeMediaPath;		
		
		}
	//	alert(":"+ urlSafeMediaDirectory +":");

	musiclibArtPath = elementId.replace('musiclibrary', 'musiclibArt');


id_lastMenuItem = lastMenuItem.replace('itemControls', '');
id_elementId = elementId.replace('musiclibrary', '');

	if(id_lastMenuItem != id_elementId && !effectInProgress){

//alert("not the second time:"+lastMenuItem+"  isOpen:"+$(elementId).attributes.isOpen.value + "   elementId:"+elementId+"  id_lastMenuItem:"+id_lastMenuItem+"  itemControlsPath:"+itemControlsPath+" "+"  itemControlsPath.innerHTML:"+$(itemControlsPath).innerHTML);


effectInProgress = true;
	var slideeffect = new Effect.Scale(elementId, 400, {scaleX:false, scaleY:true, scaleContent:false, queue: 'end', afterFinish:function(){

		new Effect.PhaseIn(musiclibArtPath);

//	showThumbnail($(elementId)['Thumb'], musiclibArtPath);

//////////////////////////////////////////////////////////////////////

	     var url = '/xbmcCmds/xbmcHttp?command=gettagfromfilename&parameter='+urlSafeMediaPath;
	     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(u){
	
		subresponseArr = u.responseText.split("<li>");
	
		for (j=0;j<subresponseArr.length-1;j++){
	
if (subresponseArr[j] != ""){
	
			responseArr2 = subresponseArr[j].split(":");

if (responseArr2[0] != ""){
//alert("responseArr2.length:"+responseArr2.length);
			if(responseArr2.length < 2){
			//	elementName = responseArr2[0];
			//	responseArr2 = responseArr2.slice(1);
		//		elementValue = responseArr2.join(":");
			//	alert(elementName+'='+elementValue);
	
		//		$('elementId')[elementName] = elementValue;
//	alert(elementId + "  " +elementName+" = "+elementValue);
			}else{
//	alert(""+responseArr2[0] +"="+ responseArr2[1]);
	
	//		    $('elementId')[responseArr2[0]] = responseArr2[1];

			}

}
}

		}
	//	alert("showing thumbnail for: "+$(elementId).Thumb);


			}, onFailure:getPlaylistFailure});
////////////////////////////////////////////////////////////////////


effectInProgress = false;

	}

	});


	lastMenuItem = elementId.replace('musiclibrary', 'itemControls');

	}else{
slideeffect = "";

	//	$(itemControlsPath).innerHTML = "";
		lastmusiclibArtPath = lastMenuItem.replace('itemControls', 'musiclibArt');

		$(lastmusiclibArtPath).innerHTML = "<img src='images/folder_small.png'  align=left hspace=20 onClick='javascript:getMediaLocation(\""+urlSafeMediaPath+"\");'>";


		//	new Effect.Scale(lastMenuItem, 25, {scaleX:false, scaleY:true, scaleContent:false});


	lastMenuItem = "";

	}

}



//////////////////////////////////
//// XBMC Commands
//////////////////////////////////

function SetCurrentPlaylist(playlistId){
currentPlaylist = playlistId;
var url6 = '/xbmcCmds/xbmcHttp?command=SetCurrentPlaylist&parameter='+playlistId;
var setup6 = new Ajax.Request(url6, {method:'get'});
getPlaylistContents(currentPlaylist);
}

function getDirectorySuccess(t, mediapath){

	responseArr = t.responseText.split("<li>");
	
	for (i=0;i<responseArr.length;i++){
	strippedPath = responseArr[i].replace(mediapath, '');
	new Insertion.Bottom('musiclibrary', '<li class="green" style="display:none;" id=musiclibrary'+i+' mediapath='+responseArr[i]+'>'+strippedPath+'</li>');
	$('musiclibrary'+i).toggle();


	$('musiclibrary'+i).mediapath = responseArr[i];
 	//Event.observe('musiclibrary'+i, 'click', function(obj){li=Event.element(obj);AddToPlayList(li.mediapath);}, false);
	//AddToPlayList(mediapath)
	}
	
	refreshDraggables();
}

function connectionFailure(t){

//	alert('failure t:'+t);

}


function getDirectory(mediapath){
     var url = '/xbmcCmds/xbmcHttp?command=GetDirectory&parameter='+mediapath;
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(obj){getDirectorySuccess(obj,mediapath);}, onFailure:connectionFailure});
	}

function connectionFailure(t){

//	alert('failure t:'+t);

}


function addDivToLibrary(locationPath){

new Insertion.Bottom('musiclibrary', locationPath)


}

function pushMediaList(t, mediapath){

$('musiclibraryHolder').innerHTML = t.responseText;
	refreshDraggables();


}

function setMediaType(mediaType){

	currentMediaType = mediaType;

if(mediaType == "videos"){
currentPlaylist	 = "2";
}else{
currentPlaylist	 = "0";
}


SetCurrentPlaylist(currentPlaylist);

	var url = 'musicList.asp?Action='+mediaType;
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(obj){pushMediaList(obj,mediapath);}, onFailure:connectionFailure});


}

function navigateToLocation(locationId){
	pollInProgress = true;
	$('musiclibrary').innerHTML = "<div id='loadingWidget'><br><br><center><img src='images/indicator.gif'> Loading</center><br><br></div>";
if(locationId != undefined && locationId != ""){
     var url = 'musicList.asp?command=select&item='+locationId;
}else{
     var url = 'musicList.asp';
}
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(obj){pushMediaList(obj,locationId);}, onFailure:connectionFailure});

}


function mediaLocationPopulateList(){

for(var j=0;j<10;j++){

if(musicListItem.length < 1){

clearInterval(musicListLoop);
refreshDraggables();

}else{


thisMusicItem = musicListItem.pop();

i=thisMusicItem[0];
mediapath=thisMusicItem[1];
elementName=thisMusicItem[2];
elementPath=thisMusicItem[3];
elementIsDir=thisMusicItem[4];
urlSafeMediaPath=thisMusicItem[5];
urlSafeMediaDirectory=thisMusicItem[6];


	locationPath = '<li class="green" id="musiclibrary'+i+'" isDir="'+elementIsDir+'" mediapath="'+ urlSafeMediaPath+'"';
	
	if (elementIsDir == 1){
	locationPath += "onclick='javascript:showMenu2(\"musiclibrary"+i+"\", true)'>";
	locationPath += "<span id='musiclibArt"+i+"' align='left' valign='center'><img src='images/folder_small.png' align=left hspace=20 onClick='javascript:getMediaLocation(\""+urlSafeMediaPath+"\");'></span>";


	}else{
	locationPath += "onclick='javascript:showMenu2(\"musiclibrary"+i+"\", \"false\")'><span id='musiclibArt"+i+"' align='left' valign='top'><img src='images/music.png'  align=left hspace=20 onClick='javascript:PlayMedia(\""+urlSafeMediaPath+"\")'></span>";

	locationPath += "";
	}


	locationPath += '<div id=musiclibSongInfo'+ i +' style="overflow:auto;width:60%;">' + elementName+'</div><div id="itemControls'+i+'"" style="position:absolute;right:0;top:0px;width:100px;vertical-align:top">';


		if(elementIsDir == 1){
	locationPath	 += "<img src='images/openfolder.png' border=0 onclick='javascript:getMediaLocation(\"" + urlSafeMediaPath + "\")'>";
		}else{
	locationPath	 += "<img src='images/playfile.png' border=0 onclick='javascript:PlayMedia(\"" + urlSafeMediaPath + "\")'>";
		}
	locationPath	 += "&nbsp;&nbsp;<img src='images/addtoplaylist.png' border=0 onclick='javascript:SetCurrentPlaylist(1);AddToPlayList(\"" + urlSafeMediaPath + "\")'>";


	locationPath += '</div></li>';
/*
	locationPath = '<li id="musiclibrary'+i+'" isDir="'+isDir+'">'+ urlSafeMediaPath+'</li>';
*/	

	new Insertion.Bottom('musiclibrary', locationPath);

//	asignDragAndDrop("musiclibSongInfo"+i);
}

}

}

function getMediaLocationSuccess(t, mediapath){

var j = 0;

//	stopQueuedEffects();

	$('musiclibrary').innerHTML = "";
	responseArr = t.responseText.split("<li>");

	for (i=0;i<responseArr.length;i++){

		responseArr2 = responseArr[i].split(";");

		    //$('currentlyPlayingText')[responseArr2[0]] = responseArr2[1];

	if(responseArr2[1] != undefined){
	
	elementName = responseArr2[0];
	elementPath = responseArr2[1];
	elementIsDir = responseArr2[2];

		urlSafeMediaPath = URLEncode(elementPath);

		justFilePath = urlSafeMediaPath.split("/");
		justFilePath = justFilePath.slice(0,-1);
		justFilePath = justFilePath.join("/");
		urlSafeMediaDirectory =justFilePath;

		musicListItem[j] = [i, mediapath, elementName, elementPath, elementIsDir, urlSafeMediaPath, urlSafeMediaDirectory];

		j++;

//send to display function
	
	}
	
		}
			musicListItem.reverse();
			mediaLocationPopulateList();
			musicListLoop =	window.setInterval("mediaLocationPopulateList()", 300);

		//	refreshDraggables();
}

function getMediaLocation(mediapath){
	pollInProgress = true;
	urlSafeMediaPath = mediapath;
	lastMusicLibItem[lastMusicLibItem.length] = mediapath;
	$('musiclibrary').innerHTML = "<div id='loadingWidget'><br><br><center><img src='images/indicator.gif'> Loading</center><br><br></div>";
     var url = '/xbmcCmds/xbmcHttp?command=getmedialocation&parameter=music;'+mediapath;
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(obj){getMediaLocationSuccess(obj,mediapath);}, onFailure:connectionFailure});

	//Set some variables so the navigation system knows where we are
	lastMenuItem = "";
	lastNavigationItem = lastMusicLibItem.length;
	lastMusicLibItem[lastNavigationItem] = mediapath;

}

function stopQueuedEffects(){
	var queue = Effect.Queues.get('global');
	queue.each(function(e) { e.cancel();});
}


function PlayId(mediapath){

	 var url = '/xbmcCmds/xbmcForm?command=catalog&parameter=select,'+mediapath;
	 var myAjax = new Ajax.Request(url, {method:'get'});

}



function PlayMedia(mediapath){

	 var url = '/xbmcCmds/xbmcHttp?command=playfile&parameter='+mediapath;
	 var myAjax = new Ajax.Request(url, {method:'get'});

}



function AddIdToPlayList(mediapath){


     var url = '/xbmcCmds/xbmcForm?command=catalog&parameter=que,'+mediapath;
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){getPlaylistContents(currentPlaylist)}, onFailure:connectionFailure});

}

function AddToPlayList(mediapath){


//Check for shout:// or musicdb://
checkPath = new RegExp("shout", "i")
shoutdblink = mediapath.match(checkPath);

checkPath = new RegExp("musicdb", "i")
musicdblink = mediapath.match(checkPath);


if(shoutdblink || musicdblink){
alert("musicdblink: "+musicdblink+"  shoutdblink:"+shoutdblink);
}



     var url = '/xbmcCmds/xbmcHttp?command=AddToPlayList&parameter='+mediapath;
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){getPlaylistContents(currentPlaylist)}, onFailure:connectionFailure});

}



function SetPlaylistSong(songNum){

     var url = '/xbmcCmds/xbmcHttp?command=SetPlaylistSong&parameter='+songNum;
     var myAjax = new Ajax.Request(url, {method:'get'});

	GetCurrentlyPlaying();
}



function showScreenshot(){

     var url = '/xbmcCmds/xbmcHttp?command=takescreenshot&parameter=test.jpg;false;0;200;130;90;true';
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(obj, returnPath){
	tempResponse = obj.responseText.split("<li>");

	//Change this
	$('albumArt').innerHTML = '<a href="javascript:showScreenshot();"><img src="data:image/jpg;base64,'+ tempResponse[0] + '"></a>';


}, onFailure:connectionFailure});

}

function showLargeScreenshot(){

     var url = '/xbmcCmds/xbmcHttp?command=takescreenshot&parameter=test.jpg;false;0;640;480;90;true';
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(obj, returnPath){
	tempResponse = obj.responseText.split("<li>");

	//Change this
	$('largeScreenshot').innerHTML = '<a href="javascript:showLargeScreenshot();"><img src="data:image/jpg;base64,'+ tempResponse[0] + '"></a>';


}, onFailure:connectionFailure});

}

function downloadThumbnail(thumbPath, albumName, returnPath){

	var thumburl = '/xbmcCmds/xbmcHttp?command=lookupalbum&parameter='+albumName;
     //var thumburl = '/xbmcCmds/xbmcHttp?command=GetThumbFilename&parameter='+albumName+';'+thumbPath;
     var thumbAjax = new Ajax.Request(thumburl, {method:'get', onSuccess:function(t, returnPath){
	tempLocation = t.responseText.split("<li>");
	//showThumbnail(tempLocation[1], returnPath)
	tempLocation2 = tempLocation[1].split("<@@>");

			var thumburl2 = '/xbmcCmds/xbmcHttp?command=choosealbum&parameter='+tempLocation2[1];
   			var thumbAjax2 = new Ajax.Request(thumburl2, {method:'get', onSuccess:function(y){
	
				tempLocation3 = y.responseText.split("<li>");
				tempLocation4 = tempLocation3[0].split(":");

			tempLocation5 = tempLocation4.slice(1);
			tempLocation6 = tempLocation5.join(":");

			$('albumArt').innerHTML = '<img src="'+tempLocation6+'">';

			
			}, onFailure:connectionFailure});


	}, onFailure:connectionFailure});



}



function getThumbnail(filePath, returnDiv){


thumburl = '/xbmcCmds/xbmcHttp?command=GetThumbFilename&parameter='+filePath+";";
thumbAjax = new Ajax.Request(thumburl, {method:'get', onSuccess:function(t){
	tempLocation = t.responseText.split("<li>");
	tempLocation2 = tempLocation[1].split("\\");

			thumburl2 = '/xbmcCmds/xbmcHttp?command=filedownload&parameter=Q:\\albums\\thumbs\\temp\\'+escape(tempLocation2[tempLocation2.length-1]);
   			thumbAjax2 = new Ajax.Request(thumburl2, {method:'get', onSuccess:function(y){

				tempLocation3 = y.responseText.split("<li>");
				imageData = tempLocation3[0];

		if(imageData.length > 1){
				$(returnDiv).innerHTML = '<img src="data:image/jpg;base64,'+ imageData + '"  align=left hspace=5 >';
		}else{
				$(returnDiv).innerHTML = '<img src="images/defaultAlbumCover.png"  align=left hspace=5 >';
		}

	
			}, onFailure:connectionFailure});


	}, onFailure:connectionFailure});

}


function showThumbnail(imageData, returnPath){

	tempLocation3 = imageData.split("\\");
	thumburl3 = '/xbmcCmds/xbmcHttp?command=filedownload&parameter=Q:\\albums\\thumbs\\temp\\'+escape(tempLocation3[tempLocation3.length-1]);
     var myAjax = new Ajax.Request(thumburl3, {method:'get', onSuccess:function(obj, returnPath){

	tempResponse = obj.responseText.split("<li>");
	$(returnPath).innerHTML = '<img src="data:image/jpg;base64,'+ tempResponse[0] + '"   align=left hspace=5>';
	
	}, onFailure:connectionFailure});
}


function addItemToPlaylistDiv(i, infoArray){

if(infoArray=="[Empty]"){

	locationPath ='<li nowrap id=playlist0';
	locationPath += "<a href='#'><center><br><br><br><b>The playlist is Empty</b><br><br>To Add Songs:<br>Click and Drag a song or album on the left to this column.<br><b>-or-</b><br>Click on a Song or album on the left and goto -Add to Playlist-<br><br><br></center></a></li>";

}else{
	displayTitle = infoArray.split("/");
	displayExtention =  infoArray.split(".");


		locationPath = "";


	//Some string cleaning
	displayExtention = "."+displayExtention[displayExtention.length-1];
	displayExtention = displayExtention.split(unescape("%0A"));
	displayExtention = displayExtention[0];

	for(e=0; e<supportedAudioExtentions.length; e++){
		if(supportedAudioExtentions[e] == displayExtention){

		locationPath +='<li nowrap id=playlist'+i+' mediapath="'+ escape(infoArray) + '"';
		locationPath += " ondblclick='javascript:PlayMedia(\""+escape(infoArray)+"\");'>";
		locationPath += "<a href='#'><img src='images/play.png' border=0 onclick='javascript:SetPlaylistSong("+(parseInt(i)-1)+");'>&nbsp;&nbsp;&nbsp;"+displayTitle[displayTitle.length-1]+"</a></li>";	
		}
		}


	for(e=0; e<supportedVideoExtentions.length; e++){
		if(supportedVideoExtentions[e] == displayExtention){

		locationPath +='<li nowrap id=playlist'+i+' mediapath="'+ escape(infoArray) + '"';
		locationPath += " ondblclick='javascript:PlayMedia(\""+escape(infoArray)+"\");'>";
		locationPath += "<a href='#'><img src='images/play.png' border=0 onclick='javascript:SetPlaylistSong("+(parseInt(i)-1)+");'>&nbsp;&nbsp;&nbsp;"+displayTitle[displayTitle.length-1]+"</a></li>";	
		}
		}


}

	new Insertion.Bottom('playlist', locationPath);




}

function getPlaylistSuccess(t){

	$('playlist').innerHTML = "";
	
	responseArr6 = t.responseText.split("<li>");
	
	


	for (var i=0;i<responseArr6.length;i++){

	if((responseArr6[i]!="") && (escape(responseArr6[i]) != "%0A")){
	
		mediapath = responseArr6[i];
	

	
	if(responseArr6[i] != "html>"){

//alert("got: "+responseArr6[i]);

	addItemToPlaylistDiv(i,responseArr6[i]);

	//get file information from id3 tags
	/*
	
	     var url = '/xbmcCmds/xbmcHttp?command=gettagfromfilename&parameter='+mediapath;
	     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(u){
	
		subresponseArr = u.responseText.split("<li>");
	
	
		for (var j=0;j<subresponseArr.length-1;j++){

			responseArr2 = subresponseArr[j].split(":");

			if(responseArr2.length > 2){

				elementName = responseArr2[0];
				responseArr2 = responseArr2.slice(1);
				elementValue = responseArr2.join(":");
				//alert(elementName+'='+elementValue);
	
				$('playlist'+i)[elementName] = elementValue;
				finalAnswer =  elementValue;
	
			}else{
			//alert(responseArr2[0]+'='+responseArr2[1]);
	
			    $('playlist'+i)[responseArr2[0]] = responseArr2[1];
				finalAnswer = responseArr2[1];


			}

	
		}

	
			}, onFailure:getPlaylistFailure});

	*/
	}
	}
	}
//	refreshDraggables();
}

function getPlaylistFailure(t){

//	alert('failure t:'+t);

}


function getPlaylistContents(playlistNum){
	if(playlistNum == undefined){
	var playlistNum = 0; //Playlist 0 is the default
	}
     var url = '/xbmcCmds/xbmcHttp?command=GetPlaylistContents&parameter='+playlistNum;
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){getPlaylistSuccess(t)}, onFailure:getPlaylistFailure});

	$('playlist').innerHTML = "<div id='loadingWidget'><br><br><center><img src='images/indicator.gif'> Loading</center><br><br></div>";
}

function GetCurrentlyPlaying(){

     var url = '/xbmcCmds/xbmcHttp?command=GetCurrentlyPlaying';
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){

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
	//
	
	if($('currentlyPlayingText').Title != undefined){

if($('currentlyPlayingText').Album == undefined){
$('currentlyPlayingText').Album = "";
}

if($('currentlyPlayingText').Artist == undefined){
$('currentlyPlayingText').Artist = "";
}
	
	//alert("fdsfd"+$('currentlyPlayingText').Title);
	
	$('currentlyPlayingText').innerHTML = "<b>"+$('currentlyPlayingText').Title+"<br>  "+$('currentlyPlayingText').Album+"</b><br>"+$('currentlyPlayingText').Artist+"<br> </div>"+$('currentlyPlayingText').Time+" / "+$('currentlyPlayingText').Duration+"</div>";
	
s.setValue($('currentlyPlayingText').Percentage);
s.setMinimum(0);
s.setMaximum(100);

//$('currentlyPlayingText').SeekPercentage

	
	justFilePath = $('currentlyPlayingText').Filename.split("/");
	justFilePath = justFilePath.slice(0,-1);
	justFilePath = justFilePath.join("/");
	
	 
	//Only download image once
	if($('currentlyPlayingText').Title != lastTitle){
	getThumbnail(justFilePath, "albumArt");}
	lastTitle = $('currentlyPlayingText').Title;
	
	}else if(lastTitle=="screenshot"){

		
	}else{
	$('currentlyPlayingText').innerHTML = "Nothing Playing";
	showScreenshot();
	lastTitle = "screenshot";
	}



	pollInProgress = false;
		}, onFailure:getPlaylistFailure});
	}
	

var lastTitle = "";


function GetVolume(){
     var url = '/xbmcCmds/xbmcHttp?command=GetVolume';
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){

	responseArr = t.responseText.split("<li>");

	//alert(responseArr[1]);

	$('currentVolume').value=responseArr[1];


		}});
}


function gettagfromfilename(mediapath){
     var url = '/xbmcCmds/xbmcHttp?command=gettagfromfilename&parameter='+mediapath;
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){

	responseArr = t.responseText.split("<li>");
	$('currentlyPlayingText').innerHTML = responseArr;

	for (i=0;i<responseArr.length;i++){
	//strippedPath = responseArr[i].replace(mediapath, '');
	$(currentlyPlayingObj).id = responseArr[i][0];
	$F(currentlyPlayingObj) = responseArr[i][0];

		responseArr2 = t.responseArr.split(":");

		if(responseArr2.length > 1){
			elementName = responseArr[0];
			responseArr[0]="";
			//elementName = responseArr.join();
			
		}
	}

		}, onFailure:getPlaylistFailure});
}




function ExecBuiltIn(builtInCmd){

     var url = '/xbmcCmds/xbmcHttp?command=ExecBuiltIn&parameter='+builtInCmd;
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){

	//alert(t.responseText);
	//	responseArr = t.responseText.split(":");

	//	$(currentlyPlayingText).innerHTML = responseArr[1];




		}, onFailure:getPlaylistFailure});

}


function SendKey(keyToSend){

     var url = '/xbmcCmds/xbmcHttp?command=SendKey&parameter='+keyToSend;
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){

	//alert(t.responseText);


		}, onFailure:getPlaylistFailure});

}

function SeekPercentage(percentage){

     var url = '/xbmcCmds/xbmcHttp?command=SeekPercentage&parameter='+percentage;
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){

	//alert(t.responseText);


		}, onFailure:getPlaylistFailure});

}



function GeneratePlaylistM3U(playlistName){

	playlistContents="";
	playlistNum = currentPlaylist; //Playlist currentPlaylist is the default

     var url = '/xbmcCmds/xbmcHttp?command=GetPlaylistContents&parameter='+playlistNum;
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



}, onFailure:getPlaylistFailure});

}

function saveSmartPlaylist(){

playlistName="smartPlaylist-Eminem.xsp"
playlistContents="";

	playlistContents+='<smartplaylist>\n';
	playlistContents+='<name>Party Mode</name>\n';
	playlistContents+='<match>all</match>\n';
	playlistContents+='<rule field="artist" operator="is">Eminem</rule>\n';
	playlistContents+='</smartplaylist>\n';



SavePlaylist(playlistName, playlistContents);


//PlayMedia("c:\\playlists\\"+playlistName);


}

function SavePlaylist(playlistName, playlistContents){


//alert("saving playlist string:"+playlistName+"----"+playlistContents);

playlistContents64 = encodeBase64(playlistContents)

//alert("base64 string:"+playlistContents64);

     var url = '/xbmcCmds/xbmcHttp?command=FileUpload&parameter=c:\\playlists\\'+playlistName+';'+playlistContents64;
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){

	//alert(t.responseText);
	//	responseArr = t.responseText.split(":");
	//	$(currentlyPlayingText).innerHTML = responseArr[1];


	disableKeys = false;
	closeKeyboard();	
	getMediaLocation("C:\\playlists\\");

		}, onFailure:getPlaylistFailure});

}

function musicExtentions(supExt){

	extArr= supExt.split("<li>")
	supportedAudioExtentions = extArr[1];

	supportedAudioExtentions = supportedAudioExtentions.split("|")

//	alert("we support the following audio formats:"+supportedAudioExtentions);

}

function videoExtentions(supExt){

	extArr= supExt.split("<li>")
	supportedVideoExtentions = extArr[1];

supportedVideoExtentions = supportedVideoExtentions.split("|")

//	alert("we support the following video formats:"+supportedVideoExtentions);

}


function xbmcCmds(command, callbackFunction){

     var url = '/xbmcCmds/xbmcHttp?command='+command;
     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:function(t){
    	callbackFunction(t.responseText);
		}, onFailure:getPlaylistFailure});

}



connectToXbox();

///////////////////////
///Custom A/V Hooks////
///////////////////////
//if you set cutom = true this can talk to the a/v control system to control colume on the reciever instead of xbmc
//Connections to A/V Reciever
//

function pullScript(fileName)
{
var oHead = document.getElementsByTagName("HEAD")[0];
var oScript = document.createElement('script');
oScript.setAttribute('src',fileName);
oScript.setAttribute('type','text/javascript');
oHead.appendChild(oScript);
}

function volumeCtrl(direction){
if(direction == "up"){

	if(!custom){
	     var url = '/xbmcCmds/xbmcHttp?command=SetVolume&parameter='+(parseInt($('currentVolume').value)+5);
	     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:GetVolume, onFailure:getPlaylistFailure});
	}else{
		pullScript("http://"+customIP+"/pullJS.asp?direction=up");
	}

}else{

	if(!custom){
	     var url = '/xbmcCmds/xbmcHttp?command=SetVolume&parameter='+(parseInt($('currentVolume').value)-5);
	     var myAjax = new Ajax.Request(url, {method:'get', onSuccess:GetVolume, onFailure:getPlaylistFailure});
	}else{
		pullScript("http://"+customIP+"/pullJS.asp?direction=down");
	}




}
}


 // ]]>
 </script>
</div>
</body>
</html>
