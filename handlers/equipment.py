from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database import get_user
from keyboards import equipment_kb
from config import TOOLS, ZONES

router = Router()


@router.message(F.text == "🎒 Equipment")
@router.message(Command("equipment"))
async def show_equipment(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Ketik /start untuk mendaftar!")
        return

    tool = TOOLS.get(user["current_tool"], TOOLS["stone_pick"])
    zone = ZONES.get(user.get("current_zone", "surface"), ZONES["surface"])

    # Owned tools list
    tools_txt = ""
    for i, tid in enumerate(user["owned_tools"], 1):
        t = TOOLS.get(tid)
        if t:
            active = " ← *AKTIF*" if tid == user["current_tool"] else ""
            tools_txt += f"{i}. {t['emoji']} *{t['name']}* (Tier {t['tier']}){active}\n"

    text = (
        f"🎒 *Peralatan Kamu*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚒️ *Alat Aktif:*\n"
        f"   {tool['emoji']} *{tool['name']}*\n"
        f"   ├ Tier     : {tool['tier']} ({tool['tier_name']})\n"
        f"   ├ Power    : `+{tool['power']}` koin/mine\n"
        f"   ├ Speed    : `{tool['speed_mult']}x`\n"
        f"   ├ Crit     : `+{int(tool['crit_bonus']*100)}%`\n"
        f"   ├ Luck     : `+{int(tool['luck_bonus']*100)}%`\n"
        f"   ├ Energy   : `-{tool['energy_cost']}`/mine\n"
        f"   └ Special  : {tool.get('special') or 'Tidak ada'}\n\n"
        f"📍 *Zona Aktif:* {zone['name']}\n\n"
        f"🛠️ *Alat yang Dimiliki ({len(user['owned_tools'])} buah):*\n"
        f"{tools_txt}\n"
        f"Tekan alat untuk ganti:"
    )
    await message.answer(text, reply_markup=equipment_kb(user["owned_tools"], user["current_tool"]),
                         parse_mode="Markdown")
