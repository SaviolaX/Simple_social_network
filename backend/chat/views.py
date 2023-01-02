from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q


from .models import Room
from .serializers import RoomSerializer, CreateRoomSerializer, RoomsListSerializer
from profiles.models import Profile


class CreateRoomView(CreateAPIView):
    """ Create a new chat room view """
    queryset = Room.objects.all()
    serializer_class = CreateRoomSerializer
    permission_classes = (IsAuthenticated, )
    
    
class ChatRoomView(RetrieveAPIView):
    """ Retrieve a room detail """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (IsAuthenticated, )
    lookup_field = 'pk'

class MyChatsListView(APIView):
    """ Retrieve a list of all chat rooms where current user participate """
    permission_classes = (IsAuthenticated, )
    
    def get(self, request):
        my_chats = Room.objects.filter(Q(initiator=request.user) | Q(receiver=request.user))
        serializer = RoomsListSerializer(my_chats, many=True)
        return Response(serializer.data)


class DeleteChatView(DestroyAPIView):
    """ Delete a chat room """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = (IsAuthenticated, )
    lookup_field = 'pk'
