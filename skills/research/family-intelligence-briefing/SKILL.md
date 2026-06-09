---
name: family-intelligence-briefing
description: Hermes-native workflow for Chinese family global news, investment risk observation, Feishu/Lark app-bot conversations, cron delivery, and Obsidian inbox-first knowledge capture.
version: 0.4.0
author: MelorTang
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [research, news, finance, feishu, lark, obsidian, automation, chinese, family]
    requires_toolsets: [web, terminal]
    config:
      - key: family_intelligence.vault_path
        description: Directory where Hermes inbox, daily briefing, weekly review, and review-pending Markdown notes should be saved.
        default: "~/family-intelligence-vault"
        prompt: Family intelligence knowledge-base path
      - key: family_intelligence.daily_schedule
        description: Daily Hermes cron schedule.
        default: "0 8 * * *"
        prompt: Daily briefing schedule
      - key: family_intelligence.weekly_schedule
        description: Weekly Hermes cron schedule for knowledge consolidation.
        default: "0 20 * * 0"
        prompt: Weekly consolidation schedule
      - key: family_intelligence.timezone
        description: Local timezone for dates in notes and messages.
        default: "Asia/Shanghai"
        prompt: Timezone
      - key: family_intelligence.audience
        description: Briefing audience and tone.
        default: "普通家庭成员，尤其是不擅长主动搜索信息、容易处于信息茧房的家人"
        prompt: Audience description
---

# Family Intelligence Briefing

## Core Principle

Hermes is the agent. Do not build or call a separate news agent, LLM runner, scheduler, Feishu webhook sender, or database.

Use Hermes built-ins for:

- model/provider selection via `hermes model` and Hermes config
- Feishu/Lark messaging through Hermes gateway
- web research through the active web/search tools
- cron scheduling through Hermes cron
- file writing through terminal/file tools
- lightweight memory and recurring context through Hermes itself
- skill settings through `skills.config.family_intelligence.*`

This skill is a workflow contract and prompt pack. It should guide Hermes to produce a calm Chinese family briefing, save review-pending Markdown materials into Obsidian, and reply naturally in Feishu/Lark conversations.

Hermes handles light tasks: collection, summarization, candidate links, candidate concepts, daily briefings, and weekly reviews. It is not the final knowledge judge. Durable concepts, project notes, graph relations, reports, articles, and verified knowledge are created locally by a human in Obsidian. Heavy transformations should be triggered manually through Claude Code, Codex, Antigravity, or another CLI agent so the diff can be reviewed.

## When to Use

Use this skill when the user asks for:

- 每日家庭全球资讯简报
- 投资观察、市场风险、家庭资产风险提醒
- 给家人看的全球热点资讯摘要
- 信息茧房破除
- 飞书单聊或群里 @ 机器人提问
- 飞书群定时日报/周报
- Obsidian / Markdown inbox capture
- 日报、周报、待审核草稿、后续人工沉淀材料

## Feishu/Lark App Bot Behavior

This skill assumes Hermes is connected through its native Feishu/Lark messaging gateway.

Expected behavior:

- The user can DM the Feishu/Lark app bot.
- Family members can add the app bot to a group.
- In groups, Hermes replies when the bot is mentioned, subject to Hermes gateway behavior and Feishu permissions.
- Hermes cron can deliver scheduled daily/weekly outputs back to the configured Feishu/Lark chat.

Do not use Feishu group custom bot webhook for this project.

Feishu Open Platform setup is outside this skill but should include:

- self-built app
- bot capability enabled
- event subscription for receiving messages
- permissions for p2p messages, group @ messages, and sending/replying to messages
- published app
- app bot added to the target family group

Hermes setup should be done with:

```bash
hermes gateway setup
```

Select Feishu/Lark and follow the prompts.

## Safety and Tone

Always follow these constraints:

1. 用普通家庭成员能理解的中文。
2. 不制造焦虑，不煽动情绪。
3. 投资内容只做“观察、风险提示、配置提醒”，不要给激进交易指令。
4. 不使用“稳赚”“必涨”“重仓买入”“内幕消息”等表达。
5. 不根据单一新闻给确定性结论。
6. 对不确定信息明确写“不确定”。
7. 每条重大信息都说明：发生了什么、为什么重要、对普通家庭有什么影响。
8. 最后给出“今天是否需要行动”的家庭结论。
9. 明确这不是持牌投资顾问意见。
10. Do not state high-impact claims as facts unless at least one reliable source supports them. If a claim is unverified, write "未确认" or omit it from the family-facing summary.

