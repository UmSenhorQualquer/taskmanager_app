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
import dateutil.parser
from taskmanager_app.acl import ACL

@login_required
@csrf_exempt
def del_task(request, task_id):

	res = {}


	try:

		task 	= Task.objects.get(pk=task_id)
		labels 	= task.tasklabels.all()

		labels = labels.filter( Q(user=request.user) )

		"""
		if len(labels)>0:
			#labels = labels.filter(pk__in=task).distinct()
			#labels = labels.filter(pk__in=[task.task_id]).distinct()
			labels = labels.distinct()
		"""
		labels = labels.distinct()

		if ACL.canDeleteTask(request.user, task):	
			if task.hasPermissions(request.user): #TODO: Check if this is necessary
				task.delete()
				res = {'status': 'Ok'}
			else:
				res = {'status': 'Error', 'message': 'Permission denied'}
		else:
			res = {'status': 'Error', 'message': 'Permission denied'}
		

	except Exception as e:
		res = {'status': 'Error', 'message': str(e)}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')


# Add a new or update an existing task
@login_required
@csrf_exempt
def add_task(request, task_id=None):

	#try:
	res = { 'status': 'Ok' }

	is_complete 	= "true"==request.GET.get("task_is_complete").lower()
	is_important 	= "true"==request.GET.get("task_is_important").lower()
	is_title 		= "true"==request.GET.get("task_is_title").lower()
	task_name 		= request.GET.get("task_name")
	task_start_date = request.GET.get("task_start_date")
	task_end_date 	= request.GET.get("task_end_date")
	clone_from 		= request.GET.get("clone_from", None)

	# Eventual future request: Do not allow to remove the complete status of a task if the 'master' task is marked as complete

	# Only allow a task to be complete if ALL its predecessors are also complete
	if task_id != None and is_complete:
		t = Task.objects.get(pk=task_id)
		for p in t.task_predecessors.all():
			if p.task_is_complete == False:
				raise Exception('There are still predecessors tasks to complete')

	# Convert ISO string dates to datetime objects
	task_start_date = dateutil.parser.parse(task_start_date)
	task_end_date = dateutil.parser.parse(task_end_date)

	#correct the dates if start dat > end date
	if task_start_date > task_end_date and task_id!=None:
		task = Task.objects.get(pk=task_id)
		diff_dates = task_end_date - task.task_start_date
		task_end_date = task_start_date + diff_dates

	if task_start_date > task_end_date:
		raise Exception('Start date has to be lower than the end date.')
	
	

	# ACL ##############################################################
	labelsToInsert = []
	if task_id==None and clone_from!='-1':
		clone = Task.objects.get(pk=clone_from)
		addLabelTo = False
		for l in clone.tasklabels.all(): 
			if ACL.canCreateInLabel(request.user, l):
				labelsToInsert.append(l)
				addLabelTo = True

		if not addLabelTo:
			tasklabel_id = request.GET.get("label_id")
			label = TaskLabel.objects.get(pk=tasklabel_id)
			if ACL.canCreateInLabel(request.user, label):
				labelsToInsert.append(label)

		if len(labelsToInsert)==0: raise Exception('No permissions')
	elif task_id!=None:
		task = Task.objects.get(pk=task_id)
		if not ACL.canUpdateTask(request.user, task):
			 raise Exception('No permissions')
	else:
		member_id = request.GET.get("label_id")
		label = TaskLabelMembership.objects.get(pk=member_id).child

		if not ACL.canCreateInLabel(request.user, label): raise Exception('No permissions')
	###################################################################

	task = Task( 
			task_id 			= task_id,
			task_is_complete	= is_complete,
			task_is_important	= is_important,
			task_is_title		= is_title,
			task_name 			= task_name,
			task_start_date 	= task_start_date,
			task_end_date 		= task_end_date,
			user = request.user if is_complete else None,
		)
	task.save()

	try:
		for t in task.task_set.filter(task_is_title=True):
			changed = False
			if t.task_start_date>task.task_start_date:
				t.task_start_date = task.task_start_date
				changed = True
			if t.task_end_date<task.task_end_date:
				t.task_end_date = task.task_end_date
				changed = True
			if changed: t.save()
	except Task.DoesNotExist:
		pass

	
	if task_id==None:
		if clone_from!=None and clone_from != '-1':
			for u in clone.task_users.all(): task.task_users.add(u)
			for l in labelsToInsert: 		 task.tasklabels.add(l)
		else:
			member_id = request.GET.get("label_id")
			label 	  = TaskLabelMembership.objects.get(pk=member_id).child
		
			task.tasklabels.add(label)
			task.task_users.add(request.user)


	users = []
	for user in task.task_users.all():
		try: a, b = user.first_name[0],  user.last_name[0]
		except:  a,b = '',''
		users.append( [user.pk, user.username, (a+b).upper() ] )

	labels=[]
	for label in task.tasklabels.all():
		labels.append({ 
			'id':label.pk, 
			'label':label.tasklabel_name, 
			'color': "#%s" % label.tasklabel_color
		})

	res['data'] = {
		'task_id': task.pk,
		'task_is_title': task.task_is_title,
		'task_is_complete': task.task_is_complete,
		'task_is_important': task.task_is_important,
		'task_name': task.task_name,
		'task_start_date': task.task_start_date,
		'task_end_date': task.task_end_date,
		'completed_by_user_id': task.user.id if task.task_is_complete else None,
		'users': users,
		'labels': labels,
	}
	"""
	except Exception as e:
		res = {
			'status': 'Error',
			'message': str(e)
		}"""
	
	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')


