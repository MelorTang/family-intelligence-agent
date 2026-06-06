# 云端部署说明

这个项目现在按 Hermes-first 思路设计：Hermes Agent 是真正的 agent，负责自然语言控制、云端 gateway、cron 调度和排障；本项目是一个稳定的 Python runner，负责 Tavily 搜索、OpenAI 总结、Markdown 写入和飞书推送。

## 推荐架构：Hermes-first

```text
VPS / 云主机
  ├─ Hermes Gateway 常驻
  │    └─ Hermes Cron
  │         ├─ cd family-intelligence-agent && python main.py run-daily
  │         └─ cd family-intelligence-agent && python main.py run-weekly
  └─ family-intelligence-agent
       ├─ Python runner
       ├─ data/ JSON 和日志
       ├─ obsidian_output/ 日报、周报、主题页
       └─ Feishu Webhook
```

保留 Python runner 的原因不是“再做一个 agent”，而是把需要稳定重复执行的细节固化下来。Hermes skill 负责告诉 Hermes 如何调用它、如何排查它、如何创建定时任务。

## 安装 Hermes Skill

本仓库包含 skill：

```text
skills/research/family-intelligence-briefing/
```

复制到 Hermes skills 目录：

```bash
mkdir -p ~/.hermes/skills/research
cp -R skills/research/family-intelligence-briefing ~/.hermes/skills/research/
```

之后可以在 Hermes 里使用：

```text
/family-intelligence-briefing 跑一次今天的日报
```

## Docker Compose 部署

在服务器上准备代码和 `.env`：

```bash
cd family-intelligence-agent
cp .env.example .env
nano .env
```

如果只想把 runner 容器化，也可以启动：

```bash
docker compose up -d --build
```

查看日志：

```bash
docker compose logs -f
```

手动跑一次日报：

```bash
docker compose run --rm family-intelligence-agent python main.py run-daily
```

停止：

```bash
docker compose down
```

## VPS 直接部署

```bash
cd family-intelligence-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
python main.py run-daily
python main.py schedule
```

如果使用 `systemd`，可以创建服务让它开机自启：

```ini
[Unit]
Description=Family Intelligence Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/family-intelligence-agent
EnvironmentFile=/opt/family-intelligence-agent/.env
ExecStart=/opt/family-intelligence-agent/.venv/bin/python main.py schedule
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Hermes Agent 用法建议

Hermes 文档里 Cron 由 gateway daemon 执行；云端要保证 `hermes gateway` 常驻，可以安装成系统服务。Hermes Cron 支持 `--workdir`，因此要指定本项目的绝对路径。

示例：

```bash
hermes cron create "every 1d at 08:00" \
  "Run: python main.py run-daily. If it fails, summarize the error log from data/logs/app.log." \
  --workdir /opt/family-intelligence-agent \
  --name family-daily-briefing
```

周报和知识库沉淀：

```bash
hermes cron create "every sunday at 20:00" \
  "Run: python main.py run-weekly. If it fails, summarize the error log from data/logs/app.log." \
  --workdir /opt/family-intelligence-agent \
  --name family-weekly-knowledge
```

如果只是执行脚本，不需要 Hermes 再启动一个 LLM agent，可以用 Hermes 的 no-agent/script-only cron 思路：让脚本直接执行 `python main.py run-daily`，stdout 作为结果投递。这样成本更低，也更稳定。

## 飞书机器人注意事项

本项目使用飞书自定义机器人 Webhook。飞书官方文档说明，自定义机器人属于当前群聊，通过向 Webhook URL 发送 HTTP 请求把消息推送到群里。

如果启用签名校验，请在 `.env` 填写 `FEISHU_SECRET`。签名规则是：

```text
timestamp + "\n" + secret 作为 HMAC-SHA256 key
对空字符串签名
结果 Base64 编码
```

项目里的 `FeishuPublisher` 已按这个规则实现。

## 云端数据持久化

至少持久化这两个目录：

```text
data/
obsidian_output/
```

如果部署在无状态平台，请挂载云盘、对象存储同步目录，或改造成把 Markdown 推送到 Git 仓库/对象存储。不要只依赖容器内部文件系统。

## 安全建议

- 不要把 `.env` 提交到 Git。
- 飞书 Webhook URL 和 Secret 都视为密钥。
- 云服务器安全组只开放必要端口。
- 日报 prompt 会处理互联网内容，后续可以增加来源白名单、黑名单和 prompt injection 过滤。
- 投资内容保持“观察和风险提示”，不要生成交易指令。
