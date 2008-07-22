<html>
	<head>
		<title>
			XBMC HTTP AJAX API
		</title>
		<link rel="stylesheet" href="style/default.css" type="text/css" media="screen" />
		<script type="text/javascript" src="javascript/prototype.js"></script>
		<script type="text/javascript" src="javascript/xbmc.js"></script>
		
		<script type="text/javascript">
			var xbmc = new XBMC();
			xbmc.SetLoadingMessageId('loadingMessage');
			
			function GetCurrentPlaying()
			{
				xbmc.GetCurrentPlaying('filename:artist:songno:type:title:track:album:url:lyrics:bitrate:samplerate:thumb:playstatus:time:duration:percentage:filesize');
				xbmc.GetCurrentPlaylist();
				xbmc.GetShares('music');
				xbmc.GetShares('video');
				xbmc.GetShares('pictures');
				xbmc.GetShares('files');
				xbmc.GetCurrentSlide();
			}
			
			
			
			function UpdateCurrentPlaying( interval )
			{
				var updateTimer = setInterval("xbmc.GetCurrentPlaying('filename:artist:songno:type:title:track:album:url:lyrics:bitrate:samplerate:thumb:playstatus:time:duration:percentage:filesize')", interval*1000);
			}
		</script>
		<style>
			html,body			{ font-family:verdana; font-size:11px; }
			table				{ width:100%; }
			td					{ font-size:11px; padding:4px; }
			.title				{ background-color:#EEE; color:#555; width:300px; padding:10px; }
			.value				{ border:1px solid #DDD; padding:10px; }
			.loadingMessage		{ position:absolute; top:10px; right:10px; padding:10px; border:1px solid #555; font-weight:bold; }
			.code				{ border:1px solid #EEE; color:green; font-family:Courier New; font-size:12px; padding:20px; }
			a					{ font-weight:normal; text-decoration:none; color:#666; }
			a:hover				{ color:#000; font-weight:bold;}
			.links				{ background-color:#EEE; border:1px solid #FFCC00; padding:20px; }
			select				{ border:1px solid #666; }
			#Directory_video	{ max-height:300px; overflow:auto; }
			#Directory_music	{ max-height:300px; overflow:auto; }
			#Directory_photos	{ max-height:300px; overflow:auto; }
			#Directory_files	{ max-height:300px; overflow:auto; }
		</style>
	</head>
<body onload="GetCurrentPlaying(); UpdateCurrentPlaying(10)">

<h1>
	XBMC HTTP AJAX API
</h1>

<div class="links">
	<ul>
		<li>
			<a href="#lConstructor">Constructor</a>
		</li>
		<li>
			<a href="#lGetCurrentPlaylist">GetCurrentPlaylist</a>
		</li>
		<li>
			<a href="#lGetShares">GetShares</a>
		</li>
		<li>
			<a href="#lGetCurrentPlaying">GetCurrentPlaying</a>
		</li>
		<li>
			<a href="#lGetCurrentSlide">GetCurrentSlide</a>
		</li>
	</ul>
</div>

<br />
<br />
<br />

<div id="temp"></div>

<div id="loadingMessage" class="loadingMessage">
	Loading...
</div>


<h2 id="lConstructor">
	 Construct class and set settings
</h2>

<div class="code">
	var xbmc = new XBMC();
	<br />
	SetLoadingMessageId(loadingMessageId);
</div>
<br />
<br />

<h2 id="lGetCurrentPlaylist">
	 GetCurrentPlaylist
</h2>

<div class="code">
	xbmc.GetCurrentPlaylist();
</div>
<br />
<table>
	<tr>
		<td align="right" class="title">
			Current Playlist Id
		</td>
		<td id="CurrentPlaylist" class="value"></td>
	</tr>
</table>
<br />
<br />

<h2 id="lGetShares">
	 GetShares
</h2>

<div class="code">
	xbmc.GeShares('music');
</div>
<br />
<table>
	<tr>
		<td align="right" class="title">
			Music Shares
		</td>
		<td id="Shares_music" class="value"></td>
	</tr>
	<tr>
		<td colspan="2" class="value">
			<div id="Directory_music"></div>
		</td>
	</tr>
</table>
<br />
<div class="code">
	xbmc.GetShares('video');
</div>
<br />
<table>
	<tr>
		<td align="right" class="title">
			Video Shares
		</td>
		<td id="Shares_video" class="value"></td>
	</tr>
	<tr>
		<td colspan="2" class="value">
			<div id="Directory_video"></div>
		</td>
	</tr>
</table>
<br />
<div class="code">
	xbmc.GetShares('pictures');
</div>
<br />
<table>
	<tr>
		<td align="right" class="title">
			Picture shares
		</td>
		<td id="Shares_pictures" class="value"></td>
	</tr>
	<tr>
		<td colspan="2" class="value">
			<div id="Directory_pictures"></div>
		</td>
	</tr>
</table>
<br />
<div class="code">
	xbmc.GetShares('files');
</div>
<br />
<table>
	<tr>
		<td align="right" class="title">
			File shares
		</td>
		<td id="Shares_files" class="value"></td>
	</tr>
	<tr>
		<td colspan="2" class="value">
			<div id="Directory_files"></div>
		</td>
	</tr>
</table>
<br />
<br />

<h2 id="lGetCurrentPlaying">
	 GetCurrentPlaying
</h2>

<div class="code">
	xbmc.GetCurrentPlaying('filename:artist:songno:type:title:track:album:url:lyrics:bitrate:samplerate:thumb:playstatus:time:duration:percentage:filesize');
</div>
<br />
<table>
	<tr>
		<td align="right" class="title">
			Filename
		</td>
		<td id="CurrentPlaying_filename" class="value"></td>
	</tr>
	<tr>
		<td align="right" class="title">
			Song Number (in playlist)
		</td>
		<td id="CurrentPlaying_songno" class="value"></td>
	</tr>
	<tr>
		<td align="right" class="title">
			Media type
		</td>
		<td id="CurrentPlaying_type" class="value"></td>
	</tr>
	<tr>
		<td align="right" class="title">
			Title
		</td>
		<td id="CurrentPlaying_title" class="value"></td>
	</tr>
	<tr>
		<td align="right" class="title">
			Track (on album)
		</td>
		<td id="CurrentPlaying_track" class="value"></td>
	</tr>
	<tr>
		<td align="right" class="title">
			Artist
		</td>
		<td id="CurrentPlaying_artist" class="value"></td>
	</tr>
	<tr>
		<td align="right" class="title">
			Album
		</td>
		<td id="CurrentPlaying_album" class="value"></td>
	</tr>
	<tr>
		<td align="right" class="title">
			URL
		</td>
		<td id="CurrentPlaying_url" class="value"></td>
	</tr>
	<tr>
		<td align="right" class="title">
			Lyrics
		</td>
		<td id="CurrentPlaying_lyrics" class="value"></td>
	</tr>
	<tr>
		<td align="right" class="title">
			Bitrate
		</td>
		<td id="CurrentPlaying_bitrate" class="value"></td>
	</tr>
	<tr>
		<td align="right" class="title">
			Samplerate
		</td>
		<td class="value">
			<span id="CurrentPlaying_samplerate"></span> Khz
		</td>
	</tr>
	<tr>
		<td align="right" class="title">
			Thumbnail
		</td>
		<td id="CurrentPlaying_thumb" class="value"></td>
	</tr>
	<tr>
		<td align="right" class="title">
			Play Status
		</td>
		<td id="CurrentPlaying_playstatus" class="value"></td>
	</tr>
	<tr>
		<td align="right" class="title">
			Current play time
		</td>
		<td id="CurrentPlaying_time" class="value"></td>
	</tr>
	<tr>
		<td align="right" class="title">
			Duration
		</td>
		<td id="CurrentPlaying_duration" class="value"></td>
	</tr>
	<tr>
		<td align="right" class="title">
			Percentage
		</td>
		<td class="value">
			<span id="CurrentPlaying_percentage"></span> %
		</td>
	</tr>
	<tr>
		<td align="right" class="title">
			File size
		</td>
		<td class="value">
			<span id="CurrentPlaying_filesize"></span> B
		</td>
	</tr>
</table>
<br />
<br />

<h2 id="lGetCurrentSlide">
	 GetCurrentSlide
</h2>

<div class="code">
	xbmc.GetCurrentSlide();
</div>
<br />
<table>
	<tr>
		<td align="right" class="title">
			Current image displayed (image, not coverart)
		</td>
		<td id="CurrentSlide" class="value"></td>
	</tr>
</table>

</body>
</html>