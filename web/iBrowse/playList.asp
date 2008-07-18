<ul id="musiclibrary" align="left" class="musiclibrary">
<%

write(xbmcAPI("GetCurrentPlayList"));

locationPath ='<li id=musiclibrary'+i+' class="row'+ i%2 + '"';
locationPath = locationPath+ "><span onclick='javascript:PlayMedia("+ i + ");' >";

locationPath = locationPath+  '<span valign="center" align="left" id="musiclibArt'+ i +'"><img hspace="20" align="left" onclick="javascript:PlayMedia('+ i + ');" src="images/music.png"/></span><div style="overflow: hidden; width: 60%;" id="musiclibSongInfo'+ i +'">'+ displayTitle[displayTitle.length-1] +'</div></span>';

locationPath = locationPath+  '<img border="0" onclick="javascript:xbmcCmds(\'setplaylistsong&parameter='+ i + '\')" src="images/play.png"  />';

locationPath = locationPath+  '<img border="0" onclick="javascript:RemoveFromPlaylist(escape(\''+ displayTitle[displayTitle.length-1] +'\'))" src="images/delete.png"/></div></li>';

%>
</ul>