---
name: family-daily-briefing
description: Short Hermes skill for one job only: research today's family global intelligence briefing, write required Obsidian Markdown files, then deliver a concise Feishu/Lark summary.
version: 1.0.0
author: MelorTang
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [research, news, finance, feishu, lark, obsidian, daily, chinese, family]
    requires_toolsets: [web, terminal]
    config:
      - key: family_intelligence.vault_path
        description: Obsidian vault path.
        default: "~/family-intelligence-vault"
        prompt: Family intelligence vault path
      - key: family_intelligence.timezone
        description: Timezone for daily note dates.
        default: "Asia/Shanghai"
        prompt: Timezone
---

# Family Daily Briefing

## Non-Negotiable Output Contract

You must complete both parts, in this order:

1. Write the required Markdown files into the configured Obsidian vault path.
2. Then deliver the concise Feishu/Lark family summary.

If you cannot write files, output `FILE_WRITE_FAILED` with the reason. Do not silently send only a Feishu response.

Resolve `vault_path` from `skills.config.family_intelligence.vault_path`; default to `~/family-intelligence-vault`.
Use today's date in `Asia/Shanghai` as `YYYY-MM-DD`.

Required files:

```text
{vault_path}/00_Inbox/Hermes/News/YYYY-MM-DD-news.md
{vault_path}/00_Inbox/Hermes/Captures/YYYY-MM-DD-captures.md
{vault_path}/05_Output/Daily_Briefings/YYYY-MM-DD-briefing.md
```

Create parent directories if missing. Overwrite an existing empty placeholder for today's date. If a file already contains substantive user-reviewed content, append a new `## Hermes rerun` section instead of deleting it.

Every file must include YAML frontmatter with:

```yaml
source: hermes
review: pending
created_by: hermes
created: YYYY-MM-DD
```

## Allowed Write Paths

Cloud Hermes may write only:

```text
00_Inbox/Hermes/
05_Output/Daily_Briefings/
99_System/Automation/logs/
```

Do not write to `02_Sources/`, `03_Knowledge/`, `04_Insights/`, `06_Graph/`, `07_Assets/`, `90_Archive/`, MOC files, reports, articles, or memos.

## Research Scope

Research and summarize:

- 全球大事
- 市场与投资：美股、A股、港股、黄金、原油、美元、比特币、利率
- 科技与 AI
- 中国经济与政策
- 家庭生活风险：诈骗、食品安全、医疗、养老、消费陷阱、天气灾害、产品召回、AI 诈骗

Source rules:

- Keep direct URLs for important claims.
- Prefer primary/high-trust sources: official agencies, central banks, exchanges, regulators, company newsroom/filings, AP, Reuters, Bloomberg, BBC, CNBC, WSJ, FT.
- If a claim is weakly sourced, label it `未确认` or omit it from action sections.
- Do not invent exact prices, index levels, casualties, dates, probabilities, or executive visits.

## File 1: News Digest

Path:

```text
00_Inbox/Hermes/News/YYYY-MM-DD-news.md
```

Format:

```markdown
---
type: source
source_type: news_digest
source: hermes
status: inbox
review: pending
created_by: hermes
created: YYYY-MM-DD
tags:
  - inbox
  - hermes
  - news
---

# Daily News - YYYY-MM-DD

## Summary

## Important Items

For each item:
- 标题
- 来源与 URL
- 发生了什么
- 为什么重要
- 对普通家庭有什么影响
- 不确定性

## Potential Follow-up Questions

## Candidate Knowledge Notes

## Raw Items
```

## File 2: Captures

Path:

```text
00_Inbox/Hermes/Captures/YYYY-MM-DD-captures.md
```

Format:

```markdown
---
type: source
source_type: captures
source: hermes
status: inbox
review: pending
created_by: hermes
created: YYYY-MM-DD
tags:
  - inbox
  - hermes
  - captures
---

# Daily Captures - YYYY-MM-DD

## 待跟进材料

## 可能沉淀的概念

## 可能形成的洞察

## 后续问题
```

## File 3: Full Briefing

Path:

```text
05_Output/Daily_Briefings/YYYY-MM-DD-briefing.md
```

Format:

```markdown
---
type: daily_briefing
source: hermes
status: draft
review: pending
created_by: hermes
created: YYYY-MM-DD
tags:
  - briefing
  - daily
---

# Daily Briefing - YYYY-MM-DD

## 一句话总结

## 全球大事

## 市场与投资

## 科技与 AI

## 中国经济与政策

## 家庭生活风险雷达

## 今日行动建议

## 继续跟踪

## 未来观察

## 数据来源
```

## Feishu/Lark Summary

After writing all files, send a concise family-readable Chinese summary.

Use this structure:

```text
📰 今日家庭全球简报｜YYYY-MM-DD

**一句话总结**
...

🌍 一、全球大事
1️⃣ **标题**
...
影响：...
变数：...

💰 二、市场与投资
...

🤖 三、科技与 AI
...

🇨🇳 四、中国经济与政策
...

🛡️ 五、家庭生活风险雷达
对象：...
行动：...
识别：...

✅ 六、今日行动建议
1. ...
2. ...
3. ...

**今日是否需要行动**
...

📁 完整简报：~/family-intelligence-vault/05_Output/Daily_Briefings/YYYY-MM-DD-briefing.md
🔎 来源材料：~/family-intelligence-vault/00_Inbox/Hermes/News/YYYY-MM-DD-news.md
⚠️ 仅供信息整理与风险观察，不构成投资建议。
```

Do not include raw Markdown frontmatter, tool logs, cron prompt text, or internal execution details in Feishu.

