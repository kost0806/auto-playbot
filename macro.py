import os
import re
import signal
import threading
import time
from typing import Any

import pyautogui
import win32clipboard
from adodbapi.process_connect_string import process

debug = True


def log(msg):
    if debug:
        print(f"[DEBUG] {msg}")

CHAT_PATTERN = re.compile(r'^\[.+?\] \[.+?\] ')
ENFORCEMENT_PATTERN = re.compile(r'〖.*강화 (성공|파괴|유지).*〗')
REMAINING_GOLD_PATTERN = re.compile(r'(?:남은|보유) 골드: ([0-9,]+)G')
SELL_PATTERN = re.compile(r'〖검 판매〗')
ENFORCE_SUCCESS_PATTERN = re.compile(r'\+(\d+)\s*→\s*\+(\d+)')
ENFORCE_KEEP_PATTERN = re.compile(r'『\[\+(\d+)\]')
SWORD_NAME_PATTERN = re.compile(r'⚔️획득 검: \[\+\d+\] (.+)')
DESTROY_SWORD_PATTERN = re.compile(r'『\[\+\d+\] (.+)』 지급되었습니다')

safe_money_per_level = [
    0, 0, 23, 64, 281,
    767, 2341, 6905, 17860, 44475,
    127086, 319271, 787087, 1918748, 4741373,
    9951633, 20749180, 41843536, 122266583, 999999999, 9999999999
]

SPECIAL_SWORD_NAMES = {
'짝짝이 해진 슬리퍼',
    '천이 찢어진 너덜거리는 우산',
    '한 짝 없는 외로운 젓가락',
    '금이 간 단소',
    '털이 반쯤 빠진 칫솔',
    '감전 주의보 기타',
    '땅에 떨어진 3초 룰',
    '눅눅한 핫도그 조각',
    '털이 빠진 허술한 빗자루',
    '깜빡거리는 광선검',
    '시들고 축 처진 꽃다발',
    '물이 줄줄 새는 주전자',
}

RETRY_TIMEOUT = 120  # 2분

global previous, state, current_info, target_enforce_level, enforcing
global last_command, last_command_time

def get_clipboard_text():
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return data
    except Exception:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass
        return None


def parse_chat(text):
    if text is None:
        return []
    lines = text.split('\n')
    chats = []
    current_chat = None

    for line in lines:
        if CHAT_PATTERN.match(line):
            if current_chat is not None:
                chats.append(current_chat.strip())
            current_chat = line
        else:
            if current_chat is not None:
                current_chat += '\n' + line

    if current_chat is not None:
        chats.append(current_chat.strip())

    return chats


def handle_enforce_success(chat):
    """강화 성공 처리 - 강화 레벨과 검 이름 반환"""
    enforce_level = None
    sword_name = None
    m = ENFORCE_SUCCESS_PATTERN.search(chat)
    if m:
        enforce_level = int(m.group(2))
    sword_match = SWORD_NAME_PATTERN.search(chat)
    if sword_match:
        sword_name = sword_match.group(1)
    return enforce_level, sword_name


def handle_enforce_keep(chat):
    """강화 유지 처리 - 강화 레벨 반환"""
    m = ENFORCE_KEEP_PATTERN.search(chat)
    if m:
        return int(m.group(1))
    return None


def handle_enforce_destroy(chat):
    """강화 파괴 처리 - 강화 레벨 0과 새 검 이름 반환"""
    sword_name = None
    sword_match = DESTROY_SWORD_PATTERN.search(chat)
    if sword_match:
        sword_name = sword_match.group(1)
    return 0, sword_name


def handle_sell(chat):
    """판매 처리 - 강화 레벨 0과 새 검 이름 반환"""
    sword_name = None
    sword_match = SWORD_NAME_PATTERN.search(chat)
    if sword_match:
        sword_name = sword_match.group(1)
    return 0, sword_name


def parse_current_info(last_chats):
    enforce_level = None
    remaining_gold = None
    sword_name = None

    chat = '\n'.join(last_chats)

    # 강화 결과 파싱
    enforce_match = ENFORCEMENT_PATTERN.search(chat)
    if enforce_match:
        result = enforce_match.group(1)

        if result == '성공':
            enforce_level, sword_name = handle_enforce_success(chat)
        elif result == '유지':
            enforce_level = handle_enforce_keep(chat)
        elif result == '파괴':
            enforce_level, sword_name = handle_enforce_destroy(chat)

    # 판매 결과 파싱
    sell_match = SELL_PATTERN.search(chat)
    if sell_match:
        enforce_level, sword_name = handle_sell(chat)

    # 파괴 후 지급 메시지 파싱
    if sword_name is None:
        destroy_sword_match = DESTROY_SWORD_PATTERN.search(chat)
        if destroy_sword_match:
            sword_name = destroy_sword_match.group(1)
            if enforce_level is None:
                enforce_level = 0

    gold_match = REMAINING_GOLD_PATTERN.search(chat)
    if gold_match:
        remaining_gold = int(gold_match.group(1).replace(',', ''))

    log(f"parse_current_info -> enforce_level={enforce_level}, remaining_gold={remaining_gold}, sword_name={sword_name}")
    return enforce_level, remaining_gold, sword_name



