from django.contrib import admin

from .models import Message, Group, Notification
admin.site.register(Group)
admin.site.register(Notification)
admin.site.register(Message)
