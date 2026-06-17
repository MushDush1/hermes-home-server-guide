# Hermes Home Server Guide

个人 Home Lab / 自动化方案记录。

## 目录

- [WeChat 4.x 自动化方案](docs/wechat-automation.md) — 完整指南
- [反向解析与实现原理](#反向解析与实现原理) — 本文

## 环境

| 组件 | 版本 |
|------|------|
| OS | Windows 10/11 x64 |
| Python | >= 3.10 |
| WeChat | **4.1.6.14**（唯一兼容版本） |
| pywinauto | >= 0.6.8 |
| pywechat127 | 1.9.8 |

## 快速开始

```bash
pip install pywechat127
python code/monitor_bot.py      # UIA 监控 Bot
python code/send_file.py        # CF_HDROP 文件传输
python code/pywinauto_uia.py    # UIA 参考
```

---

## 反向解析与实现原理

### 1. 微信 UIA 控件的版本演进

微信 PC 4.x 使用 **Qt 框架**（`Qt51514QWindowIcon`），所有 UI 控件理论上可通过 Windows UIA（UI Automation）访问。但不同版本暴露程度天差地别：

```
微信版本          Win32 类名              UIA 类名               UIA 控件树
───────────────────────────────────────────────────────────────────
4.1.6.14         Qt51514QWindowIcon  →  mmui::MainWindow    →  100+ 个控件 ✅
4.1.6.46         Qt51514QWindowIcon  →  Qt51514QWindowIcon  →  1 个 Pane  ❌
4.1.10.31        Qt51514QWindowIcon  →  Qt51514QWindowIcon  →  1 个 Pane  ❌
```

**结论：4.1.6.14 是最后保留 `mmui::` 命名空间 + 完整 Qt Accessibility 树的版本。** 后续版本（.46 起）切换了 UI 内部架构，Qt 不再向 Windows 注册 Accessibility Provider，导致 `pywinauto(backend='uia')` 只能看到顶层窗口壳。

### 2. 为什么讲述人 / QT_ACCESSIBILITY 救不了新版

尝试过：

- 设环境变量 `QT_ACCESSIBILITY=1` 启动微信 → 无效
- 先启 Windows Narrator（讲述人）再启动微信 → 无效
- 两者组合 → 无效

**根因：** 微信 4.1.6.46+ 在编译 Qt 时未链接 `Qt5AccessibilitySupport`，或主动禁用了 `QAccessible::setRootObject`。这不是运行时配置问题，是二进制编译差异。无法通过外部手段恢复。

### 3. UIA 控件树结构（4.1.6.14）

```
Dialog "微信"                                ← 主窗口
├── GroupBox                                 ← 顶层容器
│   ├── Toolbar "导航"                        ← 左侧 Tab 栏
│   │   auto_id="main_tabbar"
│   ├── GroupBox (分割线)
│   └── Custom auto_id="main_window_main_splitter_view"
│       ├── Edit (搜索框, x=1405 y=150)        ← 联系人搜索
│       ├── List "会话" (x=1355 y=196)         ← 左侧聊天列表
│       │   ├── ListItem "联系人A"
│       │   ├── ListItem "群聊B"
│       │   └── ...
│       └── List "消息" (x=1116 y=306)         ← 右侧消息面板 ★
│           ├── ListItem "对方发的第一条消息"
│           ├── ListItem "动画表情"
│           ├── ListItem "我回复的消息"
│           └── ...
├── Toolbar (最小化/最大化/关闭)
└── Edit (输入框, x=1136 y=1085)              ← 消息输入
```

**关键发现：** `List "消息"` 控件按时间顺序列出所有可见消息，每一条是独立的 `ListItem`，文本内容即 `window_text()`。持续监控该 List 长度即可检测新消息，无需截图、OCR 或外部分析。

```
监控循环:
  prev = len(List["消息"].children)
  loop:
    curr = len(List["消息"].children)
    if curr > prev:
      new_msgs = List["消息"].children[prev:]
      for each new_msg:
        if not 动画表情 and not timestamp:
          reply(new_msg.window_text())
    prev = curr
    sleep(8)
```

### 4. CF_HDROP 文件传输原理

pyweixin 的 `Files.send_files_to_friend()` 可靠，但存在 `NoSuchFriendError` 风险。备用方案：Windows 剪贴板 CF_HDROP 格式。

```
DROPFILES 结构（Unicode）:
  Offset 0:  pFiles = 20    (文件路径列表起始偏移)
  Offset 4:  pt.x = 0
  Offset 8:  pt.y = 0
  Offset 12: fNC  = 0       (非客户端坐标)
  Offset 16: fWide = 1      (Unicode 路径)
  Offset 20: "C:\path\to\file.pdf\0\0"  (UTF-16LE, 双 null 终止)

操作流程:
  1. GlobalAlloc → GlobalLock → 写入 DROPFILES + 文件路径 → GlobalUnlock
  2. SetClipboardData(CF_HDROP=15, hglobal)  ← 剪贴板持有内存
  3. pyautogui 激活微信窗口 → Ctrl+V → Enter
```

多文件支持：在路径列表中以 `\0` 分隔每个文件，最后双 `\0\0` 终止。

### 5. pyweixin 架构

```
pyweixin (Hello-Mr-Crab/pywechat)
├── WeChatTools.py
│   ├── Tools       - 微信路径/运行状态/window handle
│   └── Navigator   - 打开各种界面（会话、联系人、朋友圈）
├── WeChatAuto.py
│   ├── Messages    - send_messages_to_friend()
│   ├── Files       - send_files_to_friend()
│   ├── Contacts    - get_friends_info()
│   └── Monitor     - listen_on_chat()
├── WinSettings.py  - SystemSettings（Windows 系统设置）
├── utils.py        - parse_chat_history, scan_for_new_messages
├── Uielements.py   - UIA 控件定位配置
├── Config.py       - GlobalConfig 全局参数
└── Errors.py       - 异常定义
```

底层依赖 `pywinauto` 的 UIA backend 操作 Qt 窗口，通过 `win32gui.FindWindow('Qt51514QWindowIcon', '微信')` 获取 HWND，再 `Desktop(backend='uia').window(handle=hwnd)` 获得控件树。

### 6. 自动更新对抗

微信 4.x 的 `WeixinUpdate.exe` 会在后台静默升级到最新版，覆盖 exe 和版本目录。对抗方案：

```bash
# 安装 4.1.6.14 后立即执行：
mv 4.1.6.14/WeixinUpdate.exe 4.1.6.14/WeixinUpdate.exe.bak
echo "dummy" > 4.1.6.14/WeixinUpdate.exe
```

进程守护（taskkill 无效时）：
```python
import psutil
for p in psutil.process_iter():
    if 'weixin' in p.name().lower():
        p.suspend()  # 先挂起
        p.kill()     # 再杀
```
