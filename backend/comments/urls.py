from django.urls import path

from .views import CommentCreateView

urlpatterns = [
    path('<str:post_pk>/create_comment/', 
         CommentCreateView.as_view(), name='comment_create'),    
]