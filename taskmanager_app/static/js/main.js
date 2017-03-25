$(document).ready(Utils.readjustViewport);
$(window).resize(Utils.readjustViewport);


var g_Labels = null;
var g_Details = null;
var g_Reminders = null;
var g_Predecessors = null;
var g_Attachments = null;
var g_Observations = null;
var g_Tasks = null;
var g_Reports = null;
var g_TaskUsers = null;
var g_TaskLabels = null;


$(function(){

	g_TaskLabels 	= new TaskLabels();
	g_TaskUsers 	= new TaskUsers();
	g_Labels 		= new Labels();
	g_Details 		= new Details();
	g_Reminders 	= new Reminders();
	g_Predecessors 	= new Predecessors();
	g_Attachments 	= new Attachments();
	g_Observations 	= new Observations();
	g_Tasks 		= new Tasks();
	//g_Reports 		= new Reports();


	g_Labels.loadLabels();
	g_Tasks.sortHandlers();

	Utils.setMaximizeAndMinimize();

	var viewportHeight = $( window ).height()-60;
	var viewportWidth = $( window ).height()-60;
	$('#dashboard').height(viewportHeight).split({
		orientation:'vertical', 
		limit:100, 
		position:($( window ).width()-400)
	});
	$('#tasks-labels-dashboard').split({
		orientation:'vertical',
		limit:100,
		position:300
	});

});

