from django.db import models
from django.contrib.auth.models import User
from userapp.models import TimeStampedModel


class Group(TimeStampedModel):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name="users_group")

    def __str__(self):
        return self.name


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages", default=None)
    content = models.TextField()
    is_group_message = models.BooleanField(default=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True, )

    def __str__(self):
        return f"{self.user.username}: {self.content} [{self.created_at}]"


class Notification(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.message}"
