function Tasks() {
	this.ownerProject = 0;
	this.nofColumns = 4; // The number of columns to span the Task name (description) in a title task
	this.titleModeToken = ":";
}

// BEGIN: Utilities
Tasks.prototype.setOwnerProject = function(project_id) {
	this.ownerProject = project_id;
}


Tasks.prototype.getOwnerProject = function () {
	return this.ownerProject;
}


Tasks.prototype.newDataItem = function(dataValues) {
	var newItem = [];
	newItem[0] = dataValues.task_id;
	newItem[1] = dataValues.task_is_complete;
	newItem[2] = dataValues.task_is_important;
	newItem[3] = dataValues.task_is_title;
	newItem[4] = dataValues.task_name;
	newItem[5] = dataValues.task_start_date;
	newItem[6] = dataValues.task_end_date;
	newItem[7] = dataValues.project_id;
	return newItem;
}

/*
	Receives a date either as a valid string representation (e.g.: an ISO string date representation) or
	as a valid Date object, and returns a "local" string representation of the date for user display, by
	default in the format DD/MM/YYYY HH:MM
	Optionally, separators can be provided by passing a second argument with with a valid object such as
	{date: "-", time: "."} which would yield a date in the format DD-MM-YYYY HH.MM
*/
Tasks.prototype.dateToLocalString = function(date_str, separators) {
	var date = new Date(date_str);
	return date.toString('HH:mm dd MMM, yyyy');
}


/*
	Receives a date as a valid string representation (e.g.: a string in the format DD/MM/YYYY HH:MM) and
	returns the equivalent string representation in ISO format, useful for database write
*/
Tasks.prototype.dateToISOString = function(date_str) {
	var date = new Date(date_str);
	return date.toString('HH:mm dd MMM, yyyy');
}


Tasks.prototype.clearTasks = function() {
	$("#task_new").remove();
	$(".task").remove();
}


Tasks.prototype.createTaskLines = function(result) {

	$.each(result, function(pos, item) {
		
		var tableRow = "";

		// Do NOT honor Complete or Important status if the line is in TITLE mode
		if(item.task_is_title) tableRow = "<tr class='task title "+item.style+"' task-id='"+item.task_id+"' id='task_" + item.task_id + "'>";
		else {
			// Do NOT honor Important status if task is Complete
			if(item.task_is_complete) tableRow = "<tr class='task complete "+item.style+"' task-id='"+item.task_id+"'  id='task_" + item.task_id + "'>";
			else {
				// Is task Important?
				if(item.task_is_important) 
					tableRow = "<tr class='task important "+item.style+"' task-id='"+item.task_id+"'  id='task_" + item.task_id + "'>";
				else 
					tableRow = "<tr class='task "+item.style+"' task-id='"+item.task_id+"'  id='task_" + item.task_id + "'>";
			}
		}

		var users_html = '';
		$(item.users).each(function(pos, e) {
			var css="";
			if (e.completed_task) css="completed_task_by";

			users_html += "<div class='task-user "+css+"' id='task-user-id-"+e.user_id+"' user-id='"+e.user_id+"' >"+e.user_initials+"</div>";
		});

		var labels_html = '';
		$(item.labels).each(function(pos, e) {
			labels_html += "<div title='"+e.label+"' style='background-color:"+e.color+"' label-id='"+e.id+"' class='color ui-draggable label-color-"+e.id+"' >&nbsp;</div>";
		});
		if( labels_html.length==0) labels_html = '&nbsp;'

		$('#task_table').append(tableRow + 
			"<td class='data column-complete" + ((item.task_is_title)?" hide":"") + "'><input class='complete' type='checkbox'" + ((item.task_is_complete) ? " checked='checked'" : "") + "></td>" +
			"<td class='data column-important" + ((item.task_is_title)?" hide":"") + "'><input class='important' type='checkbox'" + ((item.task_is_complete) ? " disabled='disabled'" : "") + ((item.task_is_important) ? " checked='checked'" : "") + "></td>" +
			"<td class='column-labels " + ((item.task_is_title)?" hide":"") + "'><div class='labels-container' >"+labels_html+"</div></td>" +
			"<td " + ((item.task_is_title)?"colspan='"+g_Tasks.nofColumns+"' ":"") + "class='data column-name" + ((item.task_is_title)?" title":"") + "'><input class='name' type='text'" + ((item.task_is_complete) ? " disabled='disabled'" : "") + " value='" + item.task_name + "'></td>" +
			"<td class='data column-start-date" + ((item.task_is_title)?" title":"") + "'><input id='start_date_" + item.task_id + "' class='start-date date-time-picker' type='text'" + ((item.task_is_complete) ? " disabled='disabled'" : "") + " value='" + g_Tasks.dateToLocalString(item.task_start_date) + "'></td>" +
			"<td class='data column-end-date" + ((item.task_is_title)?" title":"") + "'><input id='end_date_" + item.task_id + "' class='end-date date-time-picker' type='text'" + ((item.task_is_complete) ? " disabled='disabled'" : "") + " value='" + g_Tasks.dateToLocalString(item.task_end_date) + "'></td>" +
			"<td class='column-users'><div class='users-container'>"+users_html+"</div></td>" +
			"<td class='column-delete'><img src='/static/img/delete.png' title='' alt=''></td>" + 
			"<td class='column-handler'><img src='/static/img/row_handler.png' title='Hold to drag and drop as a predecessor of the currently selected task' alt=''></td>" + 
			"</tr>");
	});

	g_TaskUsers.setDeleteTaskUser();
	g_TaskLabels.setAddTaskLabel();
	g_TaskUsers.setAddTaskUser();
	g_TaskLabels.setDeleteTaskLabel();
}


