"""
Handler admin:
Panel kontrol, tambah/hapus admin, blokir user.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database as db
from config import OWNER_ID
from utils.decorators import admin_only


# ── Panel Utama ───────────────────────────────────────────

@admin_only
async def panel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    stats = db.get_user_count()
    tombol = [
        [
            InlineKeyboardButton("📢 Broadcast",   callback_data="admin_broadcast"),
            InlineKeyboardButton("🎁 Promosi",     callback_data="admin_promo"),
        ],
        [
            InlineKeyboardButton("📊 Statistik",   callback_data="admin_stats"),
            InlineKeyboardButton("👥 Admin",       callback_data="admin_listadmin"),
        ],
        [
            InlineKeyboardButton("🚫 Blokir User", callback_data="admin_block"),
            InlineKeyboardButton("✅ Unblokir",    callback_data="admin_unblock"),
        ],
    ]
    teks = (
        "🔧 *Panel Admin*\n\n"
        f"👥 Total pengguna : `{stats['total']}`\n"
        f"✅ Aktif          : `{stats['total'] - stats['blocked']}`\n"
        f"🚫 Diblokir       : `{stats['blocked']}`"
    )
    await update.message.reply_text(
        teks,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(tombol)
    )


# ── Callback ──────────────────────────────────────────────

async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "admin_stats":
        stats = db.get_user_count()
        await query.edit_message_text(
            f"📊 *Statistik*\n\n"
            f"Total    : `{stats['total']}`\n"
            f"Aktif    : `{stats['total'] - stats['blocked']}`\n"
            f"Diblokir : `{stats['blocked']}`",
            parse_mode="Markdown"
        )

    elif data == "admin_listadmin":
        admins = db.get_admins()
        if admins:
            daftar = "\n".join(f"• `{aid}`" for aid in admins)
        else:
            daftar = "_Belum ada admin tambahan_"
        await query.edit_message_text(
            f"👥 *Daftar Admin*\n\n{daftar}",
            parse_mode="Markdown"
        )

    elif data == "admin_broadcast":
        await query.edit_message_text(
            "📢 Gunakan perintah /broadcast untuk mulai broadcast."
        )

    elif data == "admin_promo":
        await query.edit_message_text(
            "🎁 Gunakan perintah /promo untuk kelola promosi."
        )

    elif data == "admin_block":
        await query.edit_message_text(
            "🚫 Kirim: `/block <user_id>` untuk memblokir pengguna.",
            parse_mode="Markdown"
        )

    elif data == "admin_unblock":
        await query.edit_message_text(
            "✅ Kirim: `/unblock <user_id>` untuk membuka blokir.",
            parse_mode="Markdown"
        )


# ── Manajemen Admin ───────────────────────────────────────

@admin_only
async def add_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("⚠️ Contoh: `/addadmin 123456789`", parse_mode="Markdown")
        return
    try:
        target_id = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID tidak valid.")
        return

    db.add_admin(target_id, added_by=update.effective_user.id)
    await update.message.reply_text(f"✅ `{target_id}` ditambahkan sebagai admin.", parse_mode="Markdown")


@admin_only
async def del_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("⚠️ Contoh: `/deladmin 123456789`", parse_mode="Markdown")
        return
    try:
        target_id = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID tidak valid.")
        return

    if target_id == OWNER_ID:
        await update.message.reply_text("❌ Owner tidak bisa dihapus.")
        return

    db.remove_admin(target_id)
    await update.message.reply_text(f"✅ `{target_id}` dihapus dari admin.", parse_mode="Markdown")


@admin_only
async def list_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    admins = db.get_admins()
    daftar = "\n".join(f"• `{aid}`" for aid in admins) if admins else "_Belum ada admin tambahan_"
    await update.message.reply_text(
        f"👥 *Daftar Admin*\n\n👑 Owner: `{OWNER_ID}`\n\n{daftar}",
        parse_mode="Markdown"
    )
