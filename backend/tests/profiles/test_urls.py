from django.urls import reverse, resolve

from profiles.authentication import RegisterView, LogoutView, LoginView

def test_register_url():
    assert resolve(reverse('register')).func.view_class == RegisterView

def test_login_url():
    assert resolve(reverse('login')).func.view_class == LoginView
    
def test_logout_url():
    assert resolve(reverse('logout')).func.view_class == LogoutView