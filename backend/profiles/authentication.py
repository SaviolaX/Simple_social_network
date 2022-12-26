from django.contrib.auth import login, logout

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import AuthenticationFailed

from .models import Profile
from .serializers import RegisterProfileSerializer, LoginProfileSerializer
from .permissions import IsNotAuthenticated


class RegisterView(CreateAPIView):
    """ Create a new user """
    queryset = Profile.objects.all()
    serializer_class = RegisterProfileSerializer
    permission_classes = (AllowAny, )


class LoginView(APIView):
    """ Login user """
    serializer_class = LoginProfileSerializer
    permission_classes = (IsNotAuthenticated, )

    def post(self, request):
        if request.data == {}:
            raise ValidationError({'error': 'required email and password'})
        else:
            # get data from request
            email = request.data['email']
            password = request.data['password']

            # check if fields are not empty
            if email == '':
                raise ValidationError({'error': 'email is required'})

            if password == '':
                raise ValidationError({'error': 'password is required'})

            # check if user with this email exists in db
            user = Profile.objects.filter(email=email).first()

            if user is None:
                raise AuthenticationFailed('User not found!')

            # compare hashed passwords
            if not user.check_password(password):
                raise AuthenticationFailed('Incorrect password!')

            login(request, user=user)
            return Response({'success': 'logged in'})


class LogoutView(APIView):
    """ Logout user """
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        logout(request)
        return Response({'message': 'logged out'}, status=status.HTTP_200_OK)
