from django.db import models

from posts.models import Post
from profiles.models import Profile


class Comment(models.Model):
    """ Comments db table """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    entry = models.TextField(blank=False, null=False)
    
    def __str__(self) -> str:
        return 'Author: {} --> Post: {} -> Entry: {}'.format(self.author.id, 
                                                             self.post.id, 
                                                             self.entry)