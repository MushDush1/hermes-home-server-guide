# Hermes Home Server Guide

个人 Home Lab / 自动化方案记录。

## 目录

- [WeChat 4.x 自动化方案](docs/wechat-automation.md) — 基于 pyweixin + pywinauto UIA，微信 4.1.6.14 完全自动化，含监控 Bot + 文件传输脚本

## 环境

| 组件 | 版本 |
|------|------|
| OS | Windows 10/11 x64 |
| Python | >= 3.10 |
| WeChat | **4.1.6.14**（唯一兼容版本，4.1.6.46 / 4.1.10 不可用） |
| pywinauto | >= 0.6.8（UIA backend） |
| pywechat127 | 1.9.8 |

> 微信必须使用 4.1.6.14——此版本保留 `mmui::MainWindow` 类名和完整 Qt Accessibility 树。后续版本切换了 UI 框架但未暴露 UIA 接口，导致 pywinauto 无法读取控件树。

## 快速开始

```bash
pip install pywechat127
python code/monitor_bot.py   # 启动 UIA 监控 Bot
python code/send_file.py     # 剪贴板传文件
```
