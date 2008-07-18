<ul id="musiclibrary" align="left" class="musiclibrary">
<%
myDirectory = xbmcAPI("GetDirectory", path +";.m3u");



write("!!"+myDirectory+"!!");
 
  for (i = 0; i < itemCount; i = i + 1) {

    data = '  <li class="row' + (i % 2) + '" mediapath="'+ i + '" id="musiclibrary'+ i + '" >  <span onclick="javascript:PlayMedia('+ i + ');" >';
    data = data + '<span valign="center" align="left" id="musiclibArt'+ i +'"><img hspace="20" align="left" onclick="javascript:PlayMedia('+ i + ');" src="images/music.png"/></span><div style="overflow: hidden; width: 60%;" id="musiclibSongInfo'+ i +'">'+ file +'</div>';
    data = data + "</span>";    
    data = data + '<div style="position: absolute; right: 0pt; top: 0px; width: 100px; vertical-align: top;" id="itemControls'+ i +'">';
    data = data + '<img border="0" onclick="javascript:xbmcCmds(\'setplaylistsong&parameter='+ i + '\')" src="images/play.png"  />';  

    data = data + "</div>";
	data = data + "</li>";

    write(data+"\n");

  }

if (itemCount == 0) {
write("<li><center><br><br>The Playlist Folderis Empty.<br><br></center>");
}

%>
</ul>