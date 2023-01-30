from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class Member(AbstractUser):
    age = models.IntegerField(verbose_name="나이",default=20, null=True)