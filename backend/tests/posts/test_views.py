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

client = APIClient()


@pytest.fixture
def temporary_image() -> bytes:
    io = BytesIO()
    size = (200,200)
    color = (255,0,0,0)
    image = Image.new("RGB", size, color)
    image.save(io, format='JPEG')
    image_file = InMemoryUploadedFile(io, None, 'foo.jpg', 'jpeg', sys.getsizeof(io), None)
    image_file.seek(0)
    return image_file


@pytest.fixture
def user_payload() -> dict:
    payload = dict(
        email='test_email@email.com',
        password='test_pass'
    )
    return payload

@pytest.fixture
def user_object() -> dict:
    new_user = Profile.objects.create_user(
        email='test_email@email.com',
        username='test_user',
        password='test_pass'
    )
    return new_user

@pytest.fixture
def user_object2() -> dict:
    new_user = Profile.objects.create_user(
        email='test_email2@email.com',
        username='test_user2',
        password='test_pass2'
    )
    return new_user

@pytest.fixture
def user_object3() -> dict:
    new_user = Profile.objects.create_user(
        email='test_email3@email.com',
        username='test_user3',
        password='test_pass3'
    )
    return new_user


# friends post list
@pytest.mark.django_db
def test_post_list_not_logged_in(user_object: object, temporary_image: bytes) -> None:
    Post.objects.create(author=user_object, file=temporary_image, entry='test_entry')
    res = client.get(reverse('posts_list'))
    assert res.data['detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403

@pytest.mark.django_db
def test_friends_posts_list_logged_in(user_object: object, 
                                      user_payload: dict, 
                                      temporary_image: bytes, 
                                      user_object2: object, 
                                      user_object3: object) -> None:
    assert Post.objects.all().count() == 0
    Post.objects.create(author=user_object2, file=temporary_image, entry='test_entry2')
    Post.objects.create(author=user_object3, file=temporary_image, entry='test_entry3')
    assert Post.objects.all().count() == 2
    user_object.friends.add(user_object2)
    user_object2.friends.add(user_object)
    client.post(reverse('login'), user_payload, format='json')
    res = client.get(reverse('posts_list'))
    assert len(res.data) == 1
    assert res.data[0]['id'] == 1
    assert res.data[0]['author']['id'] == user_object2.id
    assert res.data[0]['author']['email'] == 'test_email2@email.com'
    assert res.data[0]['author']['username'] == 'test_user2'
    assert res.data[0]['author']['image'] == None
    assert res.data[0]['entry'] == 'test_entry2'
    assert res.data[0]['file'] != None
    assert res.status_code == 200
    delete_all_testing_files(str(user_object.email))
    delete_all_testing_files(str(user_object2.email))
    delete_all_testing_files(str(user_object3.email))
    
    

# create post   
@pytest.mark.django_db
def test_post_create_not_logged_in(user_object: object, temporary_image: bytes) -> None:
    assert Post.objects.all().count() == 0
    Post.objects.create(author=user_object, file=temporary_image, entry='test_entry')
    assert Post.objects.all().count() == 1
    res = client.post(reverse('post_create'))
    assert res.data['detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403
    delete_all_testing_files(str(user_object.email))
    
    
    
@pytest.mark.django_db
def test_post_create_logged_in_with_data(user_object: object, temporary_image: bytes, user_payload: dict) -> None:
    new_post_payload = dict(author=user_object, file=temporary_image, entry='test_entry')
    client.post(reverse('login'), user_payload, format='json')
    assert Post.objects.all().count() == 0
    res = client.post(reverse('post_create'), new_post_payload, format='multipart')
    assert Post.objects.all().count() == 1
    assert res.data['id'] == 1
    assert Post.objects.get(id=1).author.id == user_object.id
    assert Post.objects.get(id=1).author.email == user_object.email
    assert Post.objects.get(id=1).author.username == user_object.username
    assert res.data['entry'] == 'test_entry'
    assert res.data['file'] != None
    assert res.status_code == 201
    delete_all_testing_files(user_payload['email'])
    
@pytest.mark.django_db
def test_post_create_logged_in_no_data(user_object: object, user_payload: dict) -> None:
    empty_data = dict(entry='', file='')
    client.post(reverse('login'), user_payload, format='json')
    assert Post.objects.all().count() == 0
    res = client.post(reverse('post_create'), empty_data, format='multipart')
    assert res.data['message'][0] == 'Fill up "entry" or "file" field to create a post.'
    assert res.status_code == 400
    delete_all_testing_files(str(user_object.email))
    


# post detail
@pytest.mark.django_db
def test_post_detail_not_logged_in(user_object: object, temporary_image: bytes) -> None:
    assert Post.objects.all().count() == 0
    Post.objects.create(author=user_object, file=temporary_image, entry='test_entry')
    assert Post.objects.all().count() == 1
    res = client.get(reverse('post_detail', kwargs={'pk': 1}))
    assert res.data['detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403
    delete_all_testing_files(str(user_object.email))
    
@pytest.mark.django_db
def test_post_detail_logged_in(user_object: object, user_payload: dict, temporary_image: bytes) -> None:
    assert Post.objects.all().count() == 0
    Post.objects.create(author=user_object, file=temporary_image, entry='test_entry')
    assert Post.objects.all().count() == 1
    client.post(reverse('login'), user_payload, format='json')
    
    res = client.get(reverse('post_detail', kwargs={'pk': 1}))
    assert res.data['id'] == 1 
    assert res.data['entry'] == 'test_entry'
    assert res.data['file'] != None
    assert res.status_code == 200
    delete_all_testing_files(str(user_object.email))
    
@pytest.mark.django_db
def test_post_detail_logged_in_not_exist(user_object: object, user_payload: dict, temporary_image: bytes) -> None:
    assert Post.objects.all().count() == 0
    Post.objects.create(author=user_object, file=temporary_image, entry='test_entry')
    assert Post.objects.all().count() == 1
    client.post(reverse('login'), user_payload, format='json')
    
    res = client.get(reverse('post_detail', kwargs={'pk': 2}))
    assert res.data['detail'] == 'Not found.'
    assert res.status_code == 404
    delete_all_testing_files(str(user_object.email))
    

# post update   
@pytest.mark.django_db
def test_post_update_not_logged_in(user_object: object, temporary_image: bytes) -> None:
    assert Post.objects.all().count() == 0
    Post.objects.create(author=user_object, file=temporary_image, entry='test_entry')
    assert Post.objects.all().count() == 1
    res = client.put(reverse('post_update', kwargs={'pk': 1}))
    assert res.data['detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403
    delete_all_testing_files(str(user_object.email))
    
@pytest.mark.django_db
def test_post_update_logged_in_with_data_put_method(user_object: object, temporary_image: bytes, user_payload: dict) -> None:
    assert Post.objects.all().count() == 0
    Post.objects.create(author=user_object, file=temporary_image, entry='test_entry')
    assert Post.objects.all().count() == 1
    client.post(reverse('login'), user_payload, format='json')
    payload = dict(entry='new_entry', file='')
    res = client.put(reverse('post_update', kwargs={'pk': 1}), payload, format='multipart')
    assert res.data['id'] == 1
    assert res.data['entry'] == payload['entry']
    assert res.data['file'] == None
    assert res.status_code == 200
    delete_all_testing_files(str(user_object.email))


@pytest.mark.django_db
def test_post_update_logged_in_with_data_patch_method(user_object: object, temporary_image: bytes, user_payload: dict) -> None:
    assert Post.objects.all().count() == 0
    Post.objects.create(author=user_object, file=temporary_image, entry='test_entry')
    assert Post.objects.all().count() == 1
    client.post(reverse('login'), user_payload, format='json')
    payload = dict(entry='new_entry')
    res = client.patch(reverse('post_update', kwargs={'pk': 1}), payload, format='multipart')
    assert res.data['id'] == 1
    assert res.data['entry'] == payload['entry']
    assert res.data['file'] != None
    assert res.status_code == 200
    delete_all_testing_files(str(user_object.email))

@pytest.mark.django_db
def test_post_update_logged_in_not_exist_method_patch(user_object: object, user_payload: dict, temporary_image: bytes) -> None:
    assert Post.objects.all().count() == 0
    Post.objects.create(author=user_object, file=temporary_image, entry='test_entry')
    assert Post.objects.all().count() == 1
    client.post(reverse('login'), user_payload, format='json')
    payload = dict(entry='new_entry')
    res = client.patch(reverse('post_update', kwargs={'pk': 99}), payload, format='multipart')
    assert res.data['detail'] == 'Not found.'
    assert res.status_code == 404
    delete_all_testing_files(str(user_object.email))
    
@pytest.mark.django_db
def test_post_update_logged_in_not_exist_method_put(user_object: object, user_payload: dict, temporary_image: bytes) -> None:
    assert Post.objects.all().count() == 0
    Post.objects.create(author=user_object, file=temporary_image, entry='test_entry')
    assert Post.objects.all().count() == 1
    client.post(reverse('login'), user_payload, format='json')
    payload = dict(entry='new_entry', file='')
    res = client.put(reverse('post_update', kwargs={'pk': 99}), payload, format='multipart')
    assert res.data['detail'] == 'Not found.'
    assert res.status_code == 404
    delete_all_testing_files(str(user_object.email))
    







def delete_all_testing_files(profile_email: str) -> None:
    """Delete test files from media"""
    try:
        path_to_profile_images = os.path.join(settings.MEDIA_ROOT, f'profile\\{profile_email}')
        shutil.rmtree(path_to_profile_images, ignore_errors=True)
    except OSError:
        pass