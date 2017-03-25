from django.db import models
from django.db.models import Q

# Create your models here.
import os
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views import generic
from django.views.decorators.http import require_POST
from jfu.http import upload_receive, UploadResponse, JFUResponse

from taskmanager_app.models import TaskAttachment, Task
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
import json
from taskmanager_app.acl import ACL

def sizeof_fmt(num):
	for x in ['KB','MB','GB']:
		num /= 1000.0
		if num < 1000.0:
			return "%3.2f %s" % (num, x)
		
	return "%3.1f %s" % (num, 'TB')

@login_required
def browse_task_files(request, task_id):
	try:
		res = {
			'status': 'Ok',
			'data': [],
		}

		task = Task.objects.get(pk=task_id)

		if ACL.canViewTask(request.user, task):
			#task = Task.objects.get(pk=int(task_id))

			if task.hasPermissions(request.user):
				files = TaskAttachment.objects.filter(task=task)
				#res = []
				for f in files:
					res['data'].append({ 
						'id':  f.pk, 
						'name':os.path.basename(f.task_attachment_file.name), 
						'url':f.task_attachment_file.url, 
						'size': sizeof_fmt(f.task_attachment_file.size)
					})
			else: res['data'] = []
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
@require_POST
def upload(request):
	task_id = request.POST.get('task_id', None)
	task = Task.objects.get(pk=int(task_id))
	
	if ACL.canUpdateTask(request.user, task):
		if task.hasPermissions(request.user):
			file_dict = {'task_id': task_id}

			if task_id!=None:
				file = upload_receive( request )

				task = Task.objects.get(pk=int(task_id))
				instance = TaskAttachment( task_attachment_file = file, task=task )
				instance.save()

				basename = os.path.basename( instance.task_attachment_file.path )

				file_dict = {
					'name' : basename,
					'size' : instance.task_attachment_file.size,

					'url': settings.MEDIA_URL + str(instance.task_attachment_file),
					'thumbnailUrl': '/static/file_thumb.png',

					'deleteUrl': reverse('jfu_delete', kwargs = { 'pk': instance.pk }),
					'deleteType': 'POST',
				}
		else:
			file_dict = {}
	else:
		raise Exception('Permission denied')

	return UploadResponse( request, file_dict )

@login_required
@require_POST
def upload_delete( request, pk ):
	try:
		instance = TaskAttachment.objects.get( pk = pk )
		task = instance.task

		if ACL.canUpdateTask(request.user, task):
			#instance = TaskAttachment.objects.get( pk = pk )
			#task = instance.task
			if task.hasPermissions(request.user):
				os.unlink( instance.task_attachment_file.path )
				instance.delete()
				success = True
			else:
				success = False
		else:
			raise Exception('Permission denied')

	except TaskAttachment.DoesNotExist:
		success = False

	return JFUResponse( request, success )