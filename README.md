# playo-alerts 🏸

Automated PlayO badminton court alerts using Telegram + GitHub Actions.

The bot continuously checks available badminton court slots near Bellandur and sends clean Telegram alerts before slots get booked.

---

# Features

- 🏸 Bookable badminton courts only (self-hosting)
- 📍 Bellandur-focused search
- ⏰ Configurable time windows (supports midnight crossing)
- 🤖 Telegram alert bot
- 👥 Multi-user subscriptions
- 🧹 Auto-cleans previous alerts (chat stays clean)
- 🔄 Scheduled polling using GitHub Actions
- ⚡ Lightweight vibe-coded architecture

---

# Architecture

```text
Telegram Users
      ↓
bot_listener.py
      ↓
users.json
      ↓
GitHub Actions
      ↓
finder.py
      ↓
PlayO Public API
      ↓
Telegram Alerts
```

---

# Project structure

```text
playo-alerts/
├── src/
│   ├── finder.py
│   ├── bot_listener.py
│   └── storage.py
│
├── data/
│   ├── users.json
│   └── messages.json
│
├── .github/
│   └── workflows/
│       └── badminton.yml
│
├── .env
├── .env.example
├── .gitignore
└── README.md
```

---

# What each file does

| File | Purpose |
|---|---|
| `finder.py` | Fetches PlayO slots and sends alerts |
| `bot_listener.py` | Handles Telegram `/start` and `/stop` |
| `storage.py` | Shared JSON persistence layer |
| `users.json` | Stores subscribed Telegram users |
| `messages.json` | Stores latest sent alert message IDs |
| `badminton.yml` | GitHub Actions scheduler |

---

# Requirements

- Python 3.12+
- uv
- Telegram bot

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

# Telegram bot setup

Create a bot using :contentReference[oaicite:0]{index=0} → `@BotFather`

Commands:

```text
/newbot
```

Copy your generated bot token.

---

# Environment variables

Create `.env`

```env
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
```

---

# Local setup

Clone project:

```bash
git clone <your-repo-url>
cd playo-alerts
```

Run Telegram listener:

```bash
uv run src/bot_listener.py
```

Then open Telegram and send:

```text
/start
```

This registers your chat ID automatically.

---

# Running finder locally

Dry run:

```bash
uv run src/finder.py --verbose
```

With Telegram alerts:

```bash
uv run src/finder.py --telegram
```

Custom time window:

```bash
uv run src/finder.py \
  --start-time 19:00 \
  --end-time 01:00 \
  --telegram
```

---

# Default search configuration

| Setting | Value |
|---|---|
| Sport | Badminton |
| Location | Bellandur |
| Radius | 5 km |
| Time Window | 7 PM → 1 AM |
| Booking Type | Court booking only |

---

# Telegram commands

| Command | Description |
|---|---|
| `/start` | Subscribe to alerts |
| `/stop` | Unsubscribe from alerts |
| `/status` | Show subscriber count |

---

# Alert cleanup behavior

The bot automatically:
- deletes previous alert messages,
- sends fresh alerts,
- keeps the Telegram chat clean.

Users always see only the latest available courts.

---

# GitHub Actions setup

The scheduler runs automatically using GitHub Actions.

Path:

```text
.github/workflows/badminton.yml
```

Example schedule:

```yaml
schedule:
  - cron: "*/15 * * * *"
```

This checks slots every 15 minutes.

---

# GitHub repository secrets

Add in:

```text
Settings → Secrets and variables → Actions
```

Required:

| Secret | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |

---

# Important notes

## Keep repository PRIVATE

`users.json` contains Telegram chat IDs.

Do NOT expose publicly.

---

## Rotate exposed bot tokens

If a token is accidentally shared:

Use `@BotFather`

```text
/revoke
```

Then generate a new token.

---

# Future improvements

Possible future upgrades:

- venue prioritization
- per-user preferences
- duplicate alert prevention
- SQLite persistence
- Railway deployment
- direct PlayO app deep links
- multiple sports support

---

# Disclaimer

This project uses public PlayO APIs intended for client applications.

Use responsibly and avoid aggressive polling.

---

# Credits

Inspired by:

[Karan Sharma's PlayO automation post](https://mrkaran.dev/posts/playo-badminton/?utm_source=chatgpt.com)