Tasks.prototype.updateTaskNew = function(result) {
	// Remove disabled attibute which was previously set upon creation of the blank line
	$($("#task_new .complete")[0]).removeAttr("disabled");

	// Assign an ID to the newly created row (deletes the id 'task_new')
	g_TaskLabels.setAddTaskLabel("#task_new");
	g_TaskLabels.setDeleteTaskLabel("#task_new");
	g_TaskUsers.setAddTaskUser("#task_new");
	g_TaskUsers.setDeleteTaskUser("#task_new");
	
	$("#task_new").attr("task-id", result.task_id);
	$("#task_new").attr("id", "task_" + result.task_id);
	$("#start_date_new").attr("id", "start_date_" + result.task_id);
	$("#end_date_new").attr("id", "end_date_" + result.task_id);

	// All columns are present in the DOM even in TITLE mode where 'display:none' is set to all but the Task name column
	this.updateColumnCompleteHandler(result.task_id);
	this.updateColumnImportantHandler(result.task_id);
	this.updateColumnTaskNameHandler(result.task_id);
	this.updateColumnDeleteHandler(result.task_id);

	$("#start_date_"+result.task_id).datetimepicker({format: 'H:i d M, Y', onChangeDateTime: g_Tasks.updateColumnStartDateHandler});
	$("#end_date_"+result.task_id).datetimepicker({format: 'H:i d M, Y', onChangeDateTime: g_Tasks.updateColumnEndDateHandler});
	$("#task_"+result.task_id).addClass("task"); // We now have an effective task row
	
	g_Details.loadTaskDetails(result.task_id);
}


Tasks.prototype.createDatabaseRow = function(elem, previousLine) {
	// The row to which the 'Task name' column belongs
	var table_row = $(elem).parent().parent();

	// The task is not yet in the database 
	if("task_new" == $(table_row).attr("id")) {
		// Find all the INPUT elements
		var children 	= $(table_row).find("input");
		var label_id 	= $("#labels-list").jstree("get_selected").join();
		var clone_from 	= previousLine?previousLine.task_id:-1;

		// 'insert_line_after' will be echoed by the server in order to remember the intention, or not, of inserting a new blank line
		var dataValues = { 
			create: true,
			task_id: 0,
			task_is_complete: children[0].checked,
			task_is_important: children[1].checked,
			task_is_title: ("" == elem.value) ? false : ("" == elem.value.split(this.titleModeToken).slice(-1)[0])?true:false,
			task_name: children[2].value,
			task_start_date: new Date(children[3].value).toISOString(),
			task_end_date: new Date(children[4].value).toISOString(),
			label_id: label_id,
			clone_from: clone_from
		};

		$.ajax({url: "task/add/", 
			type: "get", 
			data: dataValues, 
			success: function(result) {
				if (result.status == "Ok") g_Tasks.updateTaskNew(result.data);
				else Utils.alert("Error: "+result.message);
			}
		});
	}
}

