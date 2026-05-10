# Deployment Guide: Playo Alerts to Vercel + Upstash

This guide walks through deploying the refactored Playo alerts bot to Vercel with Redis persistence.

## Architecture Changes

### Before (GitHub Actions + JSON)
- **Bot**: Polling bot listener running 24/7 on GitHub Actions (limited)
- **Scheduler**: GitHub Actions cron (limited to scheduled runs)
- **Storage**: JSON files (users.json, messages.json)

### After (Vercel + Upstash)
- **Bot**: Telegram webhooks (event-driven, scalable)
- **Scheduler**: Vercel cron jobs (every 15 minutes)
- **Storage**: Upstash Redis (production-grade)

## Prerequisites

1. **GitHub Account** (already have)
2. **Telegram Bot** (already created)
3. **Vercel Account** (https://vercel.com, free tier OK)
4. **Upstash Account** (https://upstash.com, free tier provides 10K commands/day)

## Step 1: Set Up Upstash Redis

### 1.1 Create Upstash Account

1. Go to https://upstash.com
2. Sign up (free)
3. Verify email

### 1.2 Create Redis Database

1. Dashboard → **Create database**
2. Name: `playo-alerts`
3. Region: Pick closest to your users (e.g., `us-east-1` or `eu-west-1`)
4. Type: **Global** (Redis)
5. Click **Create**

### 1.3 Get Credentials

Once database is created:

1. Click on your database
2. Copy these (you'll need them):
   - **REST URL** → `UPSTASH_REDIS_REST_URL`
   - **REST Token** → `UPSTASH_REDIS_REST_TOKEN`

Keep these tabs open!

## Step 2: Set Up Vercel Deployment

### 2.1 Connect GitHub to Vercel

1. Go to https://vercel.com
2. Sign up with GitHub (or sign in)
3. **Import Project** → Select your `playo-alerts` repo
4. Click **Import**

### 2.2 Add Environment Variables

On the Vercel import screen, before clicking **Deploy**:

1. Click **Environment Variables**
2. Add these variables:

```
TELEGRAM_BOT_TOKEN = <your_bot_token>
UPSTASH_REDIS_REST_URL = <paste from Upstash>
UPSTASH_REDIS_REST_TOKEN = <paste from Upstash>
```

3. Click **Deploy**

Wait 2-3 minutes for deployment...

### 2.3 Get Your Vercel URLs

Once deployed, you'll see:
- **Production URL**: `https://your-project.vercel.app`

Your endpoints:
- `https://your-project.vercel.app/api/health` → Health check
- `https://your-project.vercel.app/api/telegram` → Telegram webhook
- `https://your-project.vercel.app/api/check-slots` → Cron job (called every 15 min)

## Step 3: Configure Telegram Webhook

### 3.1 Set Telegram Webhook

Run this command (replace with your actual Vercel URL and bot token):

```bash
curl -X POST \
  https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/setWebhook \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://your-project.vercel.app/api/telegram"
  }'
```

**Expected response:**
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

### 3.2 Verify Webhook

```bash
curl \
  https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/getWebhookInfo
```

Should show:
- `"url": "https://your-project.vercel.app/api/telegram"`
- `"has_custom_certificate": false`
- `"pending_update_count": 0`

## Step 4: Test the Deployment

### 4.1 Test Health Endpoint

```bash
curl https://your-project.vercel.app/api/health
```

Response: `{"status": "ok"}`

### 4.2 Test Telegram Commands

In your Telegram bot chat:
- Send `/start` → Should respond "🏸 Subscribed..."
- Send `/status` → Shows subscriber count
- Send `/stop` → Unsubscribes you

### 4.3 Manually Trigger Cron

```bash
curl https://your-project.vercel.app/api/check-slots
```

Response:
```json
{
  "success": true,
  "users_notified": 1,
  "slots_found": 5
}
```

## Step 5: Verify Auto Cron

The cron is configured in `vercel.json`:
```json
"crons": [
  {
    "path": "/api/check-slots",
    "schedule": "*/15 * * * *"
  }
]
```

This runs `/api/check-slots` **every 15 minutes** automatically.

Check Vercel dashboard → **Functions** → **Cron Jobs** to see execution history.

## File Structure

```
playo-alerts/
├── api/                       # Serverless functions
│   ├── telegram_webhook.py    # Handles /start, /stop, /status
│   ├── check_slots.py         # Runs every 15 min via cron
│   └── health.py              # Health check
├── src/
│   ├── finder.py              # Core logic (kept mostly same)
│   ├── playo_client.py        # PlayO API calls
│   ├── storage.py             # Dual storage (JSON + Redis)
│   └── bot_listener.py        # Extra for local polling (optional)
├── vercel.json                # Vercel config + cron schedule
├── requirements.txt           # Python dependencies
└── .env.example               # Environment template
```

##Local Development (Still Works!)

### 4.1 Run Locally with JSON Storage

If you don't set `UPSTASH_REDIS_REST_URL`, the code falls back to JSON storage.

```bash
# Install deps (if not using uv)
pip install -r requirements.txt

# Run CLI locally
python src/finder.py --telegram

# Or run bot listener locally
python src/bot_listener.py
```

### 4.2 Local Testing with Redis

To test Upstash Redis locally:

```bash
# Set env vars
export UPSTASH_REDIS_REST_URL="https://..."
export UPSTASH_REDIS_REST_TOKEN="..."
export TELEGRAM_BOT_TOKEN="..."

# Run
python src/finder.py --telegram
```

## Monitoring & Debugging

### View Logs

1. Go to Vercel Dashboard
2. Select your project
3. Click **Deployments** → Latest deployment
4. Click **Functions** → Select function
5. View real-time logs

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Vercel didn't install dependencies → Rebuild project |
| Redis connection fails | Check `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`are set in Vercel |
| Webhook never called | Verify via `getWebhookInfo` that URL is correct |
| No slots alerts | Check Vercel function logs in Dashboard |

## Cost Breakdown (Free Tier)

- **Vercel**: Free (unlimited functions, 100GB bandwidth/month)
- **Upstash Redis**: Free (10K commands/day ≈ 7-8 alerts/day with margin)
- **Total**: **$0/month**

If you exceed Redis limits, you can upgrade Upstash to **$1-5/month**.

## Going Back to Local

If you want to revert to GitHub Actions:

```bash
# Push changes
git push origin main

# Vercel auto-deploys, but you can also:
# - Keep .github/workflows/badminton.yml
# - Run GitHub Actions as backup
```

The code supports **both** JSON (local) and Redis (Vercel) simultaneously!

## Next Steps

1. ✅ Complete all steps above
2. ✅ Test Telegram webhook with `/start`
3. ✅ Wait 15 minutes, verify cron runs
4. ✅ Check Vercel logs for any errors
5. Share your Telegram bot link with friends!

---

**Any questions?** Check Vercel docs: https://vercel.com/docs
