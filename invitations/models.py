from django.db import models
from django.contrib.auth.models import User

from page.models import Page

import string
import random


def random_key(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class ManagerInvitation(models.Model):
    expired = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    key = models.CharField(max_length=32, default=random_key)
    date_created = models.DateTimeField(auto_now_add=True)
    invite_to = models.EmailField()
    invite_from = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    manager_edit_page = models.BooleanField(default=False)
    manager_delete_page = models.BooleanField(default=False)
    manager_invite_page = models.BooleanField(default=False)

