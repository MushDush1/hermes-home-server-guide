# 02 - Target Architecture

目标架构：Hermes Core 是控制面；模型、agent app、CLI、bot 都是可替换适配器。

## 总体结构

```text
QQ / WeChat / Mobile / Codex Bridge
              |
        Chat Gateway
              |
Hermes Core
    |      |      |          |       |
 Task   Memory Permission Decision Trace
 Queue  Store  Kernel     Engine   Store
    |      |      |          |       |
 Model Router      Executor Router
    |                    |
 GPT / DeepSeek /        Codex / Claude Code /
 Kimi / GLM              DeepSeek TUI / Generic CLI
    |
 Finance Data Router
    |
 Market Data / Portfolio Data / Education Sources
    |
 Learning Intake Router
    |
 Web / RSS / Bilibili / Docs / User-provided Files
```

## Hermes Core

职责：

- 接收入口消息并创建 Task。
- 维护 Task 状态：created、planning、waiting_approval、running、failed、completed。
- 选择模型和执行器。
- 调用权限核查。
- 调用 Decision Engine，把建议、推荐、决策和行动分开。
- 写入 trace、日志和长期记忆。
- 向聊天入口回调结果。
- 在金融任务中强制记录数据来源、数据延迟、假设、风险提示和是否涉及个性化建议。
- 在每日学习任务中强制记录来源、授权方式、提取方式、可信度、摘要和长期记忆候选项。

Hermes Core 不应该直接依赖某个具体模型 SDK，也不应该直接拼接 Codex/Claude/DeepSeek 的命令行参数。

## Decision Engine

Hermes 要成为分身，必须能做一部分决策，而不是永远把选择题推回给你。Decision Engine 负责判断“这件事 Hermes 能不能自己拍板”。

每个决策都要输出：

```json
{
  "decision_id": "decision_...",
  "task_id": "task_...",
  "mode": "autonomous_decision",
  "decision": "use_codex_for_repo_review",
  "reason": "code.agent capability, low external risk, reversible workspace",
  "confidence": 0.82,
  "risk_level": "L2",
  "reversibility": "easy",
  "requires_approval": false,
  "review_after": "task_completion"
}
```

四种输出必须区分：

- `advice`：解释和教育，不替你选。
- `recommendation`：给出推荐，但等待你决定。
- `decision`：Hermes 在授权范围内拍板。
- `action`：Hermes 执行已经批准或被授权的决策。

默认规则：

- 低风险、可逆、金额为 0、不代表你对外发言的事情，可以自动决策。
- 中风险或会消耗明显时间/算力的事情，可以自动决策但要事后汇报。
- 涉及身份、钱、账号、外发消息、真实交易、删除数据的事情，必须审批。
- 置信度不足时，Hermes 应该提出一个默认决策和原因，而不是只罗列选项。

## Model Registry

每个模型以 registry 项登记：

```yaml
models:
  - id: openai.gpt-codex
    provider: openai
    model: gpt-5.2-codex
    base_url_env: OPENAI_BASE_URL
    api_key_env: OPENAI_API_KEY
    capabilities: [code.agent, reasoning.deep, tool.use]
    cost_tier: high
    health: unknown

  - id: deepseek.fast
    provider: deepseek
    model: deepseek-v4-flash
    base_url: https://api.deepseek.com
    api_key_env: DEEPSEEK_API_KEY
    capabilities: [fast.reply, chinese, cheap.batch]
    cost_tier: low
    health: unknown

  - id: kimi.long
    provider: kimi
    model: <fill-on-home-server>
    base_url_env: KIMI_BASE_URL
    api_key_env: KIMI_API_KEY
    capabilities: [long.context, chinese, research]
    cost_tier: medium
    health: unknown

  - id: glm.general
    provider: glm
    model: <fill-on-home-server>
    base_url_env: GLM_BASE_URL
    api_key_env: GLM_API_KEY
    capabilities: [general, chinese, structured.output]
    cost_tier: medium
    health: unknown
```

路由时用能力标签，不直接写模型名：

```text
research.deep -> 优先 deep reasoning / long context
code.agent -> 优先 Codex 或 Claude Code 执行器
fast.reply -> 优先低延迟模型
cheap.batch -> 优先低价批处理模型
long.context -> 优先长上下文模型
```

## Executor Registry

每个外部 agent/app/CLI 以执行器登记：

