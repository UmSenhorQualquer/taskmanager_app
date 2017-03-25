from taskmanager_app.models import *
from django.conf import settings
from django.db.models import Q


class ACL():

	"""
	Access Control List
	Defines all the methods to validate the user's permissions on a per view basis
	"""
	@staticmethod
	def canViewOthersTasks(user, labels):
		return True
		clearanceList = []
		
		for label in labels:
			projects = label.project_set.all()
			if len(projects)==0:  clearanceList.append(label); continue
			project = projects[0]
			userRolesInProj = ProjectUser.objects.filter( user=user, project=project )
			for projectRole in userRolesInProj:
				if projectRole.role.projectuserrole_view_others:
					clearanceList.append(label)
					break

		clearanceList = list(set(clearanceList))
		return clearanceList

	@staticmethod
	def canViewTask(user, task):
		return True
		labels = task.tasklabels.filter( Q(user=user) or Q(users=user) )
		userInTask = user in task.task_users.all()
		if userInTask: return True

		associated2projects = []
		for label in labels:
			projects = label.project_set.all()
			if len(projects)==0: continue
			
			project = projects[0]
			associated2projects.append(project)
			userRolesInProj = ProjectUser.objects.filter( user=user, project=project )
			for projectRole in userRolesInProj:
				if projectRole.role.projectuserrole_view_others: return True
		if len(associated2projects)==0: return True

		return False

		
	@staticmethod
	def canUpdateTask(user, task):
		return True
		labels = task.tasklabels.filter( Q(user=user) | Q(users=user) )
		userInTask = user in task.task_users.all()

		associated2projects = []
		for label in labels:
			projects = label.project_set.all()
			if len(projects)==0: continue
			project = projects[0]

			associated2projects.append(project)
			userRolesInProj = ProjectUser.objects.filter( user=user, project=project )
			for projectRole in userRolesInProj:
				if userInTask and projectRole.role.projectuserrole_update_own:
					return True
				elif projectRole.role.projectuserrole_update_others:
					return True
					
		if len(associated2projects)==0: return True
	
		return False


	@staticmethod
	def canDeleteTask( user, task):
		return True
		labels = task.tasklabels.filter( Q(user=user) | Q(users=user) )
		userInTask = user in task.task_users.all()

		associated2projects = []
		for label in labels:
			projects = label.project_set.all()
			if len(projects)==0: continue
			project = projects[0]
			associated2projects.append(project)
			userRolesInProj = ProjectUser.objects.filter( user=user, project=project )
			for projectRole in userRolesInProj:
				if userInTask and projectRole.role.projectuserrole_delete_own:
					return True
				elif projectRole.role.projectuserrole_delete_others:
					return True
		if len(associated2projects)==0: return True

		return False


	
	@staticmethod
	def canCreateInLabel(user, label):
		return True
		clearanceList = []
		projects = label.project_set.all()
		if len(projects)==0 and (user in label.users.all() or user==label.user): return True

		project = projects[0]
		userRolesInProj = ProjectUser.objects.filter(user=user, project=project )
		for projectRole in userRolesInProj:
			if projectRole.role.projectuserrole_create:
				return True

		return False
