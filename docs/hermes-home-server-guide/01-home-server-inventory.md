# 01 - Home Server Inventory

本章只在家里 Windows 主机上执行。当前笔记本不要运行这里的命令。

目标：在不修改现有 Hermes 的前提下，把服务器现状盘清楚，形成后续迁移的事实基础。

## 服务器基础信息

在家里服务器 PowerShell 中记录：

```powershell
$PSVersionTable
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, CsProcessor, CsTotalPhysicalMemory
Get-PSDrive -PSProvider FileSystem
ipconfig
```

记录到迁移笔记：

```text
OS:
CPU:
RAM:
Disk:
LAN IP:
公网/内网穿透方式:
远程访问方式:
开机自启方式:
```

## Runtime 盘点

```powershell
python --version
node --version
npm --version
git --version
where python
where node
where git
```

记录：

```text
Python:
Node:
Git:
包管理器:
Hermes 运行方式:
Hermes 目录:
```

## Hermes 现状盘点

只读查看，不修改：

```powershell
cd <HERMES_ROOT>
git status --short --branch
git remote -v
Get-ChildItem -Force
Get-ChildItem -Recurse -File -Include *.env*,*.json,*.yaml,*.yml,*.toml,*.ini,*.py,*.ts,*.js,*.md | Select-Object FullName
```

记录：

```text
主入口文件:
配置文件:
数据库/存储:
日志目录:
bot 入口:
已知后台进程:
当前启动命令:
```

## 模型接入盘点

记录已接入模型，不记录真实密钥：

```text
Provider: OpenAI
Env vars:
Base URL:
Model IDs:
用途标签:
调用文件:

Provider: DeepSeek
Env vars:
Base URL:
Model IDs:
用途标签:
调用文件:

Provider: Kimi
Env vars:
Base URL:
Model IDs:
用途标签:
调用文件:

Provider: GLM
Env vars:
Base URL:
Model IDs:
用途标签:
调用文件:
```

注意：DeepSeek 官方文档显示 API 可通过 OpenAI/Anthropic 兼容方式访问，并提示 `deepseek-chat` 和 `deepseek-reasoner` 有弃用日期。迁移时不要把这些旧模型名写死。

## Agent App / CLI 盘点

```powershell
where codex
where claude
where deepseek
where opencode
codex --version
claude --version
```

如果某个命令不存在，只记录“未安装”，不要为了盘点临时安装。

记录：

```text
Codex:
Claude Code:
DeepSeek TUI:
OpenCode / other:
本地脚本:
```

## 聊天入口盘点

```text
QQ bot:
  框架:
  启动方式:
  消息回调:
  当前权限:

微信 bot:
  框架:
  账号类型:
  启动方式:
  消息回调:
  当前权限:

手机端:
  入口:
  通知方式:
```

微信建议先使用独立 Hermes 账号。不要在第一阶段接管主微信。

## 盘点完成标准

- 知道 Hermes 当前在哪里、怎么启动、怎么停。
- 知道每个模型从哪里配置、谁在调用。
- 知道每个 bot 的消息入口在哪里。
- 知道 Codex/Claude Code/DeepSeek TUI 是否已安装。
- 没有修改任何源代码、配置、密钥或登录状态。

