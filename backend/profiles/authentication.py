from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Profile
from .serializers import ProfileSerializer


class Register(APIView):
    """ User registration view"""
    def post(self, request) -> dict:
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
         
        # check for empty fields
        if email == '':
            return Response({'error':'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        if password == '':
            return Response({'error':'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
        if confirm_password == '':
            return Response({'error':'Confirm password is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        
        # validate email
        splited_email = [x for x in email]
        if '@' not in splited_email:
            return Response({'error':'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)
            
        
        # check password match
        if password != confirm_password:
            return Response({'error':'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        username = email.strip().rsplit('@', 1)[0]
        
        user = Profile.objects.filter(email=email).first()
        
        if user is None:
            new_user = Profile.objects.create_user(
                email=email,
                username=username,
                password=password
            )
            serializer = ProfileSerializer(new_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    
# {
#   "email": "something@email.com",
#   "password": "some_pass",
#   "confirm_password": "some_pass"
# }