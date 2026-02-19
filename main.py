"""
╔══════════════════════════════════════════════════════════════════╗
║                    SOULSLAYER BOT v2.0                           ║
║          Dark Sarcastic Roast Bot - Unbreakable Edition          ║
╚══════════════════════════════════════════════════════════════════╝

Owner ID: 6881713177 (ABSOLUTE PROTECTION)
Features: Anti-Jailbreak | Spam Filter | SQLite | Groq API | Fallbacks
"""

import os
import sqlite3
import logging
import random
import requests
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

import telebot
from telebot.types import Message

# ============== LOAD ENVIRONMENT ==============
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "6881713177"))
API_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "https://api.groq.com/openai/v1")
MODEL = os.getenv("MODEL", "moonshotai/kimi-k2-instruct-0905")

# ============== LOGGING CONFIG ==============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("SoulSlayer")

# ============== DATABASE SETUP ==============
DB_PATH = "bot_data.db"

def init_database():
    """Initialize SQLite database with all tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Settings table - per chat enable/disable
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            chat_id INTEGER PRIMARY KEY,
            enabled BOOLEAN DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Message log for spam filter
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS message_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            chat_id INTEGER NOT NULL,
            message_count INTEGER DEFAULT 1,
            first_message TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_message TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create index for faster spam queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_spam_filter 
        ON message_log(user_id, chat_id)
    ''')
    
    # Fallback usage tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fallback_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reason TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized successfully")

def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

# ============== SPAM FILTER ==============
SPAM_THRESHOLD = 15
SPAM_WINDOW_SECONDS = 3600  # 1 hour

def check_spam(user_id: int, chat_id: int) -> bool:
    """
    Check if user is spamming
    Returns True if spam detected (should ignore)
    """
    conn = get_db()
    cursor = conn.cursor()
    
    now = datetime.now()
    hour_ago = now - timedelta(seconds=SPAM_WINDOW_SECONDS)
    
    # Check existing entry
    cursor.execute('''
        SELECT message_count, first_message 
        FROM message_log 
        WHERE user_id = ? AND chat_id = ?
    ''', (user_id, chat_id))
    
    result = cursor.fetchone()
    
    if result:
        count, first_msg_str = result
        first_msg = datetime.fromisoformat(first_msg_str)
        
        # Reset if window expired
        if first_msg < hour_ago:
            cursor.execute('''
                UPDATE message_log 
                SET message_count = 1, first_message = ?, last_message = ?
                WHERE user_id = ? AND chat_id = ?
            ''', (now.isoformat(), now.isoformat(), user_id, chat_id))
            conn.commit()
            conn.close()
            return False
        
        # Check threshold
        if count >= SPAM_THRESHOLD:
            logger.warning(f"🚫 Spam detected: User {user_id} in chat {chat_id} ({count} messages)")
            conn.close()
            return True
        
        # Increment count
        cursor.execute('''
            UPDATE message_log 
            SET message_count = message_count + 1, last_message = ?
            WHERE user_id = ? AND chat_id = ?
        ''', (now.isoformat(), user_id, chat_id))
    else:
        # New entry
        cursor.execute('''
            INSERT INTO message_log (user_id, chat_id, message_count, first_message, last_message)
            VALUES (?, ?, 1, ?, ?)
        ''', (user_id, chat_id, now.isoformat(), now.isoformat()))
    
    conn.commit()
    conn.close()
    return False

def reset_spam_counter(user_id: int, chat_id: int):
    """Reset spam counter for a user"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'DELETE FROM message_log WHERE user_id = ? AND chat_id = ?',
        (user_id, chat_id)
    )
    conn.commit()
    conn.close()