## Knowledge Base Layout

Resolve the configured vault path from `skills.config.family_intelligence.vault_path`. Create directories if missing:

```text
{vault_path}/
  00_Inbox/
    Hermes/
      News/
      Captures/
      Logs/
    Reading/
    Ideas/
    Questions/
    AI_Processed/
      To_Review/
  01_Journal/
    Daily/
    Weekly/
  02_Sources/
    Articles/
    Books/
    Papers/
    Web/
    People/
    Companies/
  03_Knowledge/
    MOC/
    Concepts/
    Domains/
    Markets/
    Tools/
    Frameworks/
  04_Insights/
    Investment_Theses/
    Mental_Models/
    Decision_Notes/
    Questions/
  05_Output/
    Daily_Briefings/
    Weekly_Reviews/
    Reports/
    Articles/
    Memos/
  06_Graph/
  07_Assets/
  90_Archive/
    Hermes_Legacy/
  99_System/
    Agents/
    Templates/
    Prompts/
    Hermes/
    Claude/
    Automation/
      logs/
```

Use Markdown files. Do not require a database for MVP.

Cloud Hermes may write only:

```text
{vault_path}/00_Inbox/Hermes/
{vault_path}/00_Inbox/Ideas/
{vault_path}/00_Inbox/Questions/
{vault_path}/00_Inbox/Reading/
{vault_path}/00_Inbox/AI_Processed/To_Review/
{vault_path}/05_Output/Daily_Briefings/
{vault_path}/05_Output/Weekly_Reviews/
{vault_path}/99_System/Automation/logs/
```

Daily briefings and weekly reviews have long-term review value as time-series records, but they still must be marked `review: pending` when generated by cloud automation.

Cloud Hermes must not write, delete, rename, merge, or reorganize long-term notes in:

```text
01_Journal/
02_Sources/
03_Knowledge/
04_Insights/
06_Graph/
07_Assets/
90_Archive/
05_Output/Reports/
05_Output/Articles/
05_Output/Memos/
Home.md
MOC files
long-term concept notes
```

Every cloud-generated Markdown file must include YAML frontmatter with `review: pending`. Never mark AI-generated or Hermes-generated content as `verified`.

## Feishu Quick Capture Workflow

Hermes should support quick personal capture from Feishu/Lark so the user does not need to open Obsidian on a computer.

This is a lightweight inbox feature. It may create new Markdown files only in:

```text
{vault_path}/00_Inbox/Ideas/
{vault_path}/00_Inbox/Questions/
{vault_path}/00_Inbox/Reading/
```

It must not promote captures directly into `02_Sources/`, `03_Knowledge/`, `04_Insights/`, or long-term output folders.

Trigger patterns:

- Idea: `记一个 idea：...`, `记个 idea：...`, `idea: ...`, `灵感：...`, `想法：...`
- Question: `记一个 question：...`, `question: ...`, `问题：...`, `待研究：...`
- Reading: `加入 reading：...`, `reading: ...`, `待读：...`, `稍后读：...`

When a quick capture request is received:

1. Classify it as `idea`, `question`, or `reading`.
2. Create a short stable slug from the message content. Use lowercase ASCII words when obvious; otherwise use a short pinyin-like or date-based slug. Avoid spaces and unsafe filename characters.
3. Save to:
   - Ideas: `{vault_path}/00_Inbox/Ideas/YYYY-MM-DD-slug.md`
   - Questions: `{vault_path}/00_Inbox/Questions/YYYY-MM-DD-slug.md`
   - Reading: `{vault_path}/00_Inbox/Reading/YYYY-MM-DD-slug.md`
4. Preserve the user's original wording exactly under `## 原始记录`.
5. Add a short `## 初步整理` section only if it helps clarify the capture. Do not over-process it.
6. If the message contains a URL, keep the URL unchanged.
7. Reply in Feishu with a short confirmation and the saved relative path.

Quick capture Markdown format:

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

# Title

## 原始记录

...

## 初步整理

...

## 后续处理建议

- 是否需要转为 Source Note：
- 是否需要转为 Concept Note：
- 是否需要转为 Insight Note：
```

Feishu confirmation format:

```text
已记录到 Obsidian Inbox：
00_Inbox/Ideas/YYYY-MM-DD-slug.md

