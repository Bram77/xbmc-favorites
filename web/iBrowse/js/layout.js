window.onload=noSelect;

function resize(){ 

	var iWidth = (window.innerWidth) ? window.innerWidth : document.body.offsetWidth;
 	var iHeight = (window.innerHeight) ? window.innerHeight : document.body.offsetHeight;
	var contentHeight = iHeight - 170;

	$('musiclibraryHolder').style.height = contentHeight;
	$('playlist-div').style.height = contentHeight;
} 


var message="Don't try to right-click";
///////////////////////////////////
function clickIE() {if (document.all) {(message);return false;}}
function clickNS(e) {if
(document.layers||(document.getElementById&&!document.all)) {
if (e.which==2||e.which==3) {(message);return false;}}}
if (document.layers)
{document.captureEvents(Event.MOUSEDOWN);document.onmousedown=clickNS;}
else{document.onmouseup=clickNS;document.oncontextmenu=clickIE;}

document.oncontextmenu=new Function("return false")



/***********************************************
* Disable select-text script- © Dynamic Drive (www.dynamicdrive.com)
* This notice MUST stay intact for legal use
* Visit http://www.dynamicdrive.com/ for full source code
* Modified here to exclude form tags properly, cross browser by jscheuer1
***********************************************/

//form tags to omit:
var omitformtags=["input", "textarea", "select"]

function disableselect(e){
for (i = 0; i < omitformtags.length; i++)
if (omitformtags[i]==(e.target.tagName.toLowerCase()))
return;
return false
}

function reEnable(){
return true
}

function noSelect(){
if (typeof document.onselectstart!="undefined"){
document.onselectstart=new Function ("return false")
if (document.getElementsByTagName){
tags=document.getElementsByTagName('*')
for (j = 0; j < tags.length; j++){
for (i = 0; i < omitformtags.length; i++)
if (tags[j].tagName.toLowerCase()==omitformtags[i]){
tags[j].onselectstart=function(){
document.onselectstart=new Function ('return true')
}
if (tags[j].onmouseup!==null){
var mUp=tags[j].onmouseup.toString()
mUp='document.onselectstart=new Function (\'return false\');\n'+mUp.substr(mUp.indexOf('{')+2,mUp.lastIndexOf('}')-mUp.indexOf('{')-3);
tags[j].onmouseup=new Function(mUp);
}
else{
tags[j].onmouseup=function(){
document.onselectstart=new Function ('return false')
}
}
}
}
}
}
else{
document.onmousedown=disableselect
document.onmouseup=reEnable
}
}

function goBack(){

	save_lastNavigationItem = lastNavigationItem;
	getMediaLocation(lastMusicLibItem[lastNavigationItem-2]);

	lastNavigationItem=save_lastNavigationItem-2;

}


//Function for custom a/v reciever zone status
function setStatus(zoneNum, statusFlag){
	
	if(statusFlag == "0"){
	
	$('statusZone'+zoneNum).innerHTML = '<IMG SRC="images/status_off.png" WIDTH=19 HEIGHT=16 ALT="">';
	
	}else if(statusFlag == "1"){
	
	$('statusZone'+zoneNum).innerHTML = '<IMG SRC="images/status_on.png" WIDTH=19 HEIGHT=16 ALT="">';
	
	}else{
	
	$('statusZone'+zoneNum).innerHTML = '<IMG SRC="images/status_unknown.png" WIDTH=19 HEIGHT=16 ALT="">';
	
	}


}
