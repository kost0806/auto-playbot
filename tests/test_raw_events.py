import pytest
import time
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from config import Config

@pytest.fixture
def slack_config():
    return Config()

@pytest.mark.integration
def test_socket_mode_connection(slack_config):
    """Socket Mode 연결 테스트"""
    web_client = WebClient(token=slack_config['slack']['bot_token'])
    socket_client = SocketModeClient(
        app_token=slack_config['slack']['app_token'],
        web_client=web_client
    )

    connected = False
    try:
        socket_client.connect()
        # 연결 확인을 위해 잠시 대기
        time.sleep(2)
        assert socket_client.is_connected() is True
        connected = True
    finally:
        socket_client.close()

if __name__ == "__main__":
    # 스크립트로 직접 실행할 때의 기존 동작 (이벤트 수신 대기) 유지
    config = Config()
    web_client = WebClient(token=config['slack']['bot_token'])
    socket_client = SocketModeClient(
        app_token=config['slack']['app_token'],
        web_client=web_client
    )

    def handle_all(client, req):
        print(f"이벤트 수신: {req.type}")
        from slack_sdk.socket_mode.response import SocketModeResponse
        client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))

    socket_client.socket_mode_request_listeners.append(handle_all)
    socket_client.connect()
    print("Socket Mode 연결됨. 이벤트를 기다리는 중... (Ctrl+C로 종료)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        socket_client.close()
