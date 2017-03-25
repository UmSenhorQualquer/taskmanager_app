var Utils = (function(){
	
	/* Remove a tail off a string 
	   E.g.: to remove "px" off a string "100px"
	   call "trimString("100px", "px");"
	   The return value will be the string "100" */
	var trimString = function(string, tail) {
		var strLen = string.length;
		if ( strLen < 1 || tail.length < 1 ) return string;

		var tailStartPos = string.lastIndexOf(tail);
		if (tailStartPos != -1) { // The 'tail' was found on 'string'
			return string.slice(0, tailStartPos);
		} else return string;
	}

	var getViewportSize = function() {
		var dimensions = [];
		if( typeof( window.innerWidth ) == 'number' ) {
			//Non-IE or IE9+
			dimensions[0] = window.innerWidth;
			dimensions[1] = window.innerHeight;
		} else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
			//IE 6+ in 'standards compliant mode'
			dimensions[0] = document.documentElement.clientWidth;
			dimensions[1] = document.documentElement.clientHeight;
		} else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) {
			//IE 4 compatible
			dimensions[0] = document.body.clientWidth;
			dimensions[1] = document.body.clientHeight;
		}
		return dimensions;
	}

	var readjustViewport = function() {
		/*
		// Holds the element "computed" width value; trimmed off 'px' for integer arithmetic
		var containerWidth = 1000; //Utils.trimString($("#grp-content-container").css("width"), "px");
		// The amount of pixels to be reduced on each block for adjustment fit purposes (e.g. a border is applied to a block)
		var offset = 2;
		column_1.style.width = containerWidth + "px";
		left_panel.style.width = parseInt(containerWidth * (15/100) - offset, 10) + "px";
		task_panel.style.width = parseInt(containerWidth * (55/100) - offset, 10) + "px";
		
		details_panel.style.width = parseInt(containerWidth * (30/100) - offset, 10) + "px";
		quick_reports.style.width = details_panel.style.width

		//Utils.alert(containerHeight);*/
	}

	var setMaximizeAndMinimize = function(){
		$("#grp-context-navigation").append("<button class='btn btn-warning' id='maximizeButton' ><i class='glyphicon glyphicon-resize-small'></i></button>");
		$("#grp-context-navigation").append("<a class='moreapps-link' href='/accounts/profile' >More applications</a>");
		

		$('#maximizeButton').click(function(){
			if( $(this).children('i').hasClass('glyphicon-resize-full') ){

				tasks_container.style.maxHeight='none';
				left_panel.style.maxHeight='none';
				$(this).children('i').removeClass('glyphicon-resize-full');
				$(this).children('i').addClass('glyphicon-resize-small');
				document.getElementById('grp-content').style.height = 'auto';

			}else{

				$(this).children('i').removeClass('glyphicon-resize-small');
				$(this).children('i').addClass('glyphicon-resize-full');
				tasks_container.style.maxHeight = ($(window).height()-200) + "px";
				left_panel.style.maxHeight = ($(window).height()-145) + "px";
				document.getElementById('grp-content').style.height = '0px';
			}
		});
	};

	var alert = function(msg) {
		//$("#status_bar").slideDown();
		$("#status_bar").text(msg);
		window.setTimeout(function() {
			$("#status_bar").slideUp();
		}, 5000);
	}

	return {
		getViewportSize: getViewportSize,
		trimString: trimString,
		readjustViewport: readjustViewport,
		alert: alert,
		setMaximizeAndMinimize: setMaximizeAndMinimize
	};
})();