// elem - An ID (prefixed with #) or a jQuery HTML Element
// previousLine - All data from previously created line
Tasks.prototype.insertLineAfterElement = function(elem, previousLine) {
	
	var task_html = "<tr id='task_new' class='task' >" + 
			"<td class='data column-complete'><input class='complete'  type='checkbox' disabled='disabled'></td>" +
			"<td class='data column-important'><input class='important' type='checkbox'></td>" +
			"<td class='column-labels'><div class='labels-container' >&nbsp;</div></td>" +
			"<td class='data column-name'><input class='name' type='text' value=''></td>" +
			"<td class='data column-start-date'><input id='start_date_new' class='start-date date-time-picker' type='text' value='" + this.dateToLocalString(new Date()) + "'></td>" +
			"<td class='data column-end-date'><input id='end_date_new' class='end-date date-time-picker' type='text' value='" + this.dateToLocalString(new Date()) + "'></td>" +
			"<td class='column-users'></td>" +
			"<td class='column-delete'><img src='/static/img/delete.png' title='' alt=''></td>" + 
			"<td class='column-handler'><img src='/static/img/row_handler.png' title='Hold to drag and drop as a predecessor of the currently selected task' alt=''></td>" +
		"</tr>"
	$(elem).after( task_html );
	
	// Insert values from previously non title line
	if(previousLine) {
		$("#task_new .important")[0].value = previousLine.task_is_important;
		$("#task_new .name")[0].value = previousLine.task_name;
		$("#task_new .start-date")[0].value = previousLine.task_start_date;
		$("#task_new .end-date")[0].value = previousLine.task_end_date;
		$("#task_new .column-users").html(previousLine.task_users);
		$("#task_new .column-labels").html(previousLine.task_labels);
	}
	$("#task_table tr").removeClass("selected");
	$("#task_new").addClass("selected");	
	// Create a temporary handler for column 'Task name' (Events: focusout, keypress)
	$("#task_new .name").keypress(function(e) { if(e.which == 13) g_Tasks.createDatabaseRow(this, previousLine); });
	// Create a temporary handler for column 'Task name' when focus is moved out from it
	$("#task_new .name").focusout(function() { g_Tasks.createDatabaseRow(this, previousLine); });
}
// END: Utilities


// BEGIN: Handlers for the possible actions for each column in a line

// Specify what to do when column 'Complete' is clicked
Tasks.prototype.updateColumnCompleteHandler = function(task_id) {

	// Remove any previously registered handlers
	$("#task_" +task_id+ " .complete").unbind();

	$("#task_" +task_id+ " .complete").click(function() {
		g_Tasks.updateDatabaseRow(this);
	});
}


// Specify what to do when column 'Important' is clicked
Tasks.prototype.updateColumnImportantHandler = function(task_id) {

	// Remove any previously registered handlers
	$("#task_" +task_id+ " .important").unbind();

	$("#task_" +task_id+ " .important").click(function() {
		g_Tasks.updateDatabaseRow(this);
	});
}


// elem - the INPUT field of the task name/description
Tasks.prototype.updateDatabaseRow = function(elem) {

	var task_id = $(elem).parent().parent().attr("task-id");

	// Ignore columns other than Complete, Important, Task name, Start date and End date
	var children = $("#task_" + task_id).children(".data");

	var dataValues = { 
		update: true,
		task_id: task_id,
		task_is_complete: children[0].firstChild.checked,
		task_is_important: children[1].firstChild.checked,
		task_is_title: ("" == children[2].firstChild.value) ? false : ("" == children[2].firstChild.value.split(this.titleModeToken).slice(-1)[0])?true:false,
		task_name: children[2].firstChild.value,
		task_start_date: new Date(children[3].firstChild.value).toISOString(),
		task_end_date: new Date(children[4].firstChild.value).toISOString()
	};

	


	$.ajax({
		url: "task/add/"+task_id, 
		type: "get", 
		data: dataValues, 
		success: g_Tasks.updateRow
	});
}


