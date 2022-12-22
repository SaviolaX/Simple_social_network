from django.urls import path

from .views import (FriendsPostsListView, PostCreateView, PostDetailView, PostUpdateView, PostDeleteView, LikePostView, DislikePostView)

urlpatterns = [
    path('', FriendsPostsListView.as_view(), name='posts_list'),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('<str:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('<str:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('<str:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    
    # likes/dislikes
    path('<str:pk>/like/', LikePostView.as_view(), name='post_like'),
    path('<str:pk>/dislike/', DislikePostView.as_view(), name='post_dislike'),
]