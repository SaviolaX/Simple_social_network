from rest_framework.serializers import ModelSerializer, CharField, ValidationError
from rest_framework import status
from rest_framework.response import Response

from .models import Profile


class ProfileSerializer(ModelSerializer):
    """ Serializer for Profile """
    class Meta:
        model = Profile
        fields = ('id', 'email', 'username')
        
class LoginProfileSerializer(ModelSerializer):
    """ Serializer for Profile login """
    email = CharField(max_length=255, required=True)
    password = CharField(max_length=255, write_only=True, required=True)
    class Meta:
        model = Profile
        fields = ('id', 'email', 'password')
    


class RegisterProfileSerializer(ModelSerializer):
    """ Serializer for Profile registration """
    email = CharField(max_length=255, required=True)
    password = CharField(max_length=255, write_only=True, required=True)
    confirm_password = CharField(max_length=255, write_only=True, required=True)
    class Meta:
        model = Profile
        fields = ('id', 'email', 'password', 'confirm_password')
        
    def validate(self, data):
        """ Validate all data from request """
        # check for empty fields
        if data['email'] == '':
            raise ValidationError({'error':'Email is required'})
        if data['password'] == '':
            raise ValidationError({'error':'Password is required'})
        if data['confirm_password'] == '':
            raise ValidationError({'error':'Confirm password is required'})
            
        
        # validate email
        splited_email = [x for x in data['email']]
        if '@' not in splited_email:
            raise ValidationError({'error':'Invalid email format'})
            
        # check for password min length
        if len(data['password']) < 6:
            raise ValidationError({'error':'Password is too short. It has to be min 6 char'})
            
        
        # check password match
        if data['password'] != data['confirm_password']:
            raise ValidationError({'error':'Passwords do not match'})
        
        user = Profile.objects.filter(email=data['email']).first()
        username = data['email'].strip().rsplit('@', 1)[0]
        
        if user is not None:
            raise ValidationError({'error': 'User with this email already exists'})
        
        validated_data = dict(
            email=data['email'],
            username=username,
            password=data['password']
        )
        return validated_data
    
    def create(self, validated_data):
        new_user = Profile.objects.create_user(**validated_data)
        return new_user
            
