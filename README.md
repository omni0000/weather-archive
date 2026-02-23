# 🌤️ Daily Weather Archive

Automated weather reporting system powered by **OpenClaw**.

## 🔄 Workflow
This repository serves as a permanent image archive for a daily weather reporting pipeline:
1. **Data Collection**: Fetch real-time weather data for 9 major South Korean cities.
2. **Visualization**: Generate a 3x3 grid weather summary image.
3. **Archiving**: Save the image to this GitHub repository in the `images/` directory.
4. **Logging**: Record the report date and GitHub image URL in a **Notion Database**.
5. **Social Posting**: Automatically post the weather report and image to **X (Twitter)** using a weathercaster persona.

## 📁 Structure
- `images/`: Contains daily weather visualization images named as `weather_YYYYMMDD.png`.

## 🤖 Tech Stack
- **Agent**: OpenClaw (Echo)
- **Automation**: OpenClaw Cron Scheduler
- **Storage**: GitHub
- **Logging**: Notion API
- **Social**: X API (Tweepy)

---
*Generated automatically every day at 07:00 AM KST.*
