from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from posts.models import Post
from .models import Comment
from .serializers import CommentCreateSerializer


class CommentCreateView(CreateAPIView):
    """ Create comment to post """
    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer
    permission_classes = (IsAuthenticated, )
    
    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)