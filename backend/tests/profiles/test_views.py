import pytest
import sys, shutil, os
from django.conf import settings
from io import BytesIO 
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient

from profiles.models import Profile

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
    payload = dict(email='test_user@email.com',
                   password='test_pass',
                   confirm_password='test_pass')
    return payload

@pytest.fixture
def user2_payload() -> dict:
    payload = dict(email='test_user2@email.com',
                   password='test_pass2',
                   confirm_password='test_pass2')
    return payload


# register view
@pytest.mark.django_db
def test_register_with_data(user_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    res = client.post(reverse('register'), user_payload, format='json')
    assert len(Profile.objects.all()) == 1
    assert res.data['email'] == user_payload['email']
    assert res.data['id'] == 1
    assert res.status_code == 201


@pytest.mark.django_db
def test_register_with_no_data() -> None:
    assert len(Profile.objects.all()) == 0
    res = client.post(reverse('register'), format='json')
    assert res.data['email'][0] == 'This field is required.'
    assert res.data['password'][0] == 'This field is required.'
    assert res.data['confirm_password'][0] == 'This field is required.'
    assert res.status_code == 400


@pytest.mark.django_db
def test_register_with_wrong_email_format(user_payload: dict) -> None:
    # make wrong email format
    user_payload['email'] = 'test_useremail.com'
    res = client.post(reverse('register'), user_payload, format='json')
    assert res.data['error'][0] == 'Invalid email format'
    assert res.status_code == 400


@pytest.mark.django_db
def test_register_with_passwords_dont_match(user_payload: dict) -> None:
    # make wrong confirm password
    user_payload['confirm_password'] = 'test_pass1'
    res = client.post(reverse('register'), user_payload, format='json')
    assert res.data['error'][0] == 'Passwords do not match'
    assert res.status_code == 400


@pytest.mark.django_db
def test_register_with_too_short_password(user_payload: dict) -> None:
    # make wrong email format
    user_payload['password'] = '123'
    user_payload['confirm_password'] = '123'
    res = client.post(reverse('register'), user_payload, format='json')
    assert res.data['error'][
        0] == 'Password is too short. It has to be min 6 char'
    assert res.status_code == 400


@pytest.mark.django_db
def test_register_if_user_already_exists(user_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    res = client.post(reverse('register'), user_payload, format='json')
    assert len(Profile.objects.all()) == 1
    new_user = dict(email='test_user@email.com',
                    password='test_pass',
                    confirm_password='test_pass')
    res = client.post(reverse('register'), new_user, format='json')
    assert res.data['error'][0] == 'User with this email already exists'
    assert res.status_code == 400
    
# login view
@pytest.mark.django_db
def test_login_with_data(user_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    client.post(reverse('register'), user_payload, format='json')
    assert len(Profile.objects.all()) == 1
    created_user = dict(email=user_payload['email'], password=user_payload['password'])
    res = client.post(reverse('login'), created_user, format='json')
    assert res.data['success'] == 'logged in'
    assert res.status_code == 200

@pytest.mark.django_db
def test_login_with_no_data() -> None:
    res = client.post(reverse('login'), format='json')
    assert res.data['error'] == 'required email and password'
    assert res.status_code == 400

@pytest.mark.django_db
def test_login_with_no_email() -> None:
    payload = dict(password='test_pass', email='')
    res = client.post(reverse('login'), payload, format='json')
    assert res.data['error'] == 'email is required'
    assert res.status_code == 400


@pytest.mark.django_db
def test_login_with_no_password() -> None:
    payload = dict(email='test_user@mail.com', password='')
    res = client.post(reverse('login'), payload, format='json')
    assert res.data['error'] == 'password is required'
    assert res.status_code == 400
    
@pytest.mark.django_db
def test_login_if_user_is_authenticated(user_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    client.post(reverse('register'), user_payload, format='json')
    assert len(Profile.objects.all()) == 1
    created_user = dict(email=user_payload['email'], password=user_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    res = client.post(reverse('login'), created_user, format='json')
    assert res.data['detail'] == 'You do not have permission to perform this action.'
    assert res.status_code == 403
    
# logout view
@pytest.mark.django_db
def test_logout_if_user_logged_in(user_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    client.post(reverse('register'), user_payload, format='json')
    assert len(Profile.objects.all()) == 1
    created_user = dict(email=user_payload['email'], password=user_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    res = client.get(reverse('logout'))
    assert res.data['message'] == 'logged out'
    assert res.status_code == 200
    
@pytest.mark.django_db
def test_logout_if_user_not_logged_in() -> None:
    res = client.get(reverse('logout'))
    assert res.data['detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403
    
# detail view
@pytest.mark.django_db
def test_detail_view_not_logged_in() -> None:
    res = client.get(reverse('profile_detail', kwargs={'pk': 1}))
    assert res.data['detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403
    
@pytest.mark.django_db
def test_detail_logged_in(user_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    client.post(reverse('register'), user_payload, format='json')
    assert len(Profile.objects.all()) == 1
    created_user = dict(email=user_payload['email'], password=user_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    res = client.get(reverse('profile_detail', kwargs={'pk': 1}))
    assert res.data['id'] == 1
    assert res.data['email'] == user_payload['email']
    assert res.data['username'] == user_payload['email'].split('@')[0]

@pytest.mark.django_db
def test_detail_another_user_profile_logged_in(user_payload: dict, user2_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    client.post(reverse('register'), user_payload, format='json')
    client.post(reverse('register'), user2_payload, format='json')
    assert len(Profile.objects.all()) == 2
    created_user = dict(email=user2_payload['email'], password=user2_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    res = client.get(reverse('profile_detail', kwargs={'pk': 1}))
    assert res.data['id'] == 1
    assert res.data['email'] == user_payload['email']
    assert res.data['username'] == user_payload['email'].split('@')[0]

# update view
# put request
@pytest.mark.django_db
def test_update_view_not_logged_in_put_req() -> None:
    res = client.put(reverse('profile_update', kwargs={'pk': 1}))
    assert res.data['detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403

# patch request
@pytest.mark.django_db
def test_update_view_not_logged_in_patch_req() -> None:
    res = client.patch(reverse('profile_update', kwargs={'pk': 1}))
    assert res.data['detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403

# get request
@pytest.mark.django_db
def test_update_view_not_logged_in_get_req() -> None:
    res = client.get(reverse('profile_update', kwargs={'pk': 1}))
    assert res.data['detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403
    
@pytest.mark.django_db
def test_update_view_logged_in_as_owner_put_request(user_payload: dict, temporary_image: bytes) -> None:
    assert len(Profile.objects.all()) == 0
    client.post(reverse('register'), user_payload, format='json')
    assert len(Profile.objects.all()) == 1
    created_user = dict(email=user_payload['email'], password=user_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    get_res = client.get(reverse('profile_update', kwargs={'pk': 1}))
    assert get_res.data['id'] == 1
    assert get_res.data['email'] == user_payload['email']
    assert get_res.data['username'] == user_payload['email'].split('@')[0]
    assert get_res.data['image'] == None
    update_profile = dict(
        email=user_payload['email'],
        username=user_payload['email'].split('@')[0],
        image=temporary_image
    )
    put_res = client.put(reverse('profile_update', kwargs={'pk': 1}), update_profile, format='multipart')
    assert put_res.data['id'] == 1
    assert put_res.data['email'] == user_payload['email']
    assert put_res.data['username'] == user_payload['email'].split('@')[0]
    assert put_res.data['image'] != None
    delete_all_testing_files(user_payload['email'])
    

@pytest.mark.django_db
def test_update_view_logged_in_as_owner_patch_request(user_payload: dict, temporary_image: bytes) -> None:
    assert len(Profile.objects.all()) == 0
    client.post(reverse('register'), user_payload, format='json')
    assert len(Profile.objects.all()) == 1
    created_user = dict(email=user_payload['email'], password=user_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    get_res = client.get(reverse('profile_update', kwargs={'pk': 1}))
    assert get_res.data['id'] == 1
    assert get_res.data['email'] == user_payload['email']
    assert get_res.data['username'] == user_payload['email'].split('@')[0]
    assert get_res.data['image'] == None
    update_profile = dict(
        image=temporary_image
    )
    put_res = client.patch(reverse('profile_update', kwargs={'pk': 1}), update_profile, format='multipart')
    assert put_res.data['id'] == 1
    assert put_res.data['email'] == user_payload['email']
    assert put_res.data['username'] == user_payload['email'].split('@')[0]
    assert put_res.data['image'] != None
    delete_all_testing_files(user_payload['email']) 
    

def delete_all_testing_files(profile_email: str) -> None:
    """Delete test files from media"""
    try:
        path_to_profile_images = os.path.join(settings.MEDIA_ROOT, f'profile\\{profile_email}')
        shutil.rmtree(path_to_profile_images, ignore_errors=True)
    except OSError:
        pass

