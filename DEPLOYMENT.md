# 云端部署：Hermes Native + Feishu/Lark 应用机器人

前提：Ubuntu Server 24.04 LTS 已安装 Hermes。

## 1. 拉取 Skill 仓库

```bash
cd ~
git clone https://github.com/MelorTang/family-intelligence-agent.git
cd family-intelligence-agent
```

## 2. 安装 Skill

```bash
mkdir -p ~/.hermes/skills/research
cp -R skills/research/family-intelligence-briefing ~/.hermes/skills/research/
```

## 3. 配置 Hermes

模型和 provider 使用 Hermes 自己的配置：

```bash
hermes model
hermes tools
hermes config show
```

配置本 skill 的非密钥设置：

```bash
hermes config set skills.config.family_intelligence.vault_path ~/family-intelligence-vault
hermes config set skills.config.family_intelligence.daily_schedule "0 8 * * *"
hermes config set skills.config.family_intelligence.weekly_schedule "0 20 * * 0"
hermes config set skills.config.family_intelligence.timezone Asia/Seoul
```

## 4. 配置飞书应用机器人

这个项目使用 Hermes 自带的 Feishu/Lark messaging gateway，对接飞书「应用机器人」。不要使用飞书群自定义机器人 webhook。

飞书开放平台侧：

1. 创建自建应用。
2. 开启机器人能力。
3. 配置事件订阅，订阅「接收消息」事件。
4. 申请权限：单聊消息、群聊 @ 消息、发送/回复消息。具体权限名称以飞书开放平台当前页面为准。
5. 发布应用。
6. 把应用机器人添加到家庭群。

Hermes 侧：

```bash
hermes gateway setup
```

选择 Feishu/Lark，按提示填入飞书应用凭据。然后启动或重启 gateway：

```bash
hermes gateway restart
hermes gateway status
```

验证方式：

- 在飞书里私聊机器人，发送 `/status`
- 在家庭群里 @ 机器人，发送 `/whoami`
- 在飞书里发送 `/family-intelligence-briefing 跑一次今天的家庭全球简报`

## 5. 手动测试知识库

在 Hermes 或飞书里运行：

```text
/family-intelligence-briefing 跑一次今天的家庭全球简报，保存到知识库，并把摘要发回当前飞书会话
```

检查：

```bash
ls -la ~/family-intelligence-vault
```

## 6. 创建 Cron

日报：

```bash
hermes cron create "0 8 * * *" \
  "Use the family-intelligence-briefing skill to produce today's family global intelligence briefing. Save the full Markdown to the configured vault path and deliver a concise family summary back to the Feishu/Lark home chat." \
  --skill family-intelligence-briefing \
  --deliver feishu \
  --name family-daily-briefing
```

周报：

```bash
hermes cron create "0 20 * * 0" \
  "Use the family-intelligence-briefing skill to consolidate the last 7 daily notes into a weekly family intelligence report and update topic notes in the configured vault path." \
  --skill family-intelligence-briefing \
  --deliver feishu \
  --name family-weekly-knowledge
```

家庭群安静模式：

```bash
hermes config set display.platforms.feishu.tool_progress off
hermes config set display.interim_assistant_messages false
hermes gateway restart
```

## 7. 运维命令

```bash
hermes cron list
hermes cron status
hermes cron run family-daily-briefing
hermes cron run family-weekly-knowledge
hermes gateway status
```

如果 Feishu/Lark 没有回复：

```bash
journalctl --user -u hermes-gateway -f
```

或根据你的安装方式查看 Hermes gateway 日志。

## 设计原则

不要在本项目里配置 LLM、Tavily、scheduler、数据库、飞书消息 API 或独立 agent。Hermes 已经处理这些。

本仓库只承担一件事：给 Hermes 一个清晰、可复用的家庭资讯工作流 skill。
