import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser

class Account(AbstractUser):
    ROLES=(('owner', '擁有者'), ('maintainer', '維護者'), ('guest', '訪客'))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    role=models.CharField(choices=ROLES, max_length=20, default='guest')
    phone = models.CharField(max_length=10, blank=True)
    last_edit_at=models.DateTimeField(auto_now=True)