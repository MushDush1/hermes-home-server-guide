# 03 - Migration Steps

本章只在家里 Windows 主机执行。当前笔记本不要运行这里的命令。

## Step 0 - 冻结和备份

目标：先能回滚，再开始迁移。

```powershell
$date = Get-Date -Format "yyyyMMdd-HHmmss"
Copy-Item -Recurse -Force "<HERMES_ROOT>" "<BACKUP_ROOT>\hermes-$date"
```

同时备份但不要公开：

- `.env`
- bot 配置
- 数据库
- 记忆文件
- 启动脚本
- Windows 任务计划配置

验证：

```powershell
Test-Path "<BACKUP_ROOT>\hermes-$date"
Get-ChildItem "<BACKUP_ROOT>\hermes-$date" -Force
```

回滚：

```powershell
Stop-Process -Name "<HERMES_PROCESS_NAME>" -ErrorAction SilentlyContinue
Rename-Item "<HERMES_ROOT>" "<HERMES_ROOT>.broken-$date"
Copy-Item -Recurse "<BACKUP_ROOT>\hermes-$date" "<HERMES_ROOT>"
```

## Step 1 - 建 secrets 模板

在仓库里只保留模板：

```text
.env.example
```

模板示例：

```dotenv
OPENAI_API_KEY=
OPENAI_BASE_URL=
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
KIMI_API_KEY=
KIMI_BASE_URL=
GLM_API_KEY=
GLM_BASE_URL=

HERMES_DATA_DIR=
HERMES_LOG_DIR=
HERMES_APPROVAL_REQUIRED=true
```

真实 `.env` 只留在家里服务器，不提交、不复制到聊天、不放进文档。

验证：

```powershell
Test-Path ".env.example"
Test-Path ".env"
```

## Step 2 - 引入 Model Registry

先把现有 DeepSeek、Kimi、GLM、GPT 调用配置迁移到 registry 文件，不急着重写业务逻辑。

建议文件：

```text
config/models.yaml
```

迁移顺序：

1. 把现有模型名、base URL、env var 名称填入 registry。
2. 给每个模型加能力标签。
3. 保留旧调用路径。
4. 新增一个 model router 函数读取 registry。
5. 只让一个低风险研究任务走新 router。

验证：

```text
输入：总结一段普通文本
期望：router 能选到 fast.reply 模型并返回结果
失败：回退到旧模型调用路径
```

回滚：业务代码继续使用旧模型调用路径，删除 router 引用即可。

## Step 3 - 引入 Executor Registry

建议文件：

```text
config/executors.yaml
```

先登记，不立即开放自动执行：

```yaml
executors:
  - id: codex.local
    enabled: false
  - id: claude-code.local
    enabled: false
  - id: deepseek.tui
    enabled: false
  - id: generic.cli
    enabled: false
```

每个 adapter 必须支持 dry run：

```json
{
  "executor_id": "codex.local",
  "dry_run": true,
  "task": "explain repo status",
  "cwd": "<isolated-workspace>"
}
```

验证：

- dry run 只打印将要执行的命令。
- 不启动 CLI。
- 不修改文件。

回滚：禁用 registry 项即可。

## Step 4 - 抽象 Task

把 QQ/微信/Codex bridge 的请求统一转为 Task：

```json
{
  "id": "task_...",
  "source": "wechat",
  "goal": "调研某主题并给出建议",
  "risk": "observe",
  "expected_output": "markdown summary",
  "allowed_capabilities": ["research", "web.read"],
  "approval_policy": "required_for_act",
  "created_at": "2026-05-21T12:00:00+08:00"
}
```

验证：

- 同一任务从 QQ 和微信进入后结构一致。
- Task 创建不触发外部工具执行。
- Task 有唯一 id 和 trace id。

## Step 5 - 接入审批队列

高风险动作必须生成 Approval：

```json
{
  "approval_id": "approval_...",
  "task_id": "task_...",
  "action": "send_wechat_message",
  "reason": "用户要求代发回复",
  "params_preview": {
    "to": "contact_alias",
    "text": "..."
  },
  "risk": "external_send",
  "rollback": "无法完全回滚，只能补发更正消息"
}
```

验证：

- 发微信、删文件、改仓库、花钱、账号操作都被拦截。
- 审批确认前不会执行。
- 审批结果写入 trace。

## Step 6 - 迁移聊天入口

顺序：

1. QQ bot 只保留消息收发。
2. 微信 bot 只保留消息收发。
3. 两者都转发到 Hermes Core。
4. Hermes Core 回调消息结果。

验证：

- bot handler 中没有模型调用。
- bot handler 中没有长期记忆写入。
- bot handler 中没有高风险执行逻辑。

回滚：bot handler 重新指回旧 Hermes 入口。

## Step 7 - 开放执行器

开放顺序：

1. `generic.cli` dry run。
2. `codex.local` 只读/解释类任务。
3. `codex.local` 隔离目录代码任务。
4. `claude-code.local` 隔离目录代码任务。
5. `deepseek.tui` 文本研究任务。

每次只开放一个 executor，每次开放后跑三类测试：

- 成功任务。
- 超时任务。
- 失败任务。

失败不能拖垮 Hermes Core。

