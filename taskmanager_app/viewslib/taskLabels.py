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
import pytz
from taskmanager_app.acl import ACL
from datetime import timedelta

@login_required
def browse_tasks_by_label(request, label_id=None):

	try:
		res = { 'status': 'Ok', 'message': '', 'data': [] }

		members = request.GET.get('ids', label_id)
		members = members.split(',')

		members = TaskLabelMembership.objects.filter(pk__in=members, user=request.user)
		label_ids = [x.child.pk for x in members]
		
		labels = TaskLabel.objects.all()
		labels = labels.filter(pk__in=label_ids).distinct()

		#only_labels = [x for x in labels if x.project_set.count()==0]
		#project_labels = [x for x in labels if x.project_set.count()>0]

		filter_codes = request.GET.get('filters', '')
		filter_codes = filter_codes.split(',')

		# E.g. sort=-task_name (sort descending for Task name/description column)
		# E.g. sort=task_name (sort ascending for Task name/description column)
		sort = request.GET.get('sort', None)

		tasks = Task.objects


		query = request.GET.get('query', '')
		queries = query.split(' ')

		for query in queries:
			if query.startswith('after:'):
				after_date = query.split(':')[1]
				after_date += ' 00:00:00'
				after_date = datetime.datetime.strptime(after_date, '%Y-%m-%d %H:%M:%S')
				tz = pytz.timezone('UTC')
				after_date = tz.localize(after_date)
				tasks = tasks.filter(task_start_date__gte = after_date)

			elif query.startswith('before:'):
				before_date = query.split(':')[1]
				before_date += ' 23:59:59'
				before_date = datetime.datetime.strptime(before_date, '%Y-%m-%d %H:%M:%S')
				tz = pytz.timezone('UTC')
				before_date = tz.localize(before_date)
				tasks = tasks.filter(task_end_date__lte = before_date)

			# The user's tasks
			elif query=='q:my': tasks = tasks.filter( task_users=request.user )
			# Today tasks (i.e. between start data, including, and end date, including)
			elif query=='q:today': tasks = tasks.filter( 
					(
						# Include complete and not complete tasks
						Q(task_start_date__lte = datetime.datetime.today()) \
						& Q(task_end_date__gte = datetime.datetime.today()) \
					) | (
						# Expired tasks (overdue)
						Q(task_end_date__lte = datetime.datetime.today()) \
						& Q(task_is_complete = False)
					) 
				)
			# Tasks within the next 7 days
			elif query=='q:next': tasks = tasks.filter(
					( 	
						Q(task_start_date__lte = datetime.datetime.today())
						& Q(task_end_date__lte = datetime.datetime.today() + datetime.timedelta(days = 7))
					) | (
						Q(task_end_date__lte = datetime.datetime.today() + datetime.timedelta(days = 7)) \
						& Q(task_is_complete = False)
					)
				)
			# Exclude tasks that have already expired (overdue tasks)
			elif query=='q:nooverdue': tasks = tasks.exclude(task_end_date__lt = datetime.datetime.today())
			# Exclude tasks that are complete
			elif query=='q:nocomplete': tasks = tasks.exclude(task_is_complete = True)

			# Non validated reminders in the next seven days
			# all reminders -> fk is label_id -> non validated
			elif query=='q:unconfirmed': tasks = tasks.filter(
					Q(reminder__reminder_non_validated=False) \
					& Q(reminder__reminder_date__lte = datetime.datetime.today() + datetime.timedelta(days = 7))
				)
			# important tasks
			elif query=='q:important': tasks = tasks.filter(task_is_important = True)
			#
			elif len(query.strip())>0: tasks = tasks.filter(task_name__contains=query)

		tasks = tasks.filter(tasklabels=labels)
		#if len(only_labels)>0: tasks = tasks.filter(tasklabels__in=only_labels)
		#if len(project_labels)>0: tasks = tasks.filter(tasklabels__in=project_labels)
		

		# Column sorting
		order_by = []
		tasks = tasks.distinct()
		if sort!=None: 
			order_by.append(sort)
		else: 
			order_by.append('task_start_date')
		order_by.append('task_name')
		tasks = tasks.order_by(*order_by)


		clearanceList = ACL.canViewOthersTasks(request.user,labels)

		for taskIndex, t in enumerate(tasks):
			users = []
			labelUsers = t.task_users.all().distinct()
			for user in labelUsers:
				try: a, b = user.first_name[0], user.last_name[0]
				except: a,b = '',''
				
				users.append({
					'user_id': user.pk, 
					'user_name': user.username, 
					'user_initials': (a+b).upper(),
					'completed_task': t.user==user
				})

			labels=[]
			for membership in TaskLabelMembership.objects.filter(user=request.user).filter(child__in=t.tasklabels.all()).distinct():
				label = membership.child
				labels.append({ 
					'id':label.pk, 
					'label':label.tasklabel_name, 
					'color': "#%s" % label.tasklabel_color
				})

			
			#Correct this because of the naive datetime
			style = 'todo' if t.task_is_complete!=True and t.task_end_date <= timezone.now() else ''
			
			#Check user permissions
			showTask = False
			if request.user in labelUsers: showTask = True
			else:
				for label in t.tasklabels.all():
					if label in clearanceList: showTask = True; break

			if showTask:
				
				res['data'].append({
					'task_id': t.task_id, 
					'task_is_complete': t.task_is_complete,
					'task_is_important': t.task_is_important, 
					'task_is_title': t.task_is_title, 
					'task_name': t.task_name, 
					'task_start_date': t.task_start_date, 
					'task_end_date': t.task_end_date, 
					'users': users,
					'labels': labels,
					'style': style
				})

				if sort==None:
					try:
						parent = t.task_set.all().earliest('task_start_date')
						orderkey = parent.task_start_date.strftime('%Y%m%d %H:%M-')+str(parent.pk)
						orderkey += 'c' if parent.task_is_title else 'a'
						res['data'][-1]['parentTitle'] = parent.pk if parent.task_is_title else None
					except Task.DoesNotExist:
						orderkey = t.task_start_date.strftime('%Y%m%d %H:%M-')+str(t.pk)+'b'
						res['data'][-1]['parentTitle'] = None
					res['data'][-1]['order'] = orderkey

		if sort==None:
			res['data'] = sorted(res['data'], key=lambda x: x['order'])
			data = res['data']
			for i in range( len(data)-1 ):
				if data[i]['parentTitle']!=None and data[i]['parentTitle']!=data[i+1]['parentTitle']:
					data[i]['style'] += ' from-group last-from-group'

				elif data[i]['parentTitle']!=None and data[i]['parentTitle']==data[i+1]['parentTitle']:
					data[i]['style'] += ' from-group'


	except Exception as e:
		res = {
			'status': 'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')







