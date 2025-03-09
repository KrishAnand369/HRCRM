from django.contrib import admin

from CRM.models import Client,Project,UserProfile,Task,Checklist,Comment,Attachment,ClockEvent
# Register your models here.
admin.site.register(Client)
admin.site.register(Project)
admin.site.register(UserProfile)
admin.site.register(Task)
admin.site.register(Checklist)
admin.site.register(Comment)
admin.site.register(Attachment)
admin.site.register(ClockEvent)
#admin.site.register()

