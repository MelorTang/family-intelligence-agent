# Family Intelligence Briefing for Hermes

这是一个 **Hermes-native skill**，用于让 Hermes 定期生成中文家庭全球资讯与投资风险观察简报。

目标不是再造一个 agent。Hermes 已经负责模型、搜索、记忆、定时任务、工具调用和云端常驻；这个仓库只提供：

- `SKILL.md`：告诉 Hermes 如何做家庭资讯日报、周报和知识沉淀
- `send_feishu_text.py`：飞书自定义机器人文本推送小脚本
- 部署说明：如何把 skill 安装到云端 Hermes

## 用途

- 每天给家人推送全球热点、市场风险、科技新闻、地缘风险、生活风险提醒
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
chmod +x ~/.hermes/skills/research/family-intelligence-briefing/scripts/send_feishu_text.py
```

然后在 Hermes 中使用：

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
hermes config set skills.config.family_intelligence.daily_schedule "every 1d at 08:00"
hermes config set skills.config.family_intelligence.weekly_schedule "every sunday at 20:00"
hermes config set skills.config.family_intelligence.timezone Asia/Seoul
hermes config set skills.config.family_intelligence.feishu_enabled true
```

也可以运行：

```bash
hermes config migrate
```

让 Hermes 根据 skill frontmatter 提示你补齐配置。

## 飞书 Webhook

飞书 webhook 和 secret 属于密钥，不要写进 Git。

这里使用的是飞书「群自定义机器人」，它的定位是：通过 webhook 向创建它的当前群聊单向推送消息。它适合日报、告警、通知这类场景。

它不是飞书「应用机器人」：

- 不能响应家人在群里 @ 机器人的消息
- 不能获取用户、租户、群成员等信息
- 不能做单聊或复杂交互

如果以后要让家人在飞书里直接提问、追问、点菜单，就需要改成飞书应用机器人，并接入事件订阅和消息 API。当前 MVP 只做定时推送，所以自定义机器人足够。

如果你的 Hermes 环境支持环境变量管理，把它们放到 Hermes 的环境里：

```bash
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/..."
export FEISHU_SECRET="..."
```

如果你的 Hermes gateway 是 systemd/服务方式运行，请把这两个变量放到 Hermes 服务实际读取的环境文件中，然后重启 gateway。

如果没有启用飞书签名，`FEISHU_SECRET` 可以为空。

建议在飞书自定义机器人安全设置里启用签名校验；脚本已经按飞书规则生成 `timestamp` 和 `sign`。也可以结合关键词或 IP 白名单，但云服务器 IP 变化时要同步更新白名单。

## 创建 Cron

日报：

```bash
hermes cron create "every 1d at 08:00" \
  "Use the family-intelligence-briefing skill to produce today's family global intelligence briefing. Save the full Markdown to the configured vault path and publish the short summary to Feishu if configured." \
  --skill family-intelligence-briefing \
  --name family-daily-briefing
```

周报和知识沉淀：

```bash
hermes cron create "every sunday at 20:00" \
  "Use the family-intelligence-briefing skill to consolidate the last 7 daily notes into a weekly family intelligence report and update topic notes in the configured vault path." \
  --skill family-intelligence-briefing \
  --name family-weekly-knowledge
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

## 为什么不写独立 Python Runner

Hermes 已经支持：

- 使用任意模型和 provider
- web/search 工具
- skills
- cron
- gateway
- memory
- 文件写入
- config 和环境变量管理

所以这个项目不再重复实现 Tavily client、LLM client、scheduler、Markdown writer。唯一保留的小脚本是飞书群自定义机器人 webhook，因为它是当前家庭群推送的最小平台适配。