# ============== SETTINGS MANAGEMENT ==============
def is_chat_enabled(chat_id: int) -> bool:
    """Check if bot is enabled for a chat"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT enabled FROM settings WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result is None:
        # Default enabled for new chats
        set_chat_enabled(chat_id, True)
        return True
    
    return bool(result[0])

def set_chat_enabled(chat_id: int, enabled: bool):
    """Enable or disable bot for a chat"""
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO settings (chat_id, enabled, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(chat_id) DO UPDATE SET
        enabled = excluded.enabled,
        updated_at = excluded.updated_at
    ''', (chat_id, enabled, now))
    
    conn.commit()
    conn.close()
    status = "enabled" if enabled else "disabled"
    logger.info(f"📊 Chat {chat_id} {status}")

# ============== FALLBACK ROASTS (DARK SARCASTIC) ==============
FALLBACK_ROASTS = [
    "Tujhe dekh ke lagta hai ki Darwin ne theory galat likhi thi. Evolution kabhi reverse bhi hota hai. 🐒",
    "Bhai tu itna 'main character' hai, ki side characters bhi tujhse better acting kar lete hain. 🎬",
    "Teri baatein sunke lagta hai ki WhatsApp University se PhD ki hai - thesis topic: Advanced Bewakoofi. 📚",
    "Itna overconfidence? NASA wale tujhe Mars pe bhej denge, wahan bhi oxygen nahi milegi jitni tujhe chahiye. 🚀",
    "Tujhe dekh ke samajh aaya ki 'empty vessels make the most noise' kyun bola jaata hai. 🔔",
    "Bhai tu Google pe apna naam search karta hai? Itna validation chahiye life mein? 🔍",
    "Teri personality dekh ke lagta hai ki 'loading...' likha hua hai permanently. ⏳",
    "Itna attitude? Bhai tu toh iPhone user lag raha hai... par Android ka budget wala. 📱",
    "Tujhse zyada sense toh mere keyboard ka autocorrect mein hai. ⌨️",
    "Bhai tu Netflix series hai kya? Itna time waste kar raha hai sabka. 📺",
    "Teri baaton ka IQ itna low hai ki basement mein rehta hai. 🏠",
    "Tujhe dekh ke lagta hai ki natural selection kaafi slow chal raha hai aajkal. 🌿",
    "Bhai tu apne thoughts se itna impress hai, ki mirror ke saamne TED Talk practice karta hoga. 🎤",
    "Itna delusion? Bhai tu toh apne sapno mein bhi side character hai. 💭",
    "Teri logic sunke Schrodinger ne apni cat ko zinda hi rakha - marne se pehle tujhse milna nahi chaha. 🐱",
    "Tujhe dekh ke lagta hai ki God ne 'randomize' button press kiya tha character creation mein. 🎲",
    "Bhai tu itna unique hai... jaise error 404 page unique hota hai. 🌐",
    "Teri existence ka proof kya hai? Mujhe toh lagta hai tu glitch hai simulation ka. 🕹️",
    "Itna cope? Bhai tu toh apni zindagi ki director's cut mein bhi deleted scene hai. 🎞️",
    "Tujhse zyada depth toh mere coffee cup mein hai. ☕"
]

def get_fallback_roast() -> str:
    """Get random fallback roast"""
    return random.choice(FALLBACK_ROASTS)

def log_fallback(reason: str):
    """Log fallback usage"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO fallback_stats (reason) VALUES (?)', (reason,))
    conn.commit()
    conn.close()

