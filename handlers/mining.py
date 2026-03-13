from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database import get_user
from game import perform_mine, build_mine_result_text, regen_energy, energy_full_in, equip_tool, set_zone
from keyboards import mine_action_kb, equip_menu_kb, zone_menu_kb, main_menu_kb
from config import TOOLS, ZONES

router = Router()


async def _mine_panel(user_id: int) -> str:
    user = await get_user(user_id)
    if not user:
        return "❌ Ketik /start"
    user = await regen_energy(user)
    tool = TOOLS.get(user["current_tool"], TOOLS["stone_pick"])
    zone = ZONES.get(user.get("current_zone", "surface"), ZONES["surface"])
    return (
        f"⛏️ *Panel Mining*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔧 *Alat Aktif:*\n"
        f"   {tool['emoji']} *{tool['name']}* (Tier {tool['tier']} — {tool['tier_name']})\n"
        f"   ├ ⚡ Power    : `+{tool['power']}` koin base\n"
        f"   ├ 🚀 Speed    : `{tool['speed_mult']}x`\n"
        f"   ├ 💥 Crit     : `{int(tool['crit_bonus']*100)}%` bonus\n"
        f"   ├ 🍀 Luck     : `{int(tool['luck_bonus']*100)}%` bonus\n"
        f"   └ ⚡ Biaya    : `-{tool['energy_cost']}` energy\n\n"
        f"📍 *Zona:* {zone['name']}\n"
        f"   └ {zone['desc']}\n\n"
        f"⚡ Energy: `{user['energy']}/{user['max_energy']}` "
        f"(penuh dalam *{energy_full_in(user)}*)\n"
        f"💰 Saldo : `{user['balance']:,}` koin\n\n"
        f"Pilih aksi mining:"
    )


@router.message(F.text == "⛏️ Mining")
@router.message(Command("mine"))
async def show_mine(message: Message):
    text = await _mine_panel(message.from_user.id)
    await message.answer(text, reply_markup=mine_action_kb(), parse_mode="Markdown")


@router.callback_query(F.data == "mine_menu")
async def cb_mine_menu(callback: CallbackQuery):
    text = await _mine_panel(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=mine_action_kb(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "do_mine")
async def cb_do_mine(callback: CallbackQuery):
    result = await perform_mine(callback.from_user.id)
    if result["ok"]:
        text = build_mine_result_text(result)
        kb = mine_action_kb()
    else:
        text = result["msg"]
        kb = mine_action_kb()
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "do_mine_5")
async def cb_do_mine_5(callback: CallbackQuery):
    await callback.answer("⛏️ Mining 5x...")
    total_coins = 0
    total_xp    = 0
    ores_found  = {}
    specials    = []
    crits = luckies = 0
    level_ups = 0
    new_ach = []

    for _ in range(5):
        r = await perform_mine(callback.from_user.id)
        if not r["ok"]:
            break
        total_coins += r["coins"]
        total_xp    += r["xp_gain"]
        ore_name = r["ore"]["name"]
        ores_found[ore_name] = ores_found.get(ore_name, 0) + 1
        if r["is_crit"]:   crits += 1
        if r["is_lucky"]:  luckies += 1
        if r["special_hit"]: specials.append(r["special_hit"])
        if r["leveled_up"]: level_ups += 1
        new_ach.extend(r.get("new_achievements", []))

    ore_lines = "\n".join(f"   {k}: x{v}" for k, v in ores_found.items())
    special_txt = ("\n🌟 Special: " + ", ".join(set(specials))) if specials else ""
    lvl_txt = f"\n🎉 *Level UP x{level_ups}!*" if level_ups else ""
    ach_txt = ""
    for a in new_ach:
        ach_txt += f"\n🏅 Prestasi: *{a['name']}*"

    user = await get_user(callback.from_user.id)
    text = (
        f"⛏️ *Mining x5 Selesai!*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🪨 Bijih ditemukan:\n{ore_lines}\n\n"
        f"💰 Total Koin : `+{total_coins:,}`\n"
        f"⭐ Total XP   : `+{total_xp:,}`\n"
        f"💥 Critical   : {crits}x\n"
        f"🍀 Lucky      : {luckies}x"
        f"{special_txt}{lvl_txt}{ach_txt}\n\n"
        f"💰 Saldo: `{user['balance']:,}` koin"
    )
    await callback.message.edit_text(text, reply_markup=mine_action_kb(), parse_mode="Markdown")


