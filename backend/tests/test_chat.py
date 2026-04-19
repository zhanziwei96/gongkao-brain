import pytest
from unittest.mock import patch


@pytest.fixture
def auth_headers(client):
    client.post("/api/auth/register", json={
        "username": "chatuser",
        "email": "chat@example.com",
        "password": "pass123"
    })
    response = client.post("/api/auth/login", json={
        "username": "chatuser",
        "password": "pass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_chat_stream(client, auth_headers):
    mock_chunks = [
        '{"delta": "Hello", "done": false}',
        '{"delta": " world", "done": false}',
        '{"delta": "", "done": true}'
    ]

    async def mock_generator(*args, **kwargs):
        for chunk in mock_chunks:
            yield chunk

    with patch("app.routers.chat.stream_claude_response", side_effect=mock_generator):
        response = client.post("/api/chat/stream", json={
            "messages": [{"role": "user", "content": "Hi"}],
            "context": {"page": "dashboard"}
        }, headers=auth_headers)

        assert response.status_code == 200
        content = response.text
        assert "data:" in content
        assert "Hello" in content
