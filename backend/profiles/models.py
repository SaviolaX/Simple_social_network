from django.db import models
from django.contrib.auth.models import AbstractUser


class Profile(AbstractUser):
    """ Profile db table """
    email = models.EmailField(max_length=255, unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]
