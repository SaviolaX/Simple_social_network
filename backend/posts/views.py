from rest_framework.generics import (ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView)
from rest_framework.permissions import IsAuthenticated

from .models import Post
from .serializers import PostSerializer, FriendsPostsListSerializer, PostCreateSerializer



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
    permission_classes = (IsAuthenticated, )
    lookup_field = 'pk'


class FriendsPostsListView(ListAPIView):
    """ Get a list of friends posts """
    queryset = Post.objects.all()
    serializer_class = FriendsPostsListSerializer
    permission_classes = (IsAuthenticated, )
    
    def get_queryset(self) -> list:
        """ Create a list of posts were created by current user friends """
        fr_posts = Post.objects.filter(author__in=self.request.user.friends.all())
        return fr_posts
    

class PostCreateView(CreateAPIView):
    """ Create a new post """
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = (IsAuthenticated, )
    
    def perform_create(self, serializer) -> None:
        """ Assign a current auth user as author """
        serializer.save(author=self.request.user)
    
