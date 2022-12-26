from django.urls import reverse, resolve

from comments.views import (
    CommentCreateView, )


def test_create_comment_url():
    assert resolve(reverse('comment_create',
                           kwargs={'post_pk':
                                   1})).func.view_class == CommentCreateView
