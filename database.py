import aiosqlite
import json
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = "mining_bot.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
        PRAGMA journal_mode=WAL;

        CREATE TABLE IF NOT EXISTS users (
            user_id         INTEGER PRIMARY KEY,
            username        TEXT    DEFAULT '',
            first_name      TEXT    DEFAULT '',
            balance         INTEGER DEFAULT 200,
            total_earned    INTEGER DEFAULT 0,
            total_mined     INTEGER DEFAULT 0,
            mine_count      INTEGER DEFAULT 0,
            energy          INTEGER DEFAULT 100,
            max_energy      INTEGER DEFAULT 100,
            level           INTEGER DEFAULT 1,
            xp              INTEGER DEFAULT 0,
            rebirth_count   INTEGER DEFAULT 0,
            perm_coin_mult  REAL    DEFAULT 1.0,
            current_tool    TEXT    DEFAULT 'stone_pick',
            current_zone    TEXT    DEFAULT 'surface',
            owned_tools     TEXT    DEFAULT '["stone_pick"]',
            unlocked_zones  TEXT    DEFAULT '["surface"]',
            inventory       TEXT    DEFAULT '{}',
            active_buffs    TEXT    DEFAULT '{}',
            achievements    TEXT    DEFAULT '[]',
            daily_streak    INTEGER DEFAULT 0,
            last_daily      TEXT    DEFAULT NULL,
            last_energy_regen TEXT  DEFAULT NULL,
            last_auto_mine  TEXT    DEFAULT NULL,
            referrer_id     INTEGER DEFAULT NULL,
            created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS mining_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            tool_id     TEXT,
            tool_name   TEXT,
            zone        TEXT,
            ore_type    TEXT,
            ore_name    TEXT,
            coins       INTEGER,
            xp_gained   INTEGER,
            is_crit     INTEGER DEFAULT 0,
            is_lucky    INTEGER DEFAULT 0,
            special_hit TEXT    DEFAULT NULL,
            mined_at    TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            type        TEXT,
            amount      INTEGER,
            description TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_mining_user  ON mining_log(user_id);
        CREATE INDEX IF NOT EXISTS idx_mining_ore   ON mining_log(ore_type);
        CREATE INDEX IF NOT EXISTS idx_users_total  ON users(total_mined);
        """)
        await db.commit()
    logger.info("✅ DB initialized")


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def _loads(val, default):
    try:
        return json.loads(val) if val else default
    except Exception:
        return default


def _row_to_user(row) -> dict:
    d = dict(row)
    d["owned_tools"]    = _loads(d.get("owned_tools"),    ["stone_pick"])
    d["unlocked_zones"] = _loads(d.get("unlocked_zones"), ["surface"])
    d["inventory"]      = _loads(d.get("inventory"),      {})
    d["active_buffs"]   = _loads(d.get("active_buffs"),   {})
    d["achievements"]   = _loads(d.get("achievements"),   [])
    return d


# ─────────────────────────────────────────────────────────────
# USER CRUD
# ─────────────────────────────────────────────────────────────
async def get_user(user_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return _row_to_user(row) if row else None


async def create_user(user_id: int, username: str, first_name: str,
                      referrer_id: int = None) -> dict:
    from config import STARTING_BALANCE, REFERRAL_BONUS
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR IGNORE INTO users
               (user_id, username, first_name, balance, referrer_id)
               VALUES (?,?,?,?,?)""",
            (user_id, username or "", first_name or "Miner",
             STARTING_BALANCE, referrer_id)
        )
        if referrer_id:
            await db.execute(
                "UPDATE users SET balance=balance+? WHERE user_id=?",
                (REFERRAL_BONUS, referrer_id)
            )
        await db.commit()
    return await get_user(user_id)


async def update_user(user_id: int, **kwargs):
    if not kwargs:
        return
    for key in ("owned_tools", "unlocked_zones", "inventory",
                "active_buffs", "achievements"):
        if key in kwargs:
            kwargs[key] = json.dumps(kwargs[key], ensure_ascii=False)
    cols = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {cols} WHERE user_id=?", vals)
        await db.commit()


async def add_balance(user_id: int, amount: int, desc: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance=balance+?, total_earned=total_earned+? WHERE user_id=?",
            (amount, max(0, amount), user_id)
        )
        if desc:
            await db.execute(
                "INSERT INTO transactions(user_id,type,amount,description) VALUES(?,?,?,?)",
                (user_id, "credit" if amount >= 0 else "debit", amount, desc)
            )
        await db.commit()


# ─────────────────────────────────────────────────────────────
# MINING LOG
# ─────────────────────────────────────────────────────────────
async def log_mine(user_id: int, tool_id: str, tool_name: str, zone: str,
                   ore_type: str, ore_name: str, coins: int, xp: int,
                   is_crit: bool = False, is_lucky: bool = False,
                   special: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO mining_log
               (user_id,tool_id,tool_name,zone,ore_type,ore_name,coins,xp_gained,is_crit,is_lucky,special_hit)
               VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (user_id, tool_id, tool_name, zone, ore_type, ore_name,
             coins, xp, int(is_crit), int(is_lucky), special)
        )
        # Update counters
        await db.execute(
            "UPDATE users SET total_mined=total_mined+?, mine_count=mine_count+1 WHERE user_id=?",
            (coins, user_id)
        )
        await db.commit()


# ─────────────────────────────────────────────────────────────
# LEADERBOARD & STATS
# ─────────────────────────────────────────────────────────────
async def get_leaderboard(limit: int = 10) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT user_id,username,first_name,total_mined,level,rebirth_count "
            "FROM users ORDER BY total_mined DESC LIMIT ?", (limit,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_user_rank(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE total_mined>"
            "(SELECT total_mined FROM users WHERE user_id=?)", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return (row[0] + 1) if row else 999


async def get_ore_stats(user_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT ore_type,ore_name,COUNT(*) as cnt,SUM(coins) as total "
            "FROM mining_log WHERE user_id=? GROUP BY ore_type ORDER BY total DESC",
            (user_id,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_all_users() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT user_id,username,first_name,balance,level,total_mined FROM users") as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_total_users() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            row = await cur.fetchone()
            return row[0] if row else 0
