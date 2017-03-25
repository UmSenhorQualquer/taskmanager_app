// Ctor
function Reminders() {

	/* Template reminder_window.html */

	$("#reminder-date").datetimepicker(
		{format: 'd M, Y', timepicker: false, onChangeDateTime: 
		function(dateObj, inputElem) { 
			dateObj.setHours(1); 
			dateObj.setMinutes(0); 
			dateObj.setSeconds(0); 
			dateObj.setMilliseconds(0); 
			$(inputElem).attr("value", dateObj.toISOString()); }
	});


	$("#reminder-window").dialog({ 
		width: 800,
		autoOpen: false,
		show: { effect: "fadeIn", duration: 200 },
		buttons: {
			SUBMIT: function() {
				var data2submit = $("#reminder-window > form").serializeArray();
				
				// Tweak for handling with timezones
				var idx = 4;
				if(data2submit.length > 7) idx++;
				data2submit[idx].value = (new Date(data2submit[idx].value + " UTC")).toISOString();
				
				// Tweak for reusing the checkbox
				var field_value = $('#reminder_non_validated').prop('checked');
				data2submit[data2submit.length] = { name: "reminder_non_validated", value: field_value }

				var task_id = $("#task_comment_list").data('active-task');
				$.ajax({
					url: "/reminders/add/"+task_id, 
					type: "post",
					data: data2submit, 
					success: function(result){
						if(result.status=='Ok'){
							g_Reminders.clearForm("#reminder-window");
							$( '#reminder-window' ).dialog( "close" );
							g_Reminders.loadReminders(task_id);
						} else Utils.alert("Error: "+result.message);
					}
				});
				
			},
			Cancel: function() {
				g_Reminders.clearForm("#reminder-window");
				$( this ).dialog( "close" );
			}
		}
	});

	$(".ui-dialog-buttonset button").addClass("btn");
	$(".ui-dialog-buttonset button:first-child").addClass("btn-primary");
	$(".ui-dialog-buttonset button:last-child").addClass("btn-warning cancel");


	/* Template task_reminders.html */

	$( "#new-reminder-button" ).click(function() {
		$( "#reminder-window" ).dialog("open");
	});
}


Reminders.prototype.clearForm = function(form) {
	$(form).find('input').val("");
	$(form).find('textarea').val("");
	$(form).find('.date-input').val('__ ___ ____');
}


Reminders.prototype.loadReminderForm = function(values) {
	$('#reminder-id').val(values.reminder_id);
	$('#reminder-subject').val(values.reminder_subject);
	$('#reminder-date').val(values.reminder_date);
	$('#reminder-to').val(values.reminder_recipients);
	$('#reminder-msg').val(values.reminder_msg);
	$('#reminder-task-id').val(values.task_id);
	$('#reminder_non_validated').prop( "checked", values.reminder_non_validated );
	
}

// When a task is clicked this method must be invoked
Reminders.prototype.reminderRow = function(id, subject, date) {
	var html = "<tr>";
	html += "<td class='subject' >"+subject+"</td>";
	html += "<td class='when' >"+date+"</td>";
	html += "<td class='edit' ><button class='edit reminder-edit-button' reminder-id='"+id+"' ><i class='glyphicon glyphicon-pencil'></i></button></td>";
	html += "<td class='delete' ><button class='delete reminder-del-button' reminder-id='"+id+"' ><i class='glyphicon glyphicon-trash'></i></button></td>";
	html += "</tr>";
	return html;
}


Reminders.prototype.loadReminders = function (task_id) {

	$.ajax({
		url: "/reminders/browse/"+task_id, 
		type: "get",
		success: function(result){
			if(result.status=='Ok') {
				var html = "";
				$(result.data.reminders).each(function(i, e){
					html += g_Reminders.reminderRow( e.id, e.subject, e.date );					
				});
				$('#reminders-list').html(html);


				html = "";
				$(result.data.emails).each(function(i, e){
					html += '<button class="btn"><i class="glyphicon glyphicon-plus"></i> <span>'+e+'</span></button>';
				});
				$('#reminder-users-list').html(html);
				
				$("#reminder-users-list button").click(function(){
					var val = $('#reminder-to').val();
					if(val.length>0) val += '; ';
					var email = $(this).children('span').text();
					if( val.indexOf(email) == -1) $('#reminder-to').val( val+email);
					return false;
				});

				$('.reminder-edit-button').click(function(){
					
					var reminder_id = $(this).attr('reminder-id');
					$.ajax({
						url: "/reminders/get/"+reminder_id, 
						type: "get",
						success: function(result){
							if(result.status == 'Ok') {
								g_Reminders.loadReminderForm(result.data);
								$( "#reminder-window" ).dialog( "open" );
							} else Utils.alert("Error: "+result.message);
						}
					});
				});

				$('.reminder-del-button').click(function() {
					var reminder_id = $(this).attr('reminder-id');
					$.ajax({
						url: "/reminders/del/"+reminder_id, 
						type: "get",
						success: function(result){
							g_Reminders.loadReminders(task_id);
						}
					});
				});
			} else Utils.alert("Error: "+result.message);
		}
	});
}