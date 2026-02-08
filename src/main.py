"""GameBot with Slack Integration"""
import time
from domain.state import GameState, ChatbotState
from domain.strategy.base import MacroMode
from domain.strategy.strategies import (
    SpecialWeaponFarming, TargetEnforcementStrategy,
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
        self.paused = True  # 시작 시 idle 모드

        # Slack 명령 핸들러 등록
        self.slack.set_command_handler(self._handle_slack_command)

    def enforce(self):
        """강화"""
        self.automation.send_command("강화")

    def sell(self):
        """판매"""
        self.automation.send_command("판매")

    def _show_help(self):
        """도움말 표시"""
        help_text = (
            "📚 *GameBot 명령어 목록*\n\n"
            "*봇 제어*\n"
            "• `!시작` - 봇 시작/재개\n"
            "• `!중단` - 봇 일시 중단\n"
            "• `!종료` - 봇 종료\n\n"
            "*강화 관리*\n"
            "• `!강화 [레벨]` - 목표 강화 레벨 설정\n"
            "  예: `!강화 10` → +10 목표\n\n"
            "*전략 변경*\n"
            "• `!전략 [이름]` - 파밍 전략 변경\n"
            "  예: `!전략 special`\n"
            "  사용 가능: special, safe, aggressive\n\n"
            "*상태 조회*\n"
            "• `!상태` - 현재 게임 상태 조회\n"
            "• `!도움` - 이 도움말 표시\n"
        )
        self.slack.send_message(help_text)

    def _handle_slack_command(self, command: str):
        """Slack 명령 처리"""
        try:
            parts = command.strip().split()
            cmd = parts[0][1:]  # Remove '!'

            if cmd == "도움" or cmd == "help":
                self._show_help()

            elif cmd == "시작" or cmd == "재개":
                if self.paused:
                    self.resume()
                    self.slack.send_message("▶️ 봇 시작/재개")
                else:
                    self.slack.send_message("ℹ️ 이미 실행 중입니다")

            elif cmd == "중단":
                if not self.paused:
                    self.pause()
                    self.slack.send_message("⏸️ 봇 중단")
                else:
                    self.slack.send_message("ℹ️ 이미 중단된 상태입니다")

            elif cmd == "강화" and len(parts) > 1:
                target = int(parts[1])
                if hasattr(self.strategy, 'config'):
                    self.strategy.config['target_level'] = target
                self.slack.send_message(f"🎯 목표 레벨 +{target}로 설정")
                if self.paused:
                    self.paused = False
                    self.slack.send_message("▶️ 강화 재개")

            elif cmd == "전략" and len(parts) > 1:
                self._change_strategy(parts[1])

            elif cmd == "상태":
                if self.state:
                    self.slack.notify_status(self.state)
                else:
                    self.slack.send_message("⚠️ 아직 상태 정보 없음")

            elif cmd == "종료":
                self.slack.send_message("👋 봇 종료 중...")
                self.stop()

            else:
                self.slack.send_message(
                    f"❓ 알 수 없는 명령: `{command}`\n"
                    "`!도움` 명령으로 사용 가능한 명령을 확인하세요."
                )

        except Exception as e:
            self.slack.send_message(f"⚠️ 오류: {e}")

    def pause(self):
        """일시 정지"""
        if not self.paused:
            self.paused = True
            print("[INFO] Bot paused")
        else:
            print("[INFO] Bot is already paused")

    def resume(self):
        """재개"""
        if self.paused:
            self.paused = False
            print("[INFO] Bot resumed")
        else:
            print("[INFO] Bot is already running")

    def stop(self):
        """매크로 종료"""
        if self.running:
            self.running = False
            print("[INFO] Stop requested - shutting down...")
        else:
            print("[INFO] Bot is not running")

    def _change_strategy(self, name: str):
        """전략 변경"""
        strategies = {
            'special': SpecialWeaponFarming(
                self.config['strategies']['special_farming']
            ),
            'target': TargetEnforcementStrategy(self.config['strategies']['target']),
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
        self.slack.send_message(
            "🤖 GameBot 준비 완료!\n"
            "⏸️ Idle 모드로 대기 중입니다.\n"
            "`!시작` 명령으로 봇을 시작하세요.\n"
            "`!도움` 명령으로 사용 가능한 명령을 확인할 수 있습니다."
        )

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
