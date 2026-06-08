# Daily Review Workflow

Use this flow locally in Obsidian.

## 1. Sync

```bash
git pull
```

Resolve conflicts before reviewing notes.

## 2. Read Daily Inputs

Open:

```text
05_Output/Daily_Briefings/
05_Output/Weekly_Reviews/
00_Inbox/Hermes/News/
00_Inbox/Hermes/Captures/
00_Inbox/AI_Processed/To_Review/
```

Start with the daily briefing, then inspect source material only where needed.

## 3. Decide What Deserves Knowledge Work

For valuable material, manually create or update:

```text
01_Projects/
02_Areas/
03_Resources/
04_LLM_Wiki/
05_Output/Reports/
05_Output/Articles/
06_Graph/
07_Daily/
```

Daily briefings and weekly reviews can be retained as useful historical records. Do not promote AI-generated or Hermes-generated claims into long-term knowledge without verification.

## 4. Link and Annotate

Add links from durable notes back to source notes when useful. Use `TODO_VERIFY` for uncertain facts. Keep tags simple.

## 5. Close the Loop

For reviewed generated files, change:

```yaml
review: pending
```

to:

```yaml
review: done
```

Unimportant generated files can stay in Inbox or be moved manually to `90_Archive/`.

## 6. Commit

```bash
git status
git add <reviewed files>
git commit -m "notes: review daily inbox YYYY-MM-DD"
git push
```

Commit human judgment separately from cloud-generated material when possible.
