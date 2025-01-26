from django.contrib import admin

from CRM.models import Client,Project,UserProfile
# Register your models here.
admin.site.register(Client)
admin.site.register(Project)
admin.site.register(UserProfile)
