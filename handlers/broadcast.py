"""
Handler Broadcast:
Kirim pesan massal ke semua pengguna.
Mendukung teks, foto, video, dokumen.
"""

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler,
    CommandHandler, MessageHandler, CallbackQueryHandler, filters
)
import database as db
from config import BROADCAST_DELAY, BROADCAST_BATCH
from utils.decorators import admin_only

# Status percakapan
PILIH_TIPE, TULIS_PESAN, KONFIRMASI = range(3)


# ── Mulai Broadcast ───────────────────────────────────────

@admin_only
async def mulai(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    tombol = [
        [
            InlineKeyboardButton("📝 Teks",    callback_data="bc_tipe_teks"),
            InlineKeyboardButton("🖼 Foto",    callback_data="bc_tipe_foto"),
        ],
        [
            InlineKeyboardButton("🎥 Video",   callback_data="bc_tipe_video"),
            InlineKeyboardButton("📄 Dokumen", callback_data="bc_tipe_dokumen"),
        ],
        [InlineKeyboardButton("❌ Batal", callback_data="bc_batal")],
    ]
    await update.message.reply_text(
        "📢 *Broadcast Baru*\n\nPilih tipe pesan:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(tombol)
    )
    return PILIH_TIPE


async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "bc_batal":
        await query.edit_message_text("❌ Broadcast dibatalkan.")
        return ConversationHandler.END

    if data.startswith("bc_tipe_"):
        tipe = data.replace("bc_tipe_", "")
        ctx.user_data["bc_tipe"] = tipe
        panduan = {
            "teks":    "✏️ Ketik pesan teks yang ingin dikirim:",
            "foto":    "🖼 Kirim foto beserta caption (opsional):",
            "video":   "🎥 Kirim video beserta caption (opsional):",
            "dokumen": "📄 Kirim dokumen/file:",
        }
        await query.edit_message_text(panduan.get(tipe, "Ketik pesan:"))
        return TULIS_PESAN

    if data == "bc_kirim":
        await query.edit_message_text("📤 Mengirim broadcast...")
        await _kirim_broadcast(update, ctx)
        return ConversationHandler.END

    if data == "bc_preview_batal":
        await query.edit_message_text("❌ Broadcast dibatalkan.")
        ctx.user_data.clear()
        return ConversationHandler.END


async def terima_pesan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Terima pesan dari admin dan tampilkan konfirmasi."""
    tipe = ctx.user_data.get("bc_tipe", "teks")

    if tipe == "teks":
        ctx.user_data["bc_konten"] = update.message.text
        preview = update.message.text

    elif tipe == "foto":
        foto = update.message.photo[-1]
        ctx.user_data["bc_konten"] = foto.file_id
        ctx.user_data["bc_caption"] = update.message.caption or ""
        preview = f"[Foto] {update.message.caption or '(tanpa caption)'}"

    elif tipe == "video":
        video = update.message.video
        ctx.user_data["bc_konten"] = video.file_id
        ctx.user_data["bc_caption"] = update.message.caption or ""
        preview = f"[Video] {update.message.caption or '(tanpa caption)'}"

    elif tipe == "dokumen":
        dok = update.message.document
        ctx.user_data["bc_konten"] = dok.file_id
        ctx.user_data["bc_caption"] = update.message.caption or ""
        preview = f"[Dokumen: {dok.file_name}]"

    else:
        ctx.user_data["bc_konten"] = update.message.text
        preview = update.message.text

    jumlah = len(db.get_all_users())
    tombol = [
        [
            InlineKeyboardButton("✅ Kirim Sekarang", callback_data="bc_kirim"),
            InlineKeyboardButton("❌ Batal",          callback_data="bc_preview_batal"),
        ]
    ]
    await update.message.reply_text(
        f"📋 *Konfirmasi Broadcast*\n\n"
        f"Tipe    : `{tipe}`\n"
        f"Penerima: `{jumlah}` pengguna\n\n"
        f"*Preview:*\n{preview[:300]}{'...' if len(preview) > 300 else ''}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(tombol)
    )
    return KONFIRMASI


async def _kirim_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Eksekusi broadcast ke semua pengguna."""
    user_ids = db.get_all_users()
    tipe     = ctx.user_data.get("bc_tipe", "teks")
    konten   = ctx.user_data.get("bc_konten", "")
    caption  = ctx.user_data.get("bc_caption", "")
    bot      = ctx.bot

    dikirim = gagal = 0
    chat_id = update.effective_chat.id

    for i, uid in enumerate(user_ids, 1):
        try:
            if tipe == "teks":
                await bot.send_message(uid, konten)
            elif tipe == "foto":
                await bot.send_photo(uid, konten, caption=caption)
            elif tipe == "video":
                await bot.send_video(uid, konten, caption=caption)
            elif tipe == "dokumen":
                await bot.send_document(uid, konten, caption=caption)
            dikirim += 1
        except Exception:
            gagal += 1

        # Update progress setiap N pesan
        if i % BROADCAST_BATCH == 0:
            try:
                await bot.send_message(
                    chat_id,
                    f"⏳ Progress: {i}/{len(user_ids)} — ✅ {dikirim} | ❌ {gagal}"
                )
            except Exception:
                pass

        await asyncio.sleep(BROADCAST_DELAY)

    # Catat ke database
    db.log_broadcast(str(konten)[:200], tipe, dikirim, gagal)

    await bot.send_message(
        chat_id,
        f"✅ *Broadcast Selesai!*\n\n"
        f"📤 Terkirim : `{dikirim}`\n"
        f"❌ Gagal    : `{gagal}`\n"
        f"📊 Total    : `{len(user_ids)}`",
        parse_mode="Markdown"
    )
    ctx.user_data.clear()


async def batal(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Broadcast dibatalkan.")
    ctx.user_data.clear()
    return ConversationHandler.END


def conv_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("broadcast", mulai)],
        states={
            PILIH_TIPE:  [CallbackQueryHandler(handle_callback, pattern="^bc_")],
            TULIS_PESAN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, terima_pesan),
                MessageHandler(filters.PHOTO,    terima_pesan),
                MessageHandler(filters.VIDEO,    terima_pesan),
                MessageHandler(filters.Document.ALL, terima_pesan),
            ],
            KONFIRMASI:  [CallbackQueryHandler(handle_callback, pattern="^bc_")],
        },
        fallbacks=[CommandHandler("batal", batal)],
        per_user=True,
    )