// Specify what to do when the ENTER key is pressed in column 'Task name' or when the focus moves out of column 'Task name'
// item - the complete row information
Tasks.prototype.updateColumnTaskNameHandler = function(task_id) {

	// Remove any previously registered handlers
	$("#task_" + task_id + " .name").unbind();

	$("#task_table .column-name input").on('input', function() {
    	$('#task-name').text($(this).val());
	});


	$("#task_" + task_id + " .name").keypress(function(e){
		/*if(e.which==13){
			$("#start_date_"+task_id).focus();
			return;
		}*/
		if(e.which == 13) {
		//if(e.which ==10 & e.ctrlKey) {
			if($('.labels-list .selected').length>1){
				Utils.alert("Please select only one label.");
				return;
			}
			//g_Tasks.updateDatabaseRow(this);

			// Copy the values
			var previousLine = {
				task_id: task_id,
				task_is_important: $("#task_" + task_id + " INPUT.important")[0].checked,
				task_name: $("#task_" + task_id + " INPUT.name")[0].value,
				task_start_date: $("#task_" + task_id + " INPUT.start-date")[0].value,
				task_end_date: $("#task_" + task_id + " INPUT.end-date")[0].value,
				task_users: $($("#task_" + task_id + " .column-users")[0]).html(),
				task_labels: $($("#task_" + task_id + " .column-labels")[0]).html()
			};

			// Create a new line
			$("#task_new").remove();
			g_Tasks.insertLineAfterElement("#task_" + task_id, previousLine);
			$($("#task_new .name")[0]).select();
		}
	});
	
	$("#task_" + task_id+ " .name").focusout(function() {
		g_Tasks.updateDatabaseRow(this);
	});

	// The selected task
	$("#task_" +task_id +' :not(.column-delete)').click(function(){

		if( !$(this).parent().hasClass('selected') ){
			$("#task_panel #task_table TR.task").removeClass("selected");
			$(this).parent().addClass("selected");
			g_Details.loadTaskDetails(task_id);
		}
	});
}




// Specify what to do when column 'Start date' is changed
Tasks.prototype.updateColumnStartDateHandler = function(dateObj, inputElem) {
	var table_row = inputElem.parent().parent();
	var table_row_id = $(table_row).attr("id").split("_").slice(-1)[0];
	$("#start_date_" + table_row_id).val( g_Tasks.dateToLocalString(dateObj.toISOString()) );
	g_Tasks.updateDatabaseRow(inputElem[0]);
}


// Specify what to do when column 'End date' is changed
Tasks.prototype.updateColumnEndDateHandler = function(dateObj, inputElem) {
	var table_row = inputElem.parent().parent();
	var table_row_id = $(table_row).attr("id").split("_").slice(-1)[0];
	$("#end_date_" + table_row_id).val( g_Tasks.dateToLocalString(dateObj.toISOString()) );
	g_Tasks.updateDatabaseRow(inputElem[0]);
}


// Specify what to do when column 'Delete' is clicked
// item - the complete row information
Tasks.prototype.updateColumnDeleteHandler = function(task_id) {
	
	// Remove any previously registered handlers
	$("#task_" +task_id + " .column-delete img").unbind();

	$("#task_" +task_id + " .column-delete img").click(function() {
		$.ajax({
			url: "task/del/"+task_id, 
			type: "get",
			success: function(data){
				if(data.status == 'Ok') {
					$("#task_" + task_id).remove();
				} else Utils.alert("Error: "+data.message);
			}
		});
	});

}
// END: Handlers for the possible actions for each column in a line



Tasks.prototype.updateRow = function(result) {

	if(result.status == "Ok") {
		var e = $("#task_" + result.data.task_id);

		if(result.data.task_is_complete) {
			e.addClass("complete");
			e.find('input:not(:first)').attr("disabled", "disabled");
		}
		else {
			e.removeClass("complete");
			e.find('input:not(:first)').removeAttr("disabled", "disabled");
		}

		if(result.data.task_is_important && !result.data.task_is_title) 
			e.addClass("important");
		else 
			e.removeClass("important");

		// Apply a different style to the user that has finished the task
		if(result.data.task_is_complete) {
			$("#task_" + result.data.task_id + " #task-user-id-"+result.data.completed_by_user_id).addClass("completed_task_by");
		}
		else {
			$("#task_" + result.data.task_id + " .completed_task_by").removeClass("completed_task_by");
		}
		
		//e.find('.start-date').val( g_Tasks.dateToLocalString(result.data.task_start_date) );
		e.find('.end-date').val( g_Tasks.dateToLocalString(result.data.task_end_date) );
		

		// Check if the line is in TITLE mode and apply CSS styles immediately without waiting for AJAX callback
		if( result.data.task_is_title ) {
			$("#task_" + result.data.task_id).addClass("title");
			$($("#task_" + result.data.task_id + " .column-complete")[0]).addClass("hide");
			$($("#task_" + result.data.task_id + " .column-important")[0]).addClass("hide");
			$($("#task_" + result.data.task_id + " .column-labels")[0]).addClass("hide");
			$($("#task_" + result.data.task_id + " .column-name")[0]).addClass("title");
			$($("#task_" + result.data.task_id + " .column-name")[0]).attr("colspan", g_Tasks.nofColumns);
			$($("#task_" + result.data.task_id + " .column-start-date")[0]).addClass("title");
			$($("#task_" + result.data.task_id + " .column-end-date")[0]).addClass("title");				
		} else {
			$("#task_" + result.data.task_id).removeClass("title");
			$($("#task_" + result.data.task_id + " .column-complete")[0]).removeClass("hide");
			$($("#task_" + result.data.task_id + " .column-important")[0]).removeClass("hide");
			$($("#task_" + result.data.task_id + " .column-labels")[0]).removeClass("hide");
			if(result.data.task_is_important) $("#task_" +result.data.task_id).addClass("important");
			$($("#task_" + result.data.task_id + " .column-name")[0]).removeClass("title");
			$($("#task_" + result.data.task_id + " .column-name")[0]).removeAttr("colspan");
			$($("#task_" + result.data.task_id + " .column-start-date")[0]).removeClass("title");
			$($("#task_" + result.data.task_id + " .column-end-date")[0]).removeClass("title");
		}

	} else 
		Utils.alert("Error: "+result.message);
}
// END AJAX callbacks for the update of a line's column



