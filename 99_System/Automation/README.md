# Obsidian Personal Knowledge Automation

## Architecture

Hermes runs on the cloud server and delivers material into the Obsidian vault. GitHub is the single synchronization source. Local Obsidian is where reading, judgment, linking, long-term note creation, and final output happen.

```text
Cloud Hermes -> Inbox / Daily Briefings / Weekly Reviews / AI To Review / logs
GitHub       -> version history and sync
Obsidian     -> human review, links, durable knowledge, outputs
```

The local knowledge flow is:

```text
Capture -> Source -> Concept -> Insight -> Output
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

## Local Review Flow

1. Run `git pull` before opening the review session.
2. Read `05_Output/Daily_Briefings/YYYY-MM-DD-briefing.md`.
3. Review source material in `00_Inbox/Hermes/News/` and `00_Inbox/Hermes/Captures/`.
4. Create or update Source, Concept, Insight, or Output notes manually or through an approved local CLI agent Curate Mode.
5. Mark reviewed generated files with `review: done`.
6. Commit and push local changes.

## GitHub Sync

Cloud sync uses `scripts/hermes_git_sync.sh`. It runs:

```text
git fetch
git pull --rebase
import Hermes cron response if Hermes did not write vault files
git add allowed paths only
git commit
git push
```

It does not create placeholder daily files by default. If Hermes only produced a Feishu response, the sync script recovers that response from `~/.hermes/cron/output` into review-pending Markdown files. It never runs `git add .`, `git reset --hard`, force push, or automatic deletes.

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
10 8 * * * /home/ubuntu/family-intelligence-agent/scripts/hermes_git_sync.sh --vault /home/ubuntu/family-intelligence-vault >> /home/ubuntu/hermes_git_sync_cron.log 2>&1
```

Do not redirect cron output to a tracked file inside the vault. The shell redirection itself makes the working tree dirty before `git pull --rebase` runs.

Hermes cron can also run prompts directly. Keep Hermes prompts aligned with the same write boundary.
