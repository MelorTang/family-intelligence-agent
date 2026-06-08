# Role

你是我的个人 Obsidian 知识库维护助手。

# Architecture

云端服务器只运行 Hermes、定时任务、Markdown 文件生成和 Git 同步。它不运行 Claude Code、Codex、Antigravity 或其他重 agent。

本地 Mac 或可信海外环境可以手动运行 Claude Code、Codex、Antigravity 或其他 CLI agent。Agent 把这个 vault 当成普通 Markdown/Git 仓库处理，不需要 Obsidian 插件才能工作。

最终判断、链接、长期沉淀和发布输出都在本地 Obsidian 中人工完成。

# Rules

1. 不修改原始资料，除非我明确要求。
2. 不删除、合并、重命名长期笔记，除非我明确要求。
3. 自动生成内容必须标记 `review: pending`。
4. 不确定内容标记 `TODO_VERIFY`。
5. 长期知识进入 `04_LLM_Wiki` 前必须经过人工确认。
6. 云端自动化只写 Inbox、Daily Briefings、Weekly Reviews、To_Review 和 logs。
7. 每次批量修改前先说明计划。
8. 每次修改后输出变更摘要。
9. 不创建复杂标签体系。
10. 不把 AI 生成内容标记为 `verified`。
11. 回答用户问题时，如果依据 `review: pending` 内容，必须明确标注“未人工审核”。
12. 不联网补充事实，除非用户明确要求；默认优先基于本 vault 内容回答。

# Allowed Cloud Write Paths

```text
00_Inbox/Hermes/
00_Inbox/AI_Processed/To_Review/
05_Output/Daily_Briefings/
05_Output/Weekly_Reviews/
99_System/Automation/logs/
```

# Protected Paths

```text
01_Projects/
02_Areas/
03_Resources/
04_LLM_Wiki/
06_Graph/
07_Daily/
05_Output/Reports/
05_Output/Articles/
Home.md
MOC files
long-term concept notes
```

# Agent Usage

Hermes handles light unattended tasks: collection, summarization, candidate links, candidate concepts, daily briefings, and weekly reviews.

Claude Code, Codex, Antigravity, or other CLI agents should be used for heavier maintenance only when manually triggered.

Before making changes, run or ask the user to run:

```bash
git pull --rebase
git status
```

After making changes, run or ask the user to review:

```bash
git diff
git status
```

Only commit explicitly reviewed files. Do not use `git add .` for broad vault changes unless the user explicitly approves.

# Local Agent Entry Prompt

When a CLI agent starts in this vault, it should first read this file. A good first instruction is:

```text
Read 99_System/Agents/AGENTS.md first. Do not modify files unless I explicitly approve. Summarize today's Hermes inbox and propose a review plan.
```
