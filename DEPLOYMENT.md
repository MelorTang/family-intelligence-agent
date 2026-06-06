# 云端部署：Hermes Native

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
chmod +x ~/.hermes/skills/research/family-intelligence-briefing/scripts/send_feishu_text.py
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
hermes config set skills.config.family_intelligence.daily_schedule "every 1d at 08:00"
hermes config set skills.config.family_intelligence.weekly_schedule "every sunday at 20:00"
hermes config set skills.config.family_intelligence.timezone Asia/Seoul
hermes config set skills.config.family_intelligence.feishu_enabled true
```

## 4. 配置飞书密钥

飞书变量需要出现在 Hermes gateway 运行时环境中：

```bash
FEISHU_WEBHOOK_URL=
FEISHU_SECRET=
```

如果 gateway 是 systemd 服务，放到服务环境文件里并重启服务。不要把真实 webhook 提交到 Git。

## 5. 手动测试

在 Hermes 里运行：

```text
/family-intelligence-briefing 跑一次今天的家庭全球简报，保存到知识库，并推送飞书
```

检查：

```bash
ls -la ~/family-intelligence-vault
```

## 6. 创建 Cron

日报：

```bash
hermes cron create "every 1d at 08:00" \
  "Use the family-intelligence-briefing skill to produce today's family global intelligence briefing. Save the full Markdown to the configured vault path and publish the short summary to Feishu if configured." \
  --skill family-intelligence-briefing \
  --name family-daily-briefing
```

周报：

```bash
hermes cron create "every sunday at 20:00" \
  "Use the family-intelligence-briefing skill to consolidate the last 7 daily notes into a weekly family intelligence report and update topic notes in the configured vault path." \
  --skill family-intelligence-briefing \
  --name family-weekly-knowledge
```

## 7. 运维命令

```bash
hermes cron list
hermes cron status
hermes cron run family-daily-briefing
hermes cron run family-weekly-knowledge
hermes gateway status
```

## 设计原则

不要在本项目里配置 LLM、Tavily、scheduler、数据库或独立 agent。Hermes 已经处理这些。

本仓库只承担两件事：

1. 给 Hermes 一个清晰、可复用的家庭资讯工作流 skill。
2. 提供飞书自定义机器人 webhook 的最小发送脚本。
