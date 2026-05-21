# 2026-05-21 Backend Change Log - Hermes Home Server Guide

## Task background

The user asked for implementation of a Markdown guide that can be migrated to a home Windows server for Hermes modernization. The current laptop must only produce documentation and must not run deployment, bot, CLI, login, or service tasks.

## Goal

Create a practical guide for migrating Hermes into a multi-model, multi-executor personal agent control plane with safety, approval, audit, and operations guidance.

## Summary of actual changes

Added a new documentation set under `docs/hermes-home-server-guide/` with overview, inventory, architecture, migration, permissions, operations, finance learning, learning intake, decision authority, and WeChat alt-account handoff chapters. The guide treats Codex, Claude Code, DeepSeek TUI, and future CLI agents as replaceable executors, and treats GPT, DeepSeek, Kimi, and GLM as model registry entries. It also defines a finance data router, learning intake router, decision engine, finance permission boundaries, and paper-portfolio-first approach.

## Added files

- `docs/hermes-home-server-guide/README.md`
- `docs/hermes-home-server-guide/00-overview.md`
- `docs/hermes-home-server-guide/01-home-server-inventory.md`
- `docs/hermes-home-server-guide/02-target-architecture.md`
- `docs/hermes-home-server-guide/03-migration-steps.md`
- `docs/hermes-home-server-guide/04-permissions-and-safety.md`
- `docs/hermes-home-server-guide/05-operations.md`
- `docs/hermes-home-server-guide/06-finance-learning.md`
- `docs/hermes-home-server-guide/07-learning-intake.md`
- `docs/hermes-home-server-guide/08-decision-authority.md`
- `docs/hermes-home-server-guide/09-wechat-alt-account-handoff.md`
- `docs/change-logs/backend/2026-05-21-backend-hermes-home-server-guide.md`

## Modified files

- `docs/hermes-home-server-guide/README.md`
- `docs/hermes-home-server-guide/02-target-architecture.md`
- `docs/hermes-home-server-guide/03-migration-steps.md`
- `docs/hermes-home-server-guide/04-permissions-and-safety.md`
- `docs/hermes-home-server-guide/05-operations.md`
- `docs/change-logs/backend/2026-05-21-backend-hermes-home-server-guide.md`

## Deleted files

None.

## Key decisions

- The laptop remains documentation-only.
- The home Windows server is the sole deployment target.
- Hermes is documented as a control plane, not a single chatbot.
- Model names and CLI details are routed through registries and adapters.
- High-risk actions require approval and trace logging.
- Financial features are education, research, budgeting, and simulation first; real trading is explicitly out of scope for the first phase.
- External learning is source-controlled and summary-first; video platforms are handled through metadata, public subtitles, user-provided material, and explicit authorization boundaries.
- Decision authority is separated from permissions so Hermes can make low-risk decisions without being allowed to cross high-risk action boundaries.
- WeChat personal alt-account handoff should start with draft-and-approval mode, while official WeCom/Official Account paths are preferred for stable automation. Desktop RPA is documented only as a controlled last-mile sender with strict contact, text, screenshot, and approval checks. The WeChat method landscape is documented across official accounts, WeCom, desktop RPA, Wechaty/Puppet, third-party personal adapters, and non-adopted Hook/protocol-reversal approaches.

## Verification status

Verified by creating and updating the Markdown guide files locally. No home-server commands were executed. No bot, CLI agent, model API, finance API, brokerage login, browser login, WeChat login, video download, service, deployment action, or external decision workflow was run from this laptop.

## Rollback notes

Remove `docs/hermes-home-server-guide/` and this change log file to roll back the documentation addition.

## Next-step handoff notes

Copy `docs/hermes-home-server-guide/` to the home Windows server and start with `01-home-server-inventory.md`. Run only the inventory commands first, then fill the registry templates from actual server facts. Keep financial work at education, read-only data, and paper-portfolio levels until the safety model has been tested. Keep daily learning summary-first and avoid private login state or media downloads unless explicitly approved. Start decision authority in label-only mode, then gradually enable low-risk autonomous decisions. For WeChat, start with WeCom approval notifications and manual draft sending before considering any automation; if desktop RPA is needed, start with paste-only mode before any send automation.
