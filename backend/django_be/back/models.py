from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    birthday = models.DateField(blank=True, null=True)
    tg_id = models.IntegerField(unique=True, null=True)

    def __str__(self):
        return self.username
