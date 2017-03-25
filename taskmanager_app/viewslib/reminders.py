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


@login_required
def browse_task_reminders(request, task_id):

	try:
		task = Task.objects.get(pk=task_id)
		
		#res = []
		res = {
			'status': 'Ok',
			'data': {}
		}

		if ACL.canViewTask(request.user, task):
			task = Task.objects.get(pk=task_id)
			
			res['data'] = {
				'emails': task.usersEmails(),
				'reminders': task.taskReminders(),
			}
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
def add_task_reminders(request, task_id):

	try:
		res = {
			'status': 'Ok',
		}

		task = Task.objects.get(pk=task_id)

		if ACL.canUpdateTask(request.user, task):

			taskid = request.POST.get('task_id', task_id )
			if taskid.strip()=='': taskid=task_id

			#task = Task.objects.get(pk=taskid)

			if request.user in task.task_users.all():
				reminder_id = request.POST.get('reminder_id', None )
				if reminder_id.strip()=='': reminder_id=None
				reminder_subject = request.POST.get('reminder_subject', None )
				reminder_msg = request.POST.get('reminder_msg', None )
				reminder_recipients = request.POST.get('reminder_recipients', None )
				reminder_date = request.POST.get('reminder_date', None )
				reminder_non_validated = request.POST.get('reminder_non_validated')

				#reminder_date = datetime.datetime.strptime(reminder_date, settings.DATE_FORMAT)

				reminder = Reminder(
					reminder_id=reminder_id,
					reminder_subject=reminder_subject,
					reminder_msg=reminder_msg,
					reminder_recipients=reminder_recipients,
					reminder_date=reminder_date,
					reminder_non_validated = True if reminder_non_validated=='true' else False,
					task = task )
				reminder.save()
			else:
				raise Exception("User doesn't have permissions")

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
def get_task_reminder(request, reminder_id):
	try:
		res = {
			'status': 'Ok',
			'data': {}
		}

		reminder = Reminder.objects.get(pk=reminder_id)
		task = reminder.task

		if ACL.canViewTask(request.user, task) :
			#reminder = Reminder.objects.get(pk=reminder_id)
			res['data'] = {
				'reminder_id': reminder.reminder_id,
				'reminder_subject': reminder.reminder_subject,
				'reminder_msg': reminder.reminder_msg,
				'reminder_recipients': reminder.reminder_recipients,
				'reminder_date': reminder.reminder_date.strftime( settings.DATE_FORMAT ),
				'task_id': reminder.task.task_id,
				'reminder_non_validated': reminder.reminder_non_validated
			}
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
def del_task_reminder(request, reminder_id):

	try:
		res = {
			'status': 'Ok',
		}
		
		reminder = Reminder.objects.get(pk=reminder_id)
		task = reminder.task
		
		if ACL.canUpdateTask(request.user, task):
			#reminder = Reminder.objects.get(pk=reminder_id)
			reminder.delete()
		else:
			raise Exception('Permission <denied></denied>')
	
	except Exception as e:
		res = {
			'status': 'Error',
		}
	
	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')


