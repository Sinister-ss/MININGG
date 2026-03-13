from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database import get_user
from game import buy_tool, buy_item, unlock_zone
from keyboards import (shop_main_kb, shop_tools_kb, tool_detail_kb,
                        shop_items_kb, item_detail_kb, shop_zones_kb,
                        zone_detail_kb)
from config import TOOLS, ITEMS, ZONES, TIER_COLORS, ADMIN_IDS

router = Router()


@router.message(F.text == "🏪 Shop")
@router.message(Command("shop"))
async def show_shop(message: Message):
    await message.answer(
        "🏪 *Toko Mining*\n\nPilih kategori:",
        reply_markup=shop_main_kb(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "shop_menu")
async def cb_shop_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏪 *Toko Mining*\n\nPilih kategori:",
        reply_markup=shop_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ── TOOLS ─────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("shop_tools_"))
async def cb_shop_tools(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start dulu!")
        return
    text = (
        f"⛏️ *Daftar Alat Mining*\n"
        f"Dari Starter (Gratis) hingga Mythical!\n\n"
        f"✅ = Dimiliki | 🔒 = Level kurang | 💸 = Koin kurang | 🛒 = Bisa dibeli"
    )
    await callback.message.edit_text(
        text,
        reply_markup=shop_tools_kb(user["owned_tools"], user["level"], user["balance"], page),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("tool_detail_"))
async def cb_tool_detail(callback: CallbackQuery):
    tool_id = callback.data.replace("tool_detail_", "")
    tool = TOOLS.get(tool_id)
    user = await get_user(callback.from_user.id)
    if not tool or not user:
        await callback.answer("❌ Tidak ditemukan!")
        return

    owned      = tool_id in user["owned_tools"]
    is_current = user["current_tool"] == tool_id
    tier_icon  = TIER_COLORS.get(tool["tier"], "⬜")
    price_txt  = "✨ *GRATIS*" if tool["price"] == 0 else f"`{tool['price']:,}` koin"
    special_txt = f"\n🌟 *Special:* {tool['special']}" if tool.get("special") else ""

    text = (
        f"{tool['emoji']} *{tool['name']}*\n"
        f"{tier_icon} Tier {tool['tier']} — {tool['tier_name']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 _{tool['description']}_\n"
        f"💬 _{tool['flavor']}_\n\n"
        f"📊 *Statistik:*\n"
        f"   ⚡ Power      : `+{tool['power']}` koin/mine\n"
        f"   🚀 Speed      : `{tool['speed_mult']}x` multiplier\n"
        f"   💥 Crit Bonus : `+{int(tool['crit_bonus']*100)}%`\n"
        f"   🍀 Luck Bonus : `+{int(tool['luck_bonus']*100)}%`\n"
        f"   ⚡ Energy/mine: `-{tool['energy_cost']}`\n"
        f"   📏 Level Req  : `{tool['level_req']}`\n"
        f"   💰 Harga      : {price_txt}"
        f"{special_txt}\n\n"
        f"{'✅ *Sudah dimiliki*' + (' _(Aktif)_' if is_current else '') if owned else '🛒 Belum dimiliki'}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=tool_detail_kb(tool_id, owned, is_current),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_tool_"))
async def cb_buy_tool(callback: CallbackQuery):
    tool_id = callback.data.replace("buy_tool_", "")
    is_admin = callback.from_user.id in ADMIN_IDS
    ok, msg = await buy_tool(callback.from_user.id, tool_id, admin=is_admin)
    await callback.answer(msg[:200], show_alert=True)
    if ok:
        # Refresh detail view
        user = await get_user(callback.from_user.id)
        tool = TOOLS.get(tool_id)
        owned = tool_id in user["owned_tools"]
        is_current = user["current_tool"] == tool_id
        await callback.message.edit_reply_markup(
            reply_markup=tool_detail_kb(tool_id, owned, is_current)
        )


# ── ITEMS ─────────────────────────────────────────────────────

@router.callback_query(F.data == "shop_items")
async def cb_shop_items(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎒 *Item & Consumable*\n\nBeli potion, scroll, dan item spesial!",
        reply_markup=shop_items_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("item_detail_"))
async def cb_item_detail(callback: CallbackQuery):
    item_id = callback.data.replace("item_detail_", "")
    item = ITEMS.get(item_id)
    user = await get_user(callback.from_user.id)
    if not item or not user:
        await callback.answer("❌ Tidak ditemukan!")
        return

    qty = user["inventory"].get(item_id, 0)
    text = (
        f"{item['emoji']} *{item['name']}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 {item['description']}\n\n"
        f"💰 Harga   : `{item['price']:,}` koin\n"
        f"📦 Dimiliki: `{qty}` buah\n"
        f"♻️ Stackable: {'Ya' if item['stackable'] else 'Tidak'}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=item_detail_kb(item_id),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_item_"))
async def cb_buy_item(callback: CallbackQuery):
    item_id = callback.data.replace("buy_item_", "")
    is_admin = callback.from_user.id in ADMIN_IDS
    ok, msg = await buy_item(callback.from_user.id, item_id, admin=is_admin)
    await callback.answer(msg[:200], show_alert=True)


# ── ZONES ─────────────────────────────────────────────────────

@router.callback_query(F.data == "shop_zones")
async def cb_shop_zones(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return
    await callback.message.edit_text(
        "🌍 *Buka Zona Mining Baru*\n\nZona berbeda memberikan ore berbeda dan lebih berharga!",
        reply_markup=shop_zones_kb(user["unlocked_zones"], user["level"], user["balance"]),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("zone_detail_"))
async def cb_zone_detail(callback: CallbackQuery):
    zone_id = callback.data.replace("zone_detail_", "")
    zone = ZONES.get(zone_id)
    user = await get_user(callback.from_user.id)
    if not zone or not user:
        await callback.answer("❌ Tidak ditemukan!")
        return

    unlocked  = zone_id in user["unlocked_zones"]
    is_active = user.get("current_zone") == zone_id
    bonus_txt = ""
    if zone["ore_bonus"]:
        from config import ORES
        for oid, mult in zone["ore_bonus"].items():
            ore = ORES.get(oid, {})
            bonus_txt += f"\n   {ore.get('emoji','')} {ore.get('name', oid)}: `{mult}x`"

    cost_txt = "✨ *Gratis*" if zone["unlock_cost"] == 0 else f"`{zone['unlock_cost']:,}` koin"
    text = (
        f"{zone['name']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 {zone['desc']}\n\n"
        f"🔓 Level Req : `{zone['level_req']}`\n"
        f"💰 Biaya     : {cost_txt}\n"
        f"📊 Ore Bonus :{bonus_txt if bonus_txt else ' Tidak ada'}\n\n"
        f"{'✅ *Sudah terbuka*' + (' _(Aktif)_' if is_active else '') if unlocked else '🔒 Belum dibuka'}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=zone_detail_kb(zone_id, unlocked, is_active),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("unlock_zone_"))
async def cb_unlock_zone(callback: CallbackQuery):
    zone_id = callback.data.replace("unlock_zone_", "")
    is_admin = callback.from_user.id in ADMIN_IDS
    ok, msg = await unlock_zone(callback.from_user.id, zone_id, admin=is_admin)
    await callback.answer(msg[:200], show_alert=True)
    if ok:
        user = await get_user(callback.from_user.id)
        zone = ZONES.get(zone_id, {})
        unlocked  = zone_id in user["unlocked_zones"]
        is_active = user.get("current_zone") == zone_id
        await callback.message.edit_reply_markup(
            reply_markup=zone_detail_kb(zone_id, unlocked, is_active)
        )
