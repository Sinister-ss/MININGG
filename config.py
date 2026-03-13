import os
from dotenv import load_dotenv
load_dotenv()

# ══════════════════════════════════════════════════════════════
# 🔑 CREDENTIALS
# ══════════════════════════════════════════════════════════════
BOT_TOKEN = os.getenv("8660124702:AAEAqsXsedrtx3wS6nbAtsHnKa6fOqTZ76E")

# ID Telegram admin (pisahkan dengan koma di env: "123,456")
_raw_admins = os.getenv("577381","7573097201")
ADMIN_IDS: list[int] = [int(x.strip()) for x in _raw_admins.split(",") if x.strip().isdigit()]

DATABASE_URL = os.getenv("DATABASE_URL", "mining_bot.db")

# ══════════════════════════════════════════════════════════════
# 💰 EKONOMI GAME
# ══════════════════════════════════════════════════════════════
STARTING_BALANCE   = 200       # Koin awal pemain baru
DAILY_BONUS_BASE   = 100       # Bonus harian dasar
DAILY_BONUS_LEVEL  = 10        # +X koin per level
REFERRAL_BONUS     = 300       # Koin bonus referral (pemberi & penerima)
ENERGY_REGEN_RATE  = 1         # Energy regen per menit
MAX_ENERGY_BASE    = 100       # Max energy default
LUCKY_CHANCE       = 0.05      # 5% base lucky strike
CRITICAL_CHANCE    = 0.10      # 10% critical hit (2x coins)

