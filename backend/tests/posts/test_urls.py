from django.urls import reverse, resolve

from posts.views import (FriendsPostsListView, PostCreateView, PostUpdateView,
                         PostDetailView, LikePostView, DislikePostView)


def test_post_list_url():
    assert resolve(
        reverse('posts_list')).func.view_class == FriendsPostsListView


def test_post_create_url():
    assert resolve(reverse('post_create')).func.view_class == PostCreateView


def test_post_update_url():
    assert resolve(reverse('post_update',
                           kwargs={'pk': 1})).func.view_class == PostUpdateView


def test_post_detail_url():
    assert resolve(reverse('post_detail',
                           kwargs={'pk': 1})).func.view_class == PostDetailView


def test_like_post_url():
    assert resolve(reverse('post_like',
                           kwargs={'pk': 1})).func.view_class == LikePostView


def test_dislike_post_url():
    assert resolve(reverse('post_dislike',
                           kwargs={'pk':
                                   1})).func.view_class == DislikePostView
