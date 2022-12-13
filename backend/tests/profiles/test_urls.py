from django.urls import reverse, resolve

from profiles.authentication import RegisterView, LogoutView, LoginView
from profiles.views import ProfileDetailView, ProfileUpdateView, FriendRequestCreateView, FriendRequestAcceptView, FriendRequestRefuseView

def test_register_url():
    assert resolve(reverse('register')).func.view_class == RegisterView

def test_login_url():
    assert resolve(reverse('login')).func.view_class == LoginView
    
def test_logout_url():
    assert resolve(reverse('logout')).func.view_class == LogoutView
    
def test_profile_detail_url():
    assert resolve(reverse('profile_detail', kwargs={'pk': 1})).func.view_class == ProfileDetailView
    
def test_profile_update_url():
    assert resolve(reverse('profile_update', kwargs={'pk': 1})).func.view_class == ProfileUpdateView
    
def test_send_friend_request_url():
    assert resolve(reverse('send_friend_request', kwargs={'sender_pk': 1, 'receiver_pk': 2})).func.view_class == FriendRequestCreateView
    
def test_accept_friend_request_url():
    assert resolve(reverse('accept_friend_request', kwargs={'user_pk': 1, 'f_req_pk': 1})).func.view_class == FriendRequestAcceptView
    
def test_refuse_friend_request_url():
    assert resolve(reverse('refuse_friend_request', kwargs={'user_pk': 1, 'f_req_pk': 1})).func.view_class == FriendRequestRefuseView