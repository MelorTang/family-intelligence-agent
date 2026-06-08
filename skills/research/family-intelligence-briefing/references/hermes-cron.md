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
  "Use the family-intelligence-briefing skill to produce today's family global intelligence briefing. Save the full Markdown to the configured vault path. Deliver the final Feishu/Lark summary using the exact template defined in the skill, without raw Markdown, tool logs, or CronJob Response text." \
  --skill family-intelligence-briefing \
  --deliver feishu \
  --name family-daily-briefing
```

Weekly review:

```bash
hermes cron create "0 20 * * 0" \
  "Use the family-intelligence-briefing skill to consolidate the last 7 daily notes into a review-pending weekly review. Save it to 05_Output/Weekly_Reviews. Do not update long-term topic, asset, graph, project, report, or article notes." \
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
