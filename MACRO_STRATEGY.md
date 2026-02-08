# Macro 스텝 정의를 위한 Strategy-like pattern
## State 정의
State는 마지막 챗봇의 메시지를 확인하고 현재 상태를 정의한다.

챗봇의 메시지 분류는 [CHAT.md](CHAT.md)를 참고한다.

### State 포함 항목
- current_gold
- current_weapon
  - enforcement_level
  - name
  - is_special_weapon
- chatbot_state

#### Chatbot State
Chatbot State는 아래와 같은 값을 갖는다.

- ENFORCEMENT_SUCCESS
- ENFORCEMENT_FAILED
- ENFORCEMENT_REMAINED
- WEAPON_SELL

## Strategy
Macro Mode별 Strategy를 정의하고 매 스텝마다 실행시킬 method를 abstract 로 가지고 있어야 한다.

### 예시
```python
class SpecialWeaponFarmingMode(MacroMode):
  def do_step(self, gamebot):
    state = gamebot.get_current_state()
    
    if state.current_gold < CONFIG['safe_money_per_level'][state.current_weapon.enforcement_level]:
      gamebot.do_sell()
      return
    
    if state.current_weapon.enforcement_level == 1 and not state.current_weapon.is_special_weapon:
      gamebot.do_sell()
      return
    
    if state.current_weapon.enforcement_level >= gamebot.bot.target_enforce_level:
      gamebot.do_sell()
    else:
      gamebot.do_enforcement()
```
