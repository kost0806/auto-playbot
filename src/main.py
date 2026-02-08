"""GameBot with Slack Integration"""
import time
from domain.state import GameState, ChatbotState
from domain.strategy.base import MacroMode
from domain.strategy.strategies import (
    SpecialWeaponFarming, SafeFarming, AggressiveFarming
)
from infrastructure.parser import ChatParser
from infrastructure.automation import GameAutomation
from infrastructure.slack import SlackBot
from config import Config


class GameBot:
    """GameBot with Slack"""

    def __init__(self, strategy: MacroMode, parser: ChatParser,
                 automation: GameAutomation, slack: SlackBot,
                 config: Config, interval: float):
        self.strategy = strategy
        self.parser = parser
        self.automation = automation
        self.slack = slack
        self.config = config
        self.interval = interval

        self.state: GameState = None
        self.prev_state: GameState = None
        self.running = False
        self.paused = False

        # Slack 명령 핸들러 등록
        self.slack.set_command_handler(self._handle_slack_command)

    def enforce(self):
        """강화"""
        self.automation.send_command("강화")

    def sell(self):
        """판매"""
        self.automation.send_command("판매")

    def _handle_slack_command(self, command: str):
        """Slack 명령 처리"""
        print(f"[DEBUG] _handle_slack_command called with: '{command}'")
        try:
            parts = command.strip().split()
            cmd = parts[0][1:]  # Remove '!'
            print(f"[DEBUG] Parsed command: '{cmd}', parts: {parts}")

            if cmd == "강화" and len(parts) > 1:
                target = int(parts[1])
                if hasattr(self.strategy, 'config'):
                    self.strategy.config['target_level'] = target
                self.slack.send_message(f"🎯 목표 레벨 +{target}로 설정")
                if self.paused:
                    self.paused = False
                    self.slack.send_message("▶️ 강화 재개")

            elif cmd == "중단":
                self.paused = True
                self.slack.send_message("⏸️ 강화 중단")

            elif cmd == "전략" and len(parts) > 1:
                self._change_strategy(parts[1])

            elif cmd == "상태":
                if self.state:
                    self.slack.notify_status(self.state)
                else:
                    self.slack.send_message("⚠️ 아직 상태 정보 없음")

            elif cmd == "종료":
                self.slack.send_message("👋 봇 종료 중...")
                self.running = False

            else:
                self.slack.send_message(
                    "❓ 사용법:\n"
                    "!강화 [레벨] - 목표 설정\n"
                    "!중단 - 일시 중단\n"
                    "!전략 [이름] - 전략 변경\n"
                    "!상태 - 상태 조회\n"
                    "!종료 - 봇 종료"
                )

        except Exception as e:
            self.slack.send_message(f"⚠️ 오류: {e}")

    def _change_strategy(self, name: str):
        """전략 변경"""
        strategies = {
            'special': SpecialWeaponFarming(
                self.config['strategies']['special_farming']
            ),
            'safe': SafeFarming(
                self.config['strategies']['safe_farming']
            ),
            'aggressive': AggressiveFarming(
                self.config['strategies']['aggressive_farming']
            )
        }

        if name in strategies:
            self.strategy = strategies[name]
            self.slack.send_message(f"⚡ 전략 변경 → {name}")
        else:
            self.slack.send_message(
                f"⚠️ 알 수 없는 전략\n"
                f"사용 가능: special, safe, aggressive"
            )

    def _notify_state_change(self):
        """상태 변화 알림 - 목표 강화 단계 달성 시에만"""
        if not self.prev_state or not self.state:
            return

        curr = self.state
        prev = self.prev_state

        # 목표 레벨 확인
        target_level = None
        if hasattr(self.strategy, 'config'):
            target_level = self.strategy.config.get('target_level') or \
                          self.strategy.config.get('max_level')

        # 강화 성공 & 목표 달성
        if (curr.bot_state == ChatbotState.SUCCESS and
            curr.weapon.level > prev.weapon.level and
            target_level and curr.weapon.level >= target_level):
            self.slack.notify_success(
                prev.weapon.level,
                curr.weapon.level,
                curr.gold
            )

    def run(self):
        """메인 루프"""
        self.running = True
        self.slack.start()
        self.slack.send_message("🤖 GameBot 시작!")

        try:
            while self.running:
                if self.paused:
                    time.sleep(0.5)
                    continue

                # 1. 채팅 수집 & 파싱
                text = self.automation.get_chat()
                self.prev_state = self.state
                self.state = self.parser.parse(text)

                # 2. 상태 변화 알림
                self._notify_state_change()

                # 3. 전략 실행
                if self.state.bot_state != ChatbotState.IDLE:
                    self.strategy.do_step(self)

                # 4. 대기
                time.sleep(self.interval)

        except KeyboardInterrupt:
            pass

        finally:
            self.running = False
            self.slack.send_message("👋 GameBot 종료")
            self.slack.stop()
            print("\nStopped.")


def main():
    # 설정 로드
    config = Config()

    # 전략 선택
    strategy = SpecialWeaponFarming(
        config['strategies']['special_farming']
    )

    # 서비스 생성
    parser = ChatParser(set(config['special_weapons']))
    automation = GameAutomation(config['automation']['delays'])
    slack = SlackBot(
        bot_token=config['slack']['bot_token'],
        app_token=config['slack']['app_token'],
        channel=config['slack']['channel']
    )

    # GameBot 실행
    bot = GameBot(
        strategy=strategy,
        parser=parser,
        automation=automation,
        slack=slack,
        config=config,
        interval=config['bot']['interval']
    )

    print("GameBot with Slack started.")
    print("Use Slack commands to control the bot.")

    bot.run()


if __name__ == "__main__":
    main()
