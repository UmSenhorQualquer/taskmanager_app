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



@login_required
def add_task_user(request, task_id):
	try:
		res = {
			'status': 'Ok',
		}

		user_id = request.GET.get('id', None )

		user = User.objects.get(pk=user_id)
		task = Task.objects.get(pk=task_id)
		if not task.task_is_complete:
			task.task_users.add(user)
			task.save()

	except Exception as e: #User.DoesNotExist,  Task.DoesNotExist :
		res = {
			'status': 'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')


@login_required
def del_task_user(request, task_id):
	try:
		res = {
			'status': 'Ok',
		}

		user_id = request.GET.get('id', None )

		task = Task.objects.get(pk=task_id)
		if not task.task_is_complete:
			if task.task_users.count()>1:
				user = User.objects.get(pk=user_id)
				task.task_users.remove(user)
				task.save()

	except Exception as e: #User.DoesNotExist,  Task.DoesNotExist :
		res = {
			'status': 'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')


# Views to help define which users are available to assign to tasks
def search_user(request):
	keyword = request.GET.get('term', '')
	users = User.objects.filter(username__contains=keyword)

	res = []
	for user in users:
		try:
			a = user.first_name[0]
			b = user.last_name[0]
		except: 
			a,b = '',''

		res.append({
				'label': user.username,
				'initials': (a+b).upper(),
				'value': user.username,
				'id': user.pk
			})
	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')


def browse_label_users(request, member_id):
	try:
		res = {
			'status': 'Ok',
			'data': [],
		}
		keyword = request.GET.get('term', '')
		member 	= TaskLabelMembership.objects.get(pk=member_id)
		label 	= member.child
		members = TaskLabelMembership.objects.filter(child=label)

		for member in members:
			user = member.user
			try:
				a = user.first_name[0]
				b = user.last_name[0]
			except: 
				a,b = '',''

			res['data'].append({
				'label': user.username,
				'initials': (a+b).upper(),
				'value': user.username,
				'id': user.pk
			})
	except Exception as e:
		res = {
			'status': 'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')


def add_label_user(request, label_id):
	try:
		res = {
			'status': 'Ok',
		}

		user_id = request.GET.get('id', None )

		user = User.objects.get(pk=user_id)
		label = TaskLabel.objects.get(pk=label_id)
		label.users.add(user)
		label.save()

	except Exception as e: #User.DoesNotExist,  TaskLabel.DoesNotExist :
		res = {
			'status': 'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')

def del_label_user(request, label_id):
	try:
		res = {
			'status': 'Ok',
		}
		user_id = request.GET.get('id', None )

		user = User.objects.get(pk=user_id)
		label = TaskLabel.objects.get(pk=label_id)
		label.users.remove(user)
		label.save()

	except Exception as e: #User.DoesNotExist,  TaskLabel.DoesNotExist :
		res = {
			'status': 'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')