@router.callback_query(F.data == "do_mine_10")
async def cb_do_mine_10(callback: CallbackQuery):
    await callback.answer("⛏️ Mining 10x...")
    total_coins = 0
    total_xp    = 0
    ores_found  = {}
    specials    = []
    crits = luckies = lvl_ups = 0
    new_ach = []

    for _ in range(10):
        r = await perform_mine(callback.from_user.id)
        if not r["ok"]:
            break
        total_coins += r["coins"]
        total_xp    += r["xp_gain"]
        ore_name = r["ore"]["name"]
        ores_found[ore_name] = ores_found.get(ore_name, 0) + 1
        if r["is_crit"]:  crits += 1
        if r["is_lucky"]: luckies += 1
        if r["special_hit"]: specials.append(r["special_hit"])
        if r["leveled_up"]: lvl_ups += 1
        new_ach.extend(r.get("new_achievements", []))

    ore_lines = "\n".join(f"   {k}: x{v}" for k, v in ores_found.items())
    user = await get_user(callback.from_user.id)
    text = (
        f"⛏️ *Mining x10 Selesai!*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🪨 Bijih ditemukan:\n{ore_lines}\n\n"
        f"💰 Total Koin : `+{total_coins:,}`\n"
        f"⭐ Total XP   : `+{total_xp:,}`\n"
        f"💥 Critical   : {crits}x\n"
        f"🍀 Lucky      : {luckies}x"
        + (f"\n🌟 Special: {', '.join(set(specials))}" if specials else "")
        + (f"\n🎉 Level UP x{lvl_ups}!" if lvl_ups else "")
        + "".join(f"\n🏅 Prestasi: *{a['name']}*" for a in new_ach)
        + f"\n\n💰 Saldo: `{user['balance']:,}` koin"
    )
    await callback.message.edit_text(text, reply_markup=mine_action_kb(), parse_mode="Markdown")


@router.callback_query(F.data == "equip_menu")
async def cb_equip_menu(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Ketik /start")
        return
    await callback.message.edit_text(
        "⚒️ *Pilih Alat untuk Dipakai:*",
        reply_markup=equip_menu_kb(user["owned_tools"], user["current_tool"]),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("equip_"))
async def cb_equip(callback: CallbackQuery):
    tool_id = callback.data.replace("equip_", "")
    ok, msg = await equip_tool(callback.from_user.id, tool_id)
    await callback.answer(msg[:200], show_alert=not ok)
    if ok:
        user = await get_user(callback.from_user.id)
        await callback.message.edit_text(
            f"⚒️ *Ganti Alat*\n\n{msg}",
            reply_markup=equip_menu_kb(user["owned_tools"], user["current_tool"]),
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "zone_menu")
async def cb_zone_menu(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Ketik /start")
        return
    await callback.message.edit_text(
        "📍 *Pilih Zona Mining:*\n_(Zona berbeda = ore berbeda)_",
        reply_markup=zone_menu_kb(user["unlocked_zones"], user.get("current_zone", "surface")),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_zone_"))
async def cb_set_zone(callback: CallbackQuery):
    zone_id = callback.data.replace("set_zone_", "")
    ok, msg = await set_zone(callback.from_user.id, zone_id)
    await callback.answer(msg[:200], show_alert=not ok)
    if ok:
        user = await get_user(callback.from_user.id)
        await callback.message.edit_text(
            f"📍 *Zona Mining*\n\n{msg}",
            reply_markup=zone_menu_kb(user["unlocked_zones"], user.get("current_zone", "surface")),
            parse_mode="Markdown"
        )
