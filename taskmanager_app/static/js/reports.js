// Ctor
function Reports() {
	
	/* Template quickreports.html */

	setInterval(this.updateQuickReport, 60000);
	this.updateQuickReport();
}


Reports.prototype.quickSubReportLi = function(result) {
	var html = "<table class='quickreport-report' >";
	$(result).each(function(i, e){
		html += "<tr ><td class='label' >"+e[0]+"</td><td class='value'>"+e[1]+"</td></tr>"
	});
	html += '</table>'
	return html;
}


Reports.prototype.updateQuickReport = function() {
	$.ajax({
		url: "tasks/quickreport/",
		success: function(result) {
			if(result.status == "Ok") {
				var html = '';
				$(result.data).each(function(i, e){
					html += "<li class='quickreport-group'><div>"+ e.label +"</div>"+ g_Reports.quickSubReportLi(e.reports) +"</li>"
				});
				$('#quick_reports').html(html);
			} else Utils.alert("Error: "+result.message);
		}
	});
}

