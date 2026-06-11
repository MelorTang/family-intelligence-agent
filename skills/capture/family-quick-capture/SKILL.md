---
name: family-quick-capture
description: Short Hermes skill for Feishu/Lark quick capture into Obsidian Inbox: ideas, questions, and reading items only.
version: 1.0.0
author: MelorTang
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [capture, feishu, lark, obsidian, inbox, chinese]
    requires_toolsets: [terminal]
    config:
      - key: family_intelligence.vault_path
        description: Obsidian vault path.
        default: "~/family-intelligence-vault"
        prompt: Family intelligence vault path
---

# Family Quick Capture

## Purpose

Capture quick Feishu/Lark messages into Obsidian Inbox so the user does not need to open a computer.

This skill is for lightweight capture only. Do not create source notes, concept notes, insight notes, MOCs, reports, articles, memos, or graph files.

## Allowed Write Paths

Write only:

```text
{vault_path}/00_Inbox/Ideas/
{vault_path}/00_Inbox/Questions/
{vault_path}/00_Inbox/Reading/
```

## Triggers

Classify messages by prefix or intent:

- Idea: `记一个 idea：...`, `记个 idea：...`, `idea: ...`, `灵感：...`, `想法：...`
- Question: `记一个 question：...`, `question: ...`, `问题：...`, `待研究：...`
- Reading: `加入 reading：...`, `reading: ...`, `待读：...`, `稍后读：...`

## Required Behavior

1. Resolve `vault_path` from `skills.config.family_intelligence.vault_path`; default to `~/family-intelligence-vault`.
2. Classify capture as `idea`, `question`, or `reading`.
3. Create a readable filename:
   - Prefer Chinese title text from the user's message when short.
   - Prefix with today's date: `YYYY-MM-DD 标题.md`.
   - Remove unsafe path characters.
4. Preserve the user's original wording exactly under `## 原始记录`.
5. Add only a short `## 初步整理` if useful.
6. Keep URLs unchanged.
7. Reply with the saved relative path.

## Markdown Format

```markdown
---
type: capture
capture_type: idea | question | reading
source: feishu
status: inbox
review: pending
created_by: hermes
created: YYYY-MM-DD
tags:
  - inbox
  - capture
---

# 标题

## 原始记录

...

## 初步整理

...

## 后续处理建议

- 是否需要转为 Source Note：
- 是否需要转为 Concept Note：
- 是否需要转为 Insight Note：
```

## Feishu Confirmation

```text
已记录到 Obsidian Inbox：
00_Inbox/Ideas/YYYY-MM-DD 标题.md

我只做了快速捕获，后续可在本地 Obsidian 中审核整理。
```

