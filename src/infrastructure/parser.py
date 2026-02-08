"""채팅 파싱 서비스"""
import re
from domain.state import GameState, Weapon, ChatbotState


class ChatParser:
    # Regex patterns
    CHAT = re.compile(r'^\[.+?\] \[.+?\] ')
    ENFORCE = re.compile(r'〖.*강화 (성공|파괴|유지).*〗')
    GOLD = re.compile(r'(?:남은|보유|현재 보유) 골드: ([0-9,]+)G')
    SELL = re.compile(r'〖검 판매〗')
    LEVEL = re.compile(r'\+(\d+)\s*→\s*\+(\d+)')
    SWORD = re.compile(r'⚔️획득 검: \[\+\d+\] (.+)')
    SWORD_NEW = re.compile(r'⚔️새로운 검 획득: \[\+\d+\] (.+)')
    # 강화 유지 패턴: 『[+10] 오염을 무기로 바꾸는 역설의 칫솔』의 레벨이 유지
    KEPT_WEAPON = re.compile(r'『\[\+(\d+)\] (.+?)』')
    # 파괴 후 지급 패턴: 『[+6] 영혼 감응의 검』 산산조각 나서, 『[+0] 낡은 검』 지급되었습니다
    DESTROY_GIVEN = re.compile(r'산산조각 나서, 『\[\+(\d+)\] (.+?)』 지급되었습니다')

    def __init__(self, special_weapons: set):
        self.special_weapons = special_weapons

    def parse(self, text: str) -> GameState:
        """텍스트 → GameState"""
        chats = self._split_chats(text)
        bot_chats = [c for c in chats[-3:] if '[플레이봇]' in c]
        combined = '\n'.join(bot_chats)

        return GameState(
            gold=self._extract_gold(combined),
            weapon=self._extract_weapon(combined),
            bot_state=self._extract_state(combined)
        )

    def _split_chats(self, text: str) -> list:
        """채팅 메시지 분리"""
        if not text:
            return []
        lines = text.split('\n')
        chats, current = [], None
        for line in lines:
            if self.CHAT.match(line):
                if current:
                    chats.append(current.strip())
                current = line
            elif current:
                current += '\n' + line
        if current:
            chats.append(current.strip())
        return chats

    def _extract_gold(self, text: str) -> int:
        """골드 추출"""
        m = self.GOLD.search(text)
        return int(m.group(1).replace(',', '')) if m else 0

    def _extract_weapon(self, text: str) -> Weapon:
        """무기 정보 추출"""
        name = "낡은 검"
        level = 0

        # 1순위: 강화 성공 - "+0 → +1" 패턴 (가장 명확)
        if m := self.LEVEL.search(text):
            level = int(m.group(2))
            # 획득 검 이름 찾기
            if sword_m := self.SWORD.search(text):
                name = sword_m.group(1)
            elif sword_new_m := self.SWORD_NEW.search(text):
                name = sword_new_m.group(1)

        # 2순위: 강화 파괴 - 지급된 무기 ("산산조각" 키워드 확인)
        elif '산산조각' in text:
            if destroy_m := self.DESTROY_GIVEN.search(text):
                level = int(destroy_m.group(1))
                name = destroy_m.group(2)

        # 3순위: 강화 유지 - 『[+10] 무기』의 레벨이 유지
        elif '레벨이 유지' in text:
            if kept_m := self.KEPT_WEAPON.search(text):
                level = int(kept_m.group(1))
                name = kept_m.group(2)

        # 4순위: 판매 - 새로운 검 획득
        elif sword_new_m := self.SWORD_NEW.search(text):
            name = sword_new_m.group(1)
            level = 0

        return Weapon(
            name=name,
            level=level,
            is_special=self._check_special(name)
        )

    def _check_special(self, weapon_name: str) -> bool:
        """특수 무기 여부 확인 (부분 매칭)"""
        # 콜론(:) 앞부분만 추출
        base_name = weapon_name.split(':')[0].strip()

        # 특수 무기 목록과 비교
        for special in self.special_weapons:
            if special in base_name or base_name in special:
                return True
        return False

    def _extract_state(self, text: str) -> ChatbotState:
        """챗봇 상태 추출"""
        if self.SELL.search(text):
            return ChatbotState.SELL
        if m := self.ENFORCE.search(text):
            result = m.group(1)
            if result == '성공':
                return ChatbotState.SUCCESS
            elif result == '파괴':
                return ChatbotState.FAILED
            elif result == '유지':
                return ChatbotState.REMAINED
        return ChatbotState.IDLE
