from django.urls import reverse, resolve

from posts.views import (PostListView, PostCreateView)



def test_post_list_url():
    assert resolve(reverse('posts_list')).func.view_class == PostListView

def test_post_create_url():
    assert resolve(reverse('post_create')).func.view_class == PostCreateView
    