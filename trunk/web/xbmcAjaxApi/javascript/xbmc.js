//XBMC  Javascript HTTP Api
//Check http://xbmc.org/wiki/?title=WebServerHTTP-API for documentation

var myGlobalHandlers = 
{
	onCreate: function()
	{
		if( loadingMessageId!= "" )
			Element.show(loadingMessageId);
	},
	onFailure: function()
	{
		alert("Operation Failed");
	},
	onComplete: function() 
	{
		if(Ajax.activeRequestCount == 0)
		{
			if( loadingMessageId!= "" )
				Element.hide(loadingMessageId);
		}
	}
};
Ajax.Responders.register(myGlobalHandlers);

function XbmcCmds()
{
	var xbmcHttp 			= "/xbmcCmds/xbmcHttp?command=";
	this.MediaLocationUrl	= function ( aParam ){ return xbmcHttp+"GetMediaLocation&parameter="+aParam['type']+";"+aParam['path']+";"+aParam['option']; };
	this.SharesUrl 			= function ( type ){ return xbmcHttp+"GetShares&parameter="+type; };
	this.CurrentPlaylistUrl = function (){ return xbmcHttp+"GetCurrentPlaylist"; };
	this.CurrentPlayingUrl	= function (){ return xbmcHttp+"GetCurrentlyPlaying"; };
	this.CurrentSlideUrl	= function (){ return xbmcHttp+"GetCurrentSlide"; };
	this.DirectoryUrl	 	= function ( aParam ){ return xbmcHttp+"GetDirectory&parameter="+aParam['path']+";"+aParam['extension']+";"+aParam['date_modified']; };
	this.GuiDescriptionUrl 	= function () { return xbmcHttp+"GetGuiDescription"; };
}

var loadingMessageId = "";
var XbmcCmds 		 = new XbmcCmds();

function XBMC()
{
	
	this.GetCurrentPlaylist = function ()
	{
		new Ajax.Request( XbmcCmds.CurrentPlaylistUrl(), 
		{
			method:'get', 
			onSuccess: function(transport)
			{
				var aResponseText 				= transport.responseText.split("<li>");
				$('CurrentPlaylist').innerHTML  = aResponseText[0];
			}
		});
	}
	
	this.GetShares = function ( mediaType, target )
	{
		new Ajax.Request( XbmcCmds.SharesUrl(), 
		{
			method:'get', 
			onSuccess: function(transport)
			{ 
				var aResponseText 	= transport.responseText.split("<li>");
				var aDataContainer 	= "<select id=\"select_GetDirectory\" onchange=\"javascript:xbmc.GetDirectory(this.value, 'Directory_"+mediaType+"');\" >\n<option style=\"font-weight:bold; background-color:#EEE;\">"+mediaType+"</option>\n";
				
				for( var x=0; x<aResponseText.length; x++ )
				{
					var aResponseTextElm = aResponseText[x].split(";");
					if( aResponseTextElm[0] == mediaType )
					{	
						aDataContainer += "<option value=\""+aResponseTextElm[2]+"\">"+aResponseTextElm[1]+"</option>\n";
					}	
				}
				aDataContainer += "</select>\n";
				$('Shares_'+mediaType).innerHTML = aDataContainer;
			}
		});
	}
	
	this.GetDirectory = function ( path, target )
	{
		var param				= new Array(3);
		param['path']			= path;
		param['extension']	 	= "*";
		param['date_modified'] 	= "0";
		
		new Ajax.Request( XbmcCmds.DirectoryUrl(param), 
		{
			method:'get', 
			onSuccess: function(transport)
			{ 
				var aDirUp = path.split("/");
				var dirUp = "";
				for( var w=0; w<aDirUp.length-2; w++ )
				{
					dirUp += aDirUp[w]+"/";
				}
				
				var dataContainer 	= ( path==$('select_GetDirectory').value)? "" : "<a href=\"javascript:void(0);\" onclick=\"javascript:xbmc.GetDirectory('"+dirUp+"', '"+target+"');\"><img src=\"image/icon_folder.gif\" border=\"0\">&nbsp;..</a><br />\n";
				var aResponseText  	= transport.responseText.split("<li>");
				
				for( var x=0; x<aResponseText.length; x++ )
				{
					var aResponseTextElm = aResponseText[x].split("/");
					var objName			 = aResponseTextElm[aResponseTextElm.length-2];
					dataContainer 		 += (aResponseText[x]=="" || aResponseText[x]==undefined || aResponseText[x]=="Error:Not folder" || aResponseText[x]=='Error:Missing folder' || aResponseText[x]=='<html>\n\n' || aResponseText[x]=='Error')? "" : "<a href=\"javascript:void(0);\" onclick=\"javascript:xbmc.GetDirectory('" +aResponseText[x].replace("\\", "")+ "', '" +target+ "');\"><img src=\"image/icon_folder.gif\" border=\"0\">&nbsp;" +objName+ "</a><br />\n" ;
				}
				
				$(target).innerHTML = dataContainer;
			}
		});
	}
	
	this.GetCurrentSlide = function ()
	{
		new Ajax.Request( XbmcCmds.CurrentSlideUrl(), 
		{
			method:'get', 
			onSuccess: function(transport)
			{
				var aResponseText 			= transport.responseText.split("<li>");
				$('CurrentSlide').innerHTML = aResponseText[0].replace("[", "").replace("]", "");
			}
		});
	}
	
	this.GetCurrentPlaying = function ( fields )
	{
		var aFields = fields.split(":");
		new Ajax.Request( XbmcCmds.CurrentPlayingUrl(), 
		{
			method:'get', 
			onSuccess: function(transport)
			{ 
				var aDataContainer 		= new Array();
				var aKey				= new Array();
				var aResponseText 		= transport.responseText.split("<li>");
				
				for( var x=0; x<aResponseText.length; x++ )
				{
					var aResponseTextR 		= aResponseText[x].replace(/:/,"~");
					var aResponseTextElm 	= aResponseTextR.split(/~/);
					aKey[x]					= aResponseTextElm[0].toLowerCase().replace(" ", "");
					aDataContainer[aKey[x]] = aResponseTextElm[1];
				}
				
				for( var y in aFields )
				{
					$('CurrentPlaying_'+aFields[y]).innerHTML = ( aDataContainer[aFields[y]]==undefined )? "" : aDataContainer[aFields[y]].replace("[", "").replace("]", "") ;	
				}
			}
		});
	}
	
	this.SetLoadingMessageId = function ( id )
	{
		loadingMessageId = id;
	}
}
