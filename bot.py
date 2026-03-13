#!/usr/bin/env python3
"""
╔══════════════════════════════════════╗
║   ⛏️  TELEGRAM MINING BOT  ⛏️        ║
║   Ready for Railway Deployment       ║
╚══════════════════════════════════════╝
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN, ADMIN_IDS
from database import init_db
from handlers.start import router as start_router
from handlers.mining import router as mining_router
from handlers.shop import router as shop_router
from handlers.equipment import router as equipment_router
from handlers.inventory import router as inventory_router
from handlers.profile import router as profile_router
from handlers.leaderboard import router as leaderboard_router
from handlers.admin import router as admin_router
from handlers.daily import router as daily_router
from handlers.help import router as help_router
from middlewares import ThrottlingMiddleware, RegisterMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start",       description="🏠 Menu Utama"),
        BotCommand(command="mine",        description="⛏️ Mining Sekarang"),
        BotCommand(command="profile",     description="👤 Lihat Profil"),
        BotCommand(command="shop",        description="🏪 Toko Peralatan"),
        BotCommand(command="equipment",   description="🎒 Peralatan Aktif"),
        BotCommand(command="inventory",   description="🎁 Inventaris Item"),
        BotCommand(command="daily",       description="🎁 Klaim Bonus Harian"),
        BotCommand(command="leaderboard", description="🏆 Papan Peringkat"),
        BotCommand(command="help",        description="❓ Bantuan"),
        BotCommand(command="adminhelp",   description="🔐 Bantuan Admin"),
    ]
    await bot.set_my_commands(commands)


async def main():
    logger.info("=" * 50)
    logger.info("⛏️  MINING BOT STARTING...")
    logger.info("=" * 50)

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ BOT_TOKEN not set! Check your environment variables.")
        return

    await init_db()
    logger.info("✅ Database initialized")

    # ── aiogram 3.7+ compatible: DefaultBotProperties for parse_mode ──
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Middlewares
    dp.message.middleware(ThrottlingMiddleware(limit=0.8))
    dp.message.middleware(RegisterMiddleware())
    dp.callback_query.middleware(RegisterMiddleware())

    # Routers
    dp.include_router(start_router)
    dp.include_router(mining_router)
    dp.include_router(shop_router)
    dp.include_router(equipment_router)
    dp.include_router(inventory_router)
    dp.include_router(profile_router)
    dp.include_router(leaderboard_router)
    dp.include_router(admin_router)
    dp.include_router(daily_router)
    dp.include_router(help_router)

    await set_commands(bot)
    logger.info("✅ Commands registered")
    logger.info(f"✅ Admin IDs: {ADMIN_IDS}")
    logger.info("🚀 Bot is polling...")

    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
