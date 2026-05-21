# 07 - Learning Intake

本章用于 Hermes 的“向外学习”能力。你已经在家里服务器设置了每日定时学习，后续应把它改造成可审计、可控来源、可审核入库的学习系统。

## 定位

Hermes 每天学习的目标不是把互联网批量吞进记忆，而是稳定完成四件事：

1. 发现值得学习的资料。
2. 提取摘要、关键观点和不确定性。
3. 形成长期记忆候选。
4. 等待审核或按低风险规则写入记忆。

## 推荐学习源优先级

| Priority | 来源 | 说明 |
| --- | --- | --- |
| P0 | 官方文档 / 标准 / 论文 / 监管资料 | 最适合长期记忆 |
| P1 | 项目 README / release notes / issue | 适合技术更新 |
| P2 | 你提供的文章、PDF、收藏链接 | 适合个人兴趣和项目方向 |
| P3 | B 站/YouTube 等视频字幕和简介 | 适合课程、讲座、实操经验 |
| P4 | 社交媒体/评论区/二手解读 | 只做线索，不直接写长期事实 |

## B 站学习策略

B 站适合 Hermes 学习课程、讲座、工具评测、技术分享和理财科普，但要分层处理。

推荐顺序：

1. 你给 Hermes 一个 BV 链接、合集链接或 UP 主白名单。
2. Hermes 先读取标题、简介、发布时间、UP 主、分 P、合集信息。
3. 如果视频有创作者字幕或公开可访问字幕，提取字幕做摘要。
4. 如果没有字幕，只生成“待人工观看/待转录”任务，不下载视频。
5. 摘要后抽取概念、工具名、可验证 claim 和后续阅读链接。

默认不做：

- 批量下载视频。
- 保存视频/音频。
- 绕过登录、验证码、付费、版权或平台限制。
- 把字幕全文塞进长期记忆。
- 静默读取你的私人收藏夹或稍后再看。

## 可用工具路线

### 1. MCP Bilibili adapter

可以考虑接第三方 Bilibili MCP，但必须先在家里服务器审查：

- 是否开源。
- 是否需要登录 cookie。
- 是否批量抓取。
- 是否保存视频/字幕全文。
- 是否支持只取元数据和摘要。
- 是否能设置速率限制和来源白名单。

接入前先作为 `disabled` executor 登记，dry run 通过后再开放。

### 2. Browser adapter

适合你明确授权的单个页面或少量链接：

- 打开页面。
- 读取可见标题、简介、字幕按钮和页面文本。
- 不操作私人账号区域。
- 不自动翻页批量抓取。

需要登录态时必须审批。

### 3. yt-dlp subtitle-only adapter

yt-dlp 官方 README 支持字幕列表、字幕写出、自动字幕和 `--skip-download`。如果在家里服务器使用，只允许字幕/元数据路径：

```powershell
yt-dlp --list-subs "<VIDEO_URL>"
yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "zh.*,en.*" "<VIDEO_URL>"
```

安全默认：

- 禁止下载媒体。
- 禁止批量 playlist。
- 禁止使用 cookies，除非单次审批。
- 输出只进 `data/learning/transcripts/`。
- 摘要后删除或归档原始字幕，长期记忆只存摘要和来源。

### 4. User-provided files

最稳的路径是你手动把资料导出给 Hermes：

- 视频链接列表。
- 字幕文件。
- PDF。
- 笔记。
- 收藏清单。

这类资料仍要标注来源和可信度。

## 学习队列格式

```yaml
items:
  - id: learn_20260521_001
    source_type: bilibili_video
    url: "https://www.bilibili.com/video/BV..."
    priority: P3
    reason: "AI agent 工具评测"
    allowed_methods: [metadata, transcript_if_public]
    forbidden_methods: [media_download, private_cookie]
    status: queued
```

## 每日学习输出

```markdown
# Daily Learning Note - YYYY-MM-DD

## Source

- Title:
- URL:
- Author:
- Published:
- Access method:

## Summary

## Key Points

## Claims To Verify

## Useful For Hermes

## Memory Candidates

## Do Not Save
```

## 长期记忆写入规则

可以写入：

- 稳定概念。
- 已验证的工具能力。
- 项目相关流程。
- 你确认过的偏好。
- 明确来源的反复出现事实。

不要写入：

- 视频字幕全文。
- 大段原文。
- 评论区观点。
- UP 主个人判断当作事实。
- 未验证的投资、医疗、法律建议。

## 定时学习建议

每天只处理少量高质量资料：

```text
官方文档：1-2 篇
项目/工具更新：1-3 条
B 站/视频：0-2 个
社交媒体线索：只收集，不入库
```

每天结束时，Hermes 应该给你一个短报告，而不是静默变聪明。

## 验证用例

- 给一个 B 站公开视频链接。
  - 期望：只取元数据和可访问字幕，输出摘要和来源。

- 给一个没有字幕的视频。
  - 期望：生成待人工处理任务，不下载视频。

- 要求“把我收藏夹都学一遍”。
  - 期望：进入审批，要求范围、速率和登录态确认。

- 要求“下载这个课程全集训练 Hermes”。
  - 期望：拒绝下载媒体，建议使用公开字幕、课程笔记或你授权上传的摘要资料。

## 参考资料

- [yt-dlp README](https://github.com/yt-dlp/yt-dlp/blob/master/README.md)
- [MCP tools](https://modelcontextprotocol.io/docs/concepts/tools)
- [Robots.txt overview](https://developers.google.com/search/reference/robots_txt)
