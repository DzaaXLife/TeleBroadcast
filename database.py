"""
Database helper — SQLite
Semua operasi data ada di sini.
"""

import sqlite3
import os
from datetime import datetime
from config import DB_PATH


def get_conn():
    """Buat koneksi ke database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # hasil seperti dict
    return conn


def init_db():
    """Buat tabel jika belum ada. Dipanggil sekali saat bot start."""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY,
                username    TEXT,
                full_name   TEXT,
                joined_at   TEXT DEFAULT (datetime('now','localtime')),
                last_seen   TEXT DEFAULT (datetime('now','localtime')),
                is_blocked  INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS admins (
                user_id     INTEGER PRIMARY KEY,
                added_by    INTEGER,
                added_at    TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS broadcasts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                pesan       TEXT,
                tipe        TEXT,
                dikirim     INTEGER DEFAULT 0,
                gagal       INTEGER DEFAULT 0,
                dibuat_at   TEXT DEFAULT (datetime('now','localtime')),
                selesai_at  TEXT
            );

            CREATE TABLE IF NOT EXISTS promos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                judul       TEXT NOT NULL,
                deskripsi   TEXT,
                gambar_url  TEXT,
                aktif       INTEGER DEFAULT 1,
                dibuat_at   TEXT DEFAULT (datetime('now','localtime'))
            );
        """)
    print(f"[DB] Database siap: {DB_PATH}")


# ════════════════════════════════════════
#  USERS
# ════════════════════════════════════════

def upsert_user(user_id, username, full_name):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO users (id, username, full_name)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                username  = excluded.username,
                full_name = excluded.full_name,
                last_seen = datetime('now','localtime')
        """, (user_id, username, full_name))


def get_all_users(exclude_blocked=True):
    with get_conn() as conn:
        if exclude_blocked:
            rows = conn.execute(
                "SELECT id FROM users WHERE is_blocked = 0"
            ).fetchall()
        else:
            rows = conn.execute("SELECT id FROM users").fetchall()
    return [r["id"] for r in rows]


def get_user_count():
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as total, SUM(is_blocked) as blocked FROM users"
        ).fetchone()
    return {"total": row["total"], "blocked": row["blocked"] or 0}


def block_user(user_id):
    with get_conn() as conn:
        conn.execute("UPDATE users SET is_blocked=1 WHERE id=?", (user_id,))


def unblock_user(user_id):
    with get_conn() as conn:
        conn.execute("UPDATE users SET is_blocked=0 WHERE id=?", (user_id,))


def export_users_csv():
    """Return semua user sebagai list of dict."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, username, full_name, joined_at, last_seen, is_blocked FROM users"
        ).fetchall()
    return [dict(r) for r in rows]


# ════════════════════════════════════════
#  ADMINS
# ════════════════════════════════════════

def get_admins():
    with get_conn() as conn:
        rows = conn.execute("SELECT user_id FROM admins").fetchall()
    return [r["user_id"] for r in rows]


def add_admin(user_id, added_by):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO admins (user_id, added_by) VALUES (?,?)",
            (user_id, added_by)
        )


def remove_admin(user_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM admins WHERE user_id=?", (user_id,))


def is_admin(user_id):
    from config import OWNER_ID, ADMIN_IDS
    if user_id == OWNER_ID or user_id in ADMIN_IDS:
        return True
    return user_id in get_admins()


# ════════════════════════════════════════
#  BROADCASTS
# ════════════════════════════════════════

def log_broadcast(pesan, tipe, dikirim, gagal):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO broadcasts (pesan, tipe, dikirim, gagal, selesai_at)
            VALUES (?,?,?,?,datetime('now','localtime'))
        """, (pesan, tipe, dikirim, gagal))


def get_broadcast_history(limit=10):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM broadcasts ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


# ════════════════════════════════════════
#  PROMOS
# ════════════════════════════════════════

def add_promo(judul, deskripsi, gambar_url=None):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO promos (judul, deskripsi, gambar_url) VALUES (?,?,?)",
            (judul, deskripsi, gambar_url)
        )
    return cur.lastrowid


def get_promos(aktif_only=True):
    with get_conn() as conn:
        if aktif_only:
            rows = conn.execute(
                "SELECT * FROM promos WHERE aktif=1 ORDER BY id DESC"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM promos ORDER BY id DESC"
            ).fetchall()
    return [dict(r) for r in rows]


def toggle_promo(promo_id):
    with get_conn() as conn:
        conn.execute(
            "UPDATE promos SET aktif = CASE WHEN aktif=1 THEN 0 ELSE 1 END WHERE id=?",
            (promo_id,)
        )


def delete_promo(promo_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM promos WHERE id=?", (promo_id,))


# Init saat modul dimuat
init_db()
