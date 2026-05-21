# 05 - Operations

本章用于 Hermes 在家里 Windows 主机上的日常运行和维护。

## Windows 常驻运行

推荐优先级：

1. Windows 服务：适合稳定长期运行。
2. 任务计划程序：适合简单启动和重启。
3. 手动 PowerShell：只用于调试。

任务计划程序建议配置：

```text
触发器：用户登录时 / 开机时
操作：powershell.exe
参数：-ExecutionPolicy Bypass -File <HERMES_ROOT>\scripts\start-hermes.ps1
起始位置：<HERMES_ROOT>
```

启动脚本必须：

- 设置工作目录。
- 加载 `.env`。
- 写启动日志。
- 检查端口占用。
- 启动 Hermes Core。
- 不打印真实密钥。

## 日志目录

建议结构：

```text
HERMES_LOG_DIR/
  core/
    2026-05-21.log
  tasks/
    task_<id>.jsonl
  executors/
    codex.local/
    claude-code.local/
    deepseek.tui/
  approvals/
    2026-05-21.jsonl
  finance/
    research/
    paper-portfolios/
    risk-reviews/
  learning/
    daily/
    source-health/
    memory-candidates/
  health/
    weekly-2026-W21.md
```

Trace 事件建议为 JSON Lines：

```json
{"type":"task.created","task_id":"task_...","source":"wechat","at":"2026-05-21T12:00:00+08:00"}
{"type":"model.selected","task_id":"task_...","model_id":"deepseek.fast","reason":"fast.reply"}
{"type":"approval.requested","task_id":"task_...","approval_id":"approval_...","risk":"external_send"}
{"type":"executor.finished","task_id":"task_...","executor_id":"codex.local","exit_code":0,"duration_ms":12000}
```

## 每周健康检查

每周固定跑一次，只读优先：

```text
1. Hermes Core 是否能启动。
2. QQ/微信入口是否能收消息。
3. 模型 registry 中每个模型是否可用。
4. Executor registry 中每个执行器是否能 dry run。
5. 审批队列是否能创建、同意、拒绝。
6. 日志是否正常轮转。
7. 最近失败任务是否有复盘。
8. 金融数据源是否仍可用、是否有延迟、是否误触发交易权限。
9. 每日学习是否只处理授权来源、是否产生过量抓取、是否误写长期记忆。
```

健康报告模板：

```markdown
# Hermes Weekly Health - YYYY-WW

## Summary

## Model Health

## Executor Health

## Bot Gateway Health

## Approval Queue

## Incidents

## Next Maintenance
```

## 模型和 CLI 漂移维护

模型和 agent app 会快速变化，所以维护重点放在 registry 和 adapter：

- 模型改名：只改 `config/models.yaml`。
- 模型下线：标记 `deprecated_at`，配置 replacement。
- CLI 参数变化：只改 executor adapter。
- API 返回格式变化：只改 provider adapter。
- 工具能力新增：增加 capability 标签，不改业务入口。
- 金融接口变化：只改 Finance Data Router 和 source registry，不改理财教学逻辑。
- 学习来源变化：只改 Learning Intake Router 和 source registry，不改长期记忆写入规则。

每月检查：

- OpenAI 模型页。
- DeepSeek API 文档。
- Kimi / GLM 官方文档。
- Claude Code 文档。
- Codex 文档。
- MCP 文档。
- SEC Investor.gov、FINRA、CFTC 等投资者教育和风险提示资料。
- 视频平台、字幕工具和 MCP 工具的版本变化；尤其检查是否仍符合平台规则和授权边界。

## 金融任务例行复盘

每月检查一次：

- Hermes 是否把教育内容和个性化建议区分清楚。
- 是否有任何输出像“确定买卖指令”。
- 模拟组合是否标记为 paper portfolio。
- 数据源是否标注时间戳和延迟。
- 是否出现“保证收益”“无风险高回报”等禁止表述。
- 是否有真实交易接口被启用；第一阶段应保持禁用。

## 每日学习例行复盘

每天学习任务完成后输出一份短报告：

```markdown
# Hermes Daily Learning - YYYY-MM-DD

## Sources Checked

## Learned

## Claims Needing Verification

## Memory Candidates

## Rejected Items

## Next Queue
```

每周检查：

- 学习来源是否太偏。
- 是否过度依赖短视频/二手解读。
- 是否优先学习官方文档和一手来源。
- 是否出现版权内容全文保存。
- 是否出现未授权登录态访问。
- 长期记忆候选是否有来源和时间。

## 事故处理

发生异常时，按顺序处理：

1. 暂停高风险执行器。
2. 保留日志和 trace。
3. 切换到只读模式。
4. 确认是否有外发消息、文件修改或账号操作。
5. 做最小回滚。
6. 写 incident note。

只读模式要求：

- 允许接收消息。
- 允许总结和规划。
- 禁止外发。
- 禁止写非日志文件。
- 禁止运行外部 CLI。

## 下一步扩展

稳定运行一到两周后，再考虑：

- 给 Hermes 独立微信账号。
- 接 Codex 写代码任务。
- 接 Claude Code MCP 工具。
- 给手机端做审批卡片。
- 加长期记忆 review UI。
