# Hermes Cron Notes

Use Hermes cron as the scheduler when Hermes is already deployed.

Important behavior:

- Hermes gateway executes cron jobs.
- The gateway checks due jobs periodically.
- Use `--workdir` so commands run in the project directory.
- Cron job prompts should be self-contained.
- Prefer script-only or no-agent cron for deterministic commands when available.

Recommended command:

```bash
hermes cron create "every 1d at 08:00" \
  "Run the family intelligence briefing workflow with: .venv/bin/python main.py run-daily. If it fails, inspect data/logs/app.log and summarize the error." \
  --workdir /absolute/path/to/family-intelligence-agent \
  --name family-daily-briefing
```

Recommended weekly knowledge-base job:

```bash
hermes cron create "every sunday at 20:00" \
  "Run the family intelligence weekly knowledge workflow with: .venv/bin/python main.py run-weekly. If it fails, inspect data/logs/app.log and summarize the error." \
  --workdir /absolute/path/to/family-intelligence-agent \
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
