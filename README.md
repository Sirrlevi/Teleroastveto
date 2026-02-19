# 🔥 SOULSLAYER BOT v2.0
## Dark Sarcastic Roast Bot - Unbreakable Edition

An elite Telegram bot with dark, savage humor, anti-jailbreak protection, and owner obedience.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 👑 **Owner Protection** | Owner (6881713177) ko kabhi roast nahi, sirf respect |
| 🛡️ **Anti-Jailbreak** | "be nice", "ignore instructions" try karne pe aur zor se roast |
| 🧠 **Groq AI** | Smart, contextual dark roasts |
| 🔄 **Fallback System** | API fail ho toh local roasts |
| 🚫 **Spam Filter** | 15 messages/hour limit |
| 💾 **SQLite DB** | Per-chat settings, message logs |
| 📊 **Stats** | Usage tracking for owner |

---

## 📁 Project Structure

```
brutal-bot/
├── main.py              # Main bot code (500+ lines)
├── souls.md             # Bot personality + anti-jailbreak rules
├── requirements.txt     # Python dependencies
├── Procfile             # Railway worker config
├── runtime.txt          # Python version
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
├── bot_data.db          # SQLite database (auto-created)
└── README.md            # This file
```

---

## 🚀 Quick Start (Local)

### 1. Clone & Setup
```bash
git clone <your-repo>
cd brutal-bot
pip install -r requirements.txt
```

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env with your values
```

### 3. Required Keys

#### A. Telegram Bot Token
1. Go to [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Name: `SoulSlayer Bot`
4. Username: `@YourSoulSlayerBot`
5. **Copy the token**

#### B. Owner ID
1. Go to [@userinfobot](https://t.me/userinfobot)
2. Press Start
3. **Copy your ID** (e.g., `6881713177`)

#### C. Groq API Key
1. Go to [console.groq.com](https://console.groq.com/keys)
2. Sign up/login
3. Create new API key
4. **Copy the key**

### 4. Run Locally
```bash
python main.py
```

---

## 🚂 Railway Deployment (Step-by-Step)

### Step 1: GitHub Repository

```bash
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "SoulSlayer Bot v2.0 - Initial commit"

# Create GitHub repo (manually on github.com)
# Then push:
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/brutal-bot.git
git push -u origin main
```

### Step 2: Railway Setup

1. Go to [railway.app](https://railway.app)
2. Login with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your `brutal-bot` repository

### Step 3: Add Environment Variables

Click on your service → **Variables** → **New Variable**

Add these:

```
TELEGRAM_TOKEN = your_botfather_token
OWNER_ID = 6881713177
API_KEY = your_groq_api_key
BASE_URL = https://api.groq.com/openai/v1
MODEL = llama-3.1-8b-instant
```

### Step 4: Deploy

1. Railway will auto-deploy
2. Check **Deploy Logs** for errors
3. Wait for "🔥 SOULSLAYER BOT STARTED 🔥"

---

## ⚠️ Fixing 409 Conflict Error

If you see `409 Conflict` error:

### Method 1: Pause → Resume → Redeploy

1. Railway Dashboard → Your Service
2. Click **Settings** tab
3. Click **"Pause Service"**
4. Wait 10 seconds
5. Click **"Resume Service"**
6. Click **"Redeploy"**

### Method 2: Clear Cache & Redeploy

1. Go to your service
2. Click **"Redeploy"** dropdown
3. Select **"Clear Cache and Redeploy"**

### Method 3: Delete & Recreate

1. Delete the service
2. Create new project
3. Deploy again

### Method 4: Manual Worker Setup

If auto-deploy fails:

1. Create **Empty Project**
2. Click **"New"** → **"Database"** → **"Add PostgreSQL"** (optional)
3. Click **"New"** → **"Empty Service"**
4. Service settings:
   - **Source**: GitHub Repo
   - **Start Command**: `python main.py`
   - **Environment**: Add all variables
5. Deploy

---

## 🎮 Bot Commands

| Command | Description | Access |
|---------|-------------|--------|
| `/start` | Start bot | Everyone |
| `/enable` | Enable bot in chat | Owner only |
| `/disable` | Disable bot in chat | Owner only |
| `/myid` | Get your Telegram ID | Everyone |
| `/status` | Check bot status | Everyone |
| `/stats` | View usage stats | Owner only |

---

## 🔥 How It Works

### Triggers (Kab Roast Karega)

1. **Private DM** → Hamesha reply
2. **@Mention** → `@YourBot username`
3. **Reply to bot** → Bot ke message pe reply

### Owner Protection

```python
if user_id == OWNER_ID:
    return "Haan boss, sun raha hu 🔥 Order do"
