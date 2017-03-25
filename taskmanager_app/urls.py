from django.conf.urls import url

from taskmanager_app.viewslib import utils
from taskmanager_app.viewslib import labels
from taskmanager_app.viewslib import observations
from taskmanager_app.viewslib import predecessors
from taskmanager_app.viewslib import reminders
from taskmanager_app.viewslib import reports
from taskmanager_app.viewslib import tasks
from taskmanager_app.viewslib import taskUsers
from taskmanager_app.viewslib import taskLabels
from taskmanager_app.viewslib import attachments
from taskmanager_app.views import ptm_index

urlpatterns =[
    
    url( r'^user/rss/', utils.user_rss),

    url( r'^labels/ical/(?P<label_id>\d+)/', utils.label_ical),
    url( r'^labels/print/(?P<label_id>\d+)/', utils.label_print),
    url( r'^labels/snapshot/(?P<label_id>\d+)/', utils.label_snapshot),
    
    url( r'^labels/task/add/(?P<task_id>\d+)', taskLabels.add_task_label),
    url( r'^labels/task/del/(?P<task_id>\d+)', taskLabels.del_task_label),

    url( r'^labels/browse/', labels.browse_labels),
    url( r'^labels/rename/(?P<member_id>\d+)', labels.rename_label),
    url( r'^labels/add/(?P<member_id>\d+)', labels.add_label),
    url( r'^labels/add/', labels.add_label),
    url( r'^labels/del/(?P<label_id>\d+)', labels.del_label),
    url( r'^labels/move/', labels.move_label),
    url( r'^labels/copy/', labels.copy_label),
    
    
    url( r'^predecessors/browse/', predecessors.browse_task_predecessors),
    url( r'^predecessors/add/(?P<task_id>\d+)/(?P<pred_id>\d+)', predecessors.add_task_predecessor),
    url( r'^predecessors/del/(?P<task_id>\d+)/(?P<pred_id>\d+)', predecessors.del_task_predecessor),

    url( r'^tasks/quickreport/', reports.browse_quick_report),
    url( r'^tasks/browse/(?P<label_id>\d+)', taskLabels.browse_tasks_by_label),
    url( r'^tasks/browse/', taskLabels.browse_tasks_by_label),

    

    url( r'^users/task/add/(?P<task_id>\d+)', taskUsers.add_task_user),
    url( r'^users/task/del/(?P<task_id>\d+)', taskUsers.del_task_user),

    url( r'^users/search/', taskUsers.search_user),
    url( r'^users/browse/(?P<member_id>\d+)', taskUsers.browse_label_users),
    url( r'^users/add/(?P<label_id>\d+)',taskUsers.add_label_user),
    url( r'^users/del/(?P<label_id>\d+)', taskUsers.del_label_user),

    url( r'^reminders/browse/(?P<task_id>\d+)', reminders.browse_task_reminders),    
    url( r'^reminders/add/(?P<task_id>\d+)', reminders.add_task_reminders),
    url( r'^reminders/get/(?P<reminder_id>\d+)', reminders.get_task_reminder),
    url( r'^reminders/del/(?P<reminder_id>\d+)', reminders.del_task_reminder),
    
    url( r'^observations/browse/(?P<task_id>\d+)', observations.browse_observation),
    url( r'^observations/add/(?P<task_id>\d+)', observations.add_observation),
    url( r'^observations/del/(?P<observation_id>\d+)', observations.del_observation),

    url( r'^files/browse/(?P<task_id>\d+)', attachments.browse_task_files),
    url( r'^files/add/', attachments.upload, name = 'jfu_upload' ),
    url( r'^files/del/(?P<pk>\d+)$', attachments.upload_delete, name = 'jfu_delete' ),

    url( r'^task/add/(?P<task_id>\d+)', tasks.add_task),
    url( r'^task/add/', tasks.add_task),
    url( r'^task/del/(?P<task_id>\d+)', tasks.del_task),

    url( r'', ptm_index),

]