@login_required
def add_task_label(request, task_id):

	try:
		res 	 = { 'status': 'Ok', }
		label_id = request.GET.get('label_id')
		task 	 = Task.objects.get(pk=task_id)

		if ACL.canUpdateTask(request.user, task):
			label = TaskLabel.objects.get(pk=label_id)

			if  (request.user==label.user or request.user in label.users.all()) and \
				label not in task.tasklabels.all():
				task.tasklabels.add(label)
		else:
			res = {
				'status': 'Error',
				'message': 'No permissions to update',
			}

	except Exception as e:
		res = {
			'status': 'Error',
			'message': str(e),
		}
		
	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')


@login_required
def del_task_label(request, task_id):

	try:
		res = {
			'status': 'Ok',
		}

		label_id = request.GET.get('label_id')
		
		task = Task.objects.get(pk=task_id)
		label = TaskLabel.objects.get(pk=label_id)

		if label in task.tasklabels.all():
			if ACL.canUpdateTask(request.user, task):
				
				if task.tasklabels.all().count()>1: 
					task.tasklabels.remove(label)
				else:
					res = {
						'status': 'Error',
						'message': 'No permissions to update',
					}
			else:
				res = {
					'status': 'Error',
					'message': 'No permissions to update',
				}
	
	except Exception as e:
		res = {
			'status': 'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')



