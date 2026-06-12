#!/usr/bin/env bash
set -Eeuo pipefail

DRY_RUN=false
RUN_GENERATORS=false
RUN_CRON_IMPORT=true
RUN_AI=false
VAULT_PATH="${VAULT_PATH:-}"
REMOTE="${GIT_REMOTE:-origin}"
BRANCH="${GIT_BRANCH:-main}"
TODAY="${HERMES_DATE:-$(date +%F)}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ALLOWED_PATHS=(
  "00_Inbox/Hermes/"
  "00_Inbox/Ideas/"
  "00_Inbox/Questions/"
  "00_Inbox/Reading/"
  "00_Inbox/AI_Processed/To_Review/"
  "05_Output/Daily_Briefings/"
  "05_Output/Weekly_Reviews/"
  "99_System/Automation/logs/"
)

CONTENT_PATHS=(
  "00_Inbox/Hermes/"
  "00_Inbox/Ideas/"
  "00_Inbox/Questions/"
  "00_Inbox/Reading/"
  "00_Inbox/AI_Processed/To_Review/"
  "05_Output/Daily_Briefings/"
  "05_Output/Weekly_Reviews/"
)

usage() {
  cat <<'EOF'
Usage: hermes_git_sync.sh --vault /path/to/obsidian-vault [--dry-run] [--no-cron-import] [--generate-placeholders] [--ai]

Safely syncs Hermes-generated Obsidian files through GitHub.
By default this script imports today's Hermes cron response if the skill did not write files.
It does not create placeholder daily files unless --generate-placeholders is passed.
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
    --generate-placeholders)
      RUN_GENERATORS=true
      shift
      ;;
    --no-cron-import)
      RUN_CRON_IMPORT=false
      shift
      ;;
    --no-generate)
      RUN_GENERATORS=false
      shift
      ;;
    --ai)
      RUN_AI=true
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

VAULT_PATH="$(cd "$VAULT_PATH" && pwd)"
LOG_DIR="$VAULT_PATH/99_System/Automation/logs"
LOG_FILE="$LOG_DIR/hermes_${TODAY}.log"
LOG_TO_FILE=false

mkdir -p "$LOG_DIR"

log() {
  local step="$1"
  local status="$2"
  local message="$3"
  local line
  line="$(printf '%s\tstep=%s\tstatus=%s\tmessage=%s' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$step" "$status" "$message")"
  if [[ "$LOG_TO_FILE" == "true" ]]; then
    printf '%s\n' "$line" | tee -a "$LOG_FILE"
  else
    printf '%s\n' "$line"
  fi
}

die() {
  log "$1" "error" "$2"
  exit 1
}

run() {
  log "$1" "start" "$2"
  if [[ "$DRY_RUN" == "true" ]]; then
    log "$1" "dry-run" "$2"
  else
    shift 2
    "$@"
  fi
}

is_allowed_path() {
  local path="$1"
  for allowed in "${ALLOWED_PATHS[@]}"; do
    [[ "$path" == "$allowed"* ]] && return 0
  done
  return 1
}

check_dirty_scope() {
  local line path bad=0
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    path="${line:3}"
    if [[ "$path" == *" -> "* ]]; then
      path="${path##* -> }"
    fi
    if ! is_allowed_path "$path"; then
      log "dirty-scope" "blocked" "Uncommitted change outside allowed paths: $path"
      bad=1
    fi
  done < <(git status --porcelain -uall)
  [[ "$bad" -eq 0 ]] || return 1
}

cd "$VAULT_PATH"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "preflight" "$VAULT_PATH is not a git repository"
check_dirty_scope || die "preflight" "Refusing to continue with changes outside Hermes write boundary"

STASH_CREATED=false
if [[ "$DRY_RUN" != "true" ]] && [[ -n "$(git status --porcelain -uall)" ]]; then
  before_stash="$(git rev-parse -q --verify refs/stash || true)"
  git stash push -u -m "hermes pre-pull allowed changes $TODAY" -- "${ALLOWED_PATHS[@]}" >/dev/null
  after_stash="$(git rev-parse -q --verify refs/stash || true)"
  if [[ "$before_stash" != "$after_stash" ]]; then
    STASH_CREATED=true
    log "git-stash" "ok" "Stashed allowed pre-pull changes"
  fi
fi

run "git-fetch" "git fetch $REMOTE" git fetch "$REMOTE"
run "git-pull" "git pull --rebase $REMOTE $BRANCH" git pull --rebase "$REMOTE" "$BRANCH"

if [[ "$STASH_CREATED" == "true" ]]; then
  git stash pop --index >/dev/null || die "git-stash-pop" "Failed to restore allowed pre-pull changes"
fi

LOG_TO_FILE=true
log "git-pull" "ok" "Repository is up to date with $REMOTE/$BRANCH"
if [[ "$STASH_CREATED" == "true" ]]; then
  log "git-stash-pop" "ok" "Restored allowed pre-pull changes"
fi

if [[ "$DRY_RUN" != "true" ]]; then
  check_dirty_scope || die "post-pull" "Pull produced changes outside Hermes write boundary"
fi

if [[ "$RUN_CRON_IMPORT" == "true" ]]; then
  import_args=(--vault "$VAULT_PATH" --date "$TODAY")
  [[ "$DRY_RUN" == "true" ]] && import_args+=(--dry-run)
  python3 "$SCRIPT_DIR/import_hermes_cron_output.py" "${import_args[@]}" | tee -a "$LOG_FILE"
fi

if [[ "$RUN_GENERATORS" == "true" ]]; then
  generator_args=(--vault "$VAULT_PATH" --date "$TODAY")
  [[ "$DRY_RUN" == "true" ]] && generator_args+=(--dry-run)
  python3 "$SCRIPT_DIR/generate_daily_files.py" "${generator_args[@]}" | tee -a "$LOG_FILE"
fi

if [[ "$RUN_AI" == "true" ]]; then
  ai_args=(--vault "$VAULT_PATH" --date "$TODAY")
  [[ "$DRY_RUN" == "true" ]] && ai_args+=(--dry-run)
  python3 "$SCRIPT_DIR/ai_process_inbox.py" "${ai_args[@]}" | tee -a "$LOG_FILE"
fi

check_dirty_scope || die "pre-add" "Generated changes outside Hermes write boundary"

for allowed in "${CONTENT_PATHS[@]}"; do
  if [[ -e "$allowed" ]]; then
    run "git-add" "git add $allowed" git add "$allowed"
  else
    log "git-add" "skip" "$allowed does not exist"
  fi
done

if git diff --cached --quiet; then
  log "git-commit" "ok" "No allowed changes to commit"
  exit 0
fi

if [[ -e "99_System/Automation/logs/" ]]; then
  run "git-add" "git add 99_System/Automation/logs/" git add "99_System/Automation/logs/"
fi

commit_message="chore(hermes): add daily inbox updates $TODAY"
run "git-commit" "$commit_message" git commit -m "$commit_message"

if [[ "$DRY_RUN" == "true" ]]; then
  log "git-push" "dry-run" "git push $REMOTE $BRANCH"
  exit 0
fi

git push "$REMOTE" "$BRANCH"
commit_hash="$(git rev-parse --short HEAD)"
log "git-push" "ok" "Pushed commit $commit_hash"
