import aiosqlite
from datetime import datetime
import asyncio

class Database:
    def __init__(self, db_name='mining_app.db'):
        self.db_name = db_name

    async def init_db(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                currency INTEGER DEFAULT 0,
                last_mine TEXT,
                referral_code TEXT UNIQUE,
                referred_by INTEGER,
                referrals INTEGER DEFAULT 0
            )
            ''')
            await db.execute('''
            CREATE TABLE IF NOT EXISTS games (
                user_id INTEGER,
                game_name TEXT,
                played_at TEXT,
                result TEXT,
                reward INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            ''')
            await db.commit()

    async def add_user(self, user_id, username, referred_by=None):
        async with aiosqlite.connect(self.db_name) as db:
            referral_code = f"REF{user_id}"
            await db.execute("INSERT OR IGNORE INTO users (user_id, username, referral_code, referred_by) VALUES (?, ?, ?, ?)",
                             (user_id, username, referral_code, referred_by))
            if referred_by:
                await db.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id = ?", (referred_by,))
            await db.commit()

    async def update_currency(self, user_id, amount):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("UPDATE users SET currency = currency + ? WHERE user_id = ?", (amount, user_id))
            await db.commit()

    async def get_user_currency(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT currency FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0

    async def get_last_mine(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT last_mine FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
                return datetime.fromisoformat(result[0]) if result and result[0] else None

    async def set_last_mine(self, user_id, time):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("UPDATE users SET last_mine = ? WHERE user_id = ?", (time.isoformat(), user_id))
            await db.commit()

    async def add_game_result(self, user_id, game_name, result, reward):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("INSERT INTO games (user_id, game_name, played_at, result, reward) VALUES (?, ?, ?, ?, ?)",
                             (user_id, game_name, datetime.now().isoformat(), result, reward))
            await db.commit()

    async def get_referral_info(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT referral_code, referrals FROM users WHERE user_id = ?", (user_id,)) as cursor:
                return await cursor.fetchone()

    async def get_user_by_referral_code(self, referral_code):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT user_id FROM users WHERE referral_code = ?", (referral_code,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None

    async def get_leaderboard(self, limit=10):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT username, currency FROM users ORDER BY currency DESC LIMIT ?", (limit,)) as cursor:
                return await cursor.fetchall()