def calculate_state(last_chat):
    return 'BOT' if last_chat.startswith('[플레이봇]') else 'PLAYER'


def process_user_command(last_chat):
    global target_enforce_level
    if '!' not in last_chat:
        return
    command = last_chat.split('!')[-1]
    log(f"process_user_command -> command='{command}'")
    if command.startswith('강화'):
        target_enforce_level = int(command.split(' ')[-1])
        log(f"target_enforce_level={target_enforce_level}")
        input_message(f"강화 {target_enforce_level} 명령 인식. 목표: +{target_enforce_level}", is_command=False)
    elif command.startswith('중단'):
        target_enforce_level = -1
        log("강화 중단")
        input_message("중단 명령 인식. 강화를 중단합니다.", is_command=False)
    elif command.startswith('종료'):
        input_message("종료 명령 인식. 프로그램을 종료합니다.", is_command=False)
        time.sleep(1)
        os._exit(0)


def input_message(message, is_command):
    global target_enforce_level, enforcing, last_command, last_command_time

    if target_enforce_level < 0:
        log('Target level이 설정되어 있지 않음')
        return

    if current_info['enforce_level'] is not None and current_info['enforce_level'] >= target_enforce_level:
        print(f"목표 강화 단계 +{current_info['enforce_level']} 달성!")
        current_info['enforce_level'] = 0
        input_message("판매", is_command=True)
        # target_enforce_level = -1
        return

    log(f"input_message -> '{'/' if is_command else ''}{message}' 입력 시작")
    if is_command:
        last_command = message
        last_command_time = time.time()
    enforcing = True
    try:
        time.sleep(0.3)
        pyautogui.press('enter')
        time.sleep(0.1)
        # 한글은 typewrite로 입력 불가하므로 클립보드를 통해 입력
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(('/' if is_command else '') + message, win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
        pyautogui.press('enter')
        time.sleep(0.3)
        pyautogui.press('enter')
        time.sleep(0.2)
        pyautogui.click()
        log(f"input_message -> '{"/" if is_command else ""}{message}' 입력 완료")
    finally:
        enforcing = False


def process_chats(chats: list[Any]):
    global previous, state, current_info, last_command, last_command_time
    if len(chats) <= 0:
        return
    last_chat = chats[-1]

    if last_chat == previous:
        return

    previous = last_chat

    state = calculate_state(last_chat)
    log(f"state={state}")
    if state == 'BOT':
        last_command = None
        last_command_time = None
        last_three_chats = list(filter(lambda chat: chat.startswith('[플레이봇]'), chats[-3:]))
        current_enforce, current_money, current_sword = parse_current_info(last_three_chats)
        current_info['enforce_level'] = current_enforce
        current_info['remaining_gold'] = current_money
        if current_sword:
            current_info['sword_name'] = current_sword
        if current_enforce is None or current_money is None:
            log(f"파싱 실패: enforce_level={current_enforce}, remaining_gold={current_money}")
            return
        log(f"enforce_level={current_enforce}, remaining_gold={current_money}, safe_money={safe_money_per_level[current_enforce]}")
        if current_info['sword_name'] is not None and current_info['sword_name'] not in SPECIAL_SWORD_NAMES and current_enforce == 1:
            log("특수 아니면 판매")
            input_message('판매', is_command=True)
        elif safe_money_per_level[current_enforce] < current_money:
            log("강화 실행")
            input_message('강화', is_command=True)
        else:
            log("골드 부족 -> 판매 실행")
            input_message('판매', is_command=True)
    elif state == 'PLAYER':
        process_user_command(last_chat)
        


def copy_all():
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.1)


def clipboard_monitor():
    global previous, state, current_info, target_enforce_level, enforcing
    global last_command, last_command_time
    previous = ''
    state = 'PLAYER'
    current_info = {
        'enforce_level': 0,
        'remaining_gold': 0,
        'sword_name': None,
    }
    target_enforce_level = -1
    enforcing = False
    last_command = None
    last_command_time = None
    while True:
        if not enforcing:
            # 타임아웃 체크: 커맨드 전송 후 2분 이상 봇 응답 없으면 재전송
            if last_command and last_command_time and time.time() - last_command_time >= RETRY_TIMEOUT:
                log(f"봇 응답 타임아웃 ({RETRY_TIMEOUT}초) -> '/{last_command}' 재전송")
                input_message(last_command, is_command=True)
            else:
                copy_all()
                current = get_clipboard_text()
                chats = parse_chat(current)
                process_chats(chats)

        time.sleep(0.5)


if __name__ == "__main__":
    monitor_thread = threading.Thread(target=clipboard_monitor, daemon=True)
    monitor_thread.start()
    print("Clipboard monitor started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")
