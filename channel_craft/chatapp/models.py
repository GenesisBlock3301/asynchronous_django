from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from userapp.models import TimeStampedModel


class Group(TimeStampedModel):
    owner = models.ForeignKey(User, related_name="group_owner", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name="users_group")
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class PrivateRoom(TimeStampedModel):
    name = models.CharField(max_length=255)
    user1 = models.ForeignKey(User, related_name="user1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name="user2", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        existing_room = PrivateRoom.objects.filter(
            Q(
                Q(user1=self.user1) |
                Q(user2=self.user1)
            ) &
            Q(
                Q(user1=self.user2) |
                Q(user2=self.user2)
            )
        ).exists()
        if existing_room:
            raise ValidationError("Room already exists")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Private roomID: {self.id}"


class Message(TimeStampedModel):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True,)
    is_group_message = models.BooleanField(default=False)
    room = models.ForeignKey(PrivateRoom, on_delete=models.CASCADE, blank=True, null=True)
    is_room_message = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username}: {self.content} [{self.created_at}]"


class Notification(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.message}"
