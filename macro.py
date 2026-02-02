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

safe_money_per_level = [
    0, 0, 23, 64, 281,
    767, 2341, 6905, 17860, 44475,
    127086, 319271, 787087, 1918748, 4741373,
    9951633, 20749180, 41843536, 122266583, 999999999, 9999999999
]

global previous, state, current_info, target_enforce_level, enforcing

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


def parse_current_info(last_two_chats):
    enforce_level = None
    remaining_gold = None

    for chat in last_two_chats:
        # 강화 결과 파싱
        enforce_match = ENFORCEMENT_PATTERN.search(chat)
        if enforce_match:
            result = enforce_match.group(1)

            if result == '성공':
                m = ENFORCE_SUCCESS_PATTERN.search(chat)
                if m:
                    enforce_level = int(m.group(2))
            elif result == '유지':
                m = ENFORCE_KEEP_PATTERN.search(chat)
                if m:
                    enforce_level = int(m.group(1))
            elif result == '파괴':
                enforce_level = 0

        # 판매 결과 파싱
        sell_match = SELL_PATTERN.search(chat)
        if sell_match:
            enforce_level = 0

        gold_match = REMAINING_GOLD_PATTERN.search(chat)
        if gold_match:
            remaining_gold = int(gold_match.group(1).replace(',', ''))

    log(f"parse_current_info -> enforce_level={enforce_level}, remaining_gold={remaining_gold}")
    return enforce_level, remaining_gold



def calculate_state(last_chat):
    return 'PLAYER' if last_chat.startswith('[김민영]') else 'BOT'


def process_user_command(last_chat):
    global target_enforce_level
    if '!' not in last_chat:
        return
    command = last_chat.split('!')[-1]
    log(f"process_user_command -> command='{command}'")
    if command.startswith('강화'):
        target_enforce_level = int(command.split(' ')[-1])
        log(f"target_enforce_level={target_enforce_level}")
    elif command.startswith('중단'):
        target_enforce_level = -1
        log("강화 중단")
    elif command.startswith('종료'):
        print("프로그램을 종료합니다.")
        os._exit(0)


def execute_command(command):
    global target_enforce_level, enforcing

    if target_enforce_level < 0:
        log('Target level이 설정되어 있지 않음')
        return

    if current_info['enforce_level'] is not None and current_info['enforce_level'] >= target_enforce_level:
        target_enforce_level = -1
        print(f"목표 강화 단계 +{current_info['enforce_level']} 달성!")
        return

    log(f"execute_command -> '/{command}' 입력 시작")
    enforcing = True
    try:
        time.sleep(0.3)
        pyautogui.press('enter')
        time.sleep(0.1)
        # 한글은 typewrite로 입력 불가하므로 클립보드를 통해 입력
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText('/' + command, win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
        pyautogui.press('enter')
        time.sleep(0.3)
        pyautogui.press('enter')
        time.sleep(0.2)
        pyautogui.click()
        log(f"execute_command -> '/{command}' 입력 완료")
    finally:
        enforcing = False


def process_chats(chats: list[Any]):
    global previous, state, current_info
    if len(chats) <= 0:
        return
    last_chat = chats[-1]

    if last_chat == previous:
        return

    previous = last_chat

    state = calculate_state(last_chat)
    log(f"state={state}")
    if state == 'BOT':
        last_three_chats = list(filter(lambda chat: chat.startswith('[플레이봇]'), chats[-3:]))
        current_enforce, current_money = parse_current_info(last_three_chats)
        current_info['enforce_level'] = current_enforce
        current_info['remaining_gold'] = current_money
        log(f"enforce_level={current_enforce}, remaining_gold={current_money}, safe_money={safe_money_per_level[current_enforce]}")
        if safe_money_per_level[current_enforce] < current_money:
            log("강화 실행")
            execute_command('강화')
        else:
            log("골드 부족 -> 판매 실행")
            execute_command('판매')
    elif state == 'PLAYER':
        process_user_command(last_chat)
        


def copy_all():
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.1)


def clipboard_monitor():
    global previous, state, current_info, target_enforce_level, enforcing
    previous = ''
    state = 'PLAYER'
    current_info = {
        'enforce_level': 0,
        'remaining_gold': 0,
    }
    target_enforce_level = -1
    enforcing = False
    while True:
        if not enforcing:
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
