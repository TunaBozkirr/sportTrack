from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    """
    Hangi user hangi gruba üye?
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.group.name}"


class Activity(models.Model):
    """
    Kullanıcı aktiviteleri.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.TextField()
    duration = models.IntegerField()  # Süre (dakika)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.description}"
