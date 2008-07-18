
<ul id="musiclibrary" align="left" class="musiclibrary">
<%
  var itemCount; // number of items in list
  var data;      // tmp var used in for loop
  var tmpType;   // holds isDir value
  var i;         // iterator

  navigatorstate = xbmcCommand("navigatorstate");

  if (navigatorstate == "pictures") {
    ItemIconPath = "images/image.png";
    ItemPlayIcon = "images/view.png";
    ItemAddIcon = "images/addtoplaylist.gif";
		CurrentPlayList = 0;
  }
  else if (navigatorstate == "music") {
    ItemIconPath = "images/music.png";
    ItemPlayIcon = "images/play.png";
    ItemAddIcon = "images/addtoplaylist.gif";
    CurrentPlayList = 0;
  }
  else if (navigatorstate == "videos") {
    ItemIconPath = "images/movie.png";
    ItemPlayIcon = "images/video.png";
    ItemAddIcon = "images/addtoplaylist.gif";
		CurrentPlayList = 2;
  }
  else {
		xbmcCommand("navigate", "music");
    ItemIconPath = "images/music.png";
    ItemPlayIcon = "images/play.png";
    ItemAddIcon = "images/addtoplaylist.gif";
		CurrentPlayList = 0;
	}
  
  if (isset("Action")) { xbmcCommand("navigate", Action); }
  if (isset("command")) {  
    if (command == "select") { xbmcCommand("catalog", "select," + item); } 
  }

  itemCount = xbmcCommand("catalog","items");
  file = xbmcCommand("catalog","first");
  
  for (i = 0; i < itemCount; i = i + 1) {
    tmpType = xbmcCommand("catalog","type,"+i);


   if (tmpType == "directory") {  data = '  <li class="row' + (i % 2) + '" mediapath="'+ i + '" id="musiclibrary'+ i + '">  <span  style="height:40px">'; }
    else {  data = '  <li class="row' + (i % 2) + '" mediapath="'+ i + '" id="musiclibrary'+ i + '" >  <span style="height:40px">'; }
   
    
    if (tmpType == "directory") { data = data + '<span valign="center" align="left" id="musiclibArt'+ i +'"><img hspace="20" align="left" onclick="javascript:navigateToLocation(\''+ i +'\');" src="images/folder_small.png"/></span><div style="overflow: hidden; width: 60%;" id="musiclibSongInfo'+ i +'">'+ file +'</div>'; }
    else { data = data + '<span valign="center" align="left" id="musiclibArt'+ i +'"><img hspace="20" align="left" onclick="javascript:PlayMedia('+ i + ');" src="'+ ItemIconPath +'"/></span><div style="overflow: hidden; width: 60%;" id="musiclibSongInfo'+ i +'">'+ file +'</div>';  }
    
	data = data + "</span>";

    data = data + '<div style="position: absolute; right: 0pt; top: 0px; width: 100px; vertical-align: top;" id="itemControls'+ i +'">';
    
    if (tmpType == "directory") { data = data + '<a href="javascript:navigateToLocation('+ i + ')" ><img border="0" src="images/openfolder.png" /></a>';  }
    else { data = data + '<a href="javascript:PlayId('+ i + ');" ><img border="0" src="'+ ItemPlayIcon +'"  /></a>';  }
    


    if (file != "..") data = data + '<img border="0" onclick="javascript:SetCurrentPlaylist('+CurrentPlayList+');AddIdToPlayList('+ i + ')" src="'+ ItemAddIcon +'"/>';
    data = data + '</div></li>';
    write(data+"\n");
    file = xbmcCommand("catalog","next");
  }
%>
</ul>