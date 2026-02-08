import pytest
from slack_sdk import WebClient
from config import Config

@pytest.fixture
def slack_config():
    return Config()

@pytest.mark.integration
def test_slack_connection(slack_config):
    """Slack 연결 및 기본 인증 테스트"""
    bot_token = slack_config['slack']['bot_token']
    channel = slack_config['slack']['channel']

    # 1. Bot Token 테스트
    client = WebClient(token=bot_token)
    auth_response = client.auth_test()
    assert auth_response['ok'] is True
    assert 'user' in auth_response

    # 2. 채널 접근 테스트
    channel_info = client.conversations_info(channel=channel)
    assert channel_info['ok'] is True
    assert channel_info['channel']['id'] == channel

    # 3. 메시지 전송 테스트
    response = client.chat_postMessage(
        channel=channel,
        text="🧪 [Pytest] Slack 연결 테스트 메시지"
    )
    assert response['ok'] is True
