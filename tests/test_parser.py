import pytest
from infrastructure.parser import ChatParser
from domain.state import ChatbotState

# 특수 무기 목록
SPECIAL_WEAPONS = {
    "짝짝이 해진 슬리퍼",
    "천이 찢어진 너덜거리는 우산",
    "한 짝 없는 외로운 젓가락",
    "금이 간 단소",
    "털이 반쯤 빠진 칫솔",
    "감전 주의보 기타",
    "땅에 떨어진 3초 룰",
    "눅눅한 핫도그 조각",
    "털이 빠진 허술한 빗자루",
    "깜빡거리는 광선검",
    "시들고 축 처진 꽃다발",
    "물이 줄줄 새는 주전자",
    "신들의 치아를 닦은 칫솔",
    "오염을 무기로 바꾸는 역설의 칫솔",
}

@pytest.fixture
def parser():
    return ChatParser(SPECIAL_WEAPONS)

@pytest.mark.parametrize("name, text, expected_state, expected_level, expected_gold, expected_weapon_name, expected_is_special", [
    (
        "강화 성공 (+10 미만)",
        """[플레이봇] [오후 12:32] @사용자 〖✨강화 성공✨ +0 → +1〗

💬 대장장이: "이게 고작 대지의 울림이라니, 겨우 +1이 되고 시시하군. 고작 이 정도인가?"

💸사용 골드: -10G
💰남은 골드: 132,594,446G
⚔️획득 검: [+1] 대지의 울림 검
[플레이봇] [오후 12:32] [+1] 대지의 울림 검
대지의 힘이 희미하게 깃들었지만, 아직 불안정하다.""",
        ChatbotState.SUCCESS, 1, 132594446, "대지의 울림 검", False
    ),
    (
        "강화 성공 (+10 이상, 특수 무기)",
        """[플레이봇] [오후 12:31] @사용자 〖✨강화 성공✨ +10 → +11〗

💬 대장장이: "신들도 이를 닦았다고? ...신성한 구강 위생이군."

💸사용 골드: -20,000G
💰남은 골드: 131,457,557G
⚔️획득 검: [+11] 신들의 치아를 닦은 칫솔: 천상의 위생
[플레이봇] [오후 12:31] [+11] 신들의 치아를 닦은 칫솔: 천상의 위생
올림포스 신들이 연회 후 치아를 닦을 때 사용한 칫솔. 신성한 청결의 도구.
[플레이봇] [오후 12:31] 🚨[속보]🚨 @사용자님이 전설의 『[+11] 신들의 치아를 닦은 칫솔: 천상의 위생』 강화에 성공하셨습니다.""",
        ChatbotState.SUCCESS, 11, 131457557, "신들의 치아를 닦은 칫솔: 천상의 위생", True
    ),
    (
        "강화 유지",
        """[플레이봇] [오후 12:31] @사용자 〖💦강화 유지💦〗

💬 대장장이: "모든 오염을 품고도 녹아내리지 않다니... 역겹군."

『[+10] 오염을 무기로 바꾸는 역설의 칫솔』의 레벨이 유지되었습니다.

💸사용 골드: -20,000G
💰남은 골드: 131,497,557G
[플레이봇] [오후 12:31] 💬 대장장이: "계속 강화하겠나?""",
        ChatbotState.REMAINED, 10, 131497557, "오염을 무기로 바꾸는 역설의 칫솔", True
    ),
    (
        "강화 파괴 (+10 미만)",
        """[플레이봇] [오전 9:00] @사용자 〖💥강화 파괴💥〗

💬 대장장이: "결국 자신의 영혼을 감당하지 못했군. 역시 저 불안정한 영혼이 문제였어. 내 망치가 아무리 완벽해도 저런 것까진 어쩔 수 없지."

💸사용 골드: -1,000G
💰남은 골드: 133,681,007G
[플레이봇] [오전 9:00] 『[+6] 영혼 감응의 검』 산산조각 나서, 『[+0] 낡은 검』 지급되었습니다.""",
        ChatbotState.FAILED, 0, 133681007, "낡은 검", False
    ),
    (
        "강화 파괴 (+10 이상)",
        """[플레이봇] [오전 9:48] @사용자 〖💥강화 파괴💥〗

💬 대장장이: "결국 자신의 힘을 감당하지 못했군. 저 통제 불가능한 혼돈이 문제였어. 내 실수 따위는 없어."

💸사용 골드: -20,000G
💰남은 골드: 133,627,227G
[플레이봇] [오전 9:48] 『[+10] 창세의 혼돈의 막대』 산산조각 나서, 『[+0] 낡은 망치』 지급되었습니다.
[플레이봇] [오전 9:48] 모두 @사용자의 위대한 도전을 기리며 잠시 묵념하는 시간을 갖겠습니다...""",
        ChatbotState.FAILED, 0, 133627227, "낡은 망치", False
    ),
    (
        "판매",
        """[플레이봇] [오후 12:32] @사용자 〖검 판매〗

💬 감정사: "모래가 씹히는군. 관리가 엉망이야. 10G."

💶획득 골드: +10G
💰현재 보유 골드: 132,594,456G
⚔️새로운 검 획득: [+0] 낡은 검
[플레이봇] [오후 12:32] 💬 감정사: "뭐 검이 필요하면 이거나 가져가시게나." """,
        ChatbotState.SELL, 0, 132594456, "낡은 검", False
    ),
])
def test_parse_cases(parser, name, text, expected_state, expected_level, expected_gold, expected_weapon_name, expected_is_special):
    result = parser.parse(text)
    
    assert result.bot_state == expected_state
    assert result.weapon.level == expected_level
    assert result.gold == expected_gold
    assert result.weapon.name == expected_weapon_name
    assert result.weapon.is_special == expected_is_special
