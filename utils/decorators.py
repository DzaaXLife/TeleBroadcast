"""
Decorator yang sering dipakai.
"""

from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import database as db


def admin_only(func):
    """Hanya izinkan admin menjalankan command ini."""
    @wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if not db.is_admin(user_id):
            await update.message.reply_text("⛔ Kamu tidak punya izin.")
            return
        return await func(update, ctx, *args, **kwargs)
    return wrapper


def owner_only(func):
    """Hanya izinkan owner (pemilik bot) menjalankan command ini."""
    @wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        from config import OWNER_ID
        if update.effective_user.id != OWNER_ID:
            await update.message.reply_text("⛔ Hanya owner yang bisa.")
            return
        return await func(update, ctx, *args, **kwargs)
    return wrapper
