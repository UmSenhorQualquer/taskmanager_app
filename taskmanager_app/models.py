from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.conf import settings
import os

class TaskLabelPermission(models.Model):
	tasklabelpermission_id = models.AutoField(primary_key = True)
	tasklabelpermission_name = models.CharField('Name', max_length = 255)
	tasklabelpermission_type = models.SmallIntegerField('Type')

	def __unicode__(self): return self.tasklabelpermission_name
	

class TaskLabel(models.Model):
	tasklabel_id = models.AutoField(primary_key = True)
	tasklabel_name = models.CharField('Task label', max_length = 255)
	tasklabel_color = models.CharField('Color', max_length = 6, default='FFFFFF')
	tasklabel_archived = models.BooleanField('Archived', default=False)

	user 	= models.ForeignKey(		User, 		 verbose_name = 'Creator')
	#users 	= models.ManyToManyField(	User, 		 related_name = 'shared_with')

	def copy(self):
		cp = TaskLabel.objects.get(pk=self.pk)
		cp.pk=None;
		cp.save()

		for task in Task.objects.filter(tasklabels=self):
			task_cp = task.copy()
			task_cp.tasklabels.add(cp)
		return cp
	
	def hasChildrens(self, user): return TaskLabelMembership.childrens(user,self).exists()
	
	def canDelete(self, user): return self.user==user

	def delete(self):
		#delete first all tasks associated to this
		super(TaskLabel, self).delete()

	def __unicode__(self): return "%s - %s" % (self.user , self.tasklabel_name)



class TaskLabelMembership(models.Model):

	WRITE_PERMISSION = 0

	parent 		= models.ForeignKey(TaskLabel, related_name='parent',blank=True,null=True)
	child  		= models.ForeignKey(TaskLabel, related_name='child')
	permission 	= models.SmallIntegerField('Permissions')
	user 		= models.ForeignKey(User)
	order 		= models.PositiveSmallIntegerField('Order', default=0)


	def deleteLabel(self, user):
		#if not label.canDelete(request.user): raise Exception("You do not have permissions")
		#if label.task_set.count()>0: raise Exception("There are still tasks associated to the label")
		self.child.delete()
		self.delete()
		return True

	def copy(self):
		cp = TaskLabelMembership.objects.get(pk=self.pk)
		cp.pk = None
		cp.child = self.child.copy()
		cp.save()
		return cp

	@staticmethod
	def childrens(user, parent=None):
		return TaskLabelMembership.objects.filter(user=user, parent=parent)

	@staticmethod
	def childrens(user, parent=None):
		return TaskLabelMembership.objects.filter(user=user, parent=parent)




class Task(models.Model):

	task_id = models.AutoField(primary_key = True)
	task_is_complete = models.BooleanField('Complete')
	task_is_important = models.BooleanField('Important')
	task_is_title = models.BooleanField('Title')
	task_name = models.CharField('Task name', max_length = 256)
	task_start_date = models.DateTimeField('Start date') 
	task_end_date = models.DateTimeField('End date') # The date the task was completed (it may be less than or equal to due date, but it must not exceed it)

	# FK's
	user = models.ForeignKey(User, verbose_name='Completed by', blank=True, null=True)

	# m2m relations
	task_predecessors = models.ManyToManyField("Task") # A task can have multiple predecessors
	task_users = models.ManyToManyField(User, related_name = 'assigned_to') # A task can have multiple assignees
	tasklabels = models.ManyToManyField(TaskLabel)

	def copy(self):
		cp = Task.objects.get(pk=self.pk)
		cp.pk = None
		cp.save()
		#for predecessor in 
		for user in self.task_users.all(): cp.task_users.add(user)
		#for user in self.tasklabels.all(): cp.task_users.add(user)
		return cp

	def hasPermissions(self, user):
		return True
		return self.tasklabels.filter( Q(user=user) | Q(users=user) ).exists()

	def usersEmails(self):
		return []
		users_emails = []
		for label in self.tasklabels.all():
			for user in label.users.all():
				users_emails.append(user.email)
		return list(set(users_emails))

	def taskReminders(self):
		task_reminders = self.reminder_set.all().order_by('reminder_date')
		list_of_reminders = []
		for reminder in task_reminders:
			list_of_reminders.append({
				'id':reminder.pk, 
				'subject':reminder.reminder_subject, 
				'date': reminder.reminder_date.strftime( settings.DATE_FORMAT ),
			})
		return list_of_reminders


def get_upload_path(instance, filename):
	return os.path.join('uploads', 'tasks', str(instance.task.pk), filename )
	

class TaskAttachment(models.Model):
	task_attachment_id = models.AutoField(primary_key = True)
	task_attachment_file = models.FileField(upload_to=get_upload_path)

	# fk relations
	task = models.ForeignKey('Task', verbose_name = 'Task')

	@property
	def filename(self):
		return os.path.basename(self.task_attachment_file.name)


class Observation(models.Model):
	observation_id = models.AutoField(primary_key = True)
	observation_msg = models.TextField()
	observation_date = models.DateTimeField('Date', auto_now_add = True)

	# fk relations
	task = models.ForeignKey('Task', verbose_name = 'Task')	
	user = models.ForeignKey(User, verbose_name = 'Observation creator') # even for automatic observations made when a user changes a task date, in which case an automatic observation is inserted in order to register so


class LogEntry(models.Model):
	log_entry_id = models.AutoField(primary_key = True)
	log_entry_date = models.DateTimeField('Log message date')
	log_entry_msg = models.CharField('Log entry', max_length = 256)

	# fk relations
	task = models.ForeignKey('Task', verbose_name = 'Task')

class Reminder(models.Model):
	reminder_id = models.AutoField(primary_key = True)
	reminder_subject = models.CharField('Subject', max_length = 255)
	reminder_msg = models.TextField()
	reminder_recipients = models.TextField('Recipients')
	reminder_date = models.DateTimeField('Reminder date')
	reminder_non_validated = models.BooleanField('No validated')
	reminder_send_timestamp = models.DateTimeField('Timestamp the message was sent on', blank=True, null=True)

	# fk relations
	task = models.ForeignKey('Task', verbose_name = 'Task')


class ReminderAttachment(models.Model):
	reminder_attachment_id = models.AutoField(primary_key = True)
	reminder_attachment_file = models.FileField(upload_to = 'uploads/ReminderAttachment')

	# fk relations
	reminder = models.ForeignKey('Reminder', verbose_name = 'Reminder')	



class UserDetails(models.Model):
	userdetails_dailyreminder = models.BooleanField('Remind me', help_text='Send me everyday a reminder of my tasks')
	user = models.ForeignKey(User)		