from django.db import models
from django.contrib.auth.models import AbstractUser


def get_upload_path(instance, filename):
    """ Path for uploaded images """
    return 'profile/{0}/{1}'.format(instance.email, filename)


class Profile(AbstractUser):
    """ Profile db table """
    email = models.EmailField(max_length=255, unique=True)
    image = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    friends = models.ManyToManyField('Profile', blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]
