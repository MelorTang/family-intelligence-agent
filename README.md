# Family Intelligence Skills for Hermes

这是一个 **Hermes-native skills** 仓库，用于让 Hermes 在飞书里像正常应用机器人一样工作：可以单聊、可以在群里被 @ 回复，同时支持定时日报、周报、快速捕获和 Markdown / Obsidian 风格知识沉淀。

目标不是再造 agent，也不是做飞书 webhook 通知脚本。Hermes 已经支持 Feishu/Lark messaging gateway，本仓库只提供：

- `family-daily-briefing`：每日新闻研究、写入 vault、飞书摘要
- `family-weekly-review`：每周复盘，只写周报和 To_Review 建议
- `family-quick-capture`：飞书随手记 ideas / questions / reading
- 部署说明：如何把 skill 安装到云端 Hermes，并配合 Hermes Feishu/Lark gateway 使用

## 用途

- 家人在飞书里直接和 Hermes 应用机器人单聊
- 家庭群里 @ 机器人后获得回复
- 每天定时推送全球热点、市场风险、科技新闻、地缘风险、生活风险提醒
- 帮不擅长主动搜索信息的家人打破信息茧房
- 给你自己沉淀 Markdown / Obsidian 风格知识库
- 每周整理 review-pending 周报和候选沉淀建议

> 投资内容只做信息整理、风险观察和家庭资产提醒，不是交易指令，也不是持牌投资顾问意见。

## 安装 Skills

在已经安装 Hermes 的服务器上：

```bash
git clone https://github.com/MelorTang/family-intelligence-agent.git
cd family-intelligence-agent
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

然后在 Hermes 或飞书里使用：

```text
/family-daily-briefing 跑一次今天的家庭全球简报
/family-quick-capture 记一个 idea：……
/family-weekly-review 生成本周复盘
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
hermes config set skills.config.family_intelligence.timezone Asia/Shanghai
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

## 更新已有 Cron

如果服务器上已经有旧的 `family-daily-briefing` / `family-weekly-knowledge` 任务，更新 skill 名和 prompt 后再重启 Hermes：

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
```

## Git 同步脚本

`scripts/hermes_git_sync.sh` 默认会先尝试从 `~/.hermes/cron/output` 导入当天 Hermes cron response。这样即使 Hermes 只把日报发到飞书、没有真正写入 vault，脚本也会生成 recovered 版 `News / Captures / Daily_Briefing` 后再提交。

它不会覆盖已有的实质性笔记，也不会生成空白日报占位文件。少数情况下如果只是想补目录骨架，可手动加 `--generate-placeholders`；如果想关闭 cron output 导入，可加 `--no-cron-import`。

cron 的 shell 输出不要重定向到 vault 内的 tracked 文件，否则重定向本身会让 `git pull --rebase` 看到未提交改动。推荐：

```cron
10 8 * * * /home/ubuntu/family-intelligence-agent/scripts/hermes_git_sync.sh --vault /home/ubuntu/family-intelligence-vault >> /home/ubuntu/hermes_git_sync_cron.log 2>&1
```

## 知识库结构

Hermes 会按 skill 指引创建：

```text
~/family-intelligence-vault/
  00_Inbox/
    Hermes/
      News/
      Captures/
      Logs/
    AI_Processed/
      To_Review/
  05_Output/
    Daily_Briefings/
    Weekly_Reviews/
  99_System/
    Automation/
      logs/
```

## 飞书日报格式

飞书里最终摘要采用固定模板，避免每天格式漂移：

```text
📰 今日家庭全球简报｜YYYY-MM-DD

**一句话总结**
今天市场和家庭风险的主线是……

━━━━━━━━━━━━━━
🌍 一、全球大事
1️⃣ **标题**
……
影响：……
变数：……

━━━━━━━━━━━━━━
💰 二、市场与投资
1️⃣ **标题**
……
影响：……
变数：……

**投资温度**
• 美股：偏强｜科技股带动，但利率仍是压力
• A股：震荡｜政策预期与现实数据拉扯
• 港股：偏弱｜科技股情绪仍不稳
• 黄金：偏强｜避险需求仍在
• 美元：中性｜等待利率信号
• 原油：偏强｜供应风险仍是主线

**资产快照**
• 标普500：回落｜利率担忧压制估值
• 纳斯达克：承压｜AI和科技股波动加大
• 上证综指：震荡｜成交和政策预期拉扯
• 恒生指数：偏弱｜外部市场情绪影响
• 黄金：偏强｜避险和利率预期影响
• WTI原油：偏强｜供应风险仍在
• 美元指数：中性｜等待美联储信号
• 比特币：高波动｜风险资产情绪影响较大

━━━━━━━━━━━━━━
🤖 三、科技与 AI
1️⃣ **标题**
……
影响：……
留意：……

━━━━━━━━━━━━━━
🇨🇳 四、中国经济与政策
1️⃣ **标题**
……
影响：……
留意：……

━━━━━━━━━━━━━━
🛡️ 五、家庭生活风险雷达
1️⃣ **具体风险**
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

完整来源和更长分析保存在 Markdown 知识库里，不直接刷屏到家庭群。日报和周报有长期复盘价值，但由云端生成时仍保持 `review: pending`，长期概念、项目、图谱、报告和文章由本地 Obsidian 人工沉淀。

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

所以这个项目不再重复实现 Tavily client、LLM client、scheduler、Markdown writer、飞书消息 API 或 webhook。它只提供小而明确的 Hermes skills。
