"""게임 자동화 서비스"""
import time
import pyautogui
import win32clipboard


class GameAutomation:
    def __init__(self, delays: dict):
        self.delays = delays

    def get_chat(self) -> str:
        """채팅 텍스트 가져오기"""
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.1)

        try:
            win32clipboard.OpenClipboard()
            text = win32clipboard.GetClipboardData(
                win32clipboard.CF_UNICODETEXT
            )
            win32clipboard.CloseClipboard()
            return text
        except:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
            return ""

    def send_command(self, cmd: str) -> None:
        """명령 전송"""
        time.sleep(self.delays.get('before', 0.3))
        pyautogui.press('enter')
        time.sleep(self.delays.get('after', 0.1))

        # 클립보드로 한글 입력
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(
            f"/{cmd}",
            win32clipboard.CF_UNICODETEXT
        )
        win32clipboard.CloseClipboard()

        pyautogui.hotkey('ctrl', 'v')
        time.sleep(self.delays.get('paste', 0.1))
        pyautogui.press('enter')
        time.sleep(0.3)
        pyautogui.press('enter')
        time.sleep(0.2)
        pyautogui.click()
