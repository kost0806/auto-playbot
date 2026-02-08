"""구체적 전략 구현"""
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


class SafeFarming(MacroMode):
    """안전 파밍 전략 - 150% 안전 마진"""

    def do_step(self, gamebot):
        state = gamebot.state
        safe_money = self.config['safe_money'][state.weapon.level] * 1.5

        if state.gold < safe_money:
            gamebot.sell()
        elif state.weapon.level >= self.config['target_level']:
            gamebot.sell()
        else:
            gamebot.enforce()


class AggressiveFarming(MacroMode):
    """공격적 파밍 전략 - 최소 골드만 유지"""

    def do_step(self, gamebot):
        state = gamebot.state

        if state.gold < self.config['min_gold']:
            gamebot.sell()
        elif state.weapon.level >= self.config['max_level']:
            gamebot.sell()
        else:
            gamebot.enforce()
