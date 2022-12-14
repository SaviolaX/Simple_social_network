from django.urls import path

from .authentication import RegisterView, LoginView, LogoutView
from .views import (ProfileDetailView, ProfileUpdateView, 
                    FriendRequestCreateView, FriendRequestAcceptView, 
                    FriendRequestRefuseView, RemoveFriendView)

urlpatterns = [
    # profile auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # profile detail/update
    path('<str:pk>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('<str:pk>/update/', ProfileUpdateView.as_view(), name='profile_update'),
    
    # profile friend request
    path('<str:sender_pk>/send_friend_request/<str:receiver_pk>/', FriendRequestCreateView.as_view(), name='send_friend_request'),

    # accept/refuse request
    path('<str:user_pk>/accept/<str:f_req_pk>/', FriendRequestAcceptView.as_view(), name='accept_friend_request'),
    path('<str:user_pk>/refuse/<str:f_req_pk>/', FriendRequestRefuseView.as_view(), name='refuse_friend_request'),
    
    # remove from friends list
    path('<str:user_pk>/remove/<str:friend_pk>/', RemoveFriendView.as_view(), name='remove_friend'),
    
]