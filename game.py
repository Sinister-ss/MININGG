import random
import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional

from config import (TOOLS, ORES, ITEMS, ACHIEVEMENTS, ZONES,
                    ENERGY_REGEN_RATE, LUCKY_CHANCE, CRITICAL_CHANCE,
                    xp_for_level, MAX_LEVEL)
from database import get_user, update_user, log_mine, add_balance

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# ENERGY SYSTEM
# ══════════════════════════════════════════════════════════════
async def regen_energy(user: dict) -> dict:
    now = datetime.now()
    last = user.get("last_energy_regen")
    if last:
        try:
            last_dt = datetime.fromisoformat(last)
            minutes = (now - last_dt).total_seconds() / 60
            gain = int(minutes * ENERGY_REGEN_RATE)
            if gain > 0:
                new_e = min(user["energy"] + gain, user["max_energy"])
                await update_user(user["user_id"], energy=new_e,
                                  last_energy_regen=now.isoformat())
                user["energy"] = new_e
        except Exception:
            pass
    else:
        await update_user(user["user_id"], last_energy_regen=now.isoformat())
    return user


def energy_full_in(user: dict) -> str:
    if user["energy"] >= user["max_energy"]:
        return "✅ PENUH"
    needed = user["max_energy"] - user["energy"]
    mins = needed / ENERGY_REGEN_RATE
    h, m = divmod(int(mins), 60)
    return f"{h}j {m}m" if h else f"{m}m"


# ══════════════════════════════════════════════════════════════
# BUFF SYSTEM
# ══════════════════════════════════════════════════════════════
def get_active_buffs(user: dict) -> dict:
    """Return still-active buffs, clean expired ones."""
    buffs = user.get("active_buffs", {})
    now = datetime.now()
    clean = {}
    for k, v in buffs.items():
        exp = v.get("expires")
        if exp:
            try:
                if datetime.fromisoformat(exp) > now:
                    clean[k] = v
            except Exception:
                pass
        else:
            clean[k] = v
    return clean


def get_buff_val(buffs: dict, key: str, default=0):
    b = buffs.get(key, {})
    return b.get("value", default)


# ══════════════════════════════════════════════════════════════
# ORE ROLLER
# ══════════════════════════════════════════════════════════════
def roll_ore(user: dict, buffs: dict, zone_id: str) -> Tuple[str, dict]:
    zone = ZONES.get(zone_id, ZONES["surface"])
    ore_bonus = zone.get("ore_bonus", {})
    luck_buff = get_buff_val(buffs, "luck_buff", 0)
    tool = TOOLS.get(user["current_tool"], TOOLS["stone_pick"])
    luck_bonus = tool["luck_bonus"] + luck_buff

    ores = list(ORES.items())
    weights = []
    for oid, ore in ores:
        w = ore["rarity"]
        if oid in ore_bonus:
            w *= ore_bonus[oid]
        if ore["value"] >= 300:          # rare ore gets luck boost
            w *= (1 + luck_bonus * 3)
        weights.append(max(w, 0.0001))

    total = sum(weights)
    weights = [w / total for w in weights]
    chosen = random.choices(ores, weights=weights, k=1)[0]
    return chosen[0], chosen[1]


# ══════════════════════════════════════════════════════════════
# MINING ENGINE
# ══════════════════════════════════════════════════════════════
async def perform_mine(user_id: int) -> dict:
    """
    Execute one mine action.
    Returns a result dict with all details.
    """
    user = await get_user(user_id)
    if not user:
        return {"ok": False, "msg": "❌ User tidak ditemukan. Ketik /start"}

    user = await regen_energy(user)
    buffs = get_active_buffs(user)

    tool_id   = user["current_tool"]
    tool      = TOOLS.get(tool_id, TOOLS["stone_pick"])
    zone_id   = user.get("current_zone", "surface")
    zone      = ZONES.get(zone_id, ZONES["surface"])
    energy_cost = tool["energy_cost"]

    if user["energy"] < energy_cost:
        return {
            "ok": False,
            "msg": (
                f"⚡ *Energy tidak cukup!*\n\n"
                f"Energy kamu: `{user['energy']}/{user['max_energy']}`\n"
                f"Dibutuhkan : `{energy_cost}` energy\n"
                f"⏰ Energy penuh dalam: *{energy_full_in(user)}*\n\n"
                f"💡 Gunakan ⚡ *Energy Potion* dari inventaris!"
            )
        }

    # ── Roll ore ──────────────────────────────────────────────
    ore_id, ore = roll_ore(user, buffs, zone_id)

    # ── Calculate base coins ──────────────────────────────────
    base     = tool["power"] * ore["value"]
    coin_mult  = get_buff_val(buffs, "coin_mult", 1.0) or 1.0
    perm_mult  = user.get("perm_coin_mult", 1.0) or 1.0
    coins    = int(base * coin_mult * perm_mult)

    # ── XP ────────────────────────────────────────────────────
    xp_mult  = get_buff_val(buffs, "xp_mult", 1.0) or 1.0
    xp_gain  = int(ore["xp"] * xp_mult)
    if tool.get("special") and "XP" in tool.get("special", ""):
        xp_gain = int(xp_gain * 1.1)

    # ── Critical hit ─────────────────────────────────────────
    crit_chance = CRITICAL_CHANCE + tool["crit_bonus"]
    is_crit = random.random() < crit_chance
    if is_crit:
        coins = int(coins * 2)

    # ── Lucky bonus ───────────────────────────────────────────
    luck_bonus = LUCKY_CHANCE + tool["luck_bonus"] + get_buff_val(buffs, "luck_buff", 0)
    is_lucky = random.random() < luck_bonus
    if is_lucky and not is_crit:
        coins = int(coins * 1.5)

    # ── Special tool effects ──────────────────────────────────
    special_hit = None
    if tool_id == "electric_drill" and random.random() < 0.08:
        coins *= 2
        special_hit = "⚡ Double Ore!"
    elif tool_id == "plasma_drill" and random.random() < 0.12:
        coins = int(coins * 3)
        special_hit = "🌟 Plasma Burst!"
    elif tool_id == "quantum_miner" and random.random() < 0.15:
        coins = int(coins * 2)
        xp_gain *= 2
        special_hit = "🌀 Quantum Shift!"
    elif tool_id == "void_extractor" and random.random() < 0.20:
        coins *= 2
        special_hit = "🕳️ Void Pull!"
    elif tool_id == "celestial_hammer" and random.random() < 0.25:
        coins *= 5
        special_hit = "☄️ Meteor Strike!"

    # ── Apply changes ─────────────────────────────────────────
    new_energy = user["energy"] - energy_cost
    new_bal    = user["balance"] + coins
    new_xp     = user["xp"] + xp_gain
    new_level  = user["level"]
    leveled_up = False

    while new_level < MAX_LEVEL and new_xp >= xp_for_level(new_level):
        new_xp    -= xp_for_level(new_level)
        new_level += 1
        leveled_up = True

    await update_user(
        user_id,
        energy=new_energy, balance=new_bal,
        xp=new_xp, level=new_level,
        last_energy_regen=datetime.now().isoformat()
    )
    await log_mine(user_id, tool_id, tool["name"], zone_id,
                   ore_id, ore["name"], coins, xp_gain,
                   is_crit, is_lucky, special_hit)

    # ── Check achievements ────────────────────────────────────
    new_achievements = await check_achievements(user_id)

    return {
        "ok":           True,
        "tool":         tool,
        "tool_id":      tool_id,
        "zone":         zone,
        "ore_id":       ore_id,
        "ore":          ore,
        "coins":        coins,
        "xp_gain":      xp_gain,
        "is_crit":      is_crit,
        "is_lucky":     is_lucky,
        "special_hit":  special_hit,
        "new_energy":   new_energy,
        "max_energy":   user["max_energy"],
        "new_balance":  new_bal,
        "new_level":    new_level,
        "leveled_up":   leveled_up,
        "new_achievements": new_achievements,
    }


def build_mine_result_text(r: dict) -> str:
    """Build a nicely formatted mining result message."""
    tool  = r["tool"]
    ore   = r["ore"]
    zone  = r["zone"]

    # Status badges
    badges = []
    if r["is_crit"]:    badges.append("💥 CRITICAL!")
    if r["is_lucky"]:   badges.append("🍀 LUCKY!")
    if r["special_hit"]:badges.append(r["special_hit"])
    badge_line = "  ".join(badges)

    energy_bar = make_bar(r["new_energy"], r["max_energy"], 8)

    lines = [
        f"⛏️ *HASIL MINING*",
        f"━━━━━━━━━━━━━━━━━━━━━━",
        f"",
        f"📍 Zona  : {zone['name']}",
        f"🔧 Alat  : {tool['emoji']} *{tool['name']}*",
        f"   ├ Power     : `+{tool['power']}` base",
        f"   ├ Speed     : `{tool['speed_mult']}x`",
        f"   └ Energy    : `-{tool['energy_cost']}`",
        f"",
        f"🪨 Bijih : {ore['emoji']} *{ore['name']}*",
        f"   └ Nilai dasar: `{ore['value']}` koin",
        f"",
    ]

    if badge_line:
        lines.append(f"✨ *{badge_line}*")
        lines.append("")

    lines += [
        f"╔════════════════════╗",
        f"  💰  +*{r['coins']:,}* koin",
        f"  ⭐  +*{r['xp_gain']:,}* XP",
        f"╚════════════════════╝",
        f"",
        f"⚡ Energy : {energy_bar} `{r['new_energy']}/{r['max_energy']}`",
        f"💰 Saldo  : `{r['new_balance']:,}` koin",
    ]

    if r["leveled_up"]:
        lines.append(f"")
        lines.append(f"🎉 *LEVEL UP! ➜ Level {r['new_level']}!*")

    if r["new_achievements"]:
        lines.append(f"")
        for ach in r["new_achievements"]:
            lines.append(f"🏅 *Prestasi baru: {ach['name']}* (+{ach['reward']:,}🪙)")

    return "\n".join(lines)


def make_bar(current: int, maximum: int, length: int = 10) -> str:
    if maximum <= 0:
        return "█" * length
    pct = min(current / maximum, 1.0)
    filled = round(pct * length)
    return "█" * filled + "░" * (length - filled)


# ══════════════════════════════════════════════════════════════
# ACHIEVEMENTS
# ══════════════════════════════════════════════════════════════
async def check_achievements(user_id: int) -> list:
    user = await get_user(user_id)
    if not user:
        return []
    achieved = user["achievements"]
    new_ones = []

    async def grant(ach_id: str):
        if ach_id not in achieved:
            ach = ACHIEVEMENTS[ach_id]
            achieved.append(ach_id)
            await add_balance(user_id, ach["reward"], f"Achievement: {ach['name']}")
            new_ones.append(ach)

    mc = user["mine_count"]
    bal = user["total_earned"]
    lv  = user["level"]

    if mc >= 1:    await grant("first_mine")
    if mc >= 10:   await grant("mine_10")
    if mc >= 100:  await grant("mine_100")
    if mc >= 1000: await grant("mine_1000")
    if bal >= 100000:   await grant("rich_100k")
    if bal >= 1000000:  await grant("rich_1m")
    if lv >= 10:   await grant("lvl_10")
    if lv >= 50:   await grant("lvl_50")

    if new_ones:
        await update_user(user_id, achievements=achieved)
    return new_ones


async def check_void_achievement(user_id: int):
    user = await get_user(user_id)
    if user and "void_shard" not in user["achievements"]:
        ach = ACHIEVEMENTS["void_shard"]
        user["achievements"].append("void_shard")
        await add_balance(user_id, ach["reward"], f"Achievement: {ach['name']}")
        await update_user(user_id, achievements=user["achievements"])


# ══════════════════════════════════════════════════════════════
# SHOP: BUY TOOL
# ══════════════════════════════════════════════════════════════
async def buy_tool(user_id: int, tool_id: str,
                   admin: bool = False) -> Tuple[bool, str]:
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."
    tool = TOOLS.get(tool_id)
    if not tool:
        return False, "❌ Alat tidak ditemukan."
    if tool_id in user["owned_tools"]:
        return False, f"❌ Kamu sudah punya *{tool['name']}*!"
    if not admin and user["level"] < tool["level_req"]:
        return False, f"❌ Butuh Level *{tool['level_req']}*! (Kamu Level {user['level']})"
    if not admin and user["balance"] < tool["price"]:
        return False, (f"❌ Koin tidak cukup!\n"
                       f"Butuh: `{tool['price']:,}`\n"
                       f"Punya: `{user['balance']:,}`")
    new_owned = user["owned_tools"] + [tool_id]
    updates = dict(owned_tools=new_owned, current_tool=tool_id)
    if not admin:
        updates["balance"] = user["balance"] - tool["price"]
    await update_user(user_id, **updates)
    return True, (
        f"✅ *{tool['name']}* berhasil dibeli!\n"
        f"⚒️ Alat otomatis dipasang.\n"
        f"💰 Sisa saldo: `{updates.get('balance', user['balance']):,}` koin"
    )


async def equip_tool(user_id: int, tool_id: str) -> Tuple[bool, str]:
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."
    if tool_id not in user["owned_tools"]:
        return False, "❌ Kamu tidak punya alat ini."
    tool = TOOLS[tool_id]
    await update_user(user_id, current_tool=tool_id)
    return True, f"✅ *{tool['name']}* dipasang!"


# ══════════════════════════════════════════════════════════════
# SHOP: BUY ITEM
# ══════════════════════════════════════════════════════════════
async def buy_item(user_id: int, item_id: str,
                   admin: bool = False) -> Tuple[bool, str]:
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."
    item = ITEMS.get(item_id)
    if not item:
        return False, "❌ Item tidak ditemukan."
    if not admin and user["balance"] < item["price"]:
        return False, f"❌ Koin tidak cukup! Butuh `{item['price']:,}`"
    inv = user["inventory"]
    inv[item_id] = inv.get(item_id, 0) + 1
    updates = {"inventory": inv}
    if not admin:
        updates["balance"] = user["balance"] - item["price"]
    await update_user(user_id, **updates)
    return True, (
        f"✅ *{item['name']}* dibeli!\n"
        f"📦 Cek /inventory untuk menggunakannya."
    )


async def use_item(user_id: int, item_id: str) -> Tuple[bool, str]:
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."
    item = ITEMS.get(item_id)
    if not item:
        return False, "❌ Item tidak ditemukan."
    inv = user["inventory"]
    if inv.get(item_id, 0) <= 0:
        return False, "❌ Item ini tidak ada di inventarismu."

    inv[item_id] -= 1
    if inv[item_id] <= 0:
        del inv[item_id]

    updates = {"inventory": inv}
    effect = item["effect"]
    msg_lines = [f"✅ *{item['name']}* digunakan!"]

    if "energy" in effect:
        new_e = min(user["energy"] + effect["energy"], user["max_energy"])
        updates["energy"] = new_e
        msg_lines.append(f"⚡ Energy: `{user['energy']} → {new_e}/{user['max_energy']}`")

    elif "mystery" in effect:
        reward = _mystery_box_reward()
        if reward["type"] == "coins":
            await add_balance(user_id, reward["amount"], "Mystery Box")
            msg_lines.append(f"📦 Mystery Box berisi: 💰 *+{reward['amount']:,} koin!*")
        elif reward["type"] == "item":
            inv2 = user["inventory"]
            inv2[reward["item_id"]] = inv2.get(reward["item_id"], 0) + 1
            updates["inventory"] = inv2
            msg_lines.append(f"📦 Mystery Box berisi: 🎁 *{ITEMS[reward['item_id']]['name']}!*")

    elif "luck_buff" in effect or "coin_mult" in effect or "xp_mult" in effect:
        buffs = get_active_buffs(user)
        now = datetime.now()
        dur = effect.get("duration", 20)
        exp = (now + timedelta(minutes=dur)).isoformat()
        if "luck_buff" in effect:
            buffs["luck_buff"] = {"value": effect["luck_buff"], "expires": exp}
            msg_lines.append(f"🍀 Luck +{int(effect['luck_buff']*100)}% selama {dur} menit!")
        if "coin_mult" in effect:
            buffs["coin_mult"] = {"value": effect["coin_mult"], "expires": exp}
            msg_lines.append(f"💰 {effect['coin_mult']}x koin selama {dur} menit!")
        if "xp_mult" in effect:
            buffs["xp_mult"] = {"value": effect["xp_mult"], "expires": exp}
            msg_lines.append(f"⭐ {effect['xp_mult']}x XP selama {dur} menit!")
        updates["active_buffs"] = buffs

    elif "rebirth" in effect:
        perm = user.get("perm_coin_mult", 1.0) + 0.50
        updates.update({
            "level": 1, "xp": 0, "rebirth_count": user.get("rebirth_count", 0) + 1,
            "perm_coin_mult": perm,
            "owned_tools": ["stone_pick"], "current_tool": "stone_pick",
        })
        msg_lines.append(f"🔄 *REBIRTH!* Level direset. Permanent coin bonus: `{perm:.1f}x`")

    await update_user(user_id, **updates)
    return True, "\n".join(msg_lines)


def _mystery_box_reward() -> dict:
    roll = random.random()
    if roll < 0.60:
        amount = random.randint(500, 5000)
        return {"type": "coins", "amount": amount}
    elif roll < 0.90:
        items_list = ["energy_potion", "luck_elixir", "double_coin", "xp_boost"]
        return {"type": "item", "item_id": random.choice(items_list)}
    else:
        amount = random.randint(10000, 100000)
        return {"type": "coins", "amount": amount}


# ══════════════════════════════════════════════════════════════
# ZONE UNLOCK
# ══════════════════════════════════════════════════════════════
async def unlock_zone(user_id: int, zone_id: str,
                      admin: bool = False) -> Tuple[bool, str]:
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."
    zone = ZONES.get(zone_id)
    if not zone:
        return False, "❌ Zona tidak ditemukan."
    if zone_id in user["unlocked_zones"]:
        return False, "❌ Zona sudah dibuka!"
    if not admin and user["level"] < zone["level_req"]:
        return False, f"❌ Butuh Level *{zone['level_req']}*!"
    if not admin and user["balance"] < zone["unlock_cost"]:
        return False, f"❌ Koin tidak cukup! Butuh `{zone['unlock_cost']:,}`"
    new_zones = user["unlocked_zones"] + [zone_id]
    updates = {"unlocked_zones": new_zones, "current_zone": zone_id}
    if not admin:
        updates["balance"] = user["balance"] - zone["unlock_cost"]
    await update_user(user_id, **updates)
    return True, f"✅ *{zone['name']}* terbuka! Zona aktif diganti."


async def set_zone(user_id: int, zone_id: str) -> Tuple[bool, str]:
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."
    if zone_id not in user["unlocked_zones"]:
        return False, "❌ Zona belum dibuka."
    zone = ZONES[zone_id]
    await update_user(user_id, current_zone=zone_id)
    return True, f"✅ Zona aktif: *{zone['name']}*"


# ══════════════════════════════════════════════════════════════
# DAILY BONUS
# ══════════════════════════════════════════════════════════════
async def claim_daily(user_id: int) -> Tuple[bool, str]:
    from config import DAILY_BONUS_BASE, DAILY_BONUS_LEVEL
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."
    now = datetime.now()
    last = user.get("last_daily")
    streak = user.get("daily_streak", 0)

    if last:
        try:
            last_dt = datetime.fromisoformat(last)
            diff = now - last_dt
            if diff.total_seconds() < 86400:
                rem = timedelta(seconds=86400) - diff
                h, s = divmod(int(rem.total_seconds()), 3600)
                m = s // 60
                return False, (
                    f"⏰ *Daily bonus belum bisa diklaim!*\n\n"
                    f"Tunggu lagi: *{h}j {m}m*\n"
                    f"🔥 Streak sekarang: `{streak}` hari"
                )
            if diff.total_seconds() < 172800:
                streak += 1
            else:
                streak = 1
        except Exception:
            streak = 1
    else:
        streak = 1

    bonus = DAILY_BONUS_BASE + (user["level"] * DAILY_BONUS_LEVEL)
    streak_mult = 1.0 + (min(streak, 30) * 0.05)
    bonus = int(bonus * streak_mult)

    await add_balance(user_id, bonus, "Daily Bonus")
    await update_user(user_id,
                      energy=user["max_energy"],
                      daily_streak=streak,
                      last_daily=now.isoformat())

    # Streak achievement
    new_ach = []
    if streak >= 7:
        ach = await _grant_if_new(user_id, "daily_streak_7")
        if ach: new_ach.append(ach)
    if streak >= 30:
        ach = await _grant_if_new(user_id, "daily_streak_30")
        if ach: new_ach.append(ach)

    lines = [
        f"🎁 *Daily Bonus Diklaim!*",
        f"",
        f"💰 +*{bonus:,}* koin",
        f"⚡ Energy diisi *PENUH!*",
        f"🔥 Streak: *{streak} hari* (`{streak_mult:.1f}x` multiplier)",
    ]
    if new_ach:
        for a in new_ach:
            lines.append(f"🏅 Prestasi: *{a['name']}* (+{a['reward']:,}🪙)")
    return True, "\n".join(lines)


async def _grant_if_new(user_id: int, ach_id: str):
    from config import ACHIEVEMENTS
    user = await get_user(user_id)
    if user and ach_id not in user["achievements"]:
        ach = ACHIEVEMENTS[ach_id]
        user["achievements"].append(ach_id)
        await add_balance(user_id, ach["reward"], f"Achievement: {ach['name']}")
        await update_user(user_id, achievements=user["achievements"])
        return ach
    return None
