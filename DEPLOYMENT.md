# 云端部署：Hermes Native + Feishu/Lark 应用机器人

前提：Ubuntu Server 24.04 LTS 已安装 Hermes。

## 1. 拉取 Skill 仓库

```bash
cd ~
git clone https://github.com/MelorTang/family-intelligence-agent.git
cd family-intelligence-agent
```

## 2. 安装 Skills

```bash
mkdir -p ~/.hermes/skills/research
mkdir -p ~/.hermes/skills/capture
rm -rf ~/.hermes/skills/research/family-daily-briefing
rm -rf ~/.hermes/skills/research/family-weekly-review
rm -rf ~/.hermes/skills/capture/family-quick-capture
rm -rf ~/.hermes/skills/research/family-intelligence-briefing
cp -R skills/research/family-daily-briefing ~/.hermes/skills/research/
cp -R skills/research/family-weekly-review ~/.hermes/skills/research/
cp -R skills/capture/family-quick-capture ~/.hermes/skills/capture/
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
hermes config set skills.config.family_intelligence.timezone Asia/Shanghai
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
- 在飞书里发送 `/family-daily-briefing 跑一次今天的家庭全球简报`

## 5. 手动测试知识库

在 Hermes 或飞书里运行：

```text
/family-daily-briefing 跑一次今天的家庭全球简报，保存到知识库，并把摘要发回当前飞书会话
```

检查：

```bash
ls -la ~/family-intelligence-vault
```

## 6. 创建 Cron

日报：

```bash
hermes cron create "0 8 * * *" \
  "Use family-daily-briefing. You MUST write 00_Inbox/Hermes/News/YYYY-MM-DD-news.md, 00_Inbox/Hermes/Captures/YYYY-MM-DD-captures.md, and 05_Output/Daily_Briefings/YYYY-MM-DD-briefing.md to the configured vault path before returning the Feishu summary. If file writing fails, say FILE_WRITE_FAILED." \
  --skill family-daily-briefing \
  --deliver feishu \
  --name family-daily-briefing
```

周报：

```bash
hermes cron create "0 20 * * 0" \
  "Use family-weekly-review. Write only 05_Output/Weekly_Reviews/YYYY-Www.md and optionally 00_Inbox/AI_Processed/To_Review/YYYY-MM-DD-weekly-review.md. Do not update long-term notes." \
  --skill family-weekly-review \
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

## 8. 更新已有 Cron

如果服务器已经存在旧任务，不要新建重复任务，直接更新 `~/.hermes/cron/jobs.json`：

```bash
cp ~/.hermes/cron/jobs.json ~/.hermes/cron/jobs.json.bak.$(date +%F-%H%M%S)
python3 - <<'PY'
import json
from pathlib import Path

p = Path.home() / ".hermes/cron/jobs.json"
data = json.loads(p.read_text())

daily_prompt = (
    "Use family-daily-briefing. You MUST write "
    "00_Inbox/Hermes/News/YYYY-MM-DD-news.md, "
    "00_Inbox/Hermes/Captures/YYYY-MM-DD-captures.md, and "
    "05_Output/Daily_Briefings/YYYY-MM-DD-briefing.md to the configured vault path "
    "before returning the Feishu summary. If file writing fails, say FILE_WRITE_FAILED."
)
weekly_prompt = (
    "Use family-weekly-review. Write only 05_Output/Weekly_Reviews/YYYY-Www.md and "
    "optionally 00_Inbox/AI_Processed/To_Review/YYYY-MM-DD-weekly-review.md. "
    "Do not update long-term notes."
)

for job in data.get("jobs", []):
    if job.get("name") == "family-daily-briefing":
        job["skill"] = "family-daily-briefing"
        job["skills"] = ["family-daily-briefing"]
        job["prompt"] = daily_prompt
    elif job.get("name") == "family-weekly-knowledge":
        job["skill"] = "family-weekly-review"
        job["skills"] = ["family-weekly-review"]
        job["prompt"] = weekly_prompt

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
PY
hermes gateway restart
hermes cron list
```

## 9. Git 同步脚本

`scripts/hermes_git_sync.sh` 默认只同步 Hermes 已写入的真实文件，不再生成空白日报占位文件。少数情况下如果只是想补目录骨架，可手动加 `--generate-placeholders`。

## 设计原则

不要在本项目里配置 LLM、Tavily、scheduler、数据库、飞书消息 API 或独立 agent。Hermes 已经处理这些。

本仓库只承担一件事：给 Hermes 几个短而明确的家庭资讯工作流 skills。
