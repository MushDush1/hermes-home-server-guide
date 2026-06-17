"""
Send file to WeChat via CF_HDROP clipboard + pyautogui paste.
Fallback method when pyweixin's Files API can't find the contact.
"""
import os, time, ctypes, pyautogui, pygetwindow

def copy_file_to_clipboard(file_path: str) -> bool:
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        return False
    
    ctypes.windll.user32.OpenClipboard(0)
    ctypes.windll.user32.EmptyClipboard()
    
    offset = 20
    file_list = (file_path + '\0\0').encode('utf-16-le')
    total_size = offset + len(file_list)
    
    hglobal = ctypes.windll.kernel32.GlobalAlloc(0x0002, total_size)
    ptr = ctypes.windll.kernel32.GlobalLock(hglobal)
    ctypes.memmove(ptr, (ctypes.c_uint32 * 5)(offset, 0, 0, 0, 1), 20)
    ctypes.memmove(ptr + offset, file_list, len(file_list))
    ctypes.windll.kernel32.GlobalUnlock(hglobal)
    
    ctypes.windll.user32.SetClipboardData(15, hglobal)  # CF_HDROP
    ctypes.windll.user32.CloseClipboard()
    return True

def send_file(file_path: str) -> bool:
    if not copy_file_to_clipboard(file_path):
        print(f"File not found: {file_path}")
        return False
    
    wins = [w for w in pygetwindow.getWindowsWithTitle('微信')]
    if not wins:
        print("WeChat window not found")
        return False
    
    wins[0].activate()
    time.sleep(0.8)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(2)
    pyautogui.press('enter')
    return True

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: send_file.py <path>")
    else:
        ok = send_file(sys.argv[1])
        print("OK" if ok else "FAIL")
