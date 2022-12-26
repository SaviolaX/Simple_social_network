from rest_framework.serializers import ModelSerializer

from .models import Comment
from posts.models import Post


class CommentCreateSerializer(ModelSerializer):
    """ Create comment serializer """
    
    class Meta:
        model = Comment
        fields = ('id', 'entry')
        
    def create(self, validated_data):
        # assign post to a new comment
        post_pk = self.context['view'].kwargs.get('post_pk')
        validated_data['post'] = Post.objects.filter(pk=post_pk).first()
        return super().create(validated_data)
        