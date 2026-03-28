"""
Handler untuk pengguna biasa:
/start, /help, /info, dan pelacak user.
"""

from telegram import Update
from telegram.ext import ContextTypes
from config import WELCOME_TEXT, HELP_TEXT, BOT_NAME, BOT_VERSION
import database as db


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.upsert_user(user.id, user.username, user.full_name)

    teks = WELCOME_TEXT.format(nama=user.first_name)
    await update.message.reply_text(teks, parse_mode="Markdown")


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


async def info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    stats = db.get_user_count()
    teks = (
        f"🤖 *{BOT_NAME}* v{BOT_VERSION}\n\n"
        f"👥 Total pengguna : `{stats['total']}`\n"
        f"🚫 Diblokir       : `{stats['blocked']}`\n"
        f"✅ Aktif          : `{stats['total'] - stats['blocked']}`"
    )
    await update.message.reply_text(teks, parse_mode="Markdown")


async def track(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Lacak semua pesan — simpan/perbarui data user."""
    user = update.effective_user
    if user:
        db.upsert_user(user.id, user.username, user.full_name)
