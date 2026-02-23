---
name: notion-weather
description: Automate weather report generation, GitHub image archiving, and Notion database logging. Use when the user wants to archive weather images to GitHub and track them in a Notion database with dates, weekdays, and summaries.
---

# Notion Weather Automation (GitHub Archive Edition)

This skill automates the full pipeline of weather reporting:
1. Generating a visualization image.
2. Archiving the image to a GitHub repository (`weather-archive`).
3. Creating a structured entry in a Notion database.

## Prerequisites

- **Notion API Key**: Stored in `~/.config/notion/api_key`.
- **GitHub CLI (gh)**: Authenticated and ready.
- **Local Repo**: `~/.openclaw/workspace/weather-archive` must be a cloned git repo.

## Workflow

### 1. Generate Weather Image
Standard format: 3x3 grid of major Korean cities.
Save location: `~/.openclaw/workspace/one_shot_3x3_weather.png`.

### 2. Archive and Log
The script handles GitHub upload, Notion logging, and X (Twitter) posting.

```bash
python3 scripts/upload_report.py \
  --database-id <DATABASE_ID> \
  --image-path <LOCAL_PATH> \
  --summary "<TEXT_SUMMARY>" \
  --post-x
```

- **GitHub**: Pushes the image to `main` branch.
- **Notion**: Adds a row to the History database.
- **X (Twitter)**: Posts a tweet with the image and summary.

## Target IDs
- **History Database**: `310aa2e8eb08814e81e8faa7d8664104`
