from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ValidationError


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Friend(TimeStampedModel):
    from_user = models.ForeignKey(User, related_name="from_users", on_delete=models.CASCADE, null=True, blank=True)
    to_user = models.ForeignKey(User, related_name="friends", on_delete=models.CASCADE, null=True, blank=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"user: {self.from_user.username} & friend: {self.to_user.username}"

    def save(self, *args, **kwargs):
        existing_friend = Friend.objects.filter(
            Q(
                Q(from_user=self.from_user) |
                Q(to_user=self.from_user)
            ) |
            Q(
                Q(from_user=self.to_user) |
                Q(from_user=self.to_user)
            )
        ).first()
        if existing_friend:
            return ValidationError("Friend already exists")
        super().save(*args, **kwargs)

    @classmethod
    def get_friends(cls, user):
        return cls.objects.filter(
            Q(from_user=user, is_accepted=False) |
            Q(to_user=user, is_accepted=False)
        )
