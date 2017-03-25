from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db.models import Q
from taskmanager_app.models import *
import json

@login_required
def add_label(request, member_id=None):
	try:
		
		member_id = request.GET.get('id', member_id)
		position = request.GET.get('position', 0)
		label_name = request.GET.get('label_name', None)
		label_color = request.GET.get('label_color', 'FFFFFF')
	
		if label_name==None or len(label_name)==0 or member_id==None: raise

		member = TaskLabelMembership.objects.get(id=member_id)
		
		label = TaskLabel(
			tasklabel_name=label_name, 
			tasklabel_color=label_color,
			tasklabel_archived=False)
		label.user = request.user
		label.save()

		
		newMember = TaskLabelMembership(parent=member.child,
			child=label, permission=TaskLabelMembership.WRITE_PERMISSION,
			order=int(position), user=request.user )
		newMember.save()

		res = {
			'status': 'Ok',
			'id': newMember.pk
		}

	except Exception as e:
		res = {
			'status':'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')




@login_required
def rename_label(request, member_id=None):
	try:
		
		member_id = request.GET.get('id', member_id)
		label_name = request.GET.get('label_name', None)
		
		if label_name==None or len(label_name)==0 or member_id==None: raise

		member = TaskLabelMembership.objects.get(id=member_id)
		label = member.child
		label.tasklabel_name = label_name
		label.save()

		res = {'status': 'Ok', }
	except Exception as e:
		res = {
			'status':'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')



def copy_label(request):

	
	original = request.GET.get('id')
	parent = request.GET.get('parent', None)
	position = request.GET.get('position', 0)
	
	originalMember 	= TaskLabelMembership.objects.get(id=original)
	parentMember 	= TaskLabelMembership.objects.get(id=parent)
	copyMember = originalMember.copy()
	copyMember.parent = parentMember.child
	copyMember.save()

	res = {'status': 'Ok', }
	

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')






@login_required
def del_label(request, label_id):
	try:
		res = { 'status': 'Ok' }
		membership = TaskLabelMembership.objects.get(pk=label_id)
		membership.deleteLabel(request.user)

	except Exception as e:
		res = {
			'status': 'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')


"""
@login_required
def browse_labels(request):
	
	try:
		res = {
			'status': 'Ok',
			'data': []
		}

		labels = TaskLabel.objects.filter(Q(user=request.user) | Q(users=request.user))
		labels = labels.filter(tasklabel_archived=False).distinct().order_by('tasklabel_name')

		#res = []
		for label in labels:
			#Check if user has access to the project
			
			if hasattr(label,'project_set') and \
				label.project_set.count()>0 and \
				label.project_set.filter( Q(projectuser__user=request.user) & Q(projectuser__role__projectuserrole_view_proj=True) ).count()==0: 
				continue
				
			res['data'].append({
				'id': label.pk,
				'label': label.tasklabel_name,
				'color': "#%s" % label.tasklabel_color,
				'can_delete': label.user==request.user,
				'is_project': label.project_set.count()==1
			})

	except Exception as e:
		res = {
			'status': 'Error',
			'message': str(e),
		}

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')
"""






@login_required
def move_label(request):
	try:
		memberChildId = request.GET.get('id',None)
		memberParentId = request.GET.get('parent',None)
		position = request.GET.get('position',0)

		childMember = TaskLabelMembership.objects.get(pk=memberChildId)
		parentMember = TaskLabelMembership.objects.get(pk=memberParentId)

		childMember.parent = parentMember.child
		childMember.order = int(position)

		childMember.save()

		res = True
	except Exception as e:
		res = False
	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')






@login_required
def browse_labels(request):
	user = request.user
	
	#try:
	res = []
	rootid = request.GET.get('id',None)
	
	if rootid=='#':
		memberships = TaskLabelMembership.childrens(user)

		if not memberships.exists():
			#In case there aren't any root membership, create one
			task = TaskLabel(tasklabel_name='My labels', user=user)
			task.save()

			membership = TaskLabelMembership(
				parent     = None,
				child  	   = task,
				permission = TaskLabelMembership.WRITE_PERMISSION, 
				user 	   = user)
			membership.save()
			memberships = [membership]
	else:
		root = TaskLabelMembership.objects.get(pk=rootid)
		memberships = TaskLabelMembership.childrens(user, root.child)

	memberships = memberships.order_by('order', 'child__tasklabel_name')

	for membership in memberships:
		#Check if user has access to the project
		
		
		res.append({
			'id': membership.pk,
			'labelid': membership.child.pk,
			'data': {'color': "#"+membership.child.tasklabel_color},
			'text': membership.child.tasklabel_name ,
			'children': membership.child.hasChildrens(user)
		})

	#except Exception as e: res = []

	data = json.dumps(res, cls = DjangoJSONEncoder)
	return HttpResponse(data, content_type = 'application/json')