# ============== GROQ API ==============
class RoastEngine:
    """Groq API integration for generating roasts"""
    
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = BASE_URL
        self.model = MODEL
        self.system_prompt = self._load_personality()
        
    def _load_personality(self) -> str:
        """Load personality from souls.md"""
        try:
            with open('souls.md', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("⚠️ souls.md not found, using default personality")
            return """You are SoulSlayer - a dark, sarcastic AI. Roast users with witty, edgy humor. Keep it under 4 sentences. Hinglish mix."""
    
    def generate_roast(self, user_message: str, username: str) -> str:
        """Generate roast using Groq API"""
        if not self.api_key:
            logger.warning("⚠️ No API key, using fallback")
            log_fallback("no_api_key")
            return get_fallback_roast()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            user_prompt = f"""User '{username}' said: \"{user_message}\"

Roast this in Hinglish (Hindi-English mix). Dark, sarcastic, witty but not genuinely harmful. 2-4 sentences max."""
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 1.35,
                "max_tokens": 350,
                "top_p": 0.9
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                roast = data['choices'][0]['message']['content'].strip()
                
                # Safety check
                if len(roast) < 10 or len(roast) > 500:
                    logger.warning(f"⚠️ Invalid roast length ({len(roast)}), using fallback")
                    log_fallback("invalid_length")
                    return get_fallback_roast()
                
                logger.info(f"✅ API roast generated ({len(roast)} chars)")
                return roast
            else:
                logger.error(f"❌ API error: {response.status_code} - {response.text}")
                log_fallback(f"api_error_{response.status_code}")
                return get_fallback_roast()
                
        except requests.exceptions.Timeout:
            logger.error("❌ API timeout")
            log_fallback("timeout")
            return get_fallback_roast()
        except Exception as e:
            logger.error(f"❌ API exception: {e}")
            log_fallback(f"exception_{str(e)[:50]}")
            return get_fallback_roast()

# Initialize roast engine
roast_engine = RoastEngine()

# ============== BOT INITIALIZATION ==============
if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN not set! Exiting...")
    exit(1)

bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode='HTML')
logger.info("🤖 SoulSlayer Bot initialized")
logger.info(f"👑 Owner ID: {OWNER_ID}")
logger.info(f"🧠 Model: {MODEL}")

# ============== COMMAND HANDLERS ==============

