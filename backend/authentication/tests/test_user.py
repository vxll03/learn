import re

import pytest
import pytest_asyncio
from unittest.mock import ANY


@pytest_asyncio.fixture
async def create_valid_user(client):
    async def _create_user(username='user', password='password_123'):
        response = await client.post(
            '/users/',
            json={
                'username': username,
                'password': password,
                'password_retry': password,
            },
        )
        assert response.status_code == 201
        return response.json()

    return _create_user


###############################################################


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'username, password, password_retry, is_valid',
    [
        ('user', 'password_123', 'password_123', True),
        ('SUPERUSER', 'PASSWORDDD', 'PASSWORDDD', True),
        ('use', 'password_123', 'password_123', False),
        ('USERUSER', 'USERUSER', 'USERUSER', False),
        ('user', 'pas', 'pas', False),
        ('user' * 100, 'password1', 'password1', False),
        ('user', 'pas' * 100, 'pas' * 100, False),
    ],
    ids=[
        'valid_user1',
        'valid_user2',
        'short_username',
        'incorrect_creds',
        'short_password',
        'long_username',
        'long_password',
    ],
)
async def test_create_user(client, username, password, password_retry, is_valid):
    response = await client.post(
        '/users/',
        json={
            'username': username,
            'password': password,
            'password_retry': password_retry,
        },
    )

    if is_valid:
        assert response.status_code == 201
        data = response.json()
        assert data == {
            'id': ANY,
            'username': username,
            'email': ANY,
        }
        if data.get('email') is not None:
            assert re.match(r'[^@]+@[^@]{2,10}\.[^@]{1,4}$', data.get('email')) is not None
    else:
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'username, email, password, password_retry, is_valid',
    [
        ('user_new', None, None, None, True),
        (None, 'email@new.ru', None, None, True),
        (None, None, 'new_password', 'new_password', True),
        ('use', None, None, None, False),
        ('u' * 100, None, None, None, False),
        (None, 'email2.ru', None, None, False),
        (None, None, 'new_passwor', 'new_password', False),
        (None, None, 'new', 'new', False),
        (None, None, 'n' * 100, 'n' * 100, False),
    ],
    ids=[
        'correct_username',
        'correct_email',
        'correct_password',
        'short_username',
        'long_username',
        'invalid_email',
        'different_passwords',
        'short_passwords',
        'long_passwords',
    ],
)
async def test_update_user(client, create_valid_user, username, email, password, password_retry, is_valid):
    user = await create_valid_user()
    response = await client.patch(
        f'/users/{user["id"]}/',
        json={
            'username': username,
            'email': email,
            'password': password,
            'password_retry': password_retry,
        },
    )
    if is_valid:
        assert response.status_code == 200
        data = response.json()
        assert data == {
            'id': ANY,
            'username': username if username else ANY,
            'email': email if email else ANY,
        }
    else:
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
@pytest.mark.parametrize('user_id, is_valid', [(1, True), (2398, False)], ids=['valid_id', 'invalid_id'])
async def test_get_user_by_id(client, create_valid_user, user_id, is_valid):
    user = await create_valid_user()
    response = await client.get(f'/users/{user_id}/')
    if is_valid:
        assert response.status_code == 200
        data = response.json()
        assert 'username' in data
    else:
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize('user_id, is_valid', [(1, True), (2398, False)], ids=['valid_id', 'invalid_id'])
async def test_deactivate_user(client, create_valid_user, user_id, is_valid):
    user = await create_valid_user()
    response = await client.delete(f'/users/{user_id}/')
    if is_valid:
        assert response.status_code == 200
        assert response.text == 'true'
    else:
        assert response.status_code == 404