<!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.0//EN" "http://www.wapforum.org/DTD/xhtml-mobile10.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
</head>
<body>
<h5><a href="index.html" target="_top">&lt; Back</a></h5>
<table width="90%" border="0" align="left" cellpadding="0" cellspacing="0">
<% var z; %>
<% var n; %>
<% var i; %>
<% n = xbmcCommand("catalog","items"); %>
<% i = xbmcCommand("catalog","first"); %>
<% for (z=0; z<n; z=z+1) { \
     write("<tr>" + \
           "<td width='100%' height='20'>" + \
           "<a href='/xbmcCmds/xbmcForm?command=catalog&parameter=select," + z + "&redirect=selectvideos.asp'");
           if (xbmcCommand("catalog","type," + z) == "videos")
           {
           	   write( "target='contentFrame'");
           }
           
     write("<font size='1' face='Arial, Helvetica, sans-serif'> " + i + "</font>"); \

     i = xbmcCommand("catalog","next"); \

     write("<a>  </a>"); \  
     write("<a target='contentFrame' href=/xbmcCmds/xbmcForm?command=catalog&parameter=que," + z + "&redirect=selectvideos.asp><font size='2' face='Arial, Helvetica, sans-serif'> </font></a></td>" + \
           "</a></tr>"); \
   } %>
</table>
</body>
</html>


