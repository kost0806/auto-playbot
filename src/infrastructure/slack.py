"""Slack 통합"""
import threading
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse


class SlackBot:
    """Slack Bot - 명령 수신 + 알림 전송"""

    def __init__(self, bot_token: str, app_token: str, channel: str):
        self.client = WebClient(token=bot_token)
        self.socket_client = SocketModeClient(
            app_token=app_token,
            web_client=self.client
        )
        self.channel = channel
        self.command_handler = None
        self._running = False

    def set_command_handler(self, handler):
        """명령 핸들러 등록"""
        self.command_handler = handler

    def start(self):
        """Slack 연결 시작"""
        self.socket_client.socket_mode_request_listeners.append(
            self._handle_message
        )
        self._running = True
        threading.Thread(
            target=self.socket_client.connect,
            daemon=True
        ).start()
        print("Slack bot connected.")

    def stop(self):
        """Slack 연결 종료"""
        self._running = False
        self.socket_client.close()

    def _handle_message(self, client: SocketModeClient,
                       req: SocketModeRequest):
        """메시지 처리"""
        if req.type == "events_api":
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)

            event = req.payload.get("event", {})

            # 봇 자신의 메시지 무시 (bot_id 또는 bot_profile 확인)
            if event.get("bot_id") or event.get("bot_profile"):
                return

            # 메시지 타입 확인
            if event.get("type") != "message":
                return

            # 채널 확인 (설정된 채널에서만 명령 수신)
            event_channel = event.get("channel", "")
            if event_channel != self.channel:
                return

            # subtype이 없거나 특정 subtype만 허용
            # None: 일반 메시지, message_replied: 스레드 답글
            allowed_subtypes = [None, "thread_broadcast"]
            subtype = event.get("subtype")
            if subtype not in allowed_subtypes:
                return

            text = event.get("text", "").strip()

            if text.startswith("!"):
                if self.command_handler:
                    threading.Thread(
                        target=self.command_handler,
                        args=(text,),
                        daemon=True
                    ).start()

    def send_message(self, text: str):
        """Slack 메시지 전송"""
        try:
            self.client.chat_postMessage(
                channel=self.channel,
                text=text
            )
        except Exception as e:
            print(f"Slack 전송 실패: {e}")

    def notify_success(self, from_level: int, to_level: int,
                      gold: int):
        """강화 성공 알림"""
        self.send_message(
            f"✅ *강화 성공* [+{from_level}] → [+{to_level}]\n"
            f"💰 골드: {gold:,}G"
        )

    def notify_failure(self, from_level: int, new_weapon: str):
        """강화 파괴 알림"""
        self.send_message(
            f"❌ *강화 파괴* [+{from_level}] → [+0]\n"
            f"⚔️ 새 무기: {new_weapon}"
        )

    def notify_sell(self, gold_gained: int, total_gold: int):
        """판매 알림"""
        self.send_message(
            f"💰 *판매 완료* +{gold_gained:,}G\n"
            f"💵 총 골드: {total_gold:,}G"
        )

    def notify_status(self, state):
        """상태 조회 응답"""
        self.send_message(
            f"📊 *현재 상태*\n"
            f"⚔️ 무기: [+{state.weapon.level}] {state.weapon.name}\n"
            f"💰 골드: {state.gold:,}G\n"
            f"🔸 특수: {'예' if state.weapon.is_special else '아니오'}\n"
            f"🤖 상태: {state.bot_state.value}"
        )
