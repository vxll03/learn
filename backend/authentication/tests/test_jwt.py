import pytest
import pytest_asyncio
from tests.test_user import create_valid_user

@pytest_asyncio.fixture
async def create_valid_token(client, create_valid_user):
    async def _create_token():
        response = await client.post(
            '/token/create/',
            json={
                'username': 'user',
                'password': 'password_123',
            },
        )
        return response
    return _create_token

@pytest.mark.asyncio
@pytest.mark.parametrize(
    'username, password, is_valid',
    [
        ('user', 'password_123', True),
        ('user', 'password_', False),
    ]
)
async def test_create_token(client, create_valid_user, username, password, is_valid):
    await create_valid_user()
    response = await client.post(
        '/token/create/',
        json={
            'username': username,
            'password': password,
        },
    )
    if is_valid:
        assert response.status_code == 204
        assert response.cookies.get('access') is not None
        assert response.cookies.get('refresh') is not None
    else:
        assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'username, password, is_valid',
    [
        ('user', 'password_123', True),
        ('user', 'password_', False),
    ]
)
async def test_refresh_token(client, create_valid_user, create_valid_token, username, password, is_valid):
    await create_valid_user()
    response = await create_valid_token()
    assert response.status_code == 204

    first_access = response.cookies.get('access')
    refresh_token = response.cookies.get('refresh')
    assert first_access is not None

    client.cookies['refresh'] = refresh_token
    client.cookies['access'] = first_access

    response = await client.post('/token/refresh/')
    assert response.status_code == 204

    last_access = response.cookies.get('access')
    assert last_access is not None
    assert first_access != last_access

