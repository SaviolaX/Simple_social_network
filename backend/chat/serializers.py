from rest_framework.serializers import ModelSerializer, SerializerMethodField
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework import status

from .models import Room, Message
from profiles.serializers import ProfileSerializer


class MessageSerializer(ModelSerializer):
    """ Message serializer """
    class Meta:
        model = Message
        exclude = ('room',)


class RoomsListSerializer(ModelSerializer):
    """ Serialize a list of rooms """
    initiator = ProfileSerializer()
    receiver = ProfileSerializer()
    last_message = SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'initiator', 'receiver', 'last_message']

    def get_last_message(self, instance):
        message = instance.message_set.first()
        return MessageSerializer(instance=message).data


class CreateRoomSerializer(ModelSerializer):
    """ Serialize create room view """
    class Meta:
        model = Room
        fields = ['id', 'initiator', 'receiver']
        
    def validate(self, data):
        initiator = data['initiator']
        receiver = data['receiver']
        
        # check if any chat between users exist
        chats = Room.objects.filter(Q(initiator=initiator, receiver=receiver) 
                                    | Q(initiator=receiver, receiver=initiator))
        
        if chats.count() != 0:
            raise ValidationError({'detail': 'Chat with this user already exist'})
            
        return data

        

class RoomSerializer(ModelSerializer):
    """ Serialize a room detail """
    initiator = ProfileSerializer()
    receiver = ProfileSerializer()
    message_set = MessageSerializer(many=True)

    class Meta:
        model = Room
        fields = ['id', 'initiator', 'receiver', 'message_set']