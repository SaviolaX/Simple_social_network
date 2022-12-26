from django.db import models

from profiles.models import Profile


def get_upload_path(instance, filename):
    """ Path for uploaded images """
    return 'profile/{0}/{1}'.format(instance.author.email, filename)


class Post(models.Model):
    """ Post db table """
    author = models.ForeignKey(Profile,
                               on_delete=models.CASCADE,
                               blank=False,
                               null=False)
    entry = models.TextField(blank=True, null=True)
    file = models.ImageField(upload_to=get_upload_path, blank=True, null=True)
    like = models.ManyToManyField(Profile, blank=True, related_name='Liked')
    dislike = models.ManyToManyField(Profile,
                                     blank=True,
                                     related_name='Disliked')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return '{}: {}'.format(self.author.username, self.created_at)
