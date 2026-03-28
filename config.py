"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         KONFIGURASI BOT
  ← Edit bagian ini sesuai kebutuhan →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ┌─────────────────────────────────────┐
# │  TOKEN BOT (dari @BotFather)        │
# └─────────────────────────────────────┘
BOT_TOKEN = "MASUKKAN_TOKEN_BOT_DISINI"

# ┌─────────────────────────────────────┐
# │  ADMIN AWAL (Telegram user ID)      │
# │  Cari ID kamu via @userinfobot      │
# └─────────────────────────────────────┘
OWNER_ID = 123456789          # ID pemilik (tidak bisa dihapus)
ADMIN_IDS = [123456789]       # Daftar admin awal

# ┌─────────────────────────────────────┐
# │  DATABASE                           │
# └─────────────────────────────────────┘
DB_PATH = "data/bot.db"       # Lokasi file database SQLite

# ┌─────────────────────────────────────┐
# │  BROADCAST                          │
# └─────────────────────────────────────┘
BROADCAST_DELAY = 0.05        # Jeda antar pesan (detik) agar tidak kena flood
BROADCAST_BATCH = 30          # Kirim progress setiap N pesan

# ┌─────────────────────────────────────┐
# │  TEKS DEFAULT                       │
# └─────────────────────────────────────┘
WELCOME_TEXT = """
👋 Halo {nama}!

Selamat datang di bot kami.
Ketik /help untuk melihat daftar perintah.
"""

HELP_TEXT = """
📋 *Daftar Perintah*

👤 *Umum*
/start — Mulai bot
/help  — Bantuan
/info  — Info bot

🔧 *Admin*
/admin      — Panel admin
/broadcast  — Kirim pesan massal
/promo      — Kelola promosi
/stats      — Statistik pengguna
/export     — Export data pengguna
"""

# ┌─────────────────────────────────────┐
# │  NAMA & DESKRIPSI BOT               │
# └─────────────────────────────────────┘
BOT_NAME = "MyBot"
BOT_VERSION = "1.0.0"
