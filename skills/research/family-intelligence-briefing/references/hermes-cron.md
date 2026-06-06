# Hermes Cron Notes

Use Hermes cron directly. Do not run a separate scheduler service for this project.

Important behavior:

- Hermes gateway executes cron jobs.
- Cron jobs can attach skills with `--skill`.
- Prompts should be self-contained because cron runs in fresh sessions.
- Use `hermes cron status` and `hermes cron list` for operations.

Daily briefing:

```bash
hermes cron create "0 8 * * *" \
  "Use the family-intelligence-briefing skill to produce today's family global intelligence briefing. Save the full Markdown to the configured vault path and deliver a concise family summary back to the Feishu/Lark home chat." \
  --skill family-intelligence-briefing \
  --deliver feishu \
  --name family-daily-briefing
```

Weekly consolidation:

```bash
hermes cron create "0 20 * * 0" \
  "Use the family-intelligence-briefing skill to consolidate the last 7 daily notes into a weekly family intelligence report and update topic notes in the configured vault path." \
  --skill family-intelligence-briefing \
  --deliver feishu \
  --name family-weekly-knowledge
```

Lifecycle commands:

```bash
hermes cron list
hermes cron status
hermes cron run family-daily-briefing
hermes cron run family-weekly-knowledge
hermes cron pause family-daily-briefing
hermes cron resume family-daily-briefing
hermes cron remove family-daily-briefing
```
