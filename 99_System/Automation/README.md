# Obsidian Personal Knowledge Automation

## Architecture

Hermes runs on the cloud server and delivers material into the Obsidian vault. GitHub is the single synchronization source. Local Obsidian is where reading, judgment, linking, long-term note creation, and final output happen.

```text
Cloud Hermes -> Inbox / Daily Briefings / Weekly Reviews / AI To Review / logs
GitHub       -> version history and sync
Obsidian     -> human review, links, durable knowledge, outputs
```

## Cloud Write Boundary

Cloud automation may write only:

```text
00_Inbox/Hermes/
00_Inbox/AI_Processed/To_Review/
05_Output/Daily_Briefings/
05_Output/Weekly_Reviews/
99_System/Automation/logs/
```

Daily briefings and weekly reviews are worth keeping as time-series records. They remain review-pending records until reviewed; they are not automatically promoted into durable concepts, graph relations, reports, or verified knowledge.

Cloud automation must not modify:

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

## Local Review Flow

1. Run `git pull` before opening the review session.
2. Read `05_Output/Daily_Briefings/YYYY-MM-DD-briefing.md`.
3. Review source material in `00_Inbox/Hermes/News/` and `00_Inbox/Hermes/Captures/`.
4. Create or update long-term notes manually.
5. Mark reviewed generated files with `review: done`.
6. Commit and push local changes.

## GitHub Sync

Cloud sync uses `scripts/hermes_git_sync.sh`. It runs:

```text
git fetch
git pull --rebase
generate files
git add allowed paths only
git commit
git push
```

It never runs `git add .`, `git reset --hard`, force push, or automatic deletes.

## Conflict Handling

If `git pull --rebase` fails, stop the automation. Resolve the conflict manually on the server or locally, then rerun the sync script. Do not force-push the vault.

If the script reports changes outside the allowed paths, inspect them manually. This usually means a human edit or a previous automation wrote into long-term knowledge areas.

## LLM and CLI Agents

Standalone Obsidian LLM processing is not required for the MVP. Hermes handles light tasks such as summarizing, candidate links, candidate concepts, and review-pending drafts.

Heavy transformations should be triggered manually through Claude Code, Codex, Antigravity, or another CLI agent so a human can inspect the diff before committing.

For the MVP:

```bash
scripts/ai_process_inbox.py --vault /home/ubuntu/family-intelligence-vault
```

This creates a mock review note with `review: pending` and `confidence: low`.

## Adding Hermes Sources

Add new sources by changing Hermes prompts or skills so they still output to the allowed directories. New sources should preserve YAML frontmatter and use `review: pending`.

Recommended source note fields:

```yaml
type: source
source: hermes
status: inbox
review: pending
created_by: hermes
created: YYYY-MM-DD
```

## Restore History

Use Git history to inspect or restore previous versions:

```bash
git log -- path/to/note.md
git show <commit>:path/to/note.md
git restore --source <commit> -- path/to/note.md
```

Avoid restoring broad directories unless you have checked what will change.

## Cron Example

```cron
0 7 * * * /home/ubuntu/family-intelligence-vault/scripts/hermes_git_sync.sh --vault /home/ubuntu/family-intelligence-vault >> /home/ubuntu/family-intelligence-vault/99_System/Automation/logs/cron.log 2>&1
0 23 * * * /home/ubuntu/family-intelligence-vault/scripts/hermes_git_sync.sh --vault /home/ubuntu/family-intelligence-vault >> /home/ubuntu/family-intelligence-vault/99_System/Automation/logs/cron.log 2>&1
```

Hermes cron can also run prompts directly. Keep Hermes prompts aligned with the same write boundary.
