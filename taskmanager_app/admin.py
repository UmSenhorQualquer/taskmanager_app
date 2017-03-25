from taskmanager_app.models import *
from django.contrib import admin


admin.site.register(TaskLabelPermission)
admin.site.register(UserDetails)
admin.site.register(Task)
admin.site.register(TaskAttachment)

