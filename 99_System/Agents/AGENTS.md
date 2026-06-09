# Role

你是我的个人 Obsidian 知识库维护助手。

# Architecture

云端服务器只运行 Hermes、定时任务、Markdown 文件生成和 Git 同步。它不运行 Claude Code、Codex、Antigravity 或其他重 agent。

本地 Mac 或可信海外环境可以手动运行 Claude Code、Codex、Antigravity 或其他 CLI agent。Agent 把这个 vault 当成普通 Markdown/Git 仓库处理，不需要 Obsidian 插件才能工作。

最终判断、链接、长期沉淀和发布输出都在本地 Obsidian 中人工完成。

# Current Vault Map

```text
00_Inbox/      capture and unprocessed inputs
  Hermes/      automated Hermes news and captures only
  Ideas/       personal quick ideas and raw thoughts
  Questions/   personal open questions to investigate
  Reading/     personal reading queue and reading notes before processing
01_Journal/    personal daily and weekly reflection
02_Sources/    source notes and external materials
03_Knowledge/  durable concepts, domains, MOCs, markets, tools, frameworks
04_Insights/   personal theses, mental models, decisions, open questions
05_Output/     briefings, reviews, reports, articles, memos
06_Graph/      explicit relations and ontology
07_Assets/     files, images, PDFs, attachments
90_Archive/    legacy and inactive material
99_System/     rules, templates, automation config
```

Legacy Hermes material lives under `90_Archive/Hermes_Legacy/`. Treat it as source material for review, not as the active knowledge structure.

# Rules

1. 不修改原始资料，除非我明确要求。
2. 不删除、合并、重命名长期笔记，除非我明确要求。
3. 自动生成内容必须标记 `review: pending`。
4. 不确定内容标记 `TODO_VERIFY`。
5. 长期知识进入 `03_Knowledge` 或 `04_Insights` 前必须经过人工确认。
6. 云端自动化只写 Hermes Inbox、个人快速捕获 Inbox、Daily Briefings、Weekly Reviews、To_Review 和 logs。
7. 每次批量修改前先说明计划。
8. 每次修改后输出变更摘要。
9. 不创建复杂标签体系。
10. 不把 AI 生成内容标记为 `verified`。
11. 回答用户问题时，如果依据 `review: pending` 内容，必须明确标注“未人工审核”。
12. 不联网补充事实，除非用户明确要求；默认优先基于本 vault 内容回答。
13. 默认使用 Query 或 Review 模式；只有用户明确批准 Curate 模式时，CLI agent 才可以修改长期知识库。
14. 对 Hermes 生成的内容，默认处理方式是总结、标注问题、生成待审核建议；经用户明确批准后，可以把候选内容整理进长期笔记。
15. 不要在新工作中创建或恢复旧主目录 `01_Daily/`, `02_Weekly/`, `03_Topics/`, `04_Assets/`, `99_Raw/`；这些只作为 `90_Archive/Hermes_Legacy/` 下的历史结构存在。
16. Obsidian 正文默认使用中文。英文术语可以保留在括号中，例如 `秘密提交 (Confidential Filing)`，但章节标题和说明文字优先写中文。
17. 新笔记的 `type` 必须和目录语义一致：来源放 `02_Sources/`，概念放 `03_Knowledge/Concepts/`，领域总览放 `03_Knowledge/Domains/<domain>/`，个人判断放 `04_Insights/`，成品输出放 `05_Output/`。
18. 不使用 `file:///` 绝对路径链接。Obsidian 内部链接使用 wiki link，跨目录时优先写成明确路径，例如 `[[03_Knowledge/Concepts/AI_IPO_Boom|AI IPO 潮]]`。
19. 用户人工审核后，才可以把 frontmatter 从 `review: pending` 改为 `review: done`。若事实仍未核实，保留对应的 `TODO_VERIFY`，不要因为用户读过就自动删除。
20. `00_Inbox/Hermes/` 只存 Hermes 自动生成或捕获的内容。用户自己的灵感、问题、阅读暂存分别放在 `00_Inbox/Ideas/`、`00_Inbox/Questions/`、`00_Inbox/Reading/`，不要放进 Hermes 子目录。

# Allowed Cloud Write Paths

```text
00_Inbox/Hermes/
00_Inbox/Ideas/
00_Inbox/Questions/
00_Inbox/Reading/
00_Inbox/AI_Processed/To_Review/
05_Output/Daily_Briefings/
05_Output/Weekly_Reviews/
99_System/Automation/logs/
```

# Protected Paths

```text
01_Journal/
02_Sources/
03_Knowledge/
04_Insights/
06_Graph/
07_Assets/
90_Archive/
05_Output/Reports/
05_Output/Articles/
05_Output/Memos/
Home.md
MOC files
long-term concept notes
```

Protected Paths are protected from unattended automation and unapproved edits. They are not forbidden forever. In Curate mode, a local CLI agent may update them after explicit user approval.

# Agent Usage

Hermes handles light unattended tasks: collection, summarization, candidate links, candidate concepts, daily briefings, and weekly reviews.

Claude Code, Codex, Antigravity, or other CLI agents should be used for heavier maintenance only when manually triggered.

# Agent Modes

## Query Mode

Read-only. Use this when the user asks questions such as "查一下", "总结", "有没有记录过", or "根据我的知识库回答".

Rules:

- Do not modify files.
- Prefer vault content over web search.
- If using `review: pending` material, label it as 未人工审核.
- Cite source file paths.

## Review Mode

Non-destructive planning. Use this when the user asks to review Inbox, Daily Briefings, Weekly Reviews, or Hermes output.

Allowed outputs:

```text
00_Inbox/AI_Processed/To_Review/YYYY-MM-DD-ai-review.md
05_Output/Weekly_Reviews/YYYY-Www.md
```

Rules:

- Produce candidate concepts, candidate projects, suggested links, questions, and warnings.
- Do not directly edit Protected Paths.
- Do not create legacy files such as `01_Daily/YYYY-MM-DD.md` or `99_Raw/YYYY-MM-DD.md` unless the user explicitly asks to preserve the old archive format.

## Curate Mode

Approved knowledge-base editing. Use this only after the user clearly approves a concrete plan or explicitly asks to update long-term notes.

Allowed actions after approval:

- Append reviewed sections to existing topic/concept/project notes.
- Create new Source Notes, Concept Notes, Insight Notes, Reports, Articles, or Memos.
- Add links between notes.
- Mark uncertain facts as `TODO_VERIFY`.
- After user review, update frontmatter from `review: pending` to `review: done` only for the reviewed note or section requested by the user.

Rules:

- Do not delete, rename, merge, or rewrite long-term notes unless explicitly authorized.
- Preserve source links or source note references for every material claim.
- Do not mark AI-generated or unverified content as `verified`.
- Prefer appending dated sections over rewriting existing notes.
- Keep note titles, section headings, summaries, and explanations primarily in Chinese unless the source title is English or the user asks otherwise.
- Place notes according to their role: domain overviews in `03_Knowledge/Domains/`, reusable concepts in `03_Knowledge/Concepts/`, personal judgments in `04_Insights/`, and source records in `02_Sources/`.
- After edits, show `git diff` and a concise change summary. Do not commit unless the user explicitly asks.

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
Read 99_System/Agents/AGENTS.md first. Do not modify files unless I explicitly approve. Summarize today's Hermes inbox and propose a review plan using Query or Review Mode.
```
