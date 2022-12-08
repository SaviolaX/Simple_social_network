from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from .models import Profile
from .serializers import ProfileSerializer, RegisterProfileSerializer


class Register(CreateAPIView):
    """ Create a new user """
    queryset = Profile.objects.all()
    serializer_class = RegisterProfileSerializer
    permission_classes = (AllowAny, )

