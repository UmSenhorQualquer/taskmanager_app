from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Q
from taskmanager_app.models import *
import datetime, json


@login_required
def browse_quick_report(request):
	
	res = {}

	try:
		res = {
			'status': 'Ok',
		}

		labels = TaskLabel.objects.filter( Q(user=request.user) | Q(users=request.user) ).distinct()

		accessible_tasks = Task.objects.filter( tasklabels__in=labels )

		tasks = accessible_tasks.filter(task_end_date__lte=datetime.datetime.today())
		tasks = tasks.filter(task_is_complete = False)
		n_expired_tasks = tasks.count()
		mine_n_expired_tasks = tasks.filter(task_users=request.user).count()

		tasks = accessible_tasks.filter(
			(
				Q(task_start_date__lte = datetime.datetime.today() ) \
				& Q(task_end_date__gte = datetime.datetime.today() ) \
				& Q(task_is_complete = False)
			) | (
				Q(task_end_date__lte = datetime.datetime.today()) \
				& Q(task_is_complete = False)
			)
		)
		n_tasks_to_complete = tasks.count()
		mine_n_tasks_to_complete = tasks.filter(task_users=request.user).count()

		tasks = accessible_tasks.filter(
			( 	
				Q(task_start_date__lte = datetime.datetime.today() + datetime.timedelta(days = 7)) \
				& Q(task_end_date__gte = datetime.datetime.today() + datetime.timedelta(days = 7))
			) | (
				Q(task_end_date__lte = datetime.datetime.today()  + datetime.timedelta(days = 7)) \
				& Q(task_is_complete = False)
			)
		)
		n_tasks_to_complete_7_days = tasks.count()
		mine_n_tasks_to_complete_7_days = tasks.filter(task_users=request.user).count()

		tasks = accessible_tasks.filter(
				Q(reminder__reminder_non_validated=False) \
				& Q(reminder__reminder_date__lte = datetime.datetime.today() + datetime.timedelta(days = 7))
			)
		n_reminders_2_expire_7_days = tasks.count()

		res['data'] = [
			{
				'label': 'My tasks',
				'reports': [
					['Expired tasks',mine_n_expired_tasks],
					['Tasks to complete today',mine_n_tasks_to_complete],
					['Tasks to complete in the next 7 days',mine_n_tasks_to_complete_7_days],	
				]
			},
			{
				'label': 'My projects tasks',
				'reports': [
					['Expired tasks',n_expired_tasks],
					['Tasks to complete today',n_tasks_to_complete],
					['Tasks to complete in the next 7 days',n_tasks_to_complete_7_days],
					['Unconfirmed reminders in the next 7 days',n_reminders_2_expire_7_days]
				]
			}
		]
	except Exception as e:
		res = {
			'status': 'Error',
			'message': str(e),
		}

	
	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')