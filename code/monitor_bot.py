"""
WeChat UIA Monitor Bot — reads chat via pywinauto accessibility tree, replies automatically.
Requires: WeChat 4.1.6.14, pywechat127, pywinauto
"""
import win32gui, time
from pywinauto import Desktop
from pyweixin import Navigator, Messages

FRIEND = "REPLACE_WITH_CONTACT_NAME"

def get_chat_messages():
    hwnd = win32gui.FindWindow('Qt51514QWindowIcon', '微信')
    d = Desktop(backend='uia')
    win = d.window(handle=hwnd)
    lists = [c for c in win.descendants() if c.element_info.control_type == 'List']
    for lst in lists:
        if lst.window_text() == '消息':
            return [c.window_text() for c in lst.children()]
    return []

def reply(msg: str) -> str:
    """Customize your reply logic here."""
    if 'hello' in msg.lower() or '你好' in msg:
        return 'Hello! Im an AI bot testing WeChat automation :)'
    elif '?' in msg or '？' in msg:
        return 'Good question! Let me check...'
    else:
        return f'Received: {msg[:50]}'

def main():
    Navigator.open_dialog_window(friend=FRIEND)
    prev = get_chat_messages()
    start = time.time()
    
    while time.time() - start < 300:
        time.sleep(8)
        curr = get_chat_messages()
        if len(curr) > len(prev):
            for msg in curr[len(prev):]:
                if msg.strip() and '动画表情' not in msg:
                    r = reply(msg)
                    for attempt in range(3):
                        try:
                            Messages.send_messages_to_friend(friend=FRIEND, messages=[r])
                            break
                        except:
                            if attempt < 2: time.sleep(2)
        prev = curr

if __name__ == '__main__':
    main()
