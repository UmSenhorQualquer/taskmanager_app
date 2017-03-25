// Ctor
function TaskUsers() {

}


TaskUsers.prototype.setAutocompleteForm = function() {
	$( "#add-user-input" ).autocomplete({
		source: "/users/search/",
		minLength: 2,
		select: function( event, ui ) {
			if(ui.item){
				var countSelected = $(".labels-list .selected").length;
				if(countSelected==1){
					var label_id = $(".labels-list .selected").attr('label-id');
					g_Labels.addUser2Label(label_id, ui.item.id, ui.item.label, ui.item.initials);
					
				}else
				if(countSelected>1){
					alert("Please select only one label.");
				}else
				if(countSelected==0){
					alert("Please select one label.");
				}
			}
		},
		close: function( event, ui ){
			$("#add-user-input").val('');
			$("#add-user-input").focusout();
		}
	});
}


TaskUsers.prototype.setTrashDroppableUsers = function() {
	$( ".trash" ).droppable({
		hoverClass: "selected",
		drop: function( event, ui ) {
			var label_id = $(".labels-list .selected").attr('label-id');
			var user_id = ui.draggable.attr('user-id');
			$.ajax({
				url: "/users/del/"+label_id, 
				type: "get",
				data: { id: user_id },
				success: function(result){
					if(result.status=='Ok') {
						ui.draggable.remove();
					} else Utils.alert("Error: "+result.message);
				}
			});
		}
	});
}


TaskUsers.prototype.setDeleteTaskUser = function(rowSelector) {
	var selector = ".task-user";
	if( rowSelector ) selector = rowSelector+" "+selector;

	$( selector ).draggable({ 
		revert: true,
		drag: function( event, ui ){
			var user_id = $(this).attr('user-id');
			var task_id = $(this).parent().parent().parent().attr('task-id');
			
			if( ui.position.left>100){
				$.ajax({
					url: "/users/task/del/"+task_id, 
					type: "get",
					data: { id: user_id }, 
					success: function(result){
						if(result.status=='Ok') {
							ui.helper.remove();
						} else Utils.alert("Error: "+result.message);
					}
				});
			}
		}
	});
}


TaskUsers.prototype.setAddTaskUser = function(rowSelector) {
	var selector = ".users-container";
	if( rowSelector ) selector = rowSelector+" "+selector;

	$( selector ).droppable({
		accept: ".user-thumb",
		drop: function( event, ui ) {
			var user_id = ui.draggable.attr('user-id');
			var task_id = $(this).parent().parent().attr('task-id');
			var d = $(this);

			$.ajax({
				url: "/users/task/add/"+task_id, 
				type: "get",
				data: { id: user_id },
				success: function(result){		
					if(result.status=='Ok'){
						var user_initials = ui.draggable.attr('user-initials');
						var div = "<div class='task-user' id='task-user-id-"+user_id+"' user-id='"+user_id+"'  >"+user_initials+"</div>";
						d.append(div);

						$("#task-user-id-"+user_id).draggable({ 
							revert: true,
							drag: function( event, ui ){
								if( ui.position.left>100){
									ui.helper.remove();
								}
							}
						});
					} else Utils.alert("Error: "+result.message);
				}
			});
		}
	});
}