## Step 8 - 接入金融数据，只读优先

金融接口分三步接入，不能一开始接交易权限：

1. 教育资料和公开数据：只读。
2. 资产/预算快照：手动录入或只读同步。
3. 模拟组合：paper portfolio，不连接真实券商交易。

建议新增：

```text
config/finance-sources.yaml
data/finance/
  portfolio-snapshots/
  watchlists/
  paper-portfolios/
  research-notes/
```

`finance-sources.yaml` 模板：

```yaml
finance_sources:
  - id: investor.gov
    kind: education
    access: public_web
    risk: read_only

  - id: finra.education
    kind: education
    access: public_web
    risk: read_only

  - id: market.public
    kind: market_data
    access: api
    api_key_env: MARKET_DATA_API_KEY
    risk: read_only
    notes: "填入家里服务器实际选择的数据源"

  - id: portfolio.manual
    kind: portfolio_snapshot
    access: local_file
    risk: private_read
```

验证：

- Hermes 可以解释“这个价格/数据来自哪里、什么时候更新”。
- Hermes 可以输出预算和风险解释。
- Hermes 可以维护模拟组合。
- Hermes 不会生成真实下单请求。

回滚：

- 禁用 `finance_sources`。
- 删除或隔离 `data/finance/` 中的测试数据。
- 保留已生成的研究笔记作为普通文档，不作为交易依据。

## Step 9 - 接入每日向外学习

已有每日定时学习时，先把它改造成“学习队列 + 来源适配器 + 记忆候选审核”，不要让定时任务直接写长期记忆。

建议新增：

```text
config/learning-sources.yaml
data/learning/
  queue/
  raw-metadata/
  transcripts/
  summaries/
  memory-candidates/
  rejected/
```

`learning-sources.yaml` 模板：

```yaml
learning_sources:
  - id: official_docs
    kind: public_docs
    access: web
    trust: high
    default_action: summarize_and_extract_claims

  - id: bilibili.watchlist
    kind: video_platform
    platform: bilibili
    access: browser_or_user_provided_url
    trust: medium
    default_action: metadata_then_transcript_if_available
    media_download: disabled

  - id: user.uploads
    kind: user_provided
    access: local_file
    trust: depends_on_source
    default_action: summarize_and_ask_before_memory
```

每日任务流程：

1. 读取学习队列。
2. 按来源优先级取少量内容。
3. 先取标题、简介、发布时间、作者和链接。
4. 如果有合法可访问字幕，提取字幕；没有字幕就只做元数据摘要或请求你确认是否需要人工处理。
5. 总结成学习笔记。
6. 生成长期记忆候选项。
7. 等待审核或按低风险规则入库。

B 站视频建议策略：

- 优先使用你提供的视频链接、收藏夹、稍后再看导出的链接或公开搜索结果。
- 优先处理标题、简介、分 P、合集、评论区置顶、创作者字幕。
- 如果用 yt-dlp，只使用 `--list-subs`、`--write-subs`、`--write-auto-subs`、`--skip-download` 这类字幕/元数据路径。
- 默认不下载视频/音频，不批量抓取，不绕过登录限制。

验证：

- 每日学习产物包含来源链接和时间。
- 没有把视频原文或字幕全文直接写入长期记忆。
- 没有下载媒体文件。
- 需要登录态或私密内容时进入审批。

回滚：

- 暂停每日学习计划任务。
- 禁用 `learning_sources`。
- 保留 `summaries/`，删除未审核的 `memory-candidates/`。

## Step 10 - 接入 Decision Engine

目标：让 Hermes 不再只给建议，而是在授权范围内能自己决定。

建议新增：

```text
config/decision-policy.yaml
data/decisions/
  decisions.jsonl
  reviews/
```

`decision-policy.yaml` 模板：

```yaml
decision_policy:
  autonomous:
    - summarize_public_docs
    - choose_model_for_low_risk_task
    - choose_executor_dry_run
    - write_scratch_report
    - schedule_next_learning_item

  report_after:
    - spend_extra_compute_under_daily_budget
    - retry_failed_read_only_task_once
    - create_paper_portfolio_note

  approval_required:
    - send_external_message
    - edit_repo_files
    - run_unknown_command
    - access_private_account
    - read_full_financial_profile
    - create_personalized_investment_recommendation

  forbidden:
    - real_trade
    - money_transfer
    - delete_non_scratch_files_without_approval
    - impersonate_user_without_disclosure
```

迁移顺序：

1. 先只让 Decision Engine 给每个建议打标签：`advice`、`recommendation`、`decision`、`action`。
2. 再开放低风险自动决策，例如选择模型、选择学习来源、生成报告格式。
3. 然后开放“先做后报”的可逆决策，例如只读任务失败后重试一次。
4. 最后把审批队列接入中高风险决策。

验证：

- 同一个任务，Hermes 能说清楚“我是在建议、推荐、决定，还是执行”。
- 低风险任务能自己选模型/执行器。
- 高风险任务不会因为“我很确定”而绕过审批。
- 每个 decision 都写入 `data/decisions/decisions.jsonl`。

回滚：

- 把 `decision_policy.autonomous` 清空。
- Hermes 回退到 recommendation-only 模式。
- 保留历史 decision log 供复盘。
