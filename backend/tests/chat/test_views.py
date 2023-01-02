import pytest
import sys, shutil, os
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient

from profiles.models import Profile
from chat.models import Room, Message

client = APIClient()


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


@pytest.mark.django_db
def test_room_create_not_logged_in(user_object: Profile, user_object2: Profile) -> None:
    data = dict(initiator=user_object.pk, receiver=user_object2.pk)
    res = client.post(reverse('create_room'), data, format='json')
    assert res.data[
        'detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403
    
@pytest.mark.django_db
def test_room_create_logged_in(user_object: Profile, user_object2: Profile, user_payload: dict) -> None:
    client.post(reverse('login'), user_payload, format='json')
    data = dict(initiator=user_object.pk, receiver=user_object2.pk)
    res = client.post(reverse('create_room'), data, format='json')
    assert res.data['id'] == 1
    assert res.data['initiator'] == data['initiator']
    assert res.data['receiver'] == data['receiver']


@pytest.mark.django_db
def test_rooms_list_not_logged_in(user_object: Profile, user_object2: Profile) -> None:
    res = client.get(reverse('my_rooms'))
    assert res.data[
        'detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403
    
@pytest.mark.django_db
def test_rooms_list_logged_in(user_object: Profile, user_object2: Profile, user_payload: dict) -> None:
    client.post(reverse('login'), user_payload, format='json')
    res = client.get(reverse('my_rooms'))
    assert res.data == list()
    assert res.status_code == 200
    
@pytest.mark.django_db
def test_chat_room_not_logged_in(user_object: Profile, user_object2: Profile) -> None:
    room = Room.objects.create(initiator=user_object, receiver=user_object2)
    res = client.get(reverse('chat_room', kwargs={'pk': room.pk}))
    assert res.data[
        'detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403
    
@pytest.mark.django_db
def test_chat_room_logged_in(user_object: Profile, user_object2: Profile, user_payload: dict) -> None:
    client.post(reverse('login'), user_payload, format='json')
    room = Room.objects.create(initiator=user_object, receiver=user_object2)
    res = client.get(reverse('chat_room', kwargs={'pk': room.pk}))
    assert res.data['id'] == room.id
    assert res.data['initiator']['id'] == user_object.id 
    assert res.data['receiver']['id'] == user_object2.id 
    assert res.status_code == 200
    
    
@pytest.mark.django_db
def test_delete_chat_room_not_logged_in(user_object: Profile, user_object2: Profile) -> None:
    room = Room.objects.create(initiator=user_object, receiver=user_object2)
    res = client.delete(reverse('del_room', kwargs={'pk': room.pk}))
    assert res.data[
        'detail'] == 'Authentication credentials were not provided.'
    assert res.status_code == 403
    
@pytest.mark.django_db
def test_delete_chat_room_logged_in(user_object: Profile, user_object2: Profile, user_payload: dict) -> None:
    client.post(reverse('login'), user_payload, format='json')
    room = Room.objects.create(initiator=user_object, receiver=user_object2)
    res = client.delete(reverse('del_room', kwargs={'pk': room.pk}))
    assert res.status_code == 204
