// Ctor
function Labels() {
	g_TaskUsers.setAutocompleteForm();
	g_TaskUsers.setTrashDroppableUsers();
}


Labels.prototype.userDiv = function ( user_id, label, initials) {
	return "<div class='user-thumb' user-initials='"+initials+"' user-id='"+user_id+"' id='user-id-"+user_id+"' >"+initials+"</div>";
}


Labels.prototype.appendUser2List = function (user_id, label, initials) {
	$("#label-users-list").append(this.userDiv(user_id, label, initials));
	$("#user-id-"+user_id ).draggable({ helper: "clone" });
}


Labels.prototype.updateLabelUsers = function (project_id){
	$("#label-users-list").html("");
	
	$.ajax({
		url: "/users/browse/"+project_id, 
		type: "get", 
		success: function(result){
			if(result.status == 'Ok') {
				$(result.data).each(function(i, e){
					g_Labels.appendUser2List(e.id, e.label, e.initials);
				});
			} else Utils.alert("Error: "+result.message);
		}
	});
}


Labels.prototype.addUser2Label = function (label_id, user_id, label, initials) {
	$.ajax({
		url: "/users/add/"+label_id, 
		type: "get",
		data: { id: user_id },
		success: function(result) {
			if(result.status=='Ok') {
				g_Labels.appendUser2List(user_id, label, initials);
			} else Utils.alert("Error: "+result.message);
		}
	});
}



Labels.prototype.rgb2hex = function (rgb) {
	rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
	return ("0" + parseInt(rgb[1],10).toString(16)).slice(-2) +
		("0" + parseInt(rgb[2],10).toString(16)).slice(-2) +
		("0" + parseInt(rgb[3],10).toString(16)).slice(-2);
}

Labels.prototype.getSelectedLabels = function () {
	var labels = $("#labels-list").jstree("get_selected");
	return labels.join();
}

Labels.prototype.projectLI = function (e) {
	var html = '';
	html += "<li id='label-"+e.id+"' title='Double click to change the tag name' label-id='"+e.id+"' >";
	html += '<span>';
	html += e.label;
	html += '</span>';
	html += "<div class='color label-color-"+e.id+"' label-id='"+e.id+"' style='background-color:"+e.color+"' >&nbsp;</div>";
	
	html += '<i class="separator">&nbsp;&nbsp;</i>';
	if(!e.is_project && e.can_delete) html += '<i class="glyphicon glyphicon-trash"></i>';
	html += '</li>';
	return html;
}


Labels.prototype.getSort = function () {
	var sortCol = $("#task_table_header").find("TH[sort='sort']");
	if(sortCol.length) return sortCol.attr('name');
	return
}







