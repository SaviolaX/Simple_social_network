from django.urls import path

from .authentication import RegisterView, LoginView, LogoutView
from .views import ProfileDetailView, ProfileUpdateView

urlpatterns = [
    # auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # views
    path('<str:pk>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('<str:pk>/update', ProfileUpdateView.as_view(), name='profile_update'),
]