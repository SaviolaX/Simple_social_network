import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from profiles.models import Profile

client = APIClient()


@pytest.fixture
def user_payload() -> dict:
    payload = dict(email='test_user@email.com',
                   password='test_pass',
                   confirm_password='test_pass')
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
    assert res.data['message'] == 'You are not logged in'
    assert res.status_code == 400
