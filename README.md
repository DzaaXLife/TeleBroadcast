# 🤖 Telegram Bot — Broadcast & Promosi

Bot Telegram lengkap dengan fitur broadcast, promosi, manajemen admin, dan statistik.

---

## 📁 Struktur File

```
telegram_bot/
├── bot.py              ← Titik masuk utama (jalankan ini)
├── config.py           ← ⚙️  EDIT BAGIAN INI
├── database.py         ← Semua operasi database
├── requirements.txt    ← Dependensi Python
├── data/
│   └── bot.db          ← Database SQLite (auto-dibuat)
├── handlers/
│   ├── user.py         ← /start, /help, /info
│   ├── admin.py        ← Panel admin, kelola admin
│   ├── broadcast.py    ← Broadcast massal
│   ├── promo.py        ← Kelola promosi
│   └── stats.py        ← Statistik & export
└── utils/
    └── decorators.py   ← @admin_only, @owner_only
```

---

## 🚀 Cara Install & Jalankan

### 1. Install dependensi
```bash
pip install -r requirements.txt
```

### 2. Edit `config.py`
```python
BOT_TOKEN = "TOKEN_DARI_BOTFATHER"   # ← Wajib diisi
OWNER_ID  = 123456789                 # ← ID Telegram kamu
```

### 3. Jalankan bot
```bash
python bot.py
```

---

## 🎮 Daftar Perintah

### 👤 Pengguna Biasa
| Perintah | Fungsi |
|---------|--------|
| `/start` | Memulai bot |
| `/help`  | Daftar perintah |
| `/info`  | Info & statistik dasar |

### 🔧 Admin
| Perintah | Fungsi |
|---------|--------|
| `/admin`        | Panel kontrol admin |
| `/broadcast`    | Kirim pesan massal (teks/foto/video/dokumen) |
| `/promo`        | Kelola & broadcast promosi |
| `/stats`        | Statistik lengkap |
| `/export`       | Export data user ke CSV |
| `/addadmin ID`  | Tambah admin baru |
| `/deladmin ID`  | Hapus admin |
| `/listadmin`    | Lihat daftar admin |

---

## ✏️ Cara Kustomisasi

### Ubah pesan selamat datang
Edit `config.py`:
```python
WELCOME_TEXT = """
Halo {nama}! Selamat datang di toko kami 🎉
"""
```

### Tambah perintah baru
1. Buat fungsi di file handler yang sesuai
2. Daftarkan di `bot.py` dengan `add_handler`

### Batasi akses perintah
Gunakan decorator:
```python
from utils.decorators import admin_only

@admin_only
async def perintah_saya(update, ctx):
    ...
```

---

## 🗄️ Database

Bot menggunakan **SQLite** (tidak perlu install server).
File database ada di `data/bot.db`.

Tabel yang tersedia:
- `users` — semua pengguna yang pernah pakai bot
- `admins` — daftar admin
- `broadcasts` — riwayat broadcast
- `promos` — data promosi

---

## 💡 Tips

- Gunakan `/batal` di tengah conversation untuk membatalkan
- Broadcast mendukung: teks, foto, video, dan dokumen
- Promosi bisa di-broadcast langsung dari menu `/promo`
- Data user otomatis ter-export ke CSV via `/export`
