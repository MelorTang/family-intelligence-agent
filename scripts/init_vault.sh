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

printf 'Vault initialization complete: %s\n' "$VAULT_PATH"
