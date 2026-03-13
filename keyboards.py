"""
⌨️ Keyboards — Semua tombol inline & reply keyboard
"""
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from config import TOOLS, ITEMS, ZONES, TIER_COLORS


# ══════════════════════════════════════════════════════════════
# MAIN MENU
# ══════════════════════════════════════════════════════════════
def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⛏️ Mining"),    KeyboardButton(text="👤 Profil")],
            [KeyboardButton(text="🎒 Equipment"), KeyboardButton(text="🎁 Inventaris")],
            [KeyboardButton(text="🏪 Shop"),      KeyboardButton(text="🏆 Leaderboard")],
            [KeyboardButton(text="🎁 Daily"),     KeyboardButton(text="❓ Bantuan")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Pilih menu..."
    )


def back_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Menu Utama", callback_data="main_menu")]
    ])


# ══════════════════════════════════════════════════════════════
# MINING
# ══════════════════════════════════════════════════════════════
def mine_action_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⛏️ Mine!", callback_data="do_mine"),
            InlineKeyboardButton(text="⛏️x5 Mine!", callback_data="do_mine_5"),
        ],
        [InlineKeyboardButton(text="⛏️x10 Mine!", callback_data="do_mine_10")],
        [
            InlineKeyboardButton(text="📍 Ganti Zona", callback_data="zone_menu"),
            InlineKeyboardButton(text="🔧 Ganti Alat",  callback_data="equip_menu"),
        ],
        [InlineKeyboardButton(text="🏠 Menu Utama", callback_data="main_menu")],
    ])


# ══════════════════════════════════════════════════════════════
# SHOP
# ══════════════════════════════════════════════════════════════
def shop_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⛏️ Alat Mining",     callback_data="shop_tools_0")],
        [InlineKeyboardButton(text="🎒 Item & Consumable", callback_data="shop_items")],
        [InlineKeyboardButton(text="🌍 Buka Zona Baru",  callback_data="shop_zones")],
        [InlineKeyboardButton(text="🏠 Menu Utama",      callback_data="main_menu")],
    ])


def shop_tools_kb(owned: list, level: int, balance: int, page: int = 0) -> InlineKeyboardMarkup:
    all_tools = list(TOOLS.items())
    per_page  = 4
    start     = page * per_page
    chunk     = all_tools[start: start + per_page]
    rows      = []

    for tid, t in chunk:
        tier_icon = TIER_COLORS.get(t["tier"], "⬜")
        if tid in owned:
            label = f"✅ {t['emoji']} {t['name']}"
        elif level < t["level_req"]:
            label = f"🔒 {tier_icon} {t['name']} (Lv.{t['level_req']})"
        elif balance < t["price"]:
            label = f"💸 {tier_icon} {t['name']} ({t['price']:,}🪙)"
        else:
            label = f"🛒 {tier_icon} {t['name']} ({t['price']:,}🪙)"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"tool_detail_{tid}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️ Prev", callback_data=f"shop_tools_{page-1}"))
    if start + per_page < len(all_tools):
        nav.append(InlineKeyboardButton(text="Next ▶️", callback_data=f"shop_tools_{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(text="🔙 Shop Menu", callback_data="shop_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def tool_detail_kb(tool_id: str, owned: bool, is_current: bool) -> InlineKeyboardMarkup:
    rows = []
    if owned:
        if not is_current:
            rows.append([InlineKeyboardButton(text="⚒️ Pasang Alat Ini", callback_data=f"equip_{tool_id}")])
        else:
            rows.append([InlineKeyboardButton(text="✅ Sedang Dipakai", callback_data="noop")])
    else:
        rows.append([InlineKeyboardButton(text="🛒 Beli Sekarang", callback_data=f"buy_tool_{tool_id}")])
    rows.append([InlineKeyboardButton(text="🔙 Daftar Alat", callback_data="shop_tools_0")])
    rows.append([InlineKeyboardButton(text="🏠 Menu Utama",  callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def shop_items_kb() -> InlineKeyboardMarkup:
    rows = []
    for iid, item in ITEMS.items():
        rows.append([InlineKeyboardButton(
            text=f"{item['emoji']} {item['name']} — {item['price']:,}🪙",
            callback_data=f"item_detail_{iid}"
        )])
    rows.append([InlineKeyboardButton(text="🔙 Shop Menu", callback_data="shop_menu")])
    rows.append([InlineKeyboardButton(text="🏠 Menu Utama", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def item_detail_kb(item_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Beli Item Ini", callback_data=f"buy_item_{item_id}")],
        [InlineKeyboardButton(text="🔙 Daftar Item",   callback_data="shop_items")],
        [InlineKeyboardButton(text="🏠 Menu Utama",    callback_data="main_menu")],
    ])


def shop_zones_kb(unlocked: list, level: int, balance: int) -> InlineKeyboardMarkup:
    rows = []
    for zid, z in ZONES.items():
        if zid in unlocked:
            label = f"✅ {z['name']}"
        elif level < z["level_req"]:
            label = f"🔒 {z['name']} (Lv.{z['level_req']})"
        elif balance < z["unlock_cost"]:
            label = f"💸 {z['name']} ({z['unlock_cost']:,}🪙)"
        else:
            label = f"🔓 {z['name']} — {z['unlock_cost']:,}🪙"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"zone_detail_{zid}")])
    rows.append([InlineKeyboardButton(text="🔙 Shop Menu", callback_data="shop_menu")])
    rows.append([InlineKeyboardButton(text="🏠 Menu Utama", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def zone_detail_kb(zone_id: str, unlocked: bool, is_active: bool) -> InlineKeyboardMarkup:
    rows = []
    if unlocked:
        if not is_active:
            rows.append([InlineKeyboardButton(text="📍 Pindah ke Zona Ini", callback_data=f"set_zone_{zone_id}")])
        else:
            rows.append([InlineKeyboardButton(text="✅ Zona Aktif", callback_data="noop")])
    else:
        rows.append([InlineKeyboardButton(text="🔓 Buka Zona Ini", callback_data=f"unlock_zone_{zone_id}")])
    rows.append([InlineKeyboardButton(text="🔙 Daftar Zona",  callback_data="shop_zones")])
    rows.append([InlineKeyboardButton(text="🏠 Menu Utama",   callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ══════════════════════════════════════════════════════════════
# EQUIPMENT
# ══════════════════════════════════════════════════════════════
def equipment_kb(owned: list, current: str) -> InlineKeyboardMarkup:
    rows = []
    for tid in owned:
        t = TOOLS.get(tid)
        if not t:
            continue
        prefix = "✅ " if tid == current else "   "
        label = f"{prefix}{t['emoji']} {t['name']} (Tier {t['tier']})"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"tool_detail_{tid}")])
    rows.append([InlineKeyboardButton(text="🏪 Beli Alat Baru", callback_data="shop_tools_0")])
    rows.append([InlineKeyboardButton(text="🏠 Menu Utama",     callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def equip_menu_kb(owned: list, current: str) -> InlineKeyboardMarkup:
    rows = []
    for tid in owned:
        t = TOOLS.get(tid)
        if not t:
            continue
        label = f"{'✅' if tid == current else '⚒️'} {t['emoji']} {t['name']}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"equip_{tid}")])
    rows.append([InlineKeyboardButton(text="🔙 Kembali", callback_data="mine_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def zone_menu_kb(unlocked: list, current: str) -> InlineKeyboardMarkup:
    rows = []
    for zid in unlocked:
        z = ZONES.get(zid)
        if not z:
            continue
        label = f"{'📍' if zid == current else '  '} {z['name']}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"set_zone_{zid}")])
    rows.append([InlineKeyboardButton(text="🔓 Buka Zona Baru", callback_data="shop_zones")])
    rows.append([InlineKeyboardButton(text="🔙 Kembali",        callback_data="mine_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ══════════════════════════════════════════════════════════════
# INVENTORY
# ══════════════════════════════════════════════════════════════
def inventory_kb(inventory: dict) -> InlineKeyboardMarkup:
    rows = []
    for item_id, qty in inventory.items():
        item = ITEMS.get(item_id)
        if not item or qty <= 0:
            continue
        rows.append([InlineKeyboardButton(
            text=f"{item['emoji']} {item['name']} x{qty} — Gunakan",
            callback_data=f"use_item_{item_id}"
        )])
    if not rows:
        rows.append([InlineKeyboardButton(text="🏪 Beli Item di Shop", callback_data="shop_items")])
    rows.append([InlineKeyboardButton(text="🏠 Menu Utama", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ══════════════════════════════════════════════════════════════
# PROFILE & LEADERBOARD
# ══════════════════════════════════════════════════════════════
def profile_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Statistik Mining", callback_data="mine_stats"),
            InlineKeyboardButton(text="🏅 Prestasi",         callback_data="achievements"),
        ],
        [InlineKeyboardButton(text="🏠 Menu Utama", callback_data="main_menu")],
    ])


def leaderboard_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Refresh", callback_data="lb_refresh")],
        [InlineKeyboardButton(text="🏠 Menu Utama", callback_data="main_menu")],
    ])


# ══════════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════════
def admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistik Bot", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Daftar User",   callback_data="admin_users")],
        [InlineKeyboardButton(text="🏠 Menu Utama",    callback_data="main_menu")],
    ])
