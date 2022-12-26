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
    REQUIRED_FIELDS = [
        'username',
    ]


class FriendRequest(models.Model):
    """ Profile to profile friend request table """
    sender = models.ForeignKey(Profile,
                               on_delete=models.CASCADE,
                               blank=False,
                               null=False,
                               related_name='sender')
    receiver = models.ForeignKey(Profile,
                                 on_delete=models.CASCADE,
                                 blank=False,
                                 null=False,
                                 related_name='receiver')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.sender.email} --> {self.receiver.email}: {self.created_at}"
