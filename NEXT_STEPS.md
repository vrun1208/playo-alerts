# 🚀 Next Steps: Deploy to Vercel + Upstash

## TL;DR

Your Playo alerts bot is ready for production! Here's what to do next:

## Step 1: Commit & Push

```bash
git add -A
git commit -m "Refactor: Vercel + Upstash migration

- Add serverless API handlers (telegram webhook, cron)
- Extract PlayO client to separate module
- Refactor storage to support Redis + JSON
- Add Vercel configuration with cron
- Update requirements.txt with upstash-redis"

git push origin main
```

## Step 2: Create Upstash Database (5 min)

1. Go to https://upstash.com → Sign up
2. **Redis** → **Create Database**
3. Name: `playo-alerts`
4. Region: Choose closest to you
5. Click **Create**
6. Once created, click on it
7. Copy and save:
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN`

Keep this page open!

## Step 3: Deploy to Vercel (3 min)

1. Go to https://vercel.com → Sign in with GitHub
2. **Import Project** → Select `playo-alerts` repository
3. Click **Import**

On the configuration screen:

4. Click **Environment Variables**
5. Add three variables:
   ```
   TELEGRAM_BOT_TOKEN = <your bot token>
   UPSTASH_REDIS_REST_URL = <paste from Upstash>
   UPSTASH_REDIS_REST_TOKEN = <paste from Upstash>
   ```
6. Click **Deploy**

Wait 2-3 minutes...

Once deployed, you'll see your **Production URL**:
```
https://your-project-name.vercel.app
```

## Step 4: Set Telegram Webhook (1 min)

Replace `YOUR_TELEGRAM_BOT_TOKEN` and `YOUR_VERCEL_URL` in this command:

```bash
curl -X POST \
  https://api.telegram.org/botYOUR_TELEGRAM_BOT_TOKEN/setWebhook \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://YOUR_VERCEL_URL/api/telegram"}'
```

**Expected response:**
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

## Step 5: Test Everything (2 min)

### Test 1: Health Check
```bash
curl https://YOUR_VERCEL_URL/api/health
```
Response: `{"status": "ok"}`

### Test 2: Telegram Command
Open Telegram, send to your bot:
```
/start
```
You should get: "🏸 Subscribed to badminton court alerts!"

### Test 3: Manual Cron Trigger
```bash
curl https://YOUR_VERCEL_URL/api/check-slots
```
Response:
```json
{
  "success": true,
  "users_notified": 1,
  "slots_found": 3
}
```

### Test 4: Wait for Auto Cron
- Cron runs automatically every 15 minutes
- Check Vercel Dashboard → **Functions** → **Cron Jobs** for execution history
- You should receive a Telegram alert with available courts

## Step 6: Monitor (Optional)

### View Vercel Logs
1. Go to Vercel Dashboard
2. Select your project
3. Click **Deployments** → Latest
4. Scroll to **Functions**
5. Click on any function to see real-time logs

### Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Wait 2-3 min, then redeploy in Vercel |
| Webhook not working | Check setWebhook response, verify URL is correct |
| No alerts | Check Vercel logs, verify Redis keys exist in Upstash |
| Redis connection error | Verify env vars are set correctly in Vercel |

## Step 7: Share Your Bot! 🎉

Your bot is now live 24/7!

- **Cron alerts**: Every 15 minutes
- **Webhook commands**: `/start`, `/stop`, `/status`
- **Cost**: $0/month (free tier)
- **Downtime**: None (Vercel SLA)

Share with friends:
```
My badminton bot is live! Send /start to @your_bot_username
```

## Optional: Local Development

To test locally before deploying:

```bash
# Install deps
pip install -r requirements.txt

# Create .env
cp .env.example .env
# Edit: Add TELEGRAM_BOT_TOKEN only

# Run CLI (uses JSON storage locally)
python src/finder.py --telegram

# Or run bot listener locally
python src/bot_listener.py
```

Local mode doesn't need Redis! It uses JSON files automatically.

## Rollback (If Needed)

Your old GitHub Actions workflow still exists:

```bash
# To run game checker via GitHub Actions manually:
# Go to Actions → Badminton Alerts System → Run workflow
```

Both Vercel + GitHub Actions can coexist.

## Files You Need to Know About

- **DEPLOYMENT.md** - Detailed setup guide
- **REFACTORING_SUMMARY.md** - What changed & why
- **QUICK_REFERENCE.md** - Project structure & data flow
- **vercel.json** - Cron configuration (every 15 min)
- **requirements.txt** - Python dependencies

## Questions?

1. Check **DEPLOYMENT.md** for detailed explanations
2. Check Vercel logs (Dashboard → Functions)
3. Check Upstash dashboard for Redis status
4. Check Telegram bot's message history

---

**That's it!** Your bot is now:
✅ Event-driven (Telegram webhooks, not polling)
✅ Scheduled (Vercel cron every 15 min)
✅ Persistent (Upstash Redis)
✅ Free tier ($0/month)
✅ Production-ready (Vercel infrastructure)

Happy badminton hunting! 🏸
