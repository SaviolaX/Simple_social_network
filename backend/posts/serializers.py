from rest_framework.serializers import (ModelSerializer, SerializerMethodField, ValidationError)

from .models import Post
from profiles.models import Profile


class PostSerializer(ModelSerializer):
    """ Serializer for model Post """
    class Meta:
        model = Post
        fields = ('id', 'entry', 'file', 'created_at')
        
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
    class Meta:
        model = Post
        fields = ('id', 'author', 'entry', 'file', 'created_at')
        
        
    def get_author(self, obj):
        author = Profile.objects.filter(pk=obj.author.pk).first()
        serializer = PostProfileSerializer(author)
        return serializer.data
    

