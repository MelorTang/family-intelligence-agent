---
name: family-intelligence-briefing
description: Hermes-native workflow for Chinese family global news, investment risk observation, Feishu delivery, and Obsidian-style knowledge notes.
version: 0.2.0
author: MelorTang
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [research, news, finance, feishu, obsidian, automation, chinese, family]
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
      - key: family_intelligence.feishu_enabled
        description: Whether to publish the daily summary to a Feishu custom bot.
        default: "true"
        prompt: Enable Feishu publishing
required_environment_variables:
  - name: FEISHU_WEBHOOK_URL
    prompt: Feishu custom bot webhook URL
    help: Only required when family_intelligence.feishu_enabled is true.
    required_for: Feishu publishing
  - name: FEISHU_SECRET
    prompt: Feishu custom bot signing secret
    help: Optional. Leave empty if Feishu signing is disabled.
    required_for: Signed Feishu webhook publishing
---

# Family Intelligence Briefing

## Core Principle

Hermes is the agent. Do not build or call a separate news agent.

Use Hermes built-ins for:

- model/provider selection via `hermes model` and Hermes config
- web research through the active web/search tools
- cron scheduling through Hermes cron
- file writing through terminal/file tools
- memory and long-term learning through Hermes itself
- skill settings through `skills.config.family_intelligence.*`

This skill is a workflow contract and prompt pack. It should guide Hermes to produce a calm Chinese family briefing, save Markdown knowledge notes, and optionally post a short text summary to Feishu.

## When to Use

Use this skill when the user asks for:

- 每日家庭全球资讯简报
- 投资观察、市场风险、家庭资产风险提醒
- 给家人看的全球热点资讯摘要
- 信息茧房破除
- 飞书群定时推送
- Obsidian / Markdown 知识库沉淀
- 周报、主题页、长期知识沉淀

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
7. Publish a shorter summary to Feishu if enabled.

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

## Feishu Publishing

If `skills.config.family_intelligence.feishu_enabled` is true, send a short text summary to Feishu using `scripts/send_feishu_text.py`.

This integration uses a Feishu group custom bot webhook. Treat it as one-way publishing into the group where the custom bot was created. It is suitable for daily reports and notifications.

Do not assume the custom bot can:

- respond to @ mentions
- read user, tenant, or group-member information
- handle direct messages
- provide interactive bot menus

If the user wants interactive Q&A inside Feishu later, recommend a Feishu app bot with event subscriptions and message APIs instead of a custom bot webhook.

The Feishu message should contain:

- 标题和日期
- 一句话总结
- 今日最重要的 5 件事
- 今日投资温度
- 给家人的提醒

Keep the message under 3000 Chinese characters.

Example:

```bash
python ~/.hermes/skills/research/family-intelligence-briefing/scripts/send_feishu_text.py <<'EOF'
🌍 今日家庭全球简报｜YYYY-MM-DD

一句话总结：...

今日最重要的 5 件事：
1. ...

今日投资温度：
美股：...
A股：...

给家人的提醒：
今天没有必须马上行动的大事。不要因为单条新闻冲动投资。
EOF
```

If Feishu is not configured, still save the Markdown report and tell the user Feishu was skipped.

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
  "Use the family-intelligence-briefing skill to produce today's family global intelligence briefing. Save the full Markdown to the configured vault path and publish the short summary to Feishu if configured." \
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
- If Feishu fails, check `FEISHU_WEBHOOK_URL` and `FEISHU_SECRET` in Hermes environment.
- If notes are missing, check `skills.config.family_intelligence.vault_path`.
- If the model choice is wrong, use Hermes-native model configuration (`hermes model`, `hermes setup`, or Hermes config), not project `.env`.
- If cron does not run, check `hermes cron status` and ensure the Hermes gateway is running.
