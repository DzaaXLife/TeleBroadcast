"""
Handler Promosi:
Tambah, lihat, aktif/nonaktif, hapus promosi.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler,
    CommandHandler, MessageHandler, CallbackQueryHandler, filters
)
import database as db
from utils.decorators import admin_only

# Status percakapan
JUDUL, DESKRIPSI, GAMBAR = range(3)


# ── Menu Promosi ──────────────────────────────────────────

@admin_only
async def menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    tombol = [
        [InlineKeyboardButton("➕ Tambah Promo", callback_data="promo_tambah")],
        [InlineKeyboardButton("📋 Daftar Promo", callback_data="promo_daftar")],
        [InlineKeyboardButton("📤 Broadcast Promo", callback_data="promo_broadcast_menu")],
    ]
    await update.message.reply_text(
        "🎁 *Menu Promosi*\n\nPilih aksi:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(tombol)
    )


async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ── Tambah Promo ──
    if data == "promo_tambah":
        ctx.user_data["promo_baru"] = {}
        await query.edit_message_text("✏️ Ketik *judul* promosi:", parse_mode="Markdown")
        return JUDUL

    # ── Daftar Promo ──
    elif data == "promo_daftar":
        promos = db.get_promos(aktif_only=False)
        if not promos:
            await query.edit_message_text("📭 Belum ada promosi.")
            return

        teks = "📋 *Daftar Promosi*\n\n"
        tombol = []
        for p in promos:
            status = "✅" if p["aktif"] else "⛔"
            teks += f"{status} `[{p['id']}]` *{p['judul']}*\n"
            tombol.append([
                InlineKeyboardButton(
                    f"{'Nonaktifkan' if p['aktif'] else 'Aktifkan'} [{p['id']}]",
                    callback_data=f"promo_toggle_{p['id']}"
                ),
                InlineKeyboardButton(
                    f"🗑 Hapus [{p['id']}]",
                    callback_data=f"promo_hapus_{p['id']}"
                ),
            ])
        await query.edit_message_text(
            teks, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(tombol)
        )

    # ── Toggle Aktif/Nonaktif ──
    elif data.startswith("promo_toggle_"):
        pid = int(data.replace("promo_toggle_", ""))
        db.toggle_promo(pid)
        await query.edit_message_text(f"✅ Status promo `{pid}` diubah.", parse_mode="Markdown")

    # ── Hapus Promo ──
    elif data.startswith("promo_hapus_"):
        pid = int(data.replace("promo_hapus_", ""))
        db.delete_promo(pid)
        await query.edit_message_text(f"🗑 Promo `{pid}` dihapus.", parse_mode="Markdown")

    # ── Broadcast Promo ──
    elif data == "promo_broadcast_menu":
        promos = db.get_promos(aktif_only=True)
        if not promos:
            await query.edit_message_text("📭 Tidak ada promosi aktif.")
            return
        tombol = [
            [InlineKeyboardButton(p["judul"], callback_data=f"promo_bc_{p['id']}")]
            for p in promos
        ]
        await query.edit_message_text(
            "📤 Pilih promosi untuk di-broadcast:",
            reply_markup=InlineKeyboardMarkup(tombol)
        )

    elif data.startswith("promo_bc_"):
        pid = int(data.replace("promo_bc_", ""))
        promos = db.get_promos(aktif_only=False)
        promo = next((p for p in promos if p["id"] == pid), None)
        if not promo:
            await query.edit_message_text("❌ Promo tidak ditemukan.")
            return

        ctx.user_data["pending_promo"] = promo
        user_ids = db.get_all_users()
        tombol = [
            [
                InlineKeyboardButton("✅ Kirim",  callback_data="promo_bc_konfirm"),
                InlineKeyboardButton("❌ Batal",  callback_data="promo_bc_cancel"),
            ]
        ]
        await query.edit_message_text(
            f"📤 *Broadcast Promo*\n\n"
            f"Judul    : *{promo['judul']}*\n"
            f"Penerima : `{len(user_ids)}` pengguna\n\n"
            f"Lanjutkan?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(tombol)
        )

    elif data == "promo_bc_konfirm":
        promo = ctx.user_data.get("pending_promo")
        if not promo:
            await query.edit_message_text("❌ Data promo hilang. Mulai ulang.")
            return
        await query.edit_message_text("📤 Mengirim broadcast promosi...")
        await _broadcast_promo(update, ctx, promo)

    elif data == "promo_bc_cancel":
        ctx.user_data.pop("pending_promo", None)
        await query.edit_message_text("❌ Dibatalkan.")


# ── Tambah Promo — ConversationHandler ───────────────────

async def terima_judul(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["promo_baru"]["judul"] = update.message.text
    await update.message.reply_text("📝 Ketik *deskripsi* promosi (atau ketik `-` untuk skip):", parse_mode="Markdown")
    return DESKRIPSI


async def terima_deskripsi(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    teks = update.message.text
    ctx.user_data["promo_baru"]["deskripsi"] = "" if teks == "-" else teks
    await update.message.reply_text("🖼 Kirim URL gambar (atau ketik `-` untuk skip):")
    return GAMBAR


async def terima_gambar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    teks = update.message.text
    data = ctx.user_data["promo_baru"]
    gambar = None if teks == "-" else teks

    pid = db.add_promo(data["judul"], data.get("deskripsi"), gambar)
    ctx.user_data.pop("promo_baru", None)

    await update.message.reply_text(
        f"✅ Promosi *{data['judul']}* ditambahkan dengan ID `{pid}`.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END


async def batal(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text("❌ Dibatalkan.")
    return ConversationHandler.END


async def _broadcast_promo(update: Update, ctx: ContextTypes.DEFAULT_TYPE, promo: dict):
    import asyncio
    from config import BROADCAST_DELAY
    bot = ctx.bot
    user_ids = db.get_all_users()
    chat_id = update.effective_chat.id
    dikirim = gagal = 0

    teks_promo = f"🎁 *{promo['judul']}*\n\n{promo.get('deskripsi','')}"

    for uid in user_ids:
        try:
            if promo.get("gambar_url"):
                await bot.send_photo(uid, promo["gambar_url"], caption=teks_promo, parse_mode="Markdown")
            else:
                await bot.send_message(uid, teks_promo, parse_mode="Markdown")
            dikirim += 1
        except Exception:
            gagal += 1
        await asyncio.sleep(BROADCAST_DELAY)

    db.log_broadcast(teks_promo[:200], "promo", dikirim, gagal)
    await bot.send_message(
        chat_id,
        f"✅ Broadcast promo selesai!\n✅ {dikirim} | ❌ {gagal}",
        parse_mode="Markdown"
    )


def conv_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("promo", menu),
            CallbackQueryHandler(handle_callback, pattern="^promo_tambah$"),
        ],
        states={
            JUDUL:      [MessageHandler(filters.TEXT & ~filters.COMMAND, terima_judul)],
            DESKRIPSI:  [MessageHandler(filters.TEXT & ~filters.COMMAND, terima_deskripsi)],
            GAMBAR:     [MessageHandler(filters.TEXT & ~filters.COMMAND, terima_gambar)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        per_user=True,
    )