# ══════════════════════════════════════════════════════════════
# ⛏️ PERALATAN MINING — Dari GRATIS hingga LEGENDARY
# ══════════════════════════════════════════════════════════════
TOOLS: dict = {

    # ╔══ TIER 1 — STARTER (Gratis) ═══════════════════════════╗
    "stone_pick": {
        "name":          "⛏️ Beliung Batu",
        "emoji":         "⛏️",
        "tier":          1,
        "tier_name":     "Starter",
        "price":         0,
        "power":         2,          # koin base per mine
        "energy_cost":   10,
        "speed_mult":    1.0,
        "crit_bonus":    0.0,
        "luck_bonus":    0.0,
        "description":   "Beliung batu klasik. Gratis untuk semua pemain!",
        "flavor":        "Terbuat dari batu sungai yang dipahat kasar.",
        "level_req":     1,
        "special":       None,
    },

    # ╔══ TIER 2 — BASIC ═══════════════════════════════════════╗
    "copper_pick": {
        "name":          "🔨 Beliung Tembaga",
        "emoji":         "🔨",
        "tier":          2,
        "tier_name":     "Basic",
        "price":         800,
        "power":         5,
        "energy_cost":   9,
        "speed_mult":    1.1,
        "crit_bonus":    0.02,
        "luck_bonus":    0.0,
        "description":   "Beliung tembaga ringan. Power +5, sedikit lebih cepat.",
        "flavor":        "Dilebur dari bijih tembaga murni.",
        "level_req":     2,
        "special":       None,
    },
    "iron_pick": {
        "name":          "⚒️ Beliung Besi",
        "emoji":         "⚒️",
        "tier":          2,
        "tier_name":     "Basic",
        "price":         2500,
        "power":         12,
        "energy_cost":   8,
        "speed_mult":    1.2,
        "crit_bonus":    0.03,
        "luck_bonus":    0.01,
        "description":   "Beliung besi kokoh. Power +12, efisiensi lebih baik.",
        "flavor":        "Tempa besi kualitas tinggi dari pandai besi.",
        "level_req":     4,
        "special":       None,
    },

    # ╔══ TIER 3 — ADVANCED ════════════════════════════════════╗
    "steel_drill": {
        "name":          "🔩 Bor Baja",
        "emoji":         "🔩",
        "tier":          3,
        "tier_name":     "Advanced",
        "price":         8000,
        "power":         28,
        "energy_cost":   12,
        "speed_mult":    1.5,
        "crit_bonus":    0.05,
        "luck_bonus":    0.02,
        "description":   "Bor baja mekanik. Power +28, bisa menembus batuan keras.",
        "flavor":        "Mesin bor pertama yang menggunakan mekanisme gigi roda.",
        "level_req":     6,
        "special":       None,
    },
    "electric_drill": {
        "name":          "⚡ Bor Listrik",
        "emoji":         "⚡",
        "tier":          3,
        "tier_name":     "Advanced",
        "price":         20000,
        "power":         55,
        "energy_cost":   14,
        "speed_mult":    1.8,
        "crit_bonus":    0.06,
        "luck_bonus":    0.03,
        "description":   "Bor bertenaga listrik. Power +55, kecepatan meningkat drastis!",
        "flavor":        "Motor 500W yang menghasilkan torsi luar biasa.",
        "level_req":     8,
        "special":       "⚡ Chance 8% untuk double ore!",
    },

    # ╔══ TIER 4 — EXPERT ══════════════════════════════════════╗
    "pneumatic_jack": {
        "name":          "🏗️ Pneumatic Jackhammer",
        "emoji":         "🏗️",
        "tier":          4,
        "tier_name":     "Expert",
        "price":         60000,
        "power":         120,
        "energy_cost":   18,
        "speed_mult":    2.0,
        "crit_bonus":    0.08,
        "luck_bonus":    0.05,
        "description":   "Jackhammer pneumatik industri. Power +120, mengguncang tanah!",
        "flavor":        "Ditenagai angin bertekanan tinggi 200 PSI.",
        "level_req":     12,
        "special":       "💥 Crit damage +15%",
    },
    "diamond_drill": {
        "name":          "💠 Diamond Drill",
        "emoji":         "💠",
        "tier":          4,
        "tier_name":     "Expert",
        "price":         150000,
        "power":         250,
        "energy_cost":   20,
        "speed_mult":    2.3,
        "crit_bonus":    0.10,
        "luck_bonus":    0.07,
        "description":   "Mata bor berlapis berlian asli. Power +250, menembus apapun!",
        "flavor":        "Lapisan berlian industri grade-A untuk ketahanan maksimal.",
        "level_req":     16,
        "special":       "🔮 +7% rare ore",
    },

    # ╔══ TIER 5 — MASTER ══════════════════════════════════════╗
    "laser_cutter": {
        "name":          "🔬 Laser Cutter Pro",
        "emoji":         "🔬",
        "tier":          5,
        "tier_name":     "Master",
        "price":         400000,
        "power":         500,
        "energy_cost":   22,
        "speed_mult":    2.8,
        "crit_bonus":    0.12,
        "luck_bonus":    0.10,
        "description":   "Pemotong laser presisi tinggi. Power +500, akurasi sempurna.",
        "flavor":        "Laser CO₂ 1000W yang dapat memotong baja 50mm.",
        "level_req":     22,
        "special":       "✨ +10% bonus XP",
    },
    "plasma_drill": {
        "name":          "🌟 Plasma Drill",
        "emoji":         "🌟",
        "tier":          5,
        "tier_name":     "Master",
        "price":         900000,
        "power":         1000,
        "energy_cost":   26,
        "speed_mult":    3.2,
        "crit_bonus":    0.15,
        "luck_bonus":    0.12,
        "description":   "Bor plasma futuristik. Power +1000, mengionisasi batuan!",
        "flavor":        "Teknologi plasma yang diadaptasi dari reaktor fusi.",
        "level_req":     30,
        "special":       "🌟 Plasma Burst: 12% chance x3 coins",
    },

    # ╔══ TIER 6 — LEGENDARY ═══════════════════════════════════╗
    "quantum_miner": {
        "name":          "💎 Quantum Miner X",
        "emoji":         "💎",
        "tier":          6,
        "tier_name":     "Legendary",
        "price":         3000000,
        "power":         2500,
        "energy_cost":   30,
        "speed_mult":    4.0,
        "crit_bonus":    0.18,
        "luck_bonus":    0.15,
        "description":   "Penambang kuantum ultra-canggih. Power +2500, manipulasi quantum!",
        "flavor":        "Menggunakan superposisi kuantum untuk menambang di multi-dimensi.",
        "level_req":     40,
        "special":       "🌀 Quantum Shift: 15% chance dapat 2 ore sekaligus!",
    },
    "void_extractor": {
        "name":          "🕳️ Void Extractor",
        "emoji":         "🕳️",
        "tier":          6,
        "tier_name":     "Legendary",
        "price":         8000000,
        "power":         5000,
        "energy_cost":   35,
        "speed_mult":    5.0,
        "crit_bonus":    0.20,
        "luck_bonus":    0.20,
        "description":   "Ekstraktor lubang hitam. Power +5000, menyedot materi dari dimensi lain!",
        "flavor":        "Teknologi yang ditemukan dari reruntuhan peradaban alien.",
        "level_req":     55,
        "special":       "🕳️ Void Pull: 20% chance mendapat double loot!",
    },

    # ╔══ TIER 7 — MYTHICAL (Ultra Rare) ═══════════════════════╗
    "celestial_hammer": {
        "name":          "☄️ Celestial War Hammer",
        "emoji":         "☄️",
        "tier":          7,
        "tier_name":     "Mythical",
        "price":         25000000,
        "power":         12000,
        "energy_cost":   40,
        "speed_mult":    6.0,
        "crit_bonus":    0.25,
        "luck_bonus":    0.25,
        "description":   "Palu perang celestial dari surga. Power +12000, kekuatan dewa!",
        "flavor":        "Ditempa dari logam bintang neutron oleh para dewa tambang.",
        "level_req":     70,
        "special":       "☄️ Meteor Strike: 25% chance x5 coins! Juga +25% rare ore!",
    },
}

# ══════════════════════════════════════════════════════════════
# 🪨 JENIS BIJIH — Dari umum hingga sangat langka
# ══════════════════════════════════════════════════════════════
ORES: dict = {
    "coal":         {"name": "🪨 Batu Bara",    "emoji": "🪨", "value": 1,      "rarity": 35.0, "xp": 1},
    "stone":        {"name": "🗿 Batu Biasa",    "emoji": "🗿", "value": 2,      "rarity": 20.0, "xp": 2},
    "iron":         {"name": "⬛ Bijih Besi",    "emoji": "⬛", "value": 5,      "rarity": 18.0, "xp": 4},
    "copper":       {"name": "🟤 Bijih Tembaga", "emoji": "🟤", "value": 8,      "rarity": 10.0, "xp": 6},
    "silver":       {"name": "⬜ Perak",          "emoji": "⬜", "value": 20,     "rarity": 6.5,  "xp": 12},
    "gold":         {"name": "🟡 Emas Murni",    "emoji": "🟡", "value": 50,     "rarity": 4.0,  "xp": 25},
    "sapphire":     {"name": "🔵 Safir",          "emoji": "🔵", "value": 150,    "rarity": 2.5,  "xp": 60},
    "emerald":      {"name": "💚 Zamrud",         "emoji": "💚", "value": 300,    "rarity": 1.5,  "xp": 100},
    "ruby":         {"name": "❤️ Rubi",           "emoji": "❤️", "value": 600,    "rarity": 0.9,  "xp": 200},
    "diamond":      {"name": "💎 Berlian",        "emoji": "💎", "value": 1500,   "rarity": 0.5,  "xp": 500},
    "amethyst":     {"name": "💜 Ametis",         "emoji": "💜", "value": 3000,   "rarity": 0.25, "xp": 800},
    "mythril":      {"name": "🔮 Mithril",        "emoji": "🔮", "value": 8000,   "rarity": 0.10, "xp": 2000},
    "dragonstone":  {"name": "🐉 Batu Naga",      "emoji": "🐉", "value": 20000,  "rarity": 0.04, "xp": 5000},
    "stardust":     {"name": "✨ Debu Bintang",   "emoji": "✨", "value": 50000,  "rarity": 0.01, "xp": 10000},
    "void_shard":   {"name": "🌑 Void Shard",     "emoji": "🌑", "value": 150000, "rarity": 0.005,"xp": 30000},
}

# ══════════════════════════════════════════════════════════════
# 🎒 ITEM / CONSUMABLE
# ══════════════════════════════════════════════════════════════
ITEMS: dict = {
    "energy_potion": {
        "name":        "⚡ Energy Potion",
        "emoji":       "⚡",
        "price":       500,
        "description": "Pulihkan 50 energy seketika.",
        "effect":      {"energy": 50},
        "stackable":   True,
    },
    "energy_potion_lg": {
        "name":        "⚡⚡ Energy Potion XL",
        "emoji":       "⚡",
        "price":       1200,
        "description": "Pulihkan energy PENUH seketika.",
        "effect":      {"energy": 999},  # auto-cap at max
        "stackable":   True,
    },
    "luck_elixir": {
        "name":        "🍀 Luck Elixir",
        "emoji":       "🍀",
        "price":       3000,
        "description": "+20% peluang rare ore selama 30 menit.",
        "effect":      {"luck_buff": 0.20, "duration": 30},
        "stackable":   True,
    },
    "double_coin": {
        "name":        "💰 Double Coin Scroll",
        "emoji":       "💰",
        "price":       5000,
        "description": "2x koin selama 20 menit berikutnya.",
        "effect":      {"coin_mult": 2.0, "duration": 20},
        "stackable":   True,
    },
    "xp_boost": {
        "name":        "⭐ XP Booster",
        "emoji":       "⭐",
        "price":       4000,
        "description": "3x XP selama 20 menit.",
        "effect":      {"xp_mult": 3.0, "duration": 20},
        "stackable":   True,
    },
    "auto_miner_1h": {
        "name":        "🤖 Auto Miner (1 jam)",
        "emoji":       "🤖",
        "price":       8000,
        "description": "Mining otomatis setiap 10 menit selama 1 jam.",
        "effect":      {"auto_mine": True, "duration": 60},
        "stackable":   True,
    },
    "mystery_box": {
        "name":        "📦 Mystery Box",
        "emoji":       "📦",
        "price":       2000,
        "description": "Kotak misterius! Isi acak bisa koin, item, atau bahkan ore langka.",
        "effect":      {"mystery": True},
        "stackable":   True,
    },
    "rebirth_token": {
        "name":        "🔄 Rebirth Token",
        "emoji":       "🔄",
        "price":       500000,
        "description": "Reset level ke 1 dengan bonus permanen: +50% permanent coin boost!",
        "effect":      {"rebirth": True},
        "stackable":   False,
    },
}

# ══════════════════════════════════════════════════════════════
# 🏅 PRESTASI / ACHIEVEMENTS
# ══════════════════════════════════════════════════════════════
ACHIEVEMENTS: dict = {
    "first_mine":     {"name": "🥇 Pertama Kali!", "desc": "Lakukan mining pertama",         "reward": 50},
    "mine_10":        {"name": "⛏️ Penambang Pemula","desc": "Mining 10 kali",                "reward": 100},
    "mine_100":       {"name": "💪 Penambang Sejati","desc": "Mining 100 kali",               "reward": 500},
    "mine_1000":      {"name": "🏆 Master Miner",   "desc": "Mining 1000 kali",              "reward": 5000},
    "first_rare":     {"name": "🔮 Rare Hunter",    "desc": "Dapatkan ore rare pertama",     "reward": 300},
    "rich_100k":      {"name": "💰 Orang Kaya",     "desc": "Kumpulkan 100.000 koin",        "reward": 1000},
    "rich_1m":        {"name": "💎 Jutawan",        "desc": "Kumpulkan 1.000.000 koin",      "reward": 10000},
    "lvl_10":         {"name": "⭐ Bintang 10",     "desc": "Capai Level 10",                "reward": 500},
    "lvl_50":         {"name": "🌟 Bintang 50",     "desc": "Capai Level 50",                "reward": 5000},
    "void_shard":     {"name": "🌑 Void Seeker",    "desc": "Temukan Void Shard pertama",    "reward": 50000},
    "daily_streak_7": {"name": "🔥 7-Day Streak",   "desc": "Daily bonus 7 hari berturut",   "reward": 2000},
    "daily_streak_30":{"name": "🌙 30-Day Streak",  "desc": "Daily bonus 30 hari berturut",  "reward": 20000},
}

# ══════════════════════════════════════════════════════════════
# ⭐ LEVEL SYSTEM
# ══════════════════════════════════════════════════════════════
def xp_for_level(level: int) -> int:
    """XP yang dibutuhkan untuk naik dari level ini ke level berikutnya."""
    return int(150 * (level ** 1.6))

MAX_LEVEL = 100

# ══════════════════════════════════════════════════════════════
# 🌍 ZONA MINING (unlockable areas)
# ══════════════════════════════════════════════════════════════
ZONES: dict = {
    "surface": {
        "name": "🏔️ Permukaan",
        "desc": "Zona awal. Ore biasa.",
        "level_req": 1,
        "ore_bonus": {},
        "unlock_cost": 0,
    },
    "cave": {
        "name": "🕯️ Gua Dalam",
        "desc": "Lebih banyak ore besi & perak.",
        "level_req": 5,
        "ore_bonus": {"iron": 1.5, "silver": 1.3},
        "unlock_cost": 3000,
    },
    "underground": {
        "name": "⛰️ Bawah Tanah",
        "desc": "Emas & safir lebih sering muncul.",
        "level_req": 15,
        "ore_bonus": {"gold": 1.8, "sapphire": 1.5},
        "unlock_cost": 30000,
    },
    "lava_cave": {
        "name": "🌋 Gua Lava",
        "desc": "Rubi & berlian lebih melimpah!",
        "level_req": 25,
        "ore_bonus": {"ruby": 2.0, "diamond": 1.7},
        "unlock_cost": 150000,
    },
    "crystal_cavern": {
        "name": "🔮 Cavern Kristal",
        "desc": "Ametis & mithril berlimpah!",
        "level_req": 40,
        "ore_bonus": {"amethyst": 2.5, "mythril": 2.0},
        "unlock_cost": 600000,
    },
    "void_realm": {
        "name": "🌑 Void Realm",
        "desc": "Dimensi lain. Dragonstone & Void Shard!",
        "level_req": 60,
        "ore_bonus": {"dragonstone": 3.0, "stardust": 2.0, "void_shard": 2.5},
        "unlock_cost": 5000000,
    },
}

# ══════════════════════════════════════════════════════════════
# PESAN SISTEM
# ══════════════════════════════════════════════════════════════
TIER_COLORS = {
    1: "⬜", 2: "🟩", 3: "🟦", 4: "🟧",
    5: "🟥", 6: "💜", 7: "⭐"
}
