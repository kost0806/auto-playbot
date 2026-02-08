"""게임 상태 도메인 모델"""
from dataclasses import dataclass
from enum import Enum


class ChatbotState(Enum):
    """챗봇 상태"""
    SUCCESS = "성공"
    FAILED = "파괴"
    REMAINED = "유지"
    SELL = "판매"
    IDLE = "대기"


@dataclass
class Weapon:
    """무기 정보"""
    name: str
    level: int
    is_special: bool


@dataclass
class GameState:
    """게임 현재 상태"""
    gold: int
    weapon: Weapon
    bot_state: ChatbotState
