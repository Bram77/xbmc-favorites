<ul id="musiclibrary" align="left" class="musiclibrary">


<%



  var itemCount;
  var data;
  var first;
  var last;
  var tmpType;
  var tmpDir;
  var false = (1 == 0);
  var i;



    navigatorstate = xbmcCommand("navigatorstate");

    if (navigatorstate == "pictures"){
        ItemIconPath = "images/image.png";
        ItemPlayIcon = "images/view.png";
        ItemAddIcon = "images/addtoplaylist.png";
//		CurrentPlayList = "AddToSlideShow";
		CurrentPlayList = 0;
    } else if (navigatorstate == "music") {
        ItemIconPath = "images/music.png";
        ItemPlayIcon = "images/playfile.png";
        ItemAddIcon = "images/addtoplaylist.png";
		CurrentPlayList = 0;
    } else if (navigatorstate == "videos") {
        ItemIconPath = "images/movie.png";
        ItemPlayIcon = "images/video.png";
        ItemAddIcon = "images/addtoplaylist.png";
		CurrentPlayList = 2;
    } else {
		xbmcCommand("navigate", "music");
        ItemIconPath = "images/music.png";
        ItemPlayIcon = "images/playfile.png";
        ItemAddIcon = "images/addtoplaylist.png";
		CurrentPlayList = 0;
	}


  
    if (isset("Action")) {
        xbmcCommand("navigate", Action);
    }


  if (isset("command")) { 
    if (command == "select") { xbmcCommand("catalog", "select," + item); }
  }



  itemCount = xbmcCommand("catalog","items"); // number of items to list
  file = xbmcCommand("catalog","first");
  
  if (isset("first") == false) { first = -1; }
  if (isset("last") == false) { last = itemCount; }
  
  for (i = 0; i < itemCount; i = i + 1) {
    if (i < first) {
      file = xbmcCommand("catalog","next");
      continue; 
    }
    if (i > last) { break; }
    tmpType = xbmcCommand("catalog","type,"+i);
    if (tmpType == "directory") { tmpDir = 1; }
    else { tmpDir = 0; }



write('<li class="green" mediapath="'+ i + '" id="musiclibrary'+ i + '">') 


    if (tmpDir == 1) { 

write('<span valign="center" align="left" id="musiclibArt'+ i +'"><img hspace="20" align="left" onclick="javascript:navigateToLocation(\''+ i +'\');" src="images/folder_small.png"/></span>')

	 }
    else { 
write('<span valign="center" align="left" id="musiclibArt'+ i +'"><img hspace="20" align="left" onclick="javascript:PlayMedia('+ i + ');" src="'+ ItemIconPath +'"/></span>')
	 }

write('<div style="overflow: hidden; width: 60%;" id="musiclibSongInfo'+ i +'">'+ file +'</div>')



write('<div style="position: absolute; right: 0pt; top: 0px; width: 100px; vertical-align: top;" id="itemControls'+ i +'">')


    if (tmpDir == 1) { 

write('<img border="0" onclick="javascript:navigateToLocation(\''+ i + '\')" src="images/openfolder.png" style=""/>')
	 }
    else { 
write('<img border="0" onclick="javascript:PlayId('+ i + ')" src="'+ ItemPlayIcon +'" style=""/>')
	 }



write('<img border="0" onclick="javascript:SetCurrentPlaylist('+CurrentPlayList+');AddIdToPlayList('+ i + ')" src="'+ ItemAddIcon +'"/></div></li>')


    file = xbmcCommand("catalog","next");
  }
%>

</ul>

<script>

//alert("ok");

</script>