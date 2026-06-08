#!/usr/bin/env bash
set -Eeuo pipefail

DRY_RUN=false
VAULT_PATH="${VAULT_PATH:-}"

usage() {
  cat <<'EOF'
Usage: init_vault.sh --vault /path/to/obsidian-vault [--dry-run]

Creates the personal knowledge-base directory scaffold used by Hermes.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --vault)
      VAULT_PATH="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$VAULT_PATH" ]]; then
  echo "Missing --vault or VAULT_PATH." >&2
  exit 2
fi

run() {
  if [[ "$DRY_RUN" == "true" ]]; then
    printf '[dry-run] %s\n' "$*"
  else
    "$@"
  fi
}

write_file_if_missing() {
  local path="$1"
  local content="$2"
  if [[ -e "$path" ]]; then
    printf 'exists: %s\n' "$path"
    return 0
  fi
  if [[ "$DRY_RUN" == "true" ]]; then
    printf '[dry-run] create file: %s\n' "$path"
  else
    printf '%s\n' "$content" > "$path"
    printf 'created: %s\n' "$path"
  fi
}

directories=(
  "00_Inbox/Hermes/News"
  "00_Inbox/Hermes/Captures"
  "00_Inbox/Hermes/Logs"
  "00_Inbox/AI_Processed/To_Review"
  "01_Projects"
  "02_Areas"
  "03_Resources"
  "04_LLM_Wiki/Concepts"
  "04_LLM_Wiki/People"
  "04_LLM_Wiki/Companies"
  "04_LLM_Wiki/Tools"
  "04_LLM_Wiki/Industries"
  "04_LLM_Wiki/Frameworks"
  "05_Output/Daily_Briefings"
  "05_Output/Weekly_Reviews"
  "05_Output/Reports"
  "05_Output/Articles"
  "06_Graph"
  "07_Daily"
  "90_Archive"
  "99_System/Agents"
  "99_System/Templates"
  "99_System/Prompts"
  "99_System/Hermes"
  "99_System/Claude"
  "99_System/Automation/logs"
)

run mkdir -p "$VAULT_PATH"
for dir in "${directories[@]}"; do
  run mkdir -p "$VAULT_PATH/$dir"
done

write_file_if_missing "$VAULT_PATH/AGENTS.md" "# Vault Agent Entry

Read and follow the canonical vault rules:

