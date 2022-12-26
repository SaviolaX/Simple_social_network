import pytest
import sys, shutil, os
from django.conf import settings
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient

from profiles.models import Profile
from posts.models import Post
from comments.models import Comment

client = APIClient()


@pytest.fixture
def temporary_image() -> bytes:
    io = BytesIO()
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGB", size, color)
    image.save(io, format='JPEG')
    image_file = InMemoryUploadedFile(io, None, 'foo.jpg', 'jpeg',
                                      sys.getsizeof(io), None)
    image_file.seek(0)
    return image_file


@pytest.fixture
def user_payload() -> dict:
    payload = dict(email='test_email@email.com', password='test_pass')
    return payload


@pytest.fixture
def user_object() -> dict:
    new_user = Profile.objects.create_user(email='test_email@email.com',
                                           username='test_user',
                                           password='test_pass')
    return new_user


@pytest.fixture
def user_object2() -> dict:
    new_user = Profile.objects.create_user(email='test_email2@email.com',
                                           username='test_user2',
                                           password='test_pass2')
    return new_user


@pytest.fixture
def user_object3() -> dict:
    new_user = Profile.objects.create_user(email='test_email3@email.com',
                                           username='test_user3',
                                           password='test_pass3')
    return new_user


@pytest.fixture
def post_object(user_object: object, temporary_image: bytes) -> dict:
    post = Post.objects.create(author=user_object,
                               file=temporary_image,
                               entry='test_entry')

    return post


@pytest.mark.django_db
def test_comment_create_not_logged_in(user_object: object,
                                      post_object: object) -> None:
    assert Post.objects.all().count() == 1
    res = client.post(
        reverse('comment_create', kwargs={'post_pk': post_object.pk}))
    assert res.data[
        'detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403
    delete_all_testing_files(str(user_object.email))


@pytest.mark.django_db
def test_comment_create_logged_in_with_data(user_object: object,
                                            post_object: object,
                                            user_payload: dict) -> None:
    client.post(reverse('login'), user_payload, format='json')
    assert Post.objects.all().count() == 1
    assert Comment.objects.filter(post=post_object).count() == 0
    payload = dict(entry='Test comment entry')
    res = client.post(reverse('comment_create',
                              kwargs={'post_pk': post_object.pk}),
                      payload,
                      format='json')
    assert Comment.objects.filter(post=post_object).count() == 1
    assert res.data['id'] == 1
    assert res.data['entry'] == payload['entry']
    assert res.status_code == 201
    delete_all_testing_files(user_payload['email'])


@pytest.mark.django_db
def test_comment_create_logged_in_no_data(user_object: object,
                                          post_object: object,
                                          user_payload: dict) -> None:
    client.post(reverse('login'), user_payload, format='json')
    assert Post.objects.all().count() == 1
    assert Comment.objects.filter(post=post_object).count() == 0
    res = client.post(reverse('comment_create',
                              kwargs={'post_pk': post_object.pk}),
                      format='json')
    assert res.data['entry'][0] == 'This field is required.'
    assert res.status_code == 400
    delete_all_testing_files(str(user_object.email))


def delete_all_testing_files(profile_email: str) -> None:
    """Delete test files from media"""
    try:
        path_to_profile_images = os.path.join(settings.MEDIA_ROOT,
                                              f'profile\\{profile_email}')
        shutil.rmtree(path_to_profile_images, ignore_errors=True)
    except OSError:
        pass