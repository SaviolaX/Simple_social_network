from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Post
from .serializers import PostSerializer, PostListAllSerializer, PostCreateSerializer


class PostListView(ListAPIView):
    """ Get a list of all posts """
    queryset = Post.objects.all()
    serializer_class = PostListAllSerializer
    permission_classes = (IsAuthenticated, )
    

class PostCreateView(CreateAPIView):
    """ Create a new post """
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = (IsAuthenticated, )
    
    def perform_create(self, serializer):
        """ Assign a current auth user as author """
        serializer.save(author=self.request.user)
    
