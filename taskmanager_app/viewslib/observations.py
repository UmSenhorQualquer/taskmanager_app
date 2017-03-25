from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import utc
from django.http import HttpResponse
from taskmanager_app.models import *
import datetime, json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from taskmanager_app.acl import ACL

@login_required
def browse_observation(request, task_id):
	try:
		res = {
			'status': 'Ok',
			'data': [],
		}
		task = Task.objects.get(pk=int(task_id))

		if ACL.canViewTask(request.user, task):
			if task.hasPermissions(request.user):
				objs = Observation.objects.filter( task=task )
				for obj in objs:
					res['data'].append({
						'id': obj.pk,
						'msg':obj.observation_msg,
						'date':obj.observation_date.strftime( settings.DATETIME_FORMAT ),
						'user':obj.user.username
					})
		else:
			raise Exception('Permission denied')

	except Exception as e:
		res = {
			'status': 'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')

@login_required
@csrf_exempt
def add_observation(request, task_id):

	try:
		res = {
			'status': 'Ok',
		}

		task = Task.objects.get(pk=int(task_id))
		msg = request.POST.get('observation', '')

		
		if ACL.canUpdateTask(request.user, task):
			if task.hasPermissions(request.user) and msg!='':
				obj = Observation( observation_msg=msg, user=request.user, task=task )
				obj.save()
			else:
				raise Exception('No permissions or message empty')
		else:
			raise Exception('No permissions or message empty')

	except Exception as e:
		res = {
			'status': 'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')

@login_required
def del_observation(request, observation_id):

	try:
		res = {
			'status': 'Ok',
		}

		obj = Observation.objects.get(pk=observation_id)
		
		task = obj.task

		if ACL.canUpdateTask(request.user, task):
			if task.hasPermissions(request.user): obj.delete()
		else:
			raise Exception('No permissions or message empty')

	except Exception as e:
		res = {
			'status': 'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')

