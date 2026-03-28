"""
Handler Statistik & Export.
"""

import csv
import io
from telegram import Update
from telegram.ext import ContextTypes
import database as db
from utils.decorators import admin_only


@admin_only
async def show_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    stats    = db.get_user_count()
    history  = db.get_broadcast_history(limit=5)

    teks = (
        "📊 *Statistik Bot*\n\n"
        f"👥 Total pengguna : `{stats['total']}`\n"
        f"✅ Aktif          : `{stats['total'] - stats['blocked']}`\n"
        f"🚫 Diblokir       : `{stats['blocked']}`\n\n"
        "📢 *5 Broadcast Terakhir*\n"
    )

    if history:
        for h in history:
            teks += (
                f"\n• `{h['dibuat_at'][:16]}`\n"
                f"  Tipe: {h['tipe']} | ✅{h['dikirim']} ❌{h['gagal']}\n"
            )
    else:
        teks += "_Belum ada broadcast_"

    await update.message.reply_text(teks, parse_mode="Markdown")


@admin_only
async def export_users(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    users = db.export_users_csv()

    if not users:
        await update.message.reply_text("📭 Belum ada data pengguna.")
        return

    # Buat file CSV di memori
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=users[0].keys())
    writer.writeheader()
    writer.writerows(users)
    output.seek(0)

    await update.message.reply_document(
        document=output.read().encode("utf-8"),
        filename="users_export.csv",
        caption=f"📊 Export {len(users)} pengguna"
    )
