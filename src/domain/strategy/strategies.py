"""구체적 전략 구현"""
from datetime import datetime, timedelta

from domain.state import ChatbotState
from domain.strategy.base import MacroMode


class SpecialWeaponFarming(MacroMode):
    """특수 무기 파밍 전략"""

    def do_step(self, gamebot):
        state = gamebot.state
        safe_money = self.config['safe_money'][state.weapon.level]

        # 골드 부족
        if state.gold < safe_money:
            gamebot.sell()
            return

        # +1 일반 무기 판매
        if state.weapon.level == 1 and not state.weapon.is_special:
            gamebot.sell()
            return

        # 목표 달성
        if state.weapon.level >= self.config['target_level']:
            gamebot.sell()
        else:
            gamebot.enforce()


class TargetEnforcementStrategy(MacroMode):

    def __init__(self, config: dict):
        super().__init__(config)
        self.last_executed = datetime.now()

    def do_step(self, gamebot):
        state = gamebot.state

        if state.bot_state == ChatbotState.PROCESSING and self.last_executed < (datetime.now() - timedelta(minutes=2)):
            return

        self.last_executed = datetime.now()

        if state.gold < self.config['required_money_per_level'][state.weapon.level]:
            gamebot.stop()
            return

        if state.weapon.level >= self.config['target_level']:
            gamebot.pause()
            return

        gamebot.enforce()