from django.urls import path

from .views import (FriendsPostsListView, PostCreateView, PostDetailView, PostUpdateView)

urlpatterns = [
    path('', FriendsPostsListView.as_view(), name='posts_list'),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('<str:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('<str:pk>/update', PostUpdateView.as_view(), name='post_update'),
]