Labels.prototype.loadLabels = function () {
	
	$('#labels-list').jstree({
		'core' : {
			'data' : {
				'url' : '/labels/browse/',
				'data' : function (node) { return { 'id' : node.id }; }
			},
			'check_callback' : true,
			'themes' : { 'responsive' : false, "icons":false, 'dots':false },
			"multiple" : false,
		},
		'plugins' : ['dnd','contextmenu']
		
		//'plugins' : ['state','dnd','contextmenu','wholerow']
	}).on('move_node.jstree', function (e, data) {
		$.get(
			'/labels/move/', 
			{ 'id' : data.node.id, 'parent' : data.parent, 'position' : data.position }
		).fail(function () { data.instance.refresh(); });
	})
	.on('select_node.jstree', function (e, data) { 
		g_Labels.updateTasks(data.selected, false);
		$('.menu-button').hide();
		var button = $('#'+data.selected+".jstree-node .menu-button.menu-button-"+data.selected);
		button.show();
		button.click(function(){
			$('#'+data.selected+".jstree-node .color:first").click();
		});
	})
	.on('delete_node.jstree', function (e, data) {
		$.confirm({
			text: "Do you confirm the deletion?",
			confirm: function(button) {
			    $.ajax({
					url: "labels/del/"+data.node.id, 
					success: function(result){
						if(result.status!='Ok'){
							data.instance.refresh();
							Utils.alert("Error: "+result.message);
						}
					}
				}).fail(function () { data.instance.refresh(); });
			},
			cancel: function(button){ data.instance.refresh();	 }
		});
		
	}).on('create_node.jstree', function (e, data) {
		
		$.ajax({
			url: "labels/add/", 
			type: "get",
			data: { label_name: data.node.text, id: data.node.parent, 'position' : data.position }, 
			success: function(result){
				if(result.status=='Ok')
					data.instance.set_id(data.node, result.id);
				else{ 
					data.instance.refresh();
					Utils.alert("Error: "+result.message);
				}
			}
		}).fail(function () { data.instance.refresh(); });

	}).on('rename_node.jstree', function (e, data) {
		
		$.ajax({
			url: "labels/rename/"+data.node.id, 
			type: "get",
			data: { 
				label_name:  data.text
			}, 
			success: function(result){
				if(result.status!='Ok'){ 
					data.instance.refresh();
					Utils.alert("Error: "+result.message);
				}
			}
		});

	}).on('copy_node.jstree', function (e, data) {
		$.ajax({
			url: "labels/copy/", 
			type: "get",
			data: { 'id' : data.original.id, 'parent' : data.parent, 'position' : data.position }, 
			success: function(result){
				if(result.status!='Ok') Utils.alert("Error: "+result.message);
			}
		}).always(function (){ data.instance.refresh(); });
	}).on('redraw_node.jstree', function (e, data) {
		var hidecss = "";
		if( data.instance.is_selected(data.node.id)) hidecss = "style='display:inline'";
		
		
		$(data.li).children('i:first').after("<span "+hidecss+" class='menu-button btn btn-default menu-button-"+data.node.id+"' ><i class='glyphicon glyphicon-wrench'></i></span>");
		var color = '#FFF';
		if(data.node.data){
			color = data.node.data.color;
		}
		$(data.li).prepend("<span class='color' style='background-color:"+color+"' >&nbsp;</span>");
		

		
		$(data.li).children('.color').ColorPicker({
			color: "#FFF",
			eventName: 'click',
			onShow: function (colpkr) {
				$(".jstree-node .color").ColorPickerHide();
	            $(colpkr).fadeIn(500);
	            return false;
	        },
			onChange: function(hsb, hex, rgb){
				$(data.li).children('.color').css('background-color', '#'+hex);
			},
			onHide: function(hsb, hex, rgb){
				/*
				var name = label_elem.children('span').html();
				var color = g_Labels.rgb2hex( color_elem.css('background-color') );
				$.ajax({
					url: "labels/add/"+label_id, 
					type: "get",
					data: { 
						label_name: name,
						label_color: color
					}
				});*/
			},
		});
	});

}





