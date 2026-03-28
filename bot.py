"""
╔══════════════════════════════════════╗
║        TELEGRAM BOT - UTAMA          ║
║  broadcast | promosi | manajemen     ║
╚══════════════════════════════════════╝

Cara pakai:
1. Isi config di file config.py
2. Jalankan: python bot.py
"""

import logging
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ConversationHandler
)

from config import BOT_TOKEN
from handlers import admin, broadcast, promo, user, stats

# ── Logging ──────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Titik masuk utama bot."""
    app = Application.builder().token(BOT_TOKEN).build()

    # ── Command Handler ───────────────────────────────────
    app.add_handler(CommandHandler("start",     user.start))
    app.add_handler(CommandHandler("help",      user.help_cmd))
    app.add_handler(CommandHandler("info",      user.info))

    # Admin
    app.add_handler(CommandHandler("admin",     admin.panel))
    app.add_handler(CommandHandler("addadmin",  admin.add_admin))
    app.add_handler(CommandHandler("deladmin",  admin.del_admin))
    app.add_handler(CommandHandler("listadmin", admin.list_admin))

    # Broadcast
    app.add_handler(broadcast.conv_handler())

    # Promosi
    app.add_handler(promo.conv_handler())

    # Statistik
    app.add_handler(CommandHandler("stats",     stats.show_stats))
    app.add_handler(CommandHandler("export",    stats.export_users))

    # ── Callback Query (tombol inline) ────────────────────
    app.add_handler(CallbackQueryHandler(admin.handle_callback,     pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(broadcast.handle_callback, pattern="^bc_"))
    app.add_handler(CallbackQueryHandler(promo.handle_callback,     pattern="^promo_"))

    # ── Lacak semua pesan (simpan user baru) ─────────────
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, user.track))

    logger.info("Bot berjalan... tekan Ctrl+C untuk berhenti.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
