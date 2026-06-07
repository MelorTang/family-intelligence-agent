# Family Intelligence Briefing for Hermes

这是一个 **Hermes-native skill**，用于让 Hermes 在飞书里像正常应用机器人一样工作：可以单聊、可以在群里被 @ 回复，同时支持定时日报、周报和 Markdown / Obsidian 风格知识沉淀。

目标不是再造 agent，也不是做飞书 webhook 通知脚本。Hermes 已经支持 Feishu/Lark messaging gateway，本仓库只提供：

- `SKILL.md`：告诉 Hermes 如何做家庭资讯日报、周报和知识沉淀
- 部署说明：如何把 skill 安装到云端 Hermes，并配合 Hermes Feishu/Lark gateway 使用

## 用途

- 家人在飞书里直接和 Hermes 应用机器人单聊
- 家庭群里 @ 机器人后获得回复
- 每天定时推送全球热点、市场风险、科技新闻、地缘风险、生活风险提醒
- 帮不擅长主动搜索信息的家人打破信息茧房
- 给你自己沉淀 Markdown / Obsidian 风格知识库
- 每周整理主题页和资产观察页

> 投资内容只做信息整理、风险观察和家庭资产提醒，不是交易指令，也不是持牌投资顾问意见。

## 安装 Skill

在已经安装 Hermes 的服务器上：

```bash
git clone https://github.com/MelorTang/family-intelligence-agent.git
cd family-intelligence-agent
mkdir -p ~/.hermes/skills/research
cp -R skills/research/family-intelligence-briefing ~/.hermes/skills/research/
```

然后在 Hermes 或飞书里使用：

```text
/family-intelligence-briefing 跑一次今天的家庭全球简报
```

## Hermes 配置

模型、搜索和工具不要在本项目里配置，直接使用 Hermes 自己的配置：

```bash
hermes model
hermes tools
hermes config show
```

skill 的非密钥配置建议放到 Hermes config：

```bash
hermes config set skills.config.family_intelligence.vault_path ~/family-intelligence-vault
hermes config set skills.config.family_intelligence.daily_schedule "0 8 * * *"
hermes config set skills.config.family_intelligence.weekly_schedule "0 20 * * 0"
hermes config set skills.config.family_intelligence.timezone Asia/Seoul
```

也可以运行：

```bash
hermes config migrate
```

让 Hermes 根据 skill frontmatter 提示你补齐配置。

## 飞书应用机器人

使用 Hermes 自带的 **Feishu/Lark messaging gateway**，对应飞书开放平台里的「应用机器人」。不要使用群自定义机器人 webhook。

飞书开放平台侧需要：

- 创建自建应用
- 开启机器人能力
- 配置事件订阅，订阅「接收消息」事件
- 申请单聊消息、群聊 @ 消息、发送/回复消息相关权限
- 发布应用
- 把应用机器人添加到目标家庭群

Hermes 侧：

```bash
hermes gateway setup
```

在平台列表里选择 Feishu/Lark，按提示填入飞书应用凭据。配置完成后启动或重启 gateway：

```bash
hermes gateway restart
hermes gateway status
```

Hermes 文档中 Feishu/Lark 是完整 messaging platform，支持文本、图片、文件、线程、反应、typing、streaming 等能力，并有独立 toolset `hermes-feishu`。实际权限仍取决于飞书应用授权和事件订阅。

## 创建 Cron

日报：

```bash
hermes cron create "0 8 * * *" \
  "Use the family-intelligence-briefing skill to produce today's family global intelligence briefing. Save the full Markdown to the configured vault path. Deliver the final Feishu/Lark summary using the exact template defined in the skill, without raw Markdown, tool logs, or CronJob Response text." \
  --skill family-intelligence-briefing \
  --deliver feishu \
  --name family-daily-briefing
```

周报和知识沉淀：

```bash
hermes cron create "0 20 * * 0" \
  "Use the family-intelligence-briefing skill to consolidate the last 7 daily notes into a weekly family intelligence report and update topic notes in the configured vault path." \
  --skill family-intelligence-briefing \
  --deliver feishu \
  --name family-weekly-knowledge
```

家庭群建议关闭工具调用进度，只保留最终回复：

```bash
hermes config set display.platforms.feishu.tool_progress off
hermes config set display.interim_assistant_messages false
hermes gateway restart
```

检查：

```bash
hermes cron list
hermes cron status
```

## 知识库结构

Hermes 会按 skill 指引创建：

```text
~/family-intelligence-vault/
  01_Daily/
  02_Weekly/
  03_Topics/
  04_Assets/
  99_Raw/
```

## 飞书日报格式

飞书里最终摘要采用固定模板，避免每天格式漂移：

```text
📰 今日家庭全球简报｜YYYY-MM-DD

一句话总结：
……

━━━━━━━━━━━━━━
🌍 一、全球大事
1️⃣ 标题
发生了什么：……
对家里的影响：……
不确定性：……

━━━━━━━━━━━━━━
💰 二、市场与投资
1️⃣ 标题
发生了什么：……
对家里的影响：……
不确定性：……

今日投资温度：
• 美股：偏强/中性/偏弱/不确定｜一句话原因
• A股：偏强/中性/偏弱/不确定｜一句话原因
• 港股：偏强/中性/偏弱/不确定｜一句话原因
• 黄金：偏强/中性/偏弱/不确定｜一句话原因
• 美元：偏强/中性/偏弱/不确定｜一句话原因
• 原油：偏强/中性/偏弱/不确定｜一句话原因

━━━━━━━━━━━━━━
🤖 三、科技与 AI
1️⃣ 标题
发生了什么：……
对家里的影响：……
需要留意：……

━━━━━━━━━━━━━━
🇨🇳 四、中国经济与政策
1️⃣ 标题
发生了什么：……
对家里的影响：……
需要留意：……

━━━━━━━━━━━━━━
🛡️ 五、家庭生活风险雷达
1️⃣ 具体风险
谁容易受影响：……
家里今天怎么做：……
判断方法：……

━━━━━━━━━━━━━━
✅ 六、今日行动建议
今天建议：
1. ……
2. ……
3. ……

今日是否需要行动：
✅/⚠️ ……

📁 完整报告：~/family-intelligence-vault/01_Daily/YYYY-MM-DD.md
🔎 来源记录：~/family-intelligence-vault/99_Raw/YYYY-MM-DD.md
⚠️ 仅供信息整理与风险观察，不构成投资建议。
```

完整来源和更长分析保存在 Markdown 知识库里，不直接刷屏到家庭群。`99_Raw` 会保存查询、采用来源、放弃来源和信息缺口，便于判断后续是否需要接入更多 API 或 skill。

## 为什么不写独立 Python Runner

Hermes 已经支持：

- 使用任意模型和 provider
- web/search 工具
- skills
- cron
- gateway
- Feishu/Lark messaging platform
- memory
- 文件写入
- config 和环境变量管理

所以这个项目不再重复实现 Tavily client、LLM client、scheduler、Markdown writer、飞书消息 API 或 webhook。它只是一个 Hermes skill。
