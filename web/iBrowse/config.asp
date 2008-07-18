<%
    /*
     * xbmc configuration options
    
      xbmcCfgBookmarkSize(type)
      xbmcCfgGetBookmark(type, parameter, id)
      xbmcCfgAddBookmark(type, name, path [, position])
      xbmcCfgSaveBookmark(type, name, path, position)
      xbmcCfgRemoveBookmark(type, position)
      xbmcCfgSaveConfiguration(filename)
      xbmcCfgGetOption(name)
      xbmcCfgSetOption(name, value)
    
     */
    write("<a href='?DisplayConfiguration=true&amp;page=bookmarks'>Modify Media Bookmarks</a><br><br><a href='http://www.liquidicelabs.com/xbmc/installAJAX.php' target=_>Upgrade to the Latest Web GUI</a><br><br><a href='albumart.spy' target=_>Sync Thumbs to Web Root</a><br><br><a href='http://10.1.0.191:6246/command?MLCmd|ChangeScene~ALL~cliqk_home.mls~'><img src='images/q_quit.png'></a><br><br>\n");
    write("<br />\n");
    write("<br />\n");
    
    
    /* if action isset we want to save / edit or remove something */
    if (isset("action"))
    {
      if (action == "savebookmark")
      {
        if (isset("name") == "1" && isset("path") == "1" && isset("type") == "1" && isset("position") == "1")
        {
          xbmcCfgSaveBookmark(type, name, path, position);
        }
        else
          write("Error");
      }
      if (action == "addbookmark")
      {
        if (isset("name") == "1" && isset("path") == "1" && isset("type") == "1")
        {
          xbmcCfgAddBookmark(type, name, path);
        }
        else
          write("Error");
      }
      if (action == "remove")
      {
        if (isset("page"))
        {
          // return to bookmark page and not to editbookmarks
          page = "bookmarks";
          xbmcCfgRemoveBookmark(type, position);
        }
      }
      if (action == "saveoptions")
      {
        xbmcCfgSetOption("home", home);
        xbmcCfgSetOption("CDDBIpAddress", CDDBIpAddress);

/* Added by HR to update to 1-25 CVS */
        xbmcCfgSetOption("logpath", logpath);
        xbmcCfgSetOption("loglevel", loglevel);
        xbmcCfgSetOption("cddaplayer", cddaplayer);
        xbmcCfgSetOption("cachepath", cachepath);
        xbmcCfgSetOption("playlists", playlists);
        xbmcCfgSetOption("trainerpath", trainerpath);
        xbmcCfgSetOption("CDDARipPath", CDDARipPath);
		
        var autod = "no";
        if (isset("autodetectFG")) autod = "yes";
        xbmcCfgSetOption("autodetectFG", autod);
		
        var pcdvd = "no";
        if (isset("usePCDVDROM")) pcdvd = "yes";
        xbmcCfgSetOption("usePCDVDROM", pcdvd);
		
        var usef = "no";
        if (isset("useFDrive")) usef = "yes";
        xbmcCfgSetOption("useFDrive", usef);
		
        var useg = "no";
        if (isset("useGDrive")) useg = "yes";
        xbmcCfgSetOption("useGDrive", useg);
		
        var autoiso = "no";
        if (isset("detectAsIso")) autoiso = "yes";
        xbmcCfgSetOption("detectAsIso", autoiso);
		
        xbmcCfgSetOption("dashboard", dashboard);
        xbmcCfgSetOption("dvdplayer", dvdplayer);
        xbmcCfgSetOption("subtitles", subtitles);
        xbmcCfgSetOption("startwindow", startwindow);
        xbmcCfgSetOption("pictureextensions", pictureextensions);
        xbmcCfgSetOption("musicextensions", musicextensions);
        xbmcCfgSetOption("videoextensions", videoextensions);
        xbmcCfgSetOption("thumbnails", thumbnails);
        xbmcCfgSetOption("shortcuts", shortcuts);
        xbmcCfgSetOption("albums", albums);
        xbmcCfgSetOption("recordings", recordings);
        xbmcCfgSetOption("screenshots", screenshots);
    
        var remcodes = "no";
        if (isset("displayremotecodes")) remcodes = "yes";
        xbmcCfgSetOption("displayremotecodes", remcodes);
		
        var showmem = "no";
        if (isset("showfreemem")) showmem = "yes";
        xbmcCfgSetOption("showfreemem", showmem);

      }
      if (action == "save")
      {
        xbmcCfgSaveConfiguration("XBoxMediaCenter.xml");
      }
    }
    
    if (isset("page"))
    {
      var i;
      var name;
      var value;
      var options;
    
      if (page == "bookmarks")
      {
        var musicbookmarks = xbmcCfgBookmarkSize("music");
        var picturebookmarks = xbmcCfgBookmarkSize("pictures");
        var videobookmarks = xbmcCfgBookmarkSize("video");
        var filebookmarks = xbmcCfgBookmarkSize("files");
        var programbookmarks = xbmcCfgBookmarkSize("myprograms");
        
    
        /* Add new Bookmark button */
        write("<form name='new_bookmark' method='post' action='?DisplayConfiguration=true&amp;page=addbookmark'>\n");
        write("  <input type='submit' name='addnewbookmark' value='Add new bookmark'><br>\n");
        write("</form>\n");
    
        /* Display Music Bookmarks */
        write("<form name='music_bookmarks' method='post' action='?DisplayConfiguration=true&amp;page=editbookmark&amp;type=music'>\n");
        write("  Music Bookmarks:<br>\n");
        write("  <input type='submit' name='action' value='edit'>\n");
        write("  <input type='submit' name='action' value='remove'>\n");
        write("  <select name='position'>\n");
        i = 0;
        for (i=1; i<=musicbookmarks; i=i+1)
        {
          write("    <option value=" + i + ">" + xbmcCfgGetBookmark("music", "name", i) + "</option>\n");
        }
        write("  </select>\n");
        write("</form>\n");
    
        /* Display Picture Bookmarks */
        write("<form name='picture_bookmarks' method='post' action='?DisplayConfiguration=true&amp;page=editbookmark&amp;type=pictures'>\n");
        write("Picture Bookmarks:<br>\n");
        write("  <input type='submit' name='action' value='edit'>\n");
        write("  <input type='submit' name='action' value='remove'>\n");
        write("  <select name='position'>\n");
        i = 0;
        for (i=1; i<=picturebookmarks; i=i+1)
        {
          write("    <option value=" + i + ">" + xbmcCfgGetBookmark("pictures", "name", i) + "</option>\n");
        }
        write("  </select>\n");
        write("</form>\n");
    
        /* Display Video Bookmarks */
        write("<form name='video_bookmarks' method='post' action='?DisplayConfiguration=true&amp;page=editbookmark&amp;type=video'>\n");
        write("Video Bookmarks:<br>\n");
        write("  <input type='submit' name='action' value='edit'>\n");
        write("  <input type='submit' name='action' value='remove'>\n");
        write("  <select name='position'>\n");
        i = 0;
        for (i=1; i<=videobookmarks; i=i+1)
        {
          write("    <option value=" + i + ">" + xbmcCfgGetBookmark("video", "name", i) + "</option>\n");
        }
        write("  </select>\n");
        write("</form>\n");
    
        /* Display File Bookmarks */
        write("<form name='file_bookmarks' method='post' action='?DisplayConfiguration=true&amp;page=editbookmark&amp;type=files'>\n");
        write("File Bookmarks:<br>\n");
        write("  <input type='submit' name='action' value='edit'>\n");
        write("  <input type='submit' name='action' value='remove'>\n");
        write("  <select name='position'>\n");
        i = 0;
        for (i=1; i<=filebookmarks; i=i+1)
        {
          write("    <option value=" + i + ">" + xbmcCfgGetBookmark("files", "name", i) + "</option>\n");
        }
        write("  </select>\n");
        write("</form>\n");
    
        /* Display Program Bookmarks */
        write("<form name='program_bookmarks' method='post' action='?DisplayConfiguration=true&amp;page=editbookmark&amp;type=myprograms'>\n");
        write("Program Bookmarks:<br>\n");
        write("  <input type='submit' name='action' value='edit'>\n");
        write("  <input type='submit' name='action' value='remove'>\n");
        write("  <select name='position'>\n");
        i = 0;
        for (i=1; i<=programbookmarks; i=i+1)
        {
          write("    <option value=" + i + ">" + xbmcCfgGetBookmark("myprograms", "name", i) + "</option>\n");
        }
        write("  </select>\n");
        write("</form>\n");
      }
      else if (page == "options")
      {
        write("	<form action='?DisplayConfiguration=true' method='post' name='cfgform' id='cfgform'>" + \
              "		<input name='action' type='hidden' value='saveoptions'>" + \
              "		<input name='page' type='hidden' value='options'>" + \
              "		<table width='500'>");
        write("			<tr>" + \
              "				<td align=center><label><b>Application(s)</b></label></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>CDDA Player</label></td>" + \
              "				<td><input name='cddaplayer' type='text' value='"); write(xbmcCfgGetOption("cddaplayer")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>DVD Player</label></td>" + \
              "				<td><input name='dvdplayer' type='text' value='"); write(xbmcCfgGetOption("dvdplayer")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td align=center><label><b>Path Setting(s)</b></label></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td width='200'><label>Home Path</label></td>" + \
              "				<td><input name='home' type='text' value='"); write(xbmcCfgGetOption("home")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>Album(s) Path</label></td>" + \
              "				<td><input name='albums' type='text' value='"); write(xbmcCfgGetOption("albums")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>Cache Path</label></td>" + \
              "				<td><input name='cachepath' type='text' value='"); write(xbmcCfgGetOption("cachepath")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>CDDA Rip Path</label></td>" + \
              "				<td><input name='CDDARipPath' type='text' value='"); write(xbmcCfgGetOption("CDDARipPath")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>Playlist(s) Path</label></td>" + \
              "				<td><input name='playlists' type='text' value='"); write(xbmcCfgGetOption("playlists")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>Recording(s) Path</label></td>" + \
              "				<td><input name='recordings' type='text' value='"); write(xbmcCfgGetOption("recordings")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>Shortcut(s) Path</label></td>" + \
              "				<td><input name='shortcuts' type='text' value='"); write(xbmcCfgGetOption("shortcuts")); write("' size='25'><br></td>" + \
              "			</tr>" );
        write("			<tr>" + \
              "				<td><label>Screenshot(s) Path</label></td>" + \
              "				<td><input name='screenshots' type='text' value='"); write(xbmcCfgGetOption("screenshots")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>Subtitle(s) Path</label></td>" + \
              "				<td><input name='subtitles' type='text' value='"); write(xbmcCfgGetOption("subtitles")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>Thumbnail(s) Path</label></td>" + \
              "				<td><input name='thumbnails' type='text' value='"); write(xbmcCfgGetOption("thumbnails")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>Trainer(s) Path</label></td>" + \
              "				<td><input name='trainerpath' type='text' value='"); write(xbmcCfgGetOption("trainerpath")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td align=center><label><b>Logging</b></label></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td width='200'><label>Log Level</label></td>" + \
              "				<td><input name='loglevel' type='text' value='"); write(xbmcCfgGetOption("loglevel")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td width='200'><label>Log Path</label></td>" + \
              "				<td><input name='logpath' type='text' value='"); write(xbmcCfgGetOption("logpath")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td align=center><label><b>Extensions(s)</b></label></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>Picture Extensions</label></td>" + \
              "				<td><input name='pictureextensions' type='text' value='"); write(xbmcCfgGetOption("pictureextensions")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>Music Extensions</label></td>" + \
              "				<td><input name='musicextensions' type='text' value='"); write(xbmcCfgGetOption("musicextensions")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>Video Extensions</label></td>" + \
              "				<td><input name='videoextensions' type='text' value='"); write(xbmcCfgGetOption("videoextensions")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td align=center><label><b>Misc Settings</b></label></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>CDDB IP Address</label></td><td>" + \
              "				<input name='CDDBIpAddress' type='text' value='"); write(xbmcCfgGetOption("CDDBIpAddress")); write("' size='25'><br></td>" + \
              "			</tr>");
        write("			<tr>" + \
              "				<td><label>Startup Window</label></td>" + \
              "				<td><input name='startwindow' type='text' value='"); write(xbmcCfgGetOption("startwindow")); write("' size='25'><br></td>" + \
              "			</tr>");
	
        // AutoDetectFG
        write("			<tr>" + \
              "					<td><label>Auto Detect F/G</label></td><td>" + \
              "           <input name='autodetectFG' type='checkbox' value='true' ");
              if (xbmcCfgGetOption("autodetectFG") == "yes")	write("checked>");
              else write(">");
        write("         <br></td>" + \
              "			</tr>");
	
        // Use F Drive
        write("			<tr>" + \
              "					<td><label>Use F Drive</label></td><td>" + \
              "           <input name='useFDrive' type='checkbox' value='true' ");
              if (xbmcCfgGetOption("useFDrive") == "yes")	write("checked>");
              else write(">");
        write("         <br></td>" + \
              "			</tr>");
    
        // Use G Drive
        write("			<tr>" + \
              "					<td><label>Use G Drive</label></td><td>" + \
              "           <input name='useGDrive' type='checkbox' value='true' ");
              if (xbmcCfgGetOption("useGDrive") == "yes")	write("checked>");
              else write(">");
	
        // Use PCDVDROM
        write("			<tr>" + \
              "					<td><label>Use PC DVDROM</label></td><td>" + \
              "           <input name='usePCDVDROM' type='checkbox' value='true' ");
              if (xbmcCfgGetOption("usePCDVDROM") == "yes")	write("checked>");
              else write(">");
	
        // Detect ISO
        write("			<tr>" + \
              "					<td><label>Auto Detect UDF/ISO</label></td><td>" + \
              "           <input name='detectAsIso' type='checkbox' value='true' ");
              if (xbmcCfgGetOption("detectAsIso") == "yes")	write("checked>");
              else write(">");
        write("         <br></td>" + \
              "			</tr>");
    
        // Display remote codes
        write("			<tr>" + \
              "					<td><label>Display remote codes</label></td><td>" + \
              "           <input name='displayremotecodes' type='checkbox' value='true' ");
              if (xbmcCfgGetOption("displayremotecodes") == "yes")	write("checked>");
              else write(">");
        write("         <br></td>" + \
              "			</tr>");
        // Display Free Memory
        write("			<tr>" + \
              "					<td><label>Display Free Memory</label></td><td>" + \
              "           <input name='showfreemem' type='checkbox' value='true' ");
              if (xbmcCfgGetOption("showfreemem") == "yes")	write("checked>");
              else write(">");
        write("         <br></td>" + \
              "			</tr>");
    
        write("		</table><br>" + \
              "		<input type='submit' name='save' value='save'>" + \
              "	</form><br>");
      }
      else if (page == "editbookmark")
      {
        if (isset("type") == "1" && isset("position") == "1")
        {
          write("<form name='savebookmark' method='post' action='?DisplayConfiguration=true&amp;page=bookmarks&amp;action=savebookmark'>\n");
          write("<input name='position' type='hidden' value='" + position + "'>\n");
          write("<input name='type' type='hidden' value='" + type + "'>\n");
          write("  <table width='500' border='0'>\n");
          write("    <tr> \n");
          write("      <td><label>name</label></td>\n");
          write("      <td><input type='text' name='name' value='" + xbmcCfgGetBookmark(type, "name", position) + "'></td>\n");
          write("    </tr>\n");
          write("    <tr> \n");
          write("      <td><label>path</label></td>\n");
          write("      <td><input type='text' name='path' value='" + xbmcCfgGetBookmark(type, "path", position) + "'></td>\n");
          write("    </tr>\n");
          write("  </table><br>\n");
          write("  <input type='submit' name='save' value='save'>\n");
          write("</form>\n");
        }
      }
      else if (page == "addbookmark")
      {
        var data = "<form name='addbookmark' method='post' action='?DisplayConfiguration=true&amp;page=bookmarks&amp;action=addbookmark'>\n";
        data = data + "  <table width='500' border='0'>\n";
        data = data + "    <tr> \n";
        data = data + "      <td><label>Type</label></td>\n";
        data = data + "      <td>";
        data = data + "        <select name='type'>\n";
        data = data + "          <option value=files>File</option>\n";
        data = data + "          <option value=music>Music</option>\n";
        data = data + "          <option value=myprograms>Program</option>\n";
        data = data + "          <option value=pictures>Picture</option>\n";
        data = data + "          <option value=video>Video</option>\n";
        data = data + "        </select>\n";
        data = data + "      </td>\n";
        data = data + "    </tr>\n";
        data = data + "    <tr> \n";
        data = data + "      <td><label>Name</label></td>\n";
        data = data + "      <td><input type='text' name='name' value=''></td>\n";
        data = data + "    </tr>\n";
        data = data + "    <tr> \n";
        data = data + "      <td><label>Path</label></td>\n";
        data = data + "      <td><input type='text' name='path' value=''></td>\n";
        data = data + "    </tr>\n";
        data = data + "  </table><br>\n";
        data = data + "  <input type='submit' name='save' value='save'>\n";
        data = data + "</form>\n";
    
        write(data);
      }
      if (page == "load_save")
      {
        write("<br><br><a href='?DisplayConfiguration=true&amp;action=save'>Save</a>\n");
      }
    }
%>