// ENTRY POINT: Callback for AJAX request
Tasks.prototype.displayTasks = function(result) {

	this.clearTasks();
	
	this.createTaskLines(result);

	// Set the handler for column 'Complete' (Events: click)
	$.each(result, function(pos, item) { 
		g_Tasks.updateColumnCompleteHandler(item.task_id); 
	});

	// Set the handler for column 'Important' (Events: click)
	$.each(result, function(pos, item) { g_Tasks.updateColumnImportantHandler(item.task_id); });
	
	// Set the handler for column 'Task name' (Events: focusout, keypress)
	$.each(result, function(pos, item) { g_Tasks.updateColumnTaskNameHandler(item.task_id); });
	
	// Set the handlers for column 'Start date' and 'End date'
	$.each(result, function(pos, item) {
		$("#start_date_" + item.task_id).datetimepicker({format: 'H:i d M, Y', onChangeDateTime: g_Tasks.updateColumnStartDateHandler});
		$("#end_date_" + item.task_id).datetimepicker({format: 'H:i d M, Y', onChangeDateTime: g_Tasks.updateColumnEndDateHandler});
	});

	// Set the handler for column 'Delete'
	$.each(result, function(pos, item) { g_Tasks.updateColumnDeleteHandler(item.task_id); });

	// Insert a new line if there are no tasks
	$("#task_new").remove();
	var last_child = $("#task_table .task").filter(":last");
	if(!last_child.size()) g_Tasks.insertLineAfterElement("#task_table_header");
	
	g_Predecessors.dragAndDropPredecessors();
}


Tasks.prototype.startLoading = function(){
	this.clearTasks();
	$("#task_table_header").after("<tr><td style='text-align:center' colspan='8' class='task' ><img  src='/static/img/wait.gif' /></td></tr>");
}


Tasks.prototype.toggleSorting = function(e) {
	if( $(e).attr("sort")=='sort' ){
		if($(e).attr("name").charAt(0) == "-") $(e).attr("name", $(e).attr("name").substring(1));
		else $(e).attr("name", "-" + $(e).attr("name"));
	}
}

Tasks.prototype.queryTasks = function(e) {
	var label_id = $(".labels-list .selected").attr('label-id');
	if(label_id==undefined) 
		alert('Please select a label');
	else
		g_Labels.updateTasks(label_id);
}

