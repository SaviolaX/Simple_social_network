from django.db import models
from django.conf import settings


class Room(models.Model):
    """ Room db table """
    initiator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=False, related_name="conver_starter"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=False, related_name="conver_participant"
    )
    start_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return '{} -> {}'.format(self.initiator, self.receiver)


class Message(models.Model):
    """ Message db table """
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                              null=True, related_name='message_sender')
    text = models.CharField(max_length=200, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE,)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return '{} -> room {} | {}: {}'.format(self.sender.username, 
                                               self.room.pk, 
                                               self.timestamp, 
                                               self.text)

    class Meta:
        ordering = ('timestamp',)

