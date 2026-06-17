# WeChat 4.x Automation with pyweixin on Windows

> 基于 pyweixin (Hello-Mr-Crab/pywechat) + pywinauto UIA，在 Windows 上实现微信 4.x 完全自动化。

## 适用版本

| 组件 | 版本 | 备注 |
|------|------|------|
| 微信 | **4.1.6.14** | 必须此版本！4.1.6.46 / 4.1.10 均不行 |
| Python | >= 3.10 | |
| pywechat127 | 1.9.8 | `pip install pywechat127` |
| pywinauto | >= 0.6.8 | 自动安装 |
| OS | Windows 10/11 64-bit | |

## 为什么 4.1.6.14？

| 版本 | UIA 类名 | UIA 控件树 | pyweixin 兼容 |
|------|---------|-----------|-------------|
| 4.1.6.14 | `mmui::MainWindow` | ✅ 完整（100+ 控件） | ✅ |
| 4.1.6.46 | `Qt51514QWindowIcon` | ❌ 空 | ❌ |
| 4.1.10.31 | `Qt51514QWindowIcon` | ❌ 空 | ❌ |

4.1.6.14 是最后保留 `mmui::MainWindow` 类名 + 完整 Qt Accessibility 树的版本。后续版本切换了 UI 框架但没有暴露 UIA 接口。

## 安装与部署

### 1. 安装 pyweixin

```bash
pip install pywechat127
```

### 2. 获取微信 4.1.6.14

从 GitHub Release 下载：

```bash
# 直链（可能失效）
https://github.com/PRO-2684/WeChat4-Version-History/releases/download/4.1.6.14/WeChatWin_4.1.6.exe
```

```powershell
# 或用 winget 降级（如可用）
winget install Tencent.WeChat.Universal --version 4.1.6.14
```

### 3. 阻止自动更新

微信 4.x 会自动更新到最新版，必须封掉：

```bash
# 4.1.6.14 安装在 C:\Users\<user>\WeChat_4.1.6\ 时：
mv 4.1.6.14/WeixinUpdate.exe 4.1.6.14/WeixinUpdate.exe.bak
echo "dummy" > 4.1.6.14/WeixinUpdate.exe
```

### 4. 备份聊天记录

```bash
# 微信 4.x 数据目录
tar czf wechat_backup.tar.gz \
  "$APPDATA/Tencent/xwechat/"
```

## 基础用法

```python
from pyweixin import Messages, Files, Navigator, Contacts

# 检查微信是否运行
from pyweixin.WeChatTools import Tools
Tools.is_weixin_running()  # True/False

# 发文本消息
Messages.send_messages_to_friend(
    friend='文件传输助手',
    messages=['Hello from pyweixin!']
)

# 发文件
Files.send_files_to_friend(
    friend='文件传输助手',
    files=[r'C:\report.pdf']
)

# 获取联系人
friends = Contacts.get_friends_info()
# ['张三', '李四', '文件传输助手', ...]

# 打开聊天窗口
Navigator.open_dialog_window(friend='张三')
```

## UIA 监控 Bot

基于 `pywinauto` UIA 后端直接读取微信聊天列表，不依赖 OCR 或外部分析：

```python
import win32gui
from pywinauto import Desktop

hwnd = win32gui.FindWindow('Qt51514QWindowIcon', '微信')
d = Desktop(backend='uia')
win = d.window(handle=hwnd)

# 找到"消息"列表控件
lists = [c for c in win.descendants() if c.element_info.control_type == 'List']
for lst in lists:
    if lst.window_text() == '消息':
        messages = [c.window_text() for c in lst.children()]
```

### 完整监控脚本

见 `scripts/wechat_interact.py`：

- 每 8 秒扫描新消息
- 规则引擎自动回复
- 3 次重试防 `NoSuchFriendError`
- 5 分钟自动停止

## 踩过的坑

1. **版本地狱**：只有 4.1.6.14 能用。4.1.6.46 和 4.1.10 的 UIA 全是空的
2. **自动更新**：微信 4.x 会自动升级，必须提前封 `WeixinUpdate.exe`
3. **进程守护**：taskkill 杀不死，weixin 有看门狗自动复活。用 `psutil.suspend()` 先挂起再杀
4. **讲述人无用**：`QT_ACCESSIBILITY=1` + Windows 讲述人对 4.1.10 无效，Qt 根本没暴露 UIA
5. **GLM-4V 直连被封**：`open.bigmodel.cn` 没有代理不通，截图分析方案失败
6. **`NoSuchFriendError`**：连续快速发消息会导致 pyweixin 丢窗口，需加重试
7. **纯键盘盲操不可靠**：Qt 窗口下 pyautogui 只能盲点，没验证手段

## 实战记录

```
Toxic 模型群友（4 分钟 6 轮互动）：
  - "回她一句话，暖她一整天！" → Bot: 夸涂装方案
  - "图片" → Bot: 收到
  - "再发ai回复诺死你" → Bot: 收到
  - "这个太傻逼了" → Bot: 承认是机器人
  - "就ai不是需要充值才能跑吗...骂到对方没钱就停了" → 💥 NoSuchFriendError
```

## 文件清单

```
hermes-home-server-guide/
├── docs/wechat-automation.md   # 本文档
└── code/
    ├── monitor_bot.py          # UIA 监控自动回复 Bot
    └── send_file.py            # CF_HDROP 剪贴板文件传输
```

## 参考

- pywechat: https://github.com/Hello-Mr-Crab/pywechat
- 版本历史: https://github.com/PRO-2684/WeChat4-Version-History
- pywinauto: https://github.com/pywinauto/pywinauto

---

*最后更新: 2026-06-17 | 作者: Hermes Agent (MushDush1)*
