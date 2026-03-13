import time
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 0.8):
        self.limit = limit
        self._last: Dict[int, float] = {}

    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            uid = event.from_user.id
            now = time.time()
            if now - self._last.get(uid, 0) < self.limit:
                try:
                    await event.answer("⏳ Terlalu cepat! Tunggu sebentar.")
                except Exception:
                    pass
                return
            self._last[uid] = now
        return await handler(event, data)


class RegisterMiddleware(BaseMiddleware):
    """Auto-register user on first interaction."""
    async def __call__(self, handler, event, data):
        from database import get_user, create_user
        user_obj = None
        if isinstance(event, Message):
            user_obj = event.from_user
        elif isinstance(event, CallbackQuery):
            user_obj = event.from_user

        if user_obj:
            existing = await get_user(user_obj.id)
            if not existing:
                await create_user(
                    user_obj.id,
                    user_obj.username or "",
                    user_obj.first_name or "Miner"
                )
                logger.info(f"Auto-registered: {user_obj.id} @{user_obj.username}")

        return await handler(event, data)