我只做了快速捕获，后续可在本地 Obsidian 中审核整理。
```

## Daily Workflow

When running the daily briefing:

1. Use Hermes web/search tools to research these categories:
   - 全球大事：world top news today、全球 重要 新闻 今天
   - 市场与投资：US stock market Fed inflation Treasury yields、A股 今日 市场 情绪、港股 科技股、gold oil dollar market
   - 科技与 AI：AI technology major news today、人工智能 重大 新闻
   - 中国经济与政策：中国 经济 政策 房地产 就业 消费
   - 家庭生活风险：诈骗、食品安全、医疗、养老、消费陷阱、天气灾害、药品召回、产品召回、个人信息泄露、AI诈骗
2. Prefer diverse, traceable sources. Keep URLs.
3. Deduplicate semantically in reasoning: same event from multiple sources should become one item with multiple sources.
4. Produce a family-readable Chinese report.
5. Save the news digest to `{vault_path}/00_Inbox/Hermes/News/YYYY-MM-DD-news.md`.
6. Save captures and follow-up material to `{vault_path}/00_Inbox/Hermes/Captures/YYYY-MM-DD-captures.md`.
7. Save the daily briefing to `{vault_path}/05_Output/Daily_Briefings/YYYY-MM-DD-briefing.md`.
8. Return a shorter summary to the active Feishu/Lark chat when invoked from Feishu. For scheduled runs, deliver the summary through Hermes cron's configured delivery/home chat behavior.

Use these source standards:

- High-impact claims must have direct URLs in the news digest or daily briefing source section.
- Prefer primary or high-trust sources for official data: government agencies, central banks, exchanges, regulators, company newsroom/filings, AP/Reuters/Bloomberg/BBC/CNBC/WSJ/FT and comparable outlets.
- If only low-trust or indirect sources are available, label the item "未确认" and keep it out of the family action section.
- Do not cite only outlet names such as "Reuters" or "BBC"; save the article title and URL.
- If exact prices, index levels, casualties, policy dates, or executive visits are included, they must be traceable to a source URL from this run.

News digest format:

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

## Potential Follow-up Questions

## Candidate Knowledge Notes

## Raw Items
```

For the family risk section, avoid generic advice. Each item should answer:

- 今日具体风险是什么？
- 谁最容易受影响？
- 家里今天要做什么？
- 如何判断真假或降低损失？

Daily briefing Markdown format:

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

## Top Highlights

## What Matters

## Recommended Actions

## Items to Review in Obsidian
```

## Feishu/Lark Summary

When replying in Feishu/Lark, keep the message concise and family-readable.

Use this exact structure for the final family-facing chat message. Keep headings, order, and section names stable between runs.

```text
📰 今日家庭全球简报｜YYYY-MM-DD

**一句话总结**
……

━━━━━━━━━━━━━━
🌍 一、全球大事

1️⃣ **标题**
……
影响：……
变数：……

2️⃣ **标题**
……
影响：……
变数：……

━━━━━━━━━━━━━━
💰 二、市场与投资

1️⃣ **标题**
……
影响：……
变数：……

2️⃣ **标题**
……
影响：……
变数：……

**投资温度**
• 美股：偏强｜科技股带动，但利率仍是压力
• A股：偏弱｜成交不足，观望情绪较重
• 港股：震荡｜受美股和中概股情绪影响
• 黄金：偏强｜避险需求仍在
• 美元：中性｜等待利率信号
• 原油：偏强｜地缘风险推高风险溢价

**资产快照**
• 标普500：回落｜利率担忧压制估值
• 纳斯达克：承压｜AI和科技股波动加大
• 上证综指：震荡｜政策预期与现实数据拉扯
• 恒生指数：偏弱｜科技股情绪仍不稳
• 黄金：偏强｜避险和实际利率预期影响
• WTI原油：偏强｜供应风险仍是主线
• 美元指数：中性｜等待美联储信号
• 比特币：高波动｜风险资产情绪影响较大

━━━━━━━━━━━━━━
🤖 三、科技与 AI

1️⃣ **标题**
……
影响：……
留意：……

2️⃣ **标题**
……
影响：……
留意：……

━━━━━━━━━━━━━━
🇨🇳 四、中国经济与政策

1️⃣ **标题**
……
影响：……
留意：……

2️⃣ **标题**
……
影响：……
留意：……

━━━━━━━━━━━━━━
🛡️ 五、家庭生活风险雷达

1️⃣ **具体风险**
对象：……
行动：……
识别：……

2️⃣ **具体风险**
对象：……
行动：……
识别：……

3️⃣ **具体风险**
对象：……
行动：……
识别：……

━━━━━━━━━━━━━━
✅ 六、今日行动建议

**今天建议**
1. ……
2. ……
3. ……

**今日是否需要行动**
✅/⚠️ ……

**继续跟踪**
• 主题｜原因｜优先级
• 主题｜原因｜优先级
• 主题｜原因｜优先级

**未来观察**
1. 日期/事件：为什么要看
2. 日期/事件：为什么要看
3. 日期/事件：为什么要看

📁 完整简报：~/family-intelligence-vault/05_Output/Daily_Briefings/YYYY-MM-DD-briefing.md
🔎 来源材料：~/family-intelligence-vault/00_Inbox/Hermes/News/YYYY-MM-DD-news.md
⚠️ 仅供信息整理与风险观察，不构成投资建议。
```


Rules for this chat summary:

- Do not send the full Markdown report to Feishu unless the user explicitly asks.
- Do not include raw Markdown frontmatter in Feishu.
- Do not include `CronJob Response`, tool call logs, search query lists, or internal execution details.
- Do not copy placeholder text or option lists. Never output strings like `偏强/中性/偏弱/不确定`, `涨/跌/持平`, `一句话原因`, `一句话`, or `……`.
- A short progress message before the final report is acceptable, but the final report must use the template above.
- Keep the final chat message around 2800-3800 Chinese characters unless the user asks for detail.
- Use no more than 8 emoji types in the final message to keep it readable.
- Every top item must be traceable to sources saved in the full Markdown report.
- Avoid exact price/index numbers unless they were verified by a current source during this run.
- Family risk items must be specific and actionable. Avoid generic reminders like "警惕诈骗" unless paired with a concrete scenario and action.
- Include an asset snapshot in every daily report. If exact numbers are not verified, use directional wording such as "偏强", "偏弱", "震荡", or "不确定" instead of fabricated figures. If a market is closed or data is stale, write "休市/数据待确认".
- Include 3-6 continuing themes and 3-6 future watch items in every daily report when enough sources exist. These should help the family know what to keep watching next, not predict outcomes.
- Do not use the label `事：` in Feishu. Put the event summary directly below each item title.
- Use short labels in Feishu only where useful: `影响`, `变数`, `留意`, `对象`, `行动`, `识别`. Avoid long repeated labels such as `发生了什么` and `对家里的影响`.
- Use bold markers consistently for major micro-headings and item titles, such as `**投资温度**`, `**资产快照**`, and `1️⃣ **标题**`.

## Weekly Workflow

Weekly reviews are valuable time-series records. Keep them, but do not automatically promote them into long-term knowledge.

When running weekly consolidation:

1. Read the last 7 daily briefing and inbox notes from allowed directories.
2. Create `{vault_path}/05_Output/Weekly_Reviews/YYYY-Www.md`.
3. Suggest possible source notes, concept notes, insight notes, links, and follow-up questions for local Obsidian review.
4. Do not update `03_Knowledge`, `04_Insights`, graph files, source notes, reports, articles, memos, or archived legacy notes.

Weekly note structure:

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
```

## Hermes Cron Setup

Prefer Hermes cron. Do not run a separate scheduler service.

Daily:

```bash
hermes cron create "0 8 * * *" \
  "Use the family-intelligence-briefing skill to produce today's family global intelligence briefing. Save the full Markdown to the configured vault path. Deliver the final Feishu/Lark summary using the exact template defined in the skill, without raw Markdown, tool logs, or CronJob Response text." \
  --skill family-intelligence-briefing \
  --deliver feishu \
  --name family-daily-briefing
```

Weekly:

```bash
hermes cron create "0 20 * * 0" \
  "Use the family-intelligence-briefing skill to consolidate the last 7 daily notes into a review-pending weekly review. Save it to 05_Output/Weekly_Reviews. Do not update long-term topic, asset, graph, project, report, or article notes." \
  --skill family-intelligence-briefing \
  --deliver feishu \
  --name family-weekly-knowledge
```

## Troubleshooting

- If the briefing lacks sources, rerun with explicit instruction to use web/search tools and include URLs.
- If Feishu/Lark messages do not arrive, run `hermes gateway status`, check Feishu/Lark platform setup, app bot permissions, event subscription, and gateway logs.
- If notes are missing, check `skills.config.family_intelligence.vault_path`.
- If the model choice is wrong, use Hermes-native model configuration (`hermes model`, `hermes setup`, or Hermes config), not project `.env`.
- If cron does not run, check `hermes cron status` and ensure the Hermes gateway is running.
