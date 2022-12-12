from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Profile
from .serializers import ProfileSerializer, ProfileUpdateSerializer
from .permissions import IsProfileOwner


class ProfileDetailView(RetrieveAPIView):
    """ Display profile data """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, )
    lookup_field = 'pk'
    
class ProfileUpdateView(UpdateAPIView, RetrieveAPIView):
    """ Display profile data and update one """
    queryset = Profile.objects.all()
    serializer_class = ProfileUpdateSerializer
    permission_classes = (IsAuthenticated, IsProfileOwner, )
    lookup_field = 'pk'
