from rest_framework.generics import (ListAPIView, CreateAPIView,
                                     RetrieveAPIView, UpdateAPIView,
                                     DestroyAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Post
from .serializers import (PostSerializer, FriendsPostsListSerializer,
                          PostCreateSerializer)
from .permissions import IsPostAuthor


class LikePostView(APIView):
    """ Like post or unlike """
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        if post.like.filter(pk=request.user.pk).exists():
            post.like.remove(request.user)
        else:
            post.dislike.remove(request.user)
            post.like.add(request.user)

        return Response({'detail': 'Success'}, status=status.HTTP_200_OK)


class DislikePostView(APIView):
    """ Like post or unlike """
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        if post.dislike.filter(pk=request.user.pk).exists():
            post.dislike.remove(request.user)
        else:
            post.like.remove(request.user)
            post.dislike.add(request.user)

        return Response({'detail': 'Success'}, status=status.HTTP_200_OK)


class PostDeleteView(DestroyAPIView):
    """ Delete a single post """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsPostAuthor)
    lookup_field = 'pk'


class PostDetailView(RetrieveAPIView):
    """ Get a single post detail """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, )
    lookup_field = 'pk'


class PostUpdateView(UpdateAPIView, RetrieveAPIView):
    """ Update post data """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsPostAuthor)
    lookup_field = 'pk'


class FriendsPostsListView(ListAPIView):
    """ Get a list of friends posts """
    queryset = Post.objects.all()
    serializer_class = FriendsPostsListSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self) -> list:
        """ Create a list of posts were created by current user friends """
        fr_posts = Post.objects.filter(
            author__in=self.request.user.friends.all())
        return fr_posts


class PostCreateView(CreateAPIView):
    """ Create a new post """
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = (IsAuthenticated, )

    def perform_create(self, serializer) -> None:
        """ Assign a current auth user as author """
        serializer.save(author=self.request.user)
