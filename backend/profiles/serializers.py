from rest_framework.serializers import ModelSerializer, CharField

from .models import Profile


class ProfileSerializer(ModelSerializer):
    """ Serializer for Profile """
    email = CharField(max_length=255, required=True)
    password = CharField(max_length=255, write_only=True, required=True)
    confirm_password = CharField(max_length=255, write_only=True, required=True)
    class Meta:
        model = Profile
        fields = ('id', 'email', 'password', 'confirm_password')