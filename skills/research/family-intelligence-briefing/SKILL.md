---
name: family-intelligence-briefing
description: Hermes-native workflow for Chinese family global news, investment risk observation, Feishu/Lark app-bot conversations, cron delivery, and Obsidian-style knowledge notes.
version: 0.3.0
author: MelorTang
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [research, news, finance, feishu, lark, obsidian, automation, chinese, family]
    requires_toolsets: [web, terminal]
    config:
      - key: family_intelligence.vault_path
        description: Directory where daily, weekly, and topic Markdown notes should be saved.
        default: "~/family-intelligence-vault"
        prompt: Family intelligence knowledge-base path
      - key: family_intelligence.daily_schedule
        description: Daily Hermes cron schedule.
        default: "every 1d at 08:00"
        prompt: Daily briefing schedule
      - key: family_intelligence.weekly_schedule
        description: Weekly Hermes cron schedule for knowledge consolidation.
        default: "every sunday at 20:00"
        prompt: Weekly consolidation schedule
      - key: family_intelligence.timezone
        description: Local timezone for dates in notes and messages.
        default: "Asia/Seoul"
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
- memory and long-term learning through Hermes itself
- skill settings through `skills.config.family_intelligence.*`

This skill is a workflow contract and prompt pack. It should guide Hermes to produce a calm Chinese family briefing, save Markdown knowledge notes, and reply naturally in Feishu/Lark conversations.

## When to Use

Use this skill when the user asks for:

- 每日家庭全球资讯简报
- 投资观察、市场风险、家庭资产风险提醒
- 给家人看的全球热点资讯摘要
- 信息茧房破除
- 飞书单聊或群里 @ 机器人提问
- 飞书群定时日报/周报
- Obsidian / Markdown 知识库沉淀
- 周报、主题页、长期知识沉淀

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

## Knowledge Base Layout

Resolve the configured vault path from `skills.config.family_intelligence.vault_path`. Create directories if missing:

```text
{vault_path}/
  01_Daily/
  02_Weekly/
  03_Topics/
  04_Assets/
  99_Raw/
```

Use Markdown files. Do not require a database for MVP.

## Daily Workflow

When running the daily briefing:

1. Use Hermes web/search tools to research these categories:
   - 全球重要新闻：world top news today、全球 重要 新闻 今天
   - 市场：US stock market Fed inflation Treasury yields、A股 今日 市场 情绪、港股 科技股、gold oil dollar market
   - 科技：AI technology major news today、人工智能 重大 新闻
   - 地缘：geopolitical risk war oil gold、地缘政治 风险 黄金 原油
   - 中国：经济 政策 房地产 就业 消费
   - 家庭风险：诈骗、食品安全、医疗、养老、消费陷阱
2. Prefer diverse, traceable sources. Keep URLs.
3. Deduplicate semantically in reasoning: same event from multiple sources should become one item with multiple sources.
4. Produce a family-readable Chinese report.
5. Save full Markdown to `{vault_path}/01_Daily/YYYY-MM-DD.md`.
6. Save raw links and brief source notes to `{vault_path}/99_Raw/YYYY-MM-DD.md` when useful.
7. Return a shorter summary to the active Feishu/Lark chat when invoked from Feishu. For scheduled runs, deliver the summary through Hermes cron's configured delivery/home chat behavior.

Daily Markdown format:

```markdown
---
date: YYYY-MM-DD
type: daily_briefing
audience: family
source: hermes
---

# 今日家庭全球简报

## 一句话总结

## 今日最重要的 5 件事

### 1. 标题
发生了什么：
为什么重要：
对普通家庭的影响：
投资影响：
不确定性：
来源：

## 今日投资温度
- 美股：
- A股：
- 港股：
- 黄金：
- 美元：
- 原油：

## 投资观察

## 给家人的提醒

## 原始来源
```

## Feishu/Lark Summary

When replying in Feishu/Lark, keep the message concise and family-readable.

The chat summary should contain:

- 标题和日期
- 一句话总结
- 今日最重要的 5 件事
- 今日投资温度
- 给家人的提醒

Keep the chat message under 3000 Chinese characters unless the user explicitly asks for the full report. The full report should live in the Markdown knowledge base.

## Weekly Workflow

When running weekly consolidation:

1. Read the last 7 daily notes from `{vault_path}/01_Daily`.
2. Create `{vault_path}/02_Weekly/YYYY-Www.md`.
3. Update topic notes in `{vault_path}/03_Topics`, such as:
   - AI.md
   - 黄金.md
   - 美股.md
   - A股.md
   - 港股.md
   - 中国经济.md
   - 地缘风险.md
   - 家庭防诈骗.md
4. Update asset notes in `{vault_path}/04_Assets` when patterns recur.

Weekly note structure:

```markdown
---
week: YYYY-Www
type: weekly_briefing
audience: family
source: hermes
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
hermes cron create "every 1d at 08:00" \
  "Use the family-intelligence-briefing skill to produce today's family global intelligence briefing. Save the full Markdown to the configured vault path and deliver a concise family summary back to the Feishu/Lark home chat." \
  --skill family-intelligence-briefing \
  --name family-daily-briefing
```

Weekly:

```bash
hermes cron create "every sunday at 20:00" \
  "Use the family-intelligence-briefing skill to consolidate the last 7 daily notes into a weekly family intelligence report and update topic notes in the configured vault path." \
  --skill family-intelligence-briefing \
  --name family-weekly-knowledge
```

## Troubleshooting

- If the briefing lacks sources, rerun with explicit instruction to use web/search tools and include URLs.
- If Feishu/Lark messages do not arrive, run `hermes gateway status`, check Feishu/Lark platform setup, app bot permissions, event subscription, and gateway logs.
- If notes are missing, check `skills.config.family_intelligence.vault_path`.
- If the model choice is wrong, use Hermes-native model configuration (`hermes model`, `hermes setup`, or Hermes config), not project `.env`.
- If cron does not run, check `hermes cron status` and ensure the Hermes gateway is running.
