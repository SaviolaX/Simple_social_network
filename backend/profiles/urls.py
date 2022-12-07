from django.urls import path

from .authentication import Register

urlpatterns = [
    path('register/', Register.as_view(), name='register'),
]