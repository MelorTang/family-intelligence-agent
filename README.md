# 家庭全球资讯与投资观察助手

一个给 Hermes Agent 调用的家庭资讯日报工作流 runner：每天从互联网抓取全球热门资讯、市场信息、科技新闻、地缘风险和家庭生活风险提醒，生成适合普通家庭阅读的中文简报，保存到 Obsidian Vault，并推送到飞书群机器人。

Hermes 是 agent；本项目只负责把固定流程稳定执行完。

> 注意：本项目不是投资顾问，也不提供交易指令。输出仅用于信息整理、风险观察和家庭沟通。

## 功能

- 提供 Hermes skill：`family-intelligence-briefing`
- 使用 Tavily 搜索配置好的资讯 query
- 对搜索结果做本地 JSON 存档
- 基于 URL、标题和正文片段做简单去重
- 使用 OpenAI-compatible LLM 生成结构化中文日报
- 自动生成 Obsidian Markdown
- 从日报生成周报和主题知识沉淀
- 使用飞书自定义机器人推送摘要
- 可由 Hermes Cron 定时触发
- 也保留本地 `schedule` 作为无 Hermes 时的 fallback
- 日志写入 `data/logs/app.log`

## Hermes 用法

本仓库包含一个 Hermes skill：

```text
skills/research/family-intelligence-briefing/SKILL.md
```

安装思路：

```bash
mkdir -p ~/.hermes/skills/research
cp -R skills/research/family-intelligence-briefing ~/.hermes/skills/research/
```

然后在 Hermes 里可以使用：

```text
/family-intelligence-briefing 跑一次今天的家庭全球简报
```

或让 Hermes 创建 cron：

```bash
hermes cron create "every 1d at 08:00" \
  "Run the family intelligence briefing workflow with: .venv/bin/python main.py run-daily. If it fails, inspect data/logs/app.log and summarize the error." \
  --workdir /absolute/path/to/family-intelligence-agent \
  --name family-daily-briefing
```

周报和知识沉淀：

```bash
hermes cron create "every sunday at 20:00" \
  "Run the family intelligence weekly knowledge workflow with: .venv/bin/python main.py run-weekly. If it fails, inspect data/logs/app.log and summarize the error." \
  --workdir /absolute/path/to/family-intelligence-agent \
  --name family-weekly-knowledge
```

如果 Hermes 已经常驻云端，推荐用 Hermes Cron，而不是长期运行 `python main.py schedule`。

## 安装

```bash
cd family-intelligence-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 配置方式

Hermes-first 部署时，推荐把密钥和模型配置交给 Hermes 管理。项目里的 `.env.example` 主要是本地测试模板，不是必须长期保存真实密钥。

runner 读取这些通用变量：

```env
TAVILY_API_KEY=你的 Tavily API Key

LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=你的模型服务 API Key
LLM_MODEL=你的模型 ID

FEISHU_WEBHOOK_URL=你的飞书机器人 Webhook
FEISHU_SECRET=飞书机器人签名密钥，可留空

OBSIDIAN_VAULT_PATH=./obsidian_output
TIMEZONE=Asia/Seoul
```

兼容旧变量名：`OPENAI_BASE_URL`、`OPENAI_API_KEY`、`OPENAI_MODEL`。

## 本地 `.env` 模板

打开 `.env`，填入：

```env
TAVILY_API_KEY=你的 Tavily API Key

LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=你的模型服务 API Key
LLM_MODEL=你的模型 ID

FEISHU_WEBHOOK_URL=你的飞书机器人 Webhook
FEISHU_SECRET=飞书机器人签名密钥，可留空

OBSIDIAN_VAULT_PATH=./obsidian_output
TIMEZONE=Asia/Seoul
```

`OBSIDIAN_VAULT_PATH` 可以改成你的真实 Obsidian Vault 路径，例如：

```env
OBSIDIAN_VAULT_PATH=/Users/yourname/Documents/Obsidian/FamilyVault
```

## 创建飞书机器人 Webhook

1. 打开飞书群。
2. 进入群设置，选择「机器人」。
3. 添加「自定义机器人」。
4. 复制 Webhook 地址到 `FEISHU_WEBHOOK_URL`。
5. 如果启用了「签名校验」，复制密钥到 `FEISHU_SECRET`。
6. 第一版发送普通 text 消息，不使用复杂卡片。

## 运行一次日报

```bash
python main.py run-daily
```

运行后会生成：

- 原始搜索结果：`data/raw/YYYY-MM-DD.json`
- 处理后结果：`data/processed/YYYY-MM-DD.json`
- Obsidian Markdown：`{OBSIDIAN_VAULT_PATH}/01_Daily/YYYY-MM-DD.md`
- 日志：`data/logs/app.log`

## 启动定时任务

```bash
python main.py schedule
```

默认每天 `08:00` 运行一次。时间来自 `config.yaml`：

```yaml
schedule:
  daily_time: "08:00"
```

这个本地定时任务需要进程持续运行。已经部署 Hermes 时，优先使用 Hermes Cron；没有 Hermes 时再使用这个 fallback。

## 云端部署

项目已包含 `Dockerfile` 和 `docker-compose.yml`。如果准备部署到 VPS 或云容器，优先看 [DEPLOYMENT.md](DEPLOYMENT.md)。

推荐第一版让 Hermes Gateway 常驻云端，并用 Hermes Cron 触发 `python main.py run-daily` 和 `python main.py run-weekly`。日报业务逻辑和知识库沉淀逻辑保留在这个 runner 里，Hermes 负责调度、远程控制和失败排查。

## 修改搜索 query

编辑 `config.yaml` 里的 `queries`：

```yaml
queries:
  markets:
    - "US stock market today Fed inflation Treasury yields"
    - "A股 今日 市场 情绪"
```

可以按类别增加、删除或替换 query。建议每个类别保留 1-5 条，不要一次放太多，否则成本和运行时间都会上升。

## 命令

```bash
python main.py run-daily
python main.py run-weekly
python main.py schedule
```

`run-daily` 负责当天飞书推送和日报归档。`run-weekly` 会读取最近 7 天日报，生成 `02_Weekly/YYYY-Www.md`，并更新 `03_Topics` 下的主题页。`schedule` 仅作为没有 Hermes 时的本地 fallback。

## 鲁棒性说明

- 单个 Tavily query 失败不会中断整体任务。
- LLM JSON 解析失败时会尝试提取 JSON；仍失败则保存原始内容或 fallback Markdown。
- 飞书推送失败会写日志并在命令行显示失败，不影响本地 Markdown 保存。
- Obsidian 目录不存在会自动创建。
- 外部请求设置了 timeout。

## 重要提醒

这份简报只适合做家庭信息同步和风险观察。投资相关内容必须结合自身风险承受能力，并参考专业人士意见。不要因为单条新闻做冲动交易，不要把本工具输出当成确定性预测。
