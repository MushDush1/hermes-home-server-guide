"""
pywinauto UIA Backend Patterns
===============================
Key patterns used in WeChat 4.1.6.14 automation.
Embedded here so you don't need to pull pywinauto source separately.
"""
import win32gui
from pywinauto import Desktop
from pywinauto.application import Application


# ---- Connect to a running window by handle ----

def connect_by_title(title: str):
    """Connect to a window by its title."""
    hwnd = win32gui.FindWindow(None, title)
    # For Qt windows, use class name:
    # hwnd = win32gui.FindWindow('Qt51514QWindowIcon', '微信')
    if hwnd == 0:
        raise RuntimeError(f"Window '{title}' not found")
    d = Desktop(backend='uia')
    return d.window(handle=hwnd)


# ---- Read control tree ----

def dump_tree(win, depth=4):
    """Print the full UIA control tree."""
    win.print_control_identifiers(depth=depth)


def find_by_type(win, control_type: str):
    """Find all controls of a given type."""
    return [c for c in win.descendants()
            if c.element_info.control_type == control_type]


def find_by_text(win, text: str):
    """Find controls containing specific text."""
    return [c for c in win.descendants()
            if text in c.window_text()]


# ---- Read list content ----

def read_list_items(win, list_title: str):
    """Read all items from a List control by its title."""
    lists = find_by_type(win, 'List')
    for lst in lists:
        if lst.window_text() == list_title:
            return [c.window_text() for c in lst.children()]
    return []


# ---- Read editable text ----

def read_edit_text(win):
    """Read text from the first Edit control."""
    edits = find_by_type(win, 'Edit')
    if edits:
        return edits[0].window_text()
    return ""


# ---- Click a button by text ----

def click_button(win, button_text: str):
    """Find and click a button by its text."""
    buttons = find_by_type(win, 'Button')
    for btn in buttons:
        if btn.window_text() == button_text:
            btn.click()
            return True
    return False


# ---- Connect to a process ----

def connect_by_pid(pid: int):
    """Connect to a process by PID via UIA backend."""
    app = Application(backend='uia').connect(process=pid)
    return app.top_window()


# ---- Wait for window to appear ----

def wait_for_window(title: str, timeout: float = 10):
    """Wait for a window to appear."""
    import time
    deadline = time.time() + timeout
    while time.time() < deadline:
        hwnd = win32gui.FindWindow(None, title)
        if hwnd != 0:
            return Desktop(backend='uia').window(handle=hwnd)
        time.sleep(0.5)
    raise TimeoutError(f"Window '{title}' not found within {timeout}s")
