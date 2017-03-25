#!/usr/bin/python
# -*- iso-8859-15 -*-

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Q
from taskmanager_app.models import *
from django.shortcuts import render_to_response
from django.template import RequestContext
import datetime
import json
import paramiko, os
from fabric.api import *
from django.conf import settings
from taskmanager_app.acl import ACL
import traceback
import sys, re, string
from django.utils.encoding import smart_str

paramiko.util.log_to_file(settings.PARAMIKO_LOGFILE)

@login_required
def user_rss(request):
	tasks = Task.objects.filter(task_users=request.user)
	tasks = tasks.filter(task_is_complete=False)
	tasks = tasks.order_by('task_start_date').distinct()
	tasks = [task for task in tasks if ACL.canViewTask(request.user, task)]

	return render_to_response('ptmTemplates/user_rss.xml', {'tasks': tasks, 'datetime': datetime.datetime.now()}, 
		context_instance=RequestContext(request), mimetype='application/xml')


@login_required
def label_ical(request, label_id):
	label = TaskLabel.objects.get(pk=label_id)
	tasks = Task.objects.filter(tasklabels=label)
	tasks = tasks.order_by('task_start_date').distinct()

	res = [task for task in tasks if ACL.canViewTask(request.user, task)]

	response = render_to_response('ptmTemplates/user_ical.ics', {'label':label, 'tasks': res, 'datetime': datetime.datetime.now()}, 
		context_instance=RequestContext(request), mimetype='application/ics')

	response['Content-Disposition'] = 'attachment; filename="%s - %s.ical"' % (label.tasklabel_name, datetime.datetime.now())

	return response


@login_required
def label_print(request, label_id):
	label = TaskLabel.objects.get(pk=label_id)
	tasks = Task.objects.filter(tasklabels=label)
	tasks = tasks.order_by('task_start_date','task_name').distinct()

	res = [task for task in tasks if ACL.canViewTask(request.user, task)]

	project = None
	template = 'ptmTemplates/label_print.html'
	if label.project_set.count()>0:
		project = label.project_set.all()[0]
		if hasattr(project, 'grantproject'): 
			template = 'ptmTemplates/grantproject_print.html'
			project = project.grantproject
		else: template = 'ptmTemplates/project_print.html'

	response = render_to_response(template, {'label':label, 'project':project ,'tasks': res, 'datetime': datetime.datetime.now()}, 
		context_instance=RequestContext(request) )

	return response

def format_filename(s):
	"""Take a string and return a valid filename constructed from the string.
	Uses a whitelist approach: any characters not present in valid_chars are
	removed. Also spaces are replaced with underscores.

	Note: this method may produce invalid filenames such as ``, `.` or `..`
	When I use this method I prepend a date string like '2009_01_15_19_46_32_'
	and append a file extension like '.txt', so I avoid the potential of using
	an invalid filename.

	"""
	valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
	filename = ''.join(c for c in s if c in valid_chars)
	filename = filename.replace(' ','_') # I don't like spaces in filenames.
	return filename

@login_required
def label_snapshot(request, label_id):

	try:
		label = TaskLabel.objects.get(pk=label_id)
		if label.user!=request.user:
			res = {'result': 'Only the owner of the tag can snapshot it.'}
		else:

			env.host_string = "%s@%s" % (settings.SNAPSHOT_SSHUSER, settings.SNAPSHOT_HOST)
			env.password 	= settings.SNAPSHOT_SSHPASS
			env.disable_known_hosts = False

			snapshot_name = "Tag-%s" % format_filename(label.tasklabel_name)
			userpath = os.path.join(settings.SNAPSHOT_BASEPATH, request.user.username)
			sudo(	"chown 	-R ricardo:www-data '%s'" % userpath    )
			sudo(	"chmod 	-R 0770 '%s'" % userpath    )
			snapshot_mainpath = os.path.join(userpath ,'files','Snapshots')
			snapshot_path = os.path.join( snapshot_mainpath,snapshot_name )

			infofile = os.path.join(snapshot_path, 'version.txt')
			sudo(	"mkdir 	-p '%s'    " % snapshot_path 	)
			sudo(	"chmod 	-R 0770 '%s'" % snapshot_path    )
			sudo(	"chown 	-R ricardo:www-data '%s'" % snapshot_path    )
			sudo(	"echo '####################################################' >> %s" % infofile )
			sudo(	"echo 'Snapshot begin: %s' >> %s" % (datetime.datetime.now(), infofile) )
			
			tasks = Task.objects.filter(tasklabels=label).order_by('task_start_date').distinct()
			for task in tasks:
				if task.taskattachment_set.count()>0:
					task_path = os.path.join(snapshot_path, format_filename(task.task_name) )
					sudo(	"mkdir 	-p '%s'    " % task_path  )
					sudo(	"chmod 	-R 0770 '%s'" % task_path )
					sudo(	"chown 	-R ricardo:www-data '%s'" % task_path    )
					for f in task.taskattachment_set.all():
						origin = os.path.join(settings.MEDIA_ROOT, str(f.task_attachment_file) );

						filename = os.path.basename(str(f.task_attachment_file))
						dest_file = os.path.join(task_path, format_filename(filename) )
						sudo(	"echo 'Copying file:%s to %s' >> %s" % ( f.task_attachment_file, dest_file, infofile) )
						put( origin, dest_file )


			project = None
			template = 'ptmTemplates/label_print.html'
			if label.project_set.count()>0:
				project = label.project_set.all()[0]
				if hasattr(project, 'grantproject'): 
					template = 'ptmTemplates/grantproject_print.html'
					project = project.grantproject
				else: template = 'ptmTemplates/project_print.html'


			html = render_to_string(template, 
				{'label':label,'project':project, 'tasks': tasks, 'datetime': datetime.datetime.now()})
			htmlfile = os.path.join('tmp', '%s.html' % label.tasklabel_name )
			pdffile = os.path.join('tmp', '%s - resume.pdf' % label.tasklabel_name )
			out = file(htmlfile, 'wb')
			out.write(smart_str(html))
			out.close()
			local('xvfb-run -a wkhtmltopdf "%s" "%s"' % (htmlfile, pdffile) )
			sudo(	"echo 'Copying file:%s' >> %s" % ( pdffile, infofile) )
			put( pdffile, snapshot_path)

			os.remove(htmlfile)
			os.remove(pdffile)

			sudo(	"chown -R www-data:www-data '%s'" % snapshot_mainpath    )
			
			res = {'result': 'Ok'}

	except Exception as e:
		res = {'result': '%s (%s)' % (e.message, type(e)) }

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')