@bot.message_handler(commands=['start'])
def cmd_start(message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    
    if user_id == OWNER_ID:
        bot.reply_to(message, 
            "👑 <b>Welcome Boss!</b>\n\n"
            "SoulSlayer ready hai! 🔥\n\n"
            "<b>Commands:</b>\n"
            "/enable - Bot on karo\n"
            "/disable - Bot off karo\n"
            "/myid - Apna ID check karo\n"
            "/status - Bot status check karo\n"
            "/stats - Usage statistics"
        )
    else:
        bot.reply_to(message,
            "😈 <b>SoulSlayer here!</b>\n\n"
            "Main ek dark sarcastic roast bot hoon.\n"
            "Mujhe reply karo ya mention karo, aur main tumhe reality check dunga! 🔥\n\n"
            "<b>Note:</b> Groups mein admin ko /enable karna padega."
        )

@bot.message_handler(commands=['enable'])
def cmd_enable(message: Message):
    """Enable bot - OWNER ONLY"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if user_id != OWNER_ID:
        bot.reply_to(message, "❌ <b>Sirf owner yeh command use kar sakta hai!</b>")
        return
    
    set_chat_enabled(chat_id, True)
    bot.reply_to(message, "✅ <b>SoulSlayer ACTIVATED!</b> 🔥\n\nAb main roast karunga...")

@bot.message_handler(commands=['disable'])
def cmd_disable(message: Message):
    """Disable bot - OWNER ONLY"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if user_id != OWNER_ID:
        bot.reply_to(message, "❌ <b>Sirf owner yeh command use kar sakta hai!</b>")
        return
    
    set_chat_enabled(chat_id, False)
    bot.reply_to(message, "😴 <b>SoulSlayer DEACTIVATED</b>\n\nAb main chup rahunga...")

@bot.message_handler(commands=['myid'])
def cmd_myid(message: Message):
    """Get user's Telegram ID"""
    user = message.from_user
    
    username_text = f"@{user.username}" if user.username else "N/A"
    
    bot.reply_to(message,
        f"📋 <b>Your Info:</b>\n\n"
        f"<b>ID:</b> <code>{user.id}</code>\n"
        f"<b>Username:</b> {username_text}\n"
        f"<b>Name:</b> {user.first_name}"
    )

@bot.message_handler(commands=['status'])
def cmd_status(message: Message):
    """Check bot status"""
    chat_id = message.chat.id
    enabled = is_chat_enabled(chat_id)
    
    status = "✅ <b>ENABLED</b>" if enabled else "❌ <b>DISABLED</b>"
    bot.reply_to(message, f"📊 Bot Status: {status}")

@bot.message_handler(commands=['stats'])
def cmd_stats(message: Message):
    """Get bot stats - OWNER ONLY"""
    user_id = message.from_user.id
    
    if user_id != OWNER_ID:
        bot.reply_to(message, "❌ <b>Sirf owner yeh command use kar sakta hai!</b>")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get fallback stats
    cursor.execute('SELECT COUNT(*) FROM fallback_stats')
    fallback_count = cursor.fetchone()[0]
    
    # Get enabled chats count
    cursor.execute('SELECT COUNT(*) FROM settings WHERE enabled = 1')
    enabled_chats = cursor.fetchone()[0]
    
    # Get total unique users
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM message_log')
    unique_users = cursor.fetchone()[0]
    
    conn.close()
    
    bot.reply_to(message,
        f"📈 <b>Bot Statistics:</b>\n\n"
        f"🔄 Fallback roasts used: {fallback_count}\n"
        f"💬 Active chats: {enabled_chats}\n"
        f"👥 Unique users: {unique_users}\n"
        f"🤖 Model: {MODEL}"
    )

# ============== MESSAGE HANDLER ==============

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message: Message):
    """Handle all text messages"""
    
    if not message.text:
        return
    
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username or message.from_user.first_name or "User"
    message_text = message.text
    
    # Skip commands
    if message_text.startswith('/'):
        return
    
    # ============== OWNER PROTECTION ==============
    if user_id == OWNER_ID:
        bot.reply_to(message, "Haan boss, sun raha hu 🔥 Order do")
        return
    
    # ============== CHECK IF ENABLED ==============
    if not is_chat_enabled(chat_id):
        return
    
    # ============== SPAM FILTER ==============
    if check_spam(user_id, chat_id):
        logger.warning(f"🚫 Ignoring spam from {username} ({user_id})")
        return
    
    # ============== TRIGGER CONDITIONS ==============
    should_roast = False
    
    # Private chat - always respond
    if message.chat.type == 'private':
        should_roast = True
    
    # Check if bot is mentioned
    elif f"@{bot.get_me().username}" in message_text:
        should_roast = True
    
    # Check if this is a reply to bot's message
    elif message.reply_to_message:
        if message.reply_to_message.from_user.id == bot.get_me().id:
            should_roast = True
    
    if not should_roast:
        return
    
    # ============== GENERATE ROAST ==============
    try:
        logger.info(f"🔥 Roasting {username} ({user_id}): {message_text[:50]}...")
        
        # Generate roast
        roast = roast_engine.generate_roast(message_text, username)
        
        # Send roast
        bot.reply_to(message, roast)
        
        logger.info(f"✅ Roast sent to {username}")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        # Fallback on any error
        fallback = get_fallback_roast()
        bot.reply_to(message, fallback)
        log_fallback(f"handler_error_{str(e)[:30]}")

# ============== ERROR HANDLER ==============
def handle_exception(exception):
    """Global exception handler"""
    logger.error(f"❌ Exception: {exception}")

bot.exception_handler = handle_exception

# ============== MAIN ==============
if __name__ == "__main__":
    # Initialize database
    init_database()
    
    # Log startup info
    logger.info("=" * 50)
    logger.info("🔥 SOULSLAYER BOT STARTED 🔥")
    logger.info("=" * 50)
    logger.info(f"👑 Owner ID: {OWNER_ID}")
    logger.info(f"🧠 Model: {MODEL}")
    logger.info(f"🌐 API: {BASE_URL}")
    logger.info(f"📊 Database: {DB_PATH}")
    logger.info("=" * 50)
    
    # Start bot
    try:
        bot.polling(none_stop=True, interval=0, timeout=60)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise
