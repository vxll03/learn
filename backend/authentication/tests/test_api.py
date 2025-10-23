import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get('/check/')
    print(response.text)
    assert response.status_code == 200
    assert response.text == 'success'
