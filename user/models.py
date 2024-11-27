from django.db import models
import re

from django.core.exceptions import ValidationError

from django.contrib.auth.models import AbstractUser
from rbac.models import Role

def validate_phone_number(value):
    if not re.fullmatch(r'\+639\d{9}', value):
        raise ValidationError("Phone number must be in the format +639XXXXXXXXX")



# Create your models here.
class CustomUser(AbstractUser):
    roles = models.ForeignKey(Role, related_name='users', blank=True, on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(
            max_length=13,
            blank=True,
            null=True,
            help_text="Phone number must be in the format +639XXXXXXXXX",
            validators=[validate_phone_number],

        )