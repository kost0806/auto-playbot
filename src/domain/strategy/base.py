"""Strategy 패턴 기반 클래스 - MACRO_STRATEGY.md 준수"""
from abc import ABC, abstractmethod


class MacroMode(ABC):
    """매크로 전략 추상 기반 클래스"""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def do_step(self, gamebot) -> None:
        """
        매크로 한 스텝 실행

        Args:
            gamebot: GameBot 인스턴스
        """
        pass