Tasks.prototype.sortHandlers = function() {

	$($("#task_table_header .column-name")[0]).click(function(){
		g_Tasks.toggleSorting(this);
		$($("#task_table_header .column-start-date")[0]).removeAttr('sort');
		$($("#task_table_header .column-end-date")[0]).removeAttr('sort');
		$(this).attr('sort', 'sort');

		g_Labels.updateTasks($(".labels-list .selected").attr('label-id'));
	});
	$($("#task_table_header .column-start-date")[0]).click(function(){
		g_Tasks.toggleSorting(this);
		$($("#task_table_header .column-name")[0]).removeAttr('sort');
		$($("#task_table_header .column-end-date")[0]).removeAttr('sort');
		$(this).attr('sort', 'sort');

		g_Labels.updateTasks($(".labels-list .selected").attr('label-id'));
		
	});
	$($("#task_table_header .column-end-date")[0]).click(function(){
		g_Tasks.toggleSorting(this);
		$($("#task_table_header .column-start-date")[0]).removeAttr('sort');
		$($("#task_table_header .column-name")[0]).removeAttr('sort');
		$(this).attr('sort', 'sort');
		
		g_Labels.updateTasks($(".labels-list .selected").attr('label-id'));
		
	});

	$("#add-user-to-label-button").click(function(){
		$(this).hide();
		$('#delete-user-from-label').hide();
		$('#add-user-input').show();
		$('#add-user-input').focus();
	});



	//Begin search query
	$('#search-dialog').dialog({ 
		closeText: "hide",
		autoOpen: false, draggable: false, 
		position: { my: "left top", at: "left bottom", of: '#query-box-input' },
		width: '529px',
		dialogClass: 'search-dialog'  });

	$('#search-dialog .date-input').datetimepicker({format: 'Y-m-d'});

	$('#search-dialog-btn').click(function(){
		var query = $("#query-box-input").val();
		var filters = ['q:my','q:today','q:next','q:nooverdue','q:nocomplete','q:unconfirmed','q:important'];
		$(filters).each(function(i,e){
			query = query.replace(e+' ','');
			query = query.replace(e,'');
		});

		$('#search-dialog-filters li input:checked').each(function(i, e){
			var v = $(this).val();
			query = filters[parseInt(v)] + ' ' + query;
		});

		var startdate = $('#search-dialog #search-start-date').val();
		var enddate = $('#search-dialog #search-end-date').val();

		if(enddate.length==10){
			if(query.indexOf('before:')>=0){
				var index = query.indexOf('before:');
				var end = query.indexOf(' ',index);
				if(end<0) end = query.length;
				var sub = query.substring(index, end);
				query = query.replace(sub+' ', '');
				query = query.replace(sub, '');
				query = 'before:'+enddate+' '+query;
			}
			else
				query = 'before:'+enddate+' '+query;
		}

		if(startdate.length==10){
			if(query.indexOf('after:')>=0){
				var index = query.indexOf('after:');
				var end = query.indexOf(' ',index);
				if(end<0) end = query.length;

				var sub = query.substring(index, end);
				query = query.replace(sub+' ', '');
				query = query.replace(sub, '');
				query = 'after:'+startdate+' '+query;
			}
			else
				query = 'after:'+startdate+' '+query;
		}
		$("#query-box-input").val(query);
		$('#search-dialog').dialog('close');
		g_Tasks.queryTasks();
	});
	$("#query-winopen-btn").click(function(){
		if( $("#search-dialog").dialog( "isOpen" )){
			$('#search-dialog').dialog('close');
			return;
		}

		var query = $("#query-box-input").val();
		var filters = ['q:my','q:today','q:next','q:nooverdue','q:nocomplete','q:unconfirmed','q:important'];
		$(filters).each(function(i,e){
			if(query.indexOf(filters[i])>=0)
				$('#search-dialog-filters li input:eq('+i+')').attr('checked','checked');
			else
				$('#search-dialog-filters li input:eq('+i+')').removeAttr('checked');
		});

		if(query.indexOf('after:')>=0){
			var index = query.indexOf('after:');
			var end = query.indexOf(' ',index);
			if(end<0) end = query.length;
			var sub = query.substring(index, end).replace('after:','');
			$('#search-dialog #search-start-date').val(sub);
		}else $('#search-dialog #search-start-date').val('');
		if(query.indexOf('before:')>=0){
			var index = query.indexOf('before:');
			var end = query.indexOf(' ',index);
			if(end<0) end = query.length;
			var sub = query.substring(index, end).replace('before:','');
			$('#search-dialog #search-end-date').val(sub);
		}else $('#search-dialog #search-end-date').val('');
		$('#search-dialog').dialog('open');
	});
	

	$("#query-box-input").keypress(function( event ) {
		if ( event.which == 13 ) g_Tasks.queryTasks();
	});
	$("#query-box-btn").click(function(){ g_Tasks.queryTasks(); });
	//End search query

	$("#add-user-input").focusout(function(){
		$("#add-user-to-label-button").show();
		$('#add-user-input').hide();
		$('#delete-user-from-label').show();
	});




}
