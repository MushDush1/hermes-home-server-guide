# Hermes 家庭服务器迁移与升级指南

更新时间：2026-05-21

这套文档用于把家里 Windows 主机上的 Hermes 升级成“个人高自治分身控制面”。当前笔记本只用于编写和携带指南；所有安装、登录、密钥配置、bot 接入、CLI 运行、服务启动都只在家里服务器执行。

## 阅读顺序

1. [00-overview.md](00-overview.md)：目标定位、原则和明确不做的事。
2. [01-home-server-inventory.md](01-home-server-inventory.md)：家里服务器盘点表和只读检查清单。
3. [02-target-architecture.md](02-target-architecture.md)：Hermes Core、多模型、多执行器、聊天入口的目标架构。
4. [03-migration-steps.md](03-migration-steps.md)：迁移步骤、验证点和回滚方式。
5. [04-permissions-and-safety.md](04-permissions-and-safety.md)：权限分层、审批、外部 CLI 隔离和微信策略。
6. [05-operations.md](05-operations.md)：Windows 常驻运行、日志、健康检查和维护节奏。
7. [06-finance-learning.md](06-finance-learning.md)：金融接口、理财教学边界、模拟组合和风险控制。
8. [07-learning-intake.md](07-learning-intake.md)：每日向外学习、B 站/视频来源、MCP/浏览器/字幕工具和知识入库。
9. [08-decision-authority.md](08-decision-authority.md)：让 Hermes 从“给建议”升级到“可控地做决策”的授权协议。
10. [09-wechat-alt-account-handoff.md](09-wechat-alt-account-handoff.md)：微信小号接管、官方替代路线、审批发送和封号风险边界。

## 迁移边界

- 本笔记本：只保存和编辑这些 Markdown 指南。
- 家里 Windows 主机：唯一部署、运行、登录、接入 bot 和保存密钥的地方。
- Hermes：控制面，不是单一 chatbot。
- Codex、Claude Code、DeepSeek TUI、Kimi、GLM、DeepSeek API、未来 agent app：都视为可替换执行器或模型后端。
- 金融能力：默认用于教育、预算、风险解释、数据整理和模拟，不默认做个性化荐股或自动交易。
- 向外学习：默认学习公开资料、元数据、字幕、摘要和你授权的内容，不默认批量下载视频或绕过平台限制。
- 决策能力：默认按风险、可逆性、金额、身份影响和置信度分级；小事可自动决定，高风险必须审批。
- 微信小号：优先做“AI 起草 + 人审发送”或官方企业微信/公众号路线，不用外挂、Hook、协议逆向作为核心依赖。

## 当前官方方向参考

- [MCP](https://modelcontextprotocol.io/docs/getting-started/intro) 是连接 AI 应用与外部数据、工具和工作流的开放标准。
- [MCP tools](https://modelcontextprotocol.io/docs/concepts/tools) 支持模型发现并调用工具，同时建议高风险工具调用保留 human-in-the-loop。
- [Claude Code MCP SDK](https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-mcp) 支持通过 MCP 扩展 Claude Code 工具能力。
- [DeepSeek API](https://api-docs.deepseek.com/) 提供 OpenAI/Anthropic 兼容接口，并提示部分旧模型名存在弃用日期。
- [OpenAI Models](https://developers.openai.com/api/docs/models) 和 [Codex use cases](https://developers.openai.com/codex/explore) 可作为 GPT/Codex 路由能力参考。
- [Investor.gov](https://www.investor.gov/introduction-investing/getting-started/assessing-your-risk-tolerance) 和 [FINRA](https://www.finra.org/investors/investing/investing-basics/risk) 提醒投资决策要考虑风险承受能力、目标、期限、资产配置和分散化。
- [SEC/FINRA/NASAA AI investment fraud alert](https://www.investor.gov/index.php/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-alerts/artificial-intelligence-fraud) 与 [CFTC AI trading bots advisory](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/AITradingBots.html) 都提示要警惕 AI 投资骗局和“保证收益”交易机器人。
- [yt-dlp README](https://github.com/yt-dlp/yt-dlp/blob/master/README.md) 说明它支持字幕列表、字幕写出和 `--skip-download` 等能力；这些能力只能作为你授权的学习资料提取工具，不应绕过平台限制或版权边界。
- 企业微信群机器人可通过 Webhook 做内部群消息推送；腾讯云文档也给出了企业微信 5.0 获取群机器人 Webhook 的流程。
- 多家媒体转述微信安全中心公告：微信个人账号明确禁止外挂、多开、一键群发等破坏客户端或平台规则的行为。

## 完成标准

- 能把本目录复制到家里服务器后，按步骤完成盘点。
- 新增一个模型或 CLI agent 时，只需要增加 registry 项和 adapter，不重写 Hermes Core。
- 高风险动作都有审批点、日志和可回滚说明。
- Codex、Claude Code、DeepSeek TUI 任一失败时，不拖垮 Hermes Core。
- 金融接口接入后，Hermes 能解释数据来源、延迟、风险和假设；任何真实下单、自动跟单或个性化投资建议默认被拦截。
- 每日学习任务能输出“学了什么、证据在哪里、是否可信、是否值得写入长期记忆”，并能区分公开网页、视频字幕、人工上传资料和私密账号内容。
- Hermes 能区分 advice、recommendation、decision、action，并在允许范围内真的拍板、执行、记录结果和复盘。
- Hermes 接入微信类入口后，能区分“通知群推送、公众号客服、个人小号草稿、个人小号自动发送”，其中个人小号自动发送默认不开放。
