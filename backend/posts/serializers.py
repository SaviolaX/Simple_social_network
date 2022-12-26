from rest_framework.serializers import (ModelSerializer, SerializerMethodField, ValidationError)

from .models import Post
from profiles.models import Profile
from comments.models import Comment


class PostCommentsSerializer(ModelSerializer):
    """ Display post comments serializer """
    author = SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'entry')
        
    def get_author(self, obj):
        author = Profile.objects.filter(pk=obj.author.pk).first()
        serializer = PostProfileSerializer(author)
        return serializer.data


class PostSerializer(ModelSerializer):
    """ Serializer for model Post """
    like = SerializerMethodField()
    dislike = SerializerMethodField()
    comments = SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ('id', 'entry', 'file', 'like', 'dislike', 'created_at', 'comments')
        
    def get_like(self, obj):
        total_likes = obj.like.count()
        return total_likes
    
    def get_dislike(self, obj):
        total_dislikes = obj.dislike.count()
        return total_dislikes
    
    def get_comments(self, obj):
        post_comments = Comment.objects.filter(post__pk=obj.pk)
        serializer = PostCommentsSerializer(post_comments, many=True)
        return serializer.data
   
        
class PostCreateSerializer(ModelSerializer):
    """ Serializer for model Post """
    class Meta:
        model = Post
        fields = ('id', 'entry', 'file', 'created_at')
        
    def validate(self, data):
        if data['entry'] == '' and data['file'] == None:
            raise ValidationError({'message': 'Fill up "entry" or "file" field to create a post.'})   
        
        return data
        
class PostProfileSerializer(ModelSerializer):
    """ Serializer for Profile """

    class Meta:
        model = Profile
        fields = ('id', 'email', 'username', 'image')
  
        
class FriendsPostsListSerializer(ModelSerializer):
    """ Serializer for model Post """
    author = SerializerMethodField()
    like = SerializerMethodField()
    dislike = SerializerMethodField()
    comments = SerializerMethodField()
    total_comments = SerializerMethodField()
    
    
    class Meta:
        model = Post
        fields = ('id', 'author', 'entry', 'file', 'like', 'dislike', 'created_at', 'total_comments', 'comments')
        
    def get_like(self, obj):
        """ Get a sum of all likes to current post """
        total_likes = obj.like.count()
        return total_likes
    
    def get_dislike(self, obj):
        """ Get a sum of all dislikes to current post """
        total_dislikes = obj.dislike.count()
        return total_dislikes
        
    def get_author(self, obj):
        """ Get an author detail """
        author = Profile.objects.filter(pk=obj.author.pk).first()
        serializer = PostProfileSerializer(author)
        return serializer.data
    
    def get_comments(self, obj):
        """ Get first 3 comments to current post """
        post_comments = Comment.objects.filter(post__pk=obj.pk)[:3]
        serializer = PostCommentsSerializer(post_comments, many=True)
        return serializer.data
    
    def get_total_comments(self, obj):
        """ Get a sum of all comments to current post """
        post_comments = Comment.objects.filter(post__pk=obj.pk).count()
        return post_comments