Labels.prototype.loadLabels_ = function () {

	var selected_labels = $('.labels-list li.selected'); // Used to store the current selected labels

	$('.labels-list li').remove();
	$.ajax({
		url: "labels/browse/", 
		success: function(result){
			if (result.status == 'Ok') {
				var html = '';
				$(result.data).each(function(i, e){if(e.is_project) html+= g_Labels.projectLI(e);});
				$('#labels-list').append(html);

				html = '';
				$(result.data).each(function(i, e){if(!e.is_project) html+= g_Labels.projectLI(e)});
				$('#labels-list').append(html);

				$('.labels-list li').each(function(i, e){
					var label_elem = $(this);
					var label_id = label_elem.attr('label-id');
					var color_elem = label_elem.children('.color');
					var current_color = g_Labels.rgb2hex( color_elem.css('background-color') );
					
					color_elem.ColorPicker({
						color: "#"+current_color,
						eventName: 'dblclick',
						onShow: function (colpkr) {
				            $(colpkr).fadeIn(500);
				            return false;
				        },
				        onChange: function(hsb, hex, rgb){
							var label_id = color_elem.attr('label-id');
							$('.label-color-'+label_id).css('background-color', '#'+hex);
						},
						onHide: function(hsb, hex, rgb){
							/*
							var name = label_elem.children('span').html();
							var color = g_Labels.rgb2hex( color_elem.css('background-color') );
							$.ajax({
								url: "labels/add/"+label_id, 
								type: "get",
								data: { 
									label_name: name,
									label_color: color
								}
							});*/
						},
					});

				});

				//Label selected
				/*
				$('.labels-list li span').click(function(evt){

					if(!evt.ctrlKey){
						$('.labels-list li').removeClass('selected');
						$(this).parent().addClass('selected');
					} else {
						if( $(this).parent().hasClass('selected') && $('.labels-list li.selected').length>1 ) 
							$(this).parent().removeClass('selected');
						else
							$(this).parent().addClass('selected');
					}

					var headers = [];
					var count = 0;
					$('.labels-list li.selected span').each(function(i,e){
						headers.push($(e).html());
					});
					if(headers.length==1)
						$('#grp-content-title').html("<h1>"+headers.join()+"</h1>");
					else
						$('#grp-content-title').html("<h1><small>"+headers.join()+"</small>&nbsp;</h1>");


					var label_id = $(this).parent().attr("label-id");
					g_Labels.updateTasks(label_id, false);
				});*/
				

				// Defining the click handlers for filters
				$('#filter-panel input').click(function() {
					if ($(".labels-list .selected").length) {
						var label_id = $($("#labels-list .selected")[0]).attr("label-id");
						g_Tasks.startLoading();
						var filters = g_Labels.getFilters();
						var labels = g_Labels.getSelectedLabels();
						var sort =  g_Labels.getSort();
						$.ajax({
							url: "tasks/browse/"+label_id+"/", 
							data: {
								filters: filters,
								ids: labels,
								sort: sort
							},
							success: function(result){
								if(result.status == 'Ok') {
									g_Tasks.displayTasks(result.data);
									g_Labels.updateLabelUsers(label_id);
								} else Utils.alert("Error: "+result.message);
							}
						});
					}
				});

				$('.labels-list li span').dblclick(function(){
					var label_id = $(this).parent().attr('label-id');
					var value = $(this).parent().children('span').html();

					$(this).parent().children().hide();
					$(this).parent().append('<input type="text" class="label-input" value="'+value+'" />');
					$(this).parent().children('input').focus();

					g_Labels.editHandler($(this).parent().children('input'), label_id);

					$(this).parent().children('input').focusout(function(){
						$('#label-'+label_id).children().show();
						$(this).remove();
					});
				});

				$('.labels-list li .color').draggable({
					helper: "clone"
				});

				$('.labels-list li .glyphicon-trash').click(function(){
					var label_id = $(this).parent().attr('label-id');
					var label_elem = $(this).parent();

					$.confirm({
						text: "Do you confirm the deletion?",
						confirm: function(button) {
							    $.ajax({
								url: "labels/del/"+label_id, 
								success: function(result){
									if(result.status=='Ok'){
										label_elem.remove();
									} else Utils.alert("Error: "+result.message);
								}
							});
						}
					});
				});

				//After reloading all labels, select the previous selected labels
				selected_labels.each(function(i, e){ $("#"+$(this).attr('id')).addClass('selected'); });

			} else Utils.alert("Error: "+result.message);
		}
	});


};










Labels.prototype.getQuery = function () {
	return $("#query-box-input").val();
}

Labels.prototype.updateTasks = function (labels, sortField) {
	if(sortField==undefined) sortField = true;

	g_Details.hideDetails();
	g_Tasks.startLoading();

	var sorts = sortField ? this.getSort() : undefined;
	var query = this.getQuery();

	
	if(labels) {
		$.ajax({
			url: "tasks/browse/", 
			data: {
				ids: labels.join(),
				sort: sorts,
				query: query
			},
			success: function(result){
				if(result.status == 'Ok') {
					g_Tasks.displayTasks(result.data);
					g_Labels.updateLabelUsers(labels);
				} else Utils.alert("Error: "+result.message);
			}
		});
	}
}