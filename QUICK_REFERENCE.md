# Quick Reference: Project Structure

## Tree View

```
playo-alerts/
│
├── api/                           # Vercel Serverless Functions
│   ├── telegram_webhook.py        # Telegram /start, /stop, /status
│   ├── check_slots.py             # Scheduled cron: find slots + alert
│   └── health.py                  # Health check endpoint
│
├── src/
│   ├── finder.py                  # Core logic (CLI + functions)
│   │   ├── is_in_time_window()    # Time filtering
│   │   ├── find_matching_slots()  # REUSABLE: Main logic
│   │   ├── build_booking_link()   # REUSABLE: Link building
│   │   ├── format_price()         # Price formatting
│   │   └── main CLI               # Click command
│   │
│   ├── playo_client.py            # EXTRACTED: PlayO API
│   │   └── fetch_slots()          # Get activities from PlayO
│   │
│   ├── storage.py                 # REFACTORED: Dual storage
│   │   ├── add_user()             # Subscribe
│   │   ├── remove_user()          # Unsubscribe
│   │   ├── load_users()           # Get all users
│   │   ├── save_message_id()      # Save for cleanup
│   │   └── get_message_id()       # Retrieve for cleanup
│   │
│   ├── bot_listener.py            # Local bot (optional, for dev)
│   └── telegram_client.py         # Telegram helpers (if needed)
│
├── vercel.json                    # Vercel config + cron schedule
├── requirements.txt               # Python dependencies
├── .env.example                   # Env template
├── DEPLOYMENT.md                  # Vercel + Upstash setup guide
├── REFACTORING_SUMMARY.md         # What changed (this file)
└── .github/workflows/
    └── badminton.yml              # GitHub Actions (still works locally)
```

## How Data Flows

### Scenario 1: Cron Job (Every 15 min)
```
Vercel Cron Timer
    ↓
api/check_slots.py
    ↓ (calls)
src/playo_client.py::fetch_slots()
    ↓ (calls)
PlayO API
    ↓ (returns)
src/finder.py::find_matching_slots()
    ↓ (calls)
src/storage.py::load_users() → Upstash Redis
    ↓
For each user: send Telegram alert
    ↓ (saves)
src/storage.py::save_message_id() → Upstash Redis
```

### Scenario 2: User Command (/start)
```
Telegram User
    ↓
api/telegram_webhook.py
    ↓ (calls)
src/storage.py::add_user() → Upstash Redis
    ↓
Send confirmation message
```

### Scenario 3: Local CLI (For testing)
```
$ python src/finder.py --telegram

src/finder.py::find_games()
    ↓
src/playo_client.py::fetch_slots()
    ↓
src/finder.py::find_matching_slots()
    ↓
src/storage.py (auto-detects: JSON if local)
    ↓
Send alerts
```

## Storage Backend Auto-Detection

```python
# In src/storage.py

if os.getenv("UPSTASH_REDIS_REST_URL"):
    # Running on Vercel → Use Redis
    USE_REDIS = True
else:
    # Running locally → Use JSON
    USE_REDIS = False
```

## Environment Variables

### Local Development
```bash
# Just need this
TELEGRAM_BOT_TOKEN=your_token

# Redis vars empty/unset → Uses JSON
```

### Vercel Deployment
```bash
TELEGRAM_BOT_TOKEN=your_token
UPSTASH_REDIS_REST_URL=https://...
UPSTASH_REDIS_REST_TOKEN=...
```

## Function Dependencies

```
api/check_slots.py
├── imports: src.finder
├── imports: src.playo_client
├── imports: src.storage
└── uses: Telegram Bot

api/telegram_webhook.py
├── imports: src.storage
└── uses: Telegram Bot

src/finder.py
├── imports: src.playo_client
├── imports: src.storage
└── imports: Telegram Bot, Click, Rich

src/playo_client.py
└── imports: requests (only PlayO API)

src/storage.py
├── imports: JSON (local) OR Upstash Redis (Vercel)
└── no external dependencies for core
```

## Testing Locally

```bash
# 1. Install deps
pip install -r requirements.txt

# 2. Create .env
cp .env.example .env
# Edit .env with your TELEGRAM_BOT_TOKEN

# 3. Test finder (uses JSON storage)
python src/finder.py

# 4. Test with Telegram alerts
python src/finder.py --telegram

# 5. Test bot listener
python src/bot_listener.py
```

## Testing on Vercel

```bash
# 1. Deploy to Vercel
git push origin main

# 2. Check health
curl https://your-project.vercel.app/api/health

# 3. Manually trigger cron
curl https://your-project.vercel.app/api/check-slots

# 4. Test Telegram webhook
# Send /start to your bot in Telegram

# 5. View logs
# Vercel Dashboard → Deployments → Functions
```

## File Change Summary

| File | Status | Changes |
|------|--------|---------|
| `src/finder.py` | 🔄 Refactored | Extracted `find_matching_slots()`, imports changed, cleaned up `send_slots_to_telegram` |
| `src/storage.py` | 🔄 Refactored | Added Redis support, dual-mode storage |
| `src/playo_client.py` | ✨ NEW | Extracted PlayO API logic |
| `api/telegram_webhook.py` | ✨ NEW | Webhook handler |
| `api/check_slots.py` | ✨ NEW | Cron job handler |
| `api/health.py` | ✨ NEW | Health check |
| `vercel.json` | ✨ NEW | Vercel configuration |
| `requirements.txt` | ✨ NEW | Dependencies with upstash-redis |
| `.env.example` | 🔄 Updated | Added UPSTASH_REDIS_* vars |
| `DEPLOYMENT.md` | ✨ NEW | Full deployment guide |

## Deployment Checklist

- [ ] Create Upstash Redis instance
- [ ] Add env vars to Vercel
- [ ] Deploy to Vercel (`git push`)
- [ ] Set Telegram webhook URL
- [ ] Test `/start` command
- [ ] Wait 15 min for cron
- [ ] Verify slot alert received
- [ ] Check Vercel logs

---

**Total Files Created**: 6
**Total Files Refactored**: 2
**Breaking Changes**: 0 (backwards compatible!)
**Local Development Impact**: None (still works!)
