from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import json
from taskmanager_app.models import *
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
import datetime
from django.utils.timezone import utc
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import datetime
from taskmanager_app.acl import ACL


# Add a task predecessor
@login_required
@csrf_exempt
def add_task_predecessor(request, task_id, pred_id):

	res = {}

	try:
		res = {
			'status': 'Ok',
			'data': { 'task_id': task_id },
		}
		
		t = Task.objects.get(pk = task_id)
		p = Task.objects.get(pk = pred_id)
		if ACL.canUpdateTask(request.user, t):
			if (task_id != pred_id):
				# Receives the current task to assign predecessors to
				#t = Task.objects.get(pk = task_id)
				#p = Task.objects.get(pk = pred_id)

				# If predecessor already inserted, do nothing	
				if p not in t.task_predecessors.all():
					t.task_predecessors.add(p)
		else:
			raise Exception('Permission denied')


	except Exception as e:
		res = {
			'status': 'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')


# Delete a task predecessor
@login_required
@csrf_exempt
def del_task_predecessor(request, task_id, pred_id):

	res = {}
	try:
		res = {
			'status': 'Ok',
		}

		t = Task.objects.get(pk = task_id)
		p = Task.objects.get(pk = pred_id)

		
		if ACL.canUpdateTask(request.user, t):
			if p in t.task_predecessors.all():
				t.task_predecessors.remove(p)
		else:
			raise Exception('Permission denied')

	except Exception as e:
		res = {
			'status': 'Error'
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')


# Return all the predecessors for a specific task
@login_required
@csrf_exempt
def browse_task_predecessors(request):
	res = {}
	try:
		res = {
			'status': 'Ok',
			'message': '',
			'data': [],
		}

		t = Task.objects.get(pk = request.POST.get('task_id'))
		if ACL.canViewTask(request.user, t):
			#t = Task.objects.get(pk = request.GET.get('task_id'))
			for p in t.task_predecessors.all():
				res['data'].append({
					'task_id': p.task_id, 
					'task_name': p.task_name, 
					'task_start_date': p.task_start_date.strftime( settings.DATETIME_FORMAT )
				});
		else:
			raise Exception('Permission denied')

	except Exception as e:
		res = {
			'status': 'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')