\`\`\`text
99_System/Agents/AGENTS.md
\`\`\`

This root file exists because some CLI agents automatically look for \`AGENTS.md\` in the workspace root."

write_file_if_missing "$VAULT_PATH/README.md" "# Personal Knowledge Vault

This vault is synchronized through GitHub. Cloud automation may only write inbox, daily briefing, AI review, and automation log directories. Long-term notes are curated locally in Obsidian."

write_file_if_missing "$VAULT_PATH/06_Graph/relations.csv" "source,relation,target,type,status,created,created_by,note"

write_file_if_missing "$VAULT_PATH/06_Graph/ontology.md" "# Ontology

Manual workspace for defining relationship types and knowledge graph conventions. Cloud automation must not update this file unless explicitly authorized."

write_file_if_missing "$VAULT_PATH/99_System/Automation/config.example.yaml" "vault_path: \"$VAULT_PATH\"
timezone: \"Asia/Shanghai\"

git:
  branch: \"main\"
  remote: \"origin\"
  allowed_add_paths:
    - \"00_Inbox/Hermes/\"
    - \"00_Inbox/AI_Processed/To_Review/\"
    - \"05_Output/Daily_Briefings/\"
    - \"05_Output/Weekly_Reviews/\"
    - \"99_System/Automation/logs/\"

hermes:
  enabled: true
  news_enabled: true
  captures_enabled: true
  daily_briefing_enabled: true
  weekly_review_enabled: true

ai_processing:
  enabled: false
  provider: \"\"
  model: \"\"
  output_dir: \"00_Inbox/AI_Processed/To_Review/\"

logging:
  log_dir: \"99_System/Automation/logs/\"
  level: \"INFO\""

write_file_if_missing "$VAULT_PATH/99_System/Agents/AGENTS.md" "# Role

你是我的个人 Obsidian 知识库维护助手。

# Architecture

云端服务器只运行 Hermes、定时任务、Markdown 文件生成和 Git 同步。它不运行 Claude Code、Codex、Antigravity 或其他重 agent。

本地 Mac 或可信海外环境可以手动运行 Claude Code、Codex、Antigravity 或其他 CLI agent。Agent 把这个 vault 当成普通 Markdown/Git 仓库处理，不需要 Obsidian 插件才能工作。

最终判断、链接、长期沉淀和发布输出都在本地 Obsidian 中人工完成。

# Rules

1. 不修改原始资料，除非我明确要求。
2. 不删除、合并、重命名长期笔记，除非我明确要求。
3. 自动生成内容必须标记 \`review: pending\`。
4. 不确定内容标记 \`TODO_VERIFY\`。
5. 长期知识进入 \`04_LLM_Wiki\` 前必须经过人工确认。
6. 云端自动化只写 Inbox、Daily Briefings、Weekly Reviews、To_Review 和 logs。
7. 每次批量修改前先说明计划。
8. 每次修改后输出变更摘要。
9. 不创建复杂标签体系。
10. 不把 AI 生成内容标记为 \`verified\`。
11. 回答用户问题时，如果依据 \`review: pending\` 内容，必须明确标注“未人工审核”。
12. 不联网补充事实，除非用户明确要求；默认优先基于本 vault 内容回答。
13. 默认使用 Query 或 Review 模式；只有用户明确批准 Curate 模式时，CLI agent 才可以修改长期知识库。
14. 对 Hermes 生成的内容，默认处理方式是总结、标注问题、生成待审核建议；经用户明确批准后，可以把候选内容整理进长期笔记。

# Allowed Cloud Write Paths

\`\`\`text
00_Inbox/Hermes/
00_Inbox/AI_Processed/To_Review/
05_Output/Daily_Briefings/
05_Output/Weekly_Reviews/
99_System/Automation/logs/
\`\`\`

# Protected Paths

\`\`\`text
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
\`\`\`

Protected Paths are protected from unattended automation and unapproved edits. They are not forbidden forever. In Curate mode, a local CLI agent may update them after explicit user approval.

# Agent Usage

Hermes handles light unattended tasks: collection, summarization, candidate links, candidate concepts, daily briefings, and weekly reviews.

Claude Code, Codex, Antigravity, or other CLI agents should be used for heavier maintenance only when manually triggered.

# Agent Modes

## Query Mode

Read-only. Use this when the user asks questions such as \"查一下\", \"总结\", \"有没有记录过\", or \"根据我的知识库回答\".

Rules:

- Do not modify files.
- Prefer vault content over web search.
- If using \`review: pending\` material, label it as 未人工审核.
- Cite source file paths.

## Review Mode

Non-destructive planning. Use this when the user asks to review Inbox, Daily Briefings, Weekly Reviews, or Hermes output.

Allowed outputs:

\`\`\`text
00_Inbox/AI_Processed/To_Review/YYYY-MM-DD-ai-review.md
05_Output/Weekly_Reviews/YYYY-Www.md
\`\`\`

Rules:

- Produce candidate concepts, candidate projects, suggested links, questions, and warnings.
- Do not directly edit Protected Paths.
- Do not create legacy files such as \`01_Daily/YYYY-MM-DD.md\` or \`99_Raw/YYYY-MM-DD.md\` unless the user explicitly asks to preserve the old archive format.

## Curate Mode

Approved knowledge-base editing. Use this only after the user clearly approves a concrete plan or explicitly asks to update long-term notes.

Allowed actions after approval:

- Append reviewed sections to existing topic/concept/project notes.
- Create new Source Notes, Concept Notes, Project Notes, or Reports.
- Add links between notes.
- Mark uncertain facts as \`TODO_VERIFY\`.

Rules:

- Do not delete, rename, merge, or rewrite long-term notes unless explicitly authorized.
- Preserve source links or source note references for every material claim.
- Do not mark AI-generated or unverified content as \`verified\`.
- Prefer appending dated sections over rewriting existing notes.
- After edits, show \`git diff\` and a concise change summary. Do not commit unless the user explicitly asks.

Before making changes, run or ask the user to run:

\`\`\`bash
git pull --rebase
git status
\`\`\`

After making changes, run or ask the user to review:

\`\`\`bash
git diff
git status
\`\`\`

Only commit explicitly reviewed files. Do not use \`git add .\` for broad vault changes unless the user explicitly approves.

# Local Agent Entry Prompt

When a CLI agent starts in this vault, it should first read this file. A good first instruction is:

\`\`\`text
Read 99_System/Agents/AGENTS.md first. Do not modify files unless I explicitly approve. Summarize today's Hermes inbox and propose a review plan.
\`\`\`"

write_file_if_missing "$VAULT_PATH/99_System/Claude/CLAUDE.md" "# Claude Code Compatibility Entry

Read and follow the shared agent rules:

\`\`\`text
../Agents/AGENTS.md
\`\`\`

Do not treat this file as a Claude-only policy source. The canonical rules live in \`99_System/Agents/AGENTS.md\` so Codex, Antigravity, Claude Code, and other CLI agents can share the same knowledge-base boundary."

printf 'Vault initialization complete: %s\n' "$VAULT_PATH"
