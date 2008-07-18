<script type="text/javascript">

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



function PlayMedia(mediapath){

	var url = '/xbmcCmds/xbmcHttp?command=playfile&parameter='+mediapath;
	http.open("get",url);
	http.send("");

}

function QueryMusicDatabase(query){

	document.getElementById("results").innerHTML = "";

	var sqlquery = "SELECT strPath, strFileName, strTitle, strAlbum, strArtist  from songview WHERE strTitle LIKE '%%"+query+"%%' LIMIT 50;";
    var url = "/xbmcCmds/xbmcHttp?command=QueryMusicDatabase&parameter="+sqlquery;
	resultsHTML = "<b>"+unescape(sqlquery)+"</b><br><br>";

    http.open("get",url);
    http.onreadystatechange = function(){
		if(http.readyState == 4){
		responseArr = http.responseText.split("<li>");

			while(responseArr.length>1){

			//We know that we pulled 5 columns, 
			//so we can pop off 5 at a time for each song
			strArtist = responseArr.pop(); 
			strAlbum = responseArr.pop();
			strTitle = responseArr.pop();
			strFileName = responseArr.pop();
			strPath = responseArr.pop();

			resultsHTML += "<a href='javascript:PlayMedia(\""+escape(strPath)+"/"+escape(strFileName)+"\");'><img src='http://liquidice629.googlepages.com/play.gif' border=0>&nbsp;"+strTitle+"</a><br><b>Album:</b> "+strAlbum+"<br><b>Artist:</b> "+strArtist+"<br><br>";

			}
			document.getElementById("results").innerHTML = resultsHTML;
		}
	}
	http.send("");
}


function showTopSongs(){

sqlquery = "select * from songview join albumview on (songview.strAlbum = albumview.strAlbum and songview.strPath like albumview.strPath) where albumview.idalbum in (select song.idAlbum from song where song.iTimesPlayed>0 group by idalbum order by sum(song.iTimesPlayed) desc limit 100) order by albumview.idalbum in (select song.idAlbum from song where song.iTimesPlayed>0 group by idalbum order by sum(song.iTimesPlayed) desc limit 100)";

	document.getElementById("results").innerHTML = "";

    var url = "/xbmcCmds/xbmcHttp?command=QueryMusicDatabase&parameter="+sqlquery;
	resultsHTML = "<b>"+unescape(sqlquery)+"</b><br><br>";

    http.open("get",url);
    http.onreadystatechange = function(){
		if(http.readyState == 4){
		responseArr = http.responseText.split("<li>");



			while(responseArr.length>1){

			//We know that we pulled 5 columns, 
			//so we can pop off 5 at a time for each song
		//	strArtist = responseArr.pop(); 
		//	strAlbum = responseArr.pop();
		//	strTitle = responseArr.pop();
		//	strFileName = responseArr.pop();
		//	strPath = responseArr.pop();


	//		resultsHTML += "<a href='javascript:PlayMedia(\""+escape(strPath)+"/"+escape(strFileName)+"\");'><img src='http://liquidice629.googlepages.com/play.gif' border=0>&nbsp;"+strTitle+"</a><br><b>Album:</b> "+strAlbum+"<br><b>Artist:</b> "+strArtist+"<br><br>";

	resultsHTML += responseArr.pop() + "<br>";

			}
			document.getElementById("results").innerHTML = resultsHTML;
		}
	}
	http.send("");



}

</script>



<input onchange="QueryMusicDatabase(document.getElementById('query').value);" type="text" name="query" id="query">
&nbsp;&nbsp;&nbsp;
<a href="javascript:QueryMusicDatabase(document.getElementById('query').value);">Search</a><br><br>
<div id="results">

</div>

<script>

showTopSongs();

</script>