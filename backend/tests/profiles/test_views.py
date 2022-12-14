import pytest
import sys, shutil, os
from django.conf import settings
from io import BytesIO 
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient

from profiles.models import Profile, FriendRequest

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

@pytest.fixture
def user3_payload() -> dict:
    payload = dict(email='test_user3@email.com',
                   password='test_pass3',
                   confirm_password='test_pass3')
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
    

# friend request
@pytest.mark.django_db
def test_friend_request_not_logged_in(user_payload: dict, user2_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    user1 = client.post(reverse('register'), user_payload, format='json')
    user2 = client.post(reverse('register'), user2_payload, format='json')
    assert len(Profile.objects.all()) == 2
    req = client.post(reverse('send_friend_request', kwargs={'sender_pk': user1.data['id'], 'receiver_pk': user2.data['id']}), format='json')
    assert req.data['detail'] == 'Authentication credentials were not provided.'
    assert req.status_code == 403
    
@pytest.mark.django_db
def test_friend_request_already_created_by_user1(user_payload: dict, user2_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    user1 = client.post(reverse('register'), user_payload, format='json')
    user2 = client.post(reverse('register'), user2_payload, format='json')
    assert len(Profile.objects.all()) == 2
    FriendRequest.objects.create(
        sender=Profile.objects.filter(id=user1.data['id']).first(), 
        receiver=Profile.objects.filter(id=user2.data['id']).first()
    )
    created_user = dict(email=user_payload['email'], password=user_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    req_payload = dict(
        sender=user1.data['id'], 
        receiver=user2.data['id']
    )
    req = client.post(reverse('send_friend_request', kwargs={'sender_pk': user1.data['id'], 'receiver_pk': user2.data['id']}), req_payload, format='json')
    assert req.data['message'][0] == 'Request has sent already'
    assert req.status_code == 400
    

@pytest.mark.django_db
def test_friend_request_already_created_by_user2(user_payload: dict, user2_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    user1 = client.post(reverse('register'), user_payload, format='json')
    user2 = client.post(reverse('register'), user2_payload, format='json')
    assert len(Profile.objects.all()) == 2
    FriendRequest.objects.create(
        sender=Profile.objects.filter(id=user1.data['id']).first(), 
        receiver=Profile.objects.filter(id=user2.data['id']).first()
    )
    created_user = dict(email=user2_payload['email'], password=user2_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    req_payload = dict(
        sender=user2.data['id'], 
        receiver=user1.data['id']
    )
    req = client.post(reverse('send_friend_request', kwargs={'sender_pk': user2.data['id'], 'receiver_pk': user1.data['id']}), req_payload, format='json')
    assert req.data['message'][0] == 'The user has sent request to you already'
    assert req.status_code == 400
    
    

@pytest.mark.django_db
def test_friend_request_with_data_logged_in(user_payload: dict, user2_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    user1 = client.post(reverse('register'), user_payload, format='json')
    user2 = client.post(reverse('register'), user2_payload, format='json')
    assert len(Profile.objects.all()) == 2
    created_user = dict(email=user_payload['email'], password=user_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    req_payload = dict(
        sender=user1.data['id'], 
        receiver=user2.data['id']
    )
    req = client.post(reverse('send_friend_request', kwargs={'sender_pk': user1.data['id'], 'receiver_pk': user2.data['id']}), req_payload, format='json')
    assert req.data['id'] == 1
    assert req.data['sender'] == req_payload['sender']
    assert req.data['receiver'] == req_payload['receiver']
    assert req.status_code == 201
    
@pytest.mark.django_db
def test_friend_request_with_no_data_logged_in(user_payload: dict, user2_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    user1 = client.post(reverse('register'), user_payload, format='json')
    user2 = client.post(reverse('register'), user2_payload, format='json')
    assert len(Profile.objects.all()) == 2
    created_user = dict(email=user_payload['email'], password=user_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    req = client.post(reverse('send_friend_request', kwargs={'sender_pk': user1.data['id'], 'receiver_pk': user2.data['id']}), format='json')
    assert req.data['sender'][0] == 'This field is required.'
    assert req.data['receiver'][0] == 'This field is required.'
    assert req.status_code == 400

@pytest.mark.django_db
def test_friend_request_accept_loggen_in_as_receiver(user_payload: dict, user2_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    user1 = client.post(reverse('register'), user_payload, format='json')
    user2 = client.post(reverse('register'), user2_payload, format='json')
    assert len(Profile.objects.all()) == 2
    f_req = FriendRequest.objects.create(
        sender=Profile.objects.get(id=user2.data['id']),
        receiver=Profile.objects.get(id=user1.data['id'])
    )
    assert FriendRequest.objects.all().count() == 1
    created_user = dict(email=user_payload['email'], password=user_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    req = client.get(reverse('accept_friend_request', kwargs={'user_pk': user1.data['id'], 'f_req_pk': f_req.id}), format='json')
    assert req.data['message'] == f'{f_req.sender.username} added to your friend list.'
    assert Profile.objects.get(id=user1.data['id']).friends.count() == 1
    assert Profile.objects.get(id=user2.data['id']).friends.count() == 1
    assert req.status_code == 200
    
@pytest.mark.django_db
def test_friend_request_accept_not_loggen_in(user_payload: dict, user2_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    user1 = client.post(reverse('register'), user_payload, format='json')
    user2 = client.post(reverse('register'), user2_payload, format='json')
    assert len(Profile.objects.all()) == 2
    f_req = FriendRequest.objects.create(
        sender=Profile.objects.get(id=user2.data['id']),
        receiver=Profile.objects.get(id=user1.data['id'])
    )
    assert FriendRequest.objects.all().count() == 1
    req = client.get(reverse('accept_friend_request', kwargs={'user_pk': user1.data['id'], 'f_req_pk': f_req.id}), format='json')
    assert req.data['detail'] == 'Authentication credentials were not provided.'
    assert req.status_code == 403
    
@pytest.mark.django_db
def test_friend_request_accept_loggen_in_not_receiver(user_payload: dict, user2_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    user1 = client.post(reverse('register'), user_payload, format='json')
    user2 = client.post(reverse('register'), user2_payload, format='json')
    assert len(Profile.objects.all()) == 2
    f_req = FriendRequest.objects.create(
        sender=Profile.objects.get(id=user2.data['id']),
        receiver=Profile.objects.get(id=user1.data['id'])
    )
    assert FriendRequest.objects.all().count() == 1
    created_user = dict(email=user2_payload['email'], password=user2_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    req = client.get(reverse('accept_friend_request', kwargs={'user_pk': user1.data['id'], 'f_req_pk': f_req.id}), format='json')
    assert req.data['message'] == 'You can not perform this action.'
    assert req.status_code == 403
    
    
@pytest.mark.django_db
def test_friend_request_refuse_loggen_in_as_receiver(user_payload: dict, user2_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    user1 = client.post(reverse('register'), user_payload, format='json')
    user2 = client.post(reverse('register'), user2_payload, format='json')
    assert len(Profile.objects.all()) == 2
    f_req = FriendRequest.objects.create(
        sender=Profile.objects.get(id=user2.data['id']),
        receiver=Profile.objects.get(id=user1.data['id'])
    )
    assert FriendRequest.objects.all().count() == 1
    created_user = dict(email=user_payload['email'], password=user_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    req = client.get(reverse('refuse_friend_request', kwargs={'user_pk': user1.data['id'], 'f_req_pk': f_req.id}), format='json')
    assert req.data['message'] == 'Friend request was refused.'
    assert req.status_code == 200
    
@pytest.mark.django_db
def test_friend_request_refuse_not_loggen_in(user_payload: dict, user2_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    user1 = client.post(reverse('register'), user_payload, format='json')
    user2 = client.post(reverse('register'), user2_payload, format='json')
    assert len(Profile.objects.all()) == 2
    f_req = FriendRequest.objects.create(
        sender=Profile.objects.get(id=user2.data['id']),
        receiver=Profile.objects.get(id=user1.data['id'])
    )
    assert FriendRequest.objects.all().count() == 1
    req = client.get(reverse('refuse_friend_request', kwargs={'user_pk': user1.data['id'], 'f_req_pk': f_req.id}), format='json')
    assert req.data['detail'] == 'Authentication credentials were not provided.'
    assert req.status_code == 403
    
@pytest.mark.django_db
def test_friend_request_refuse_loggen_in_not_receiver(user_payload: dict, user2_payload: dict) -> None:
    assert len(Profile.objects.all()) == 0
    user1 = client.post(reverse('register'), user_payload, format='json')
    user2 = client.post(reverse('register'), user2_payload, format='json')
    assert len(Profile.objects.all()) == 2
    f_req = FriendRequest.objects.create(
        sender=Profile.objects.get(id=user2.data['id']),
        receiver=Profile.objects.get(id=user1.data['id'])
    )
    assert FriendRequest.objects.all().count() == 1
    created_user = dict(email=user2_payload['email'], password=user2_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    req = client.get(reverse('refuse_friend_request', kwargs={'user_pk': user1.data['id'], 'f_req_pk': f_req.id}), format='json')
    assert req.data['message'] == 'You can not perform this action.'
    assert req.status_code == 403


@pytest.mark.django_db
def test_remove_friend_not_logged_in() -> None:
    res = client.get(reverse('remove_friend', kwargs={'user_pk': 1, 'friend_pk': 2}), format='json')
    assert res.data['detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403
    
@pytest.mark.django_db
def test_remove_friend_logged_in_not_one_of_friends(user_payload:dict, user2_payload:dict, user3_payload:dict) -> None:
    u1 = client.post(reverse('register'), user_payload, format='json')
    u2 = client.post(reverse('register'), user2_payload, format='json')
    u3 = client.post(reverse('register'), user3_payload, format='json')
    user1 = Profile.objects.get(id=u1.data['id'])
    user2 = Profile.objects.get(id=u2.data['id'])
    user1.friends.add(user2)
    user2.friends.add(user1)
    created_user = dict(email=user3_payload['email'], password=user3_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    res = client.get(reverse('remove_friend', kwargs={'user_pk': 1, 'friend_pk': 2}), format='json')
    assert res.data['message'] == 'You can not perform this action.'
    assert res.status_code == 403
    

@pytest.mark.django_db
def test_remove_friend_logged_in_not_profile_owner(user_payload:dict, user2_payload:dict) -> None:
    u1 = client.post(reverse('register'), user_payload, format='json')
    u2 = client.post(reverse('register'), user2_payload, format='json')
    user1 = Profile.objects.get(id=u1.data['id'])
    user2 = Profile.objects.get(id=u2.data['id'])
    user1.friends.add(user2)
    user2.friends.add(user1)
    created_user = dict(email=user2_payload['email'], password=user2_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    res = client.get(reverse('remove_friend', kwargs={'user_pk': 1, 'friend_pk': 2}), format='json')
    assert res.data['message'] == 'You can not perform this action.'
    assert res.status_code == 403
    
    
@pytest.mark.django_db
def test_remove_friend_logged_in_profile_owner(user_payload:dict, user2_payload:dict) -> None:
    u1 = client.post(reverse('register'), user_payload, format='json')
    u2 = client.post(reverse('register'), user2_payload, format='json')
    user1 = Profile.objects.get(id=u1.data['id'])
    user2 = Profile.objects.get(id=u2.data['id'])
    user1.friends.add(user2)
    user2.friends.add(user1)
    assert user1.friends.all().count() == 1
    assert user2.friends.all().count() == 1
    created_user = dict(email=user_payload['email'], password=user_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    res = client.get(reverse('remove_friend', kwargs={'user_pk': user1.pk, 'friend_pk': user2.pk}), format='json')
    assert res.data['message'] == f"{user2.username} was deleted from friends list"
    assert res.status_code == 200


@pytest.mark.django_db
def test_friend_list_not_logged_in(user_payload:dict) -> None:
    client.post(reverse('register'), user_payload, format='json')
    res = client.get(reverse('friends_list', kwargs={'user_pk': 1}), format='json')
    assert res.data['detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403
    

@pytest.mark.django_db
def test_friend_list_logged_in_as_user1(user_payload:dict, user2_payload:dict) -> None:
    u1 = client.post(reverse('register'), user_payload, format='json')
    u2 = client.post(reverse('register'), user2_payload, format='json')
    user1 = Profile.objects.get(id=u1.data['id'])
    user2 = Profile.objects.get(id=u2.data['id'])
    user1.friends.add(user2)
    user2.friends.add(user1)
    assert user1.friends.all().count() == 1
    assert user2.friends.all().count() == 1
    created_user = dict(email=user_payload['email'], password=user_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    res = client.get(reverse('friends_list', kwargs={'user_pk': user1.pk}), format='json')
    assert res.data[0]['email'] == user2.email
    assert res.data[0]['username'] == user2.username
    assert res.data[0]['image'] == None
    assert res.status_code == 200
    
    
@pytest.mark.django_db
def test_friend_list_logged_in_as_user2(user_payload:dict, user2_payload:dict) -> None:
    u1 = client.post(reverse('register'), user_payload, format='json')
    u2 = client.post(reverse('register'), user2_payload, format='json')
    user1 = Profile.objects.get(id=u1.data['id'])
    user2 = Profile.objects.get(id=u2.data['id'])
    user1.friends.add(user2)
    user2.friends.add(user1)
    assert user1.friends.all().count() == 1
    assert user2.friends.all().count() == 1
    created_user = dict(email=user2_payload['email'], password=user2_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    res = client.get(reverse('friends_list', kwargs={'user_pk': user1.pk}), format='json')
    assert res.data[0]['email'] == user2.email
    assert res.data[0]['username'] == user2.username
    assert res.data[0]['image'] == None
    assert res.status_code == 200
    

@pytest.mark.django_db
def test_profiles_list_not_logged_in() -> None:
    res = client.get(reverse('profiles_list'), format='json')
    assert res.data['detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403
    
    
@pytest.mark.django_db
def test_profiles_list_logged_in(user_payload:dict, user2_payload:dict) -> None:
    client.post(reverse('register'), user_payload, format='json')
    client.post(reverse('register'), user2_payload, format='json')
    created_user = dict(email=user_payload['email'], password=user_payload['password'])
    client.post(reverse('login'), created_user, format='json')
    res = client.get(reverse('profiles_list'), format='json')
    assert len(res.data) == Profile.objects.all().count()
    assert res.status_code == 200

    


def delete_all_testing_files(profile_email: str) -> None:
    """Delete test files from media"""
    try:
        path_to_profile_images = os.path.join(settings.MEDIA_ROOT, f'profile\\{profile_email}')
        shutil.rmtree(path_to_profile_images, ignore_errors=True)
    except OSError:
        pass

