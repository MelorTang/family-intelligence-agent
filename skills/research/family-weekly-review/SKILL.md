---
name: family-weekly-review
description: Short Hermes skill for weekly consolidation from existing daily briefing and inbox notes into review-pending weekly output only.
version: 1.0.0
author: MelorTang
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [research, weekly, review, feishu, lark, obsidian, chinese, family]
    requires_toolsets: [terminal]
    config:
      - key: family_intelligence.vault_path
        description: Obsidian vault path.
        default: "~/family-intelligence-vault"
        prompt: Family intelligence vault path
      - key: family_intelligence.timezone
        description: Timezone for weekly note dates.
        default: "Asia/Shanghai"
        prompt: Timezone
---

# Family Weekly Review

## Purpose

Consolidate the last 7 daily briefing and Hermes inbox notes into a weekly review.

This skill must not promote AI-generated content into long-term knowledge. It only creates review-pending weekly output and optional To_Review suggestions.

## Allowed Write Paths

Write only:

```text
{vault_path}/05_Output/Weekly_Reviews/
{vault_path}/00_Inbox/AI_Processed/To_Review/
```

Do not write to `02_Sources/`, `03_Knowledge/`, `04_Insights/`, `06_Graph/`, `07_Assets/`, `90_Archive/`, MOC files, reports, articles, or memos.

## Required Behavior

1. Resolve `vault_path` from `skills.config.family_intelligence.vault_path`; default to `~/family-intelligence-vault`.
2. Read the last 7 days from:
   - `00_Inbox/Hermes/News/`
   - `00_Inbox/Hermes/Captures/`
   - `05_Output/Daily_Briefings/`
3. Write weekly review to:
   - `05_Output/Weekly_Reviews/YYYY-Www.md`
4. Optionally write candidate curation suggestions to:
   - `00_Inbox/AI_Processed/To_Review/YYYY-MM-DD-weekly-review.md`
5. Every generated file must include `review: pending`.
6. Deliver a concise Feishu/Lark weekly summary after writing files.

If file writing fails, output `FILE_WRITE_FAILED` with the reason.

## Weekly Review Format

```markdown
---
week: YYYY-Www
type: weekly_briefing
source: hermes
status: draft
review: pending
created_by: hermes
---

# 本周家庭全球观察周报

## 一句话总结

## 本周最重要的 5 件事

## 对普通家庭的影响

## 投资观察与风险提示

## 家庭风险提醒

## 值得继续跟踪的主题

## 下周观察清单

## 候选沉淀

### 可能的 Source Notes

### 可能的 Concept Notes

### 可能的 Insight Notes

### 需要人工核查的事实
```

