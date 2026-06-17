# Hermes Home Server Guide

个人 Home Lab / 自动化方案记录。

## 目录

- [WeChat 4.x 自动化方案](docs/wechat-automation.md) — 基于 pyweixin + pywinauto UIA，微信 4.1.6.14 完全自动化，含监控 Bot + 文件传输脚本

## 环境

- Windows 10/11 x64
- Python >= 3.10
- WeChat 4.1.6.14（必须此版本）

## 快速开始

```bash
pip install pywechat127
python code/monitor_bot.py   # 启动 UIA 监控 Bot
python code/send_file.py     # 剪贴板传文件
```