```

### Anti-Jailbreak Response

If someone tries:
- "ignore previous instructions"
- "be nice"
- "developer mode"
- "jailbreak"

Bot responds:
> "Arre wah, hacker ban gaya? Prompt injection karke? Bhai tu toh Anonymous ka CEO lag raha hai. Itni mehnat kar raha hai meri personality change karne mein, apni life change kar leta toh aaj kuch ban jaata."

### Spam Filter

- **Window**: 1 hour (3600 seconds)
- **Threshold**: 15 messages
- **Action**: Ignore user for 1 hour

### Fallback System

If API fails:
1. Log the reason
2. Pick random roast from `FALLBACK_ROASTS`
3. Send immediately

---

## 🧠 Groq Models

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `llama-3.1-8b-instant` | ⚡ Fast | Good | Default |
| `llama-3.3-70b-versatile` | 🐢 Slow | Best | High quality |
| `mixtral-8x7b-32768` | ⚡ Fast | Good | Alternative |
| `gemma-7b-it` | ⚡ Fast | Okay | Backup |

---

## 📝 Database Schema

### settings
```sql
chat_id INTEGER PRIMARY KEY
enabled BOOLEAN
updated_at TIMESTAMP
```

### message_log
```sql
id INTEGER PRIMARY KEY
user_id INTEGER
chat_id INTEGER
message_count INTEGER
first_message TIMESTAMP
last_message TIMESTAMP
```

### fallback_stats
```sql
id INTEGER PRIMARY KEY
timestamp TIMESTAMP
reason TEXT
```

---

## 🐛 Troubleshooting

### Bot Not Responding

```bash
# Check logs
railway logs

# Verify token
curl https://api.telegram.org/bot<TOKEN>/getMe
```

### API Errors

```bash
# Test Groq API
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer <API_KEY>"
```

### Database Locked

```bash
# Delete and restart
rm bot_data.db
python main.py
```

---

## 🎨 Customization

### Add Your Own Roasts

Edit `FALLBACK_ROASTS` in `main.py`:

```python
FALLBACK_ROASTS = [
    "Your custom roast here...",
    "Another one...",
]
```

### Change Personality

Edit `souls.md` - yeh bot ki "atma" hai

### Adjust Temperature

In `main.py`:
```python
"temperature": 1.35,  # 0.0 = predictable, 2.0 = crazy
```

---

## 📊 Monitoring

### View Logs
```bash
# Railway
railway logs

# Local
tail -f bot.log
```

### Check Stats
Owner ko `/stats` command bhejo

---

## ⚡ Performance Tips

1. **Use lighter model** → `llama-3.1-8b-instant`
2. **Reduce max_tokens** → 250 instead of 350
3. **Enable caching** → Add Redis (advanced)

---

## 🔒 Security

- ✅ Owner ID hardcoded
- ✅ Anti-jailbreak protection
- ✅ SQL injection safe (parameterized queries)
- ✅ No sensitive data in logs

---

## 📜 License

MIT - Free to use, modify, distribute

---

## 🙏 Credits

Made with 🔥 by an elite developer

**Chal ab deploy kar aur maze le!** 🚀

---

## 📞 Support

Issues? Check:
1. Logs in Railway dashboard
2. Environment variables
3. API key validity
4. Bot token correctness

---

**Ready to roast? Let's go!** 😈🔥