```yaml
executors:
  - id: codex.local
    kind: cli
    command: codex
    risk: writes_files
    workspace_policy: isolated_project_dir
    timeout_seconds: 1800
    capabilities: [code.agent, repo.edit, tests]

  - id: claude-code.local
    kind: cli
    command: claude
    risk: writes_files
    workspace_policy: isolated_project_dir
    timeout_seconds: 1800
    capabilities: [code.agent, mcp.client, repo.edit]

  - id: deepseek.tui
    kind: interactive_cli
    command: <fill-on-home-server>
    risk: text_only_by_default
    workspace_policy: isolated_scratch_dir
    timeout_seconds: 900
    capabilities: [research, chinese, draft]

  - id: generic.cli
    kind: cli
    command: <fill-on-home-server>
    risk: configurable
    workspace_policy: isolated_scratch_dir
    timeout_seconds: 600
    capabilities: [custom]
```

## Finance Data Router

金融数据不要直接散落在各个 agent prompt 里。建议新增 Finance Data Router，把行情、持仓、预算和教育材料统一成只读数据源。

建议数据源类型：

- `market_data`：价格、指数、基金/ETF 基础信息、汇率、利率等。
- `portfolio_snapshot`：手动录入或只读同步的资产、成本、现金、负债。
- `education_source`：Investor.gov、FINRA、交易所、基金公司披露文件等教育/披露资料。
- `news_research`：新闻和公告，只能作为研究材料，不能单独触发买卖结论。

金融任务输出必须带：

- 数据来源。
- 时间戳和可能的延迟。
- 关键假设。
- 风险和不确定性。
- “教育/模拟/建议草稿/真实交易”分类。

默认禁止：

- 自动下单。
- 自动跟单。
- 保证收益表述。
- 只凭单一模型输出给出买卖指令。
- 把聊天中的临时风险偏好写成永久投资画像。

## Learning Intake Router

Hermes 的向外学习能力应单独走 Learning Intake Router，不要把“搜索、抓网页、看视频、写记忆”混在主 agent prompt 里。

输入来源分级：

- `public_docs`：官方文档、论文、项目 README、监管/教育资料，优先级最高。
- `public_web`：公开网页、博客、新闻、论坛，需要记录可信度。
- `video_metadata`：视频标题、简介、合集、UP 主、发布时间、链接。
- `video_transcript`：平台字幕、创作者字幕、你手动导出的字幕。
- `user_provided`：你上传的 PDF、笔记、截图、视频链接或收藏夹。
- `private_account`：需要登录态的内容，默认不自动化，必须审批。

学习任务输出统一成：

```json
{
  "source_id": "bilibili.video.BV...",
  "source_type": "video_transcript",
  "access_method": "user_provided_url_or_browser",
  "title": "...",
  "author": "...",
  "published_at": "...",
  "fetched_at": "2026-05-21T12:00:00+08:00",
  "summary": "...",
  "key_points": [],
  "claims": [],
  "uncertainties": [],
  "memory_candidates": [],
  "copyright_boundary": "summary_only_no_media_archive"
}
```

长期记忆写入必须二次筛选：只保存稳定概念、可复用流程、重要偏好和已验证事实，不保存大段原文或视频字幕全文。

所有执行器必须捕获：

- command
- args
- cwd
- env allowlist
- stdin
- stdout/stderr
- exit code
- timeout
- output artifact paths

## Chat Gateway

QQ/微信/手机入口只做四件事：

- 鉴别用户身份。
- 收消息。
- 发消息。
- 转发审批确认。

不要把模型选择、长期记忆、权限判断写在 bot handler 里。

统一消息格式：

```json
{
  "channel": "wechat",
  "sender_id": "user-or-group-id",
  "message_id": "platform-message-id",
  "text": "帮我调研...",
  "attachments": [],
  "received_at": "2026-05-21T12:00:00+08:00"
}
```

## Memory Store

建议分四类：

- `profile_memory`：你的长期偏好、稳定身份信息。
- `project_memory`：项目级事实、目录、架构、约定。
- `task_workspace`：单次任务的中间推理、草稿、临时文件。
- `evidence_store`：网页、文档、日志、命令输出等原始证据。

长期记忆写入规则：

- 必须有来源。
- 必须有时间。
- 必须说明为什么值得长期保存。
- 不保存一次性猜测。
