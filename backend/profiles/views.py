from rest_framework.generics import (RetrieveAPIView, UpdateAPIView,
                                     CreateAPIView, ListAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Profile, FriendRequest
from .serializers import (ProfileDetailSerializer, ProfileSerializer,
                          FriendRequestCreateSerializer)
from .permissions import IsProfileOwner


class ProfileDetailView(RetrieveAPIView):
    """ Display profile data """
    queryset = Profile.objects.all()
    serializer_class = ProfileDetailSerializer
    permission_classes = (IsAuthenticated, )
    lookup_field = 'pk'


class ProfileUpdateView(UpdateAPIView, RetrieveAPIView):
    """ Display profile data and update one """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (
        IsAuthenticated,
        IsProfileOwner,
    )
    lookup_field = 'pk'


class FriendRequestCreateView(CreateAPIView):
    """ Create a friend request """
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestCreateSerializer
    permission_classes = (
        IsAuthenticated,
        IsProfileOwner,
    )


class FriendRequestAcceptView(APIView):
    permission_classes = (IsAuthenticated, )
    """ Accept a friend request and add user to friend list """

    def get(self, request, user_pk, f_req_pk):
        friend_req = FriendRequest.objects.filter(pk=f_req_pk).first()

        if request.user != friend_req.receiver:
            return Response({'message': 'You can not perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        if friend_req == None:
            raise ValueError({'error': 'Friend request does not exist.'})

        # add users to each other friend list
        sender: object = friend_req.sender
        receiver: object = friend_req.receiver

        receiver.friends.add(sender)  # receiver adds sender to friend list
        sender.friends.add(receiver)  # sender adds receiver to friend list

        # delete friend request from db
        friend_req.delete()

        return Response(
            {'message': f'{sender.username} added to your friend list.'})


class FriendRequestRefuseView(APIView):
    permission_classes = (IsAuthenticated, )
    """ Refuse a friend request and delete request object """

    def get(self, request, user_pk, f_req_pk):
        friend_req = FriendRequest.objects.filter(pk=f_req_pk).first()

        if request.user != friend_req.receiver:
            return Response({'message': 'You can not perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        if friend_req == None:
            raise ValueError({'error': 'Friend request does not exist.'})

        # delete friend request from db
        friend_req.delete()

        return Response({'message': f'Friend request was refused.'})


class RemoveFriendView(APIView):
    """ Remove friend from friend list """
    permission_classes = (IsAuthenticated, )

    def get(self, request, user_pk: str, friend_pk: str):

        if str(request.user.pk) != user_pk:
            return Response({'message': 'You can not perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        friend = Profile.objects.filter(pk=friend_pk).first()
        if friend == None:
            raise ValueError({'error': 'User does not exist.'})

        if friend not in request.user.friends.all():
            return Response(
                {'message': 'The user is not in your friend list.'},
                status=status.HTTP_403_FORBIDDEN)

        # remove friend from friend list
        request.user.friends.remove(friend)
        # remove current user from friend's list of friends
        friend.friends.remove(request.user)

        return Response(
            {'message': f'{friend.username} was deleted from friends list'})


class ProfileFriendsListView(APIView):
    """ Friends list """
    permission_classes = (IsAuthenticated, )

    def get(self, request, user_pk):
        user = Profile.objects.filter(pk=user_pk).first()
        if user == None:
            raise ValueError({'error': 'User does not exist.'})
        friends = user.friends.all()
        serializer = ProfileSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfilesListView(ListAPIView):
    """ List of all profiles """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, )