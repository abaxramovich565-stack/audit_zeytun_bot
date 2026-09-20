import sqlite3
from contextlib import closing

from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with closing(get_conn()) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS filiallar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomi TEXT NOT NULL,
                manzil TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS kategoriyalar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomi TEXT NOT NULL UNIQUE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bandlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kategoriya_id INTEGER NOT NULL,
                matn TEXT NOT NULL,
                faol INTEGER DEFAULT 1,
                FOREIGN KEY (kategoriya_id) REFERENCES kategoriyalar(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS auditlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filial_id INTEGER NOT NULL,
                auditor_id INTEGER NOT NULL,
                auditor_ism TEXT,
                boshlanish_vaqti TEXT,
                tugash_vaqti TEXT,
                umumiy_ball REAL,
                FOREIGN KEY (filial_id) REFERENCES filiallar(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS javoblar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id INTEGER NOT NULL,
                band_id INTEGER NOT NULL,
                holat TEXT NOT NULL,
                izoh TEXT,
                rasm_file_id TEXT,
                FOREIGN KEY (audit_id) REFERENCES auditlar(id),
                FOREIGN KEY (band_id) REFERENCES bandlar(id)
            )
        """)
    seed_default_data()


def seed_default_data():
    from checklist_seed import DEFAULT_CHECKLIST
    with closing(get_conn()) as conn, conn:
        cur = conn.execute("SELECT COUNT(*) as c FROM kategoriyalar")
        if cur.fetchone()["c"] > 0:
            return  # allaqachon to'ldirilgan
        for kategoriya_nomi, bandlar in DEFAULT_CHECKLIST.items():
            cur = conn.execute(
                "INSERT INTO kategoriyalar (nomi) VALUES (?)", (kategoriya_nomi,)
            )
            kat_id = cur.lastrowid
            for band_matni in bandlar:
                conn.execute(
                    "INSERT INTO bandlar (kategoriya_id, matn) VALUES (?, ?)",
                    (kat_id, band_matni),
                )


# ---------- Filiallar ----------

def filial_qoshish(nomi, manzil=None):
    with closing(get_conn()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO filiallar (nomi, manzil) VALUES (?, ?)", (nomi, manzil)
        )
        return cur.lastrowid


def filiallar_royxati():
    with closing(get_conn()) as conn:
        return conn.execute("SELECT * FROM filiallar ORDER BY nomi").fetchall()


def filial_olish(filial_id):
    with closing(get_conn()) as conn:
        return conn.execute(
            "SELECT * FROM filiallar WHERE id = ?", (filial_id,)
        ).fetchone()


# ---------- Kategoriya / Bandlar ----------

def kategoriyalar_royxati():
    with closing(get_conn()) as conn:
        return conn.execute("SELECT * FROM kategoriyalar ORDER BY id").fetchall()


def bandlar_royxati(kategoriya_id):
    with closing(get_conn()) as conn:
        return conn.execute(
            "SELECT * FROM bandlar WHERE kategoriya_id = ? AND faol = 1 ORDER BY id",
            (kategoriya_id,),
        ).fetchall()


def band_qoshish(kategoriya_id, matn):
    with closing(get_conn()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO bandlar (kategoriya_id, matn) VALUES (?, ?)",
            (kategoriya_id, matn),
        )
        return cur.lastrowid


def kategoriya_qoshish(nomi):
    with closing(get_conn()) as conn, conn:
        cur = conn.execute("INSERT INTO kategoriyalar (nomi) VALUES (?)", (nomi,))
        return cur.lastrowid


# ---------- Audit ----------

def audit_boshlash(filial_id, auditor_id, auditor_ism, vaqt):
    with closing(get_conn()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO auditlar (filial_id, auditor_id, auditor_ism, boshlanish_vaqti) "
            "VALUES (?, ?, ?, ?)",
            (filial_id, auditor_id, auditor_ism, vaqt),
        )
        return cur.lastrowid


def javob_saqlash(audit_id, band_id, holat, izoh=None, rasm_file_id=None):
    with closing(get_conn()) as conn, conn:
        conn.execute(
            "INSERT INTO javoblar (audit_id, band_id, holat, izoh, rasm_file_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (audit_id, band_id, holat, izoh, rasm_file_id),
        )


def audit_yakunlash(audit_id, vaqt, umumiy_ball):
    with closing(get_conn()) as conn, conn:
        conn.execute(
            "UPDATE auditlar SET tugash_vaqti = ?, umumiy_ball = ? WHERE id = ?",
            (vaqt, umumiy_ball, audit_id),
        )


def oxirgi_auditlar(limit=10, filial_id=None):
    with closing(get_conn()) as conn:
        if filial_id:
            return conn.execute(
                "SELECT a.*, f.nomi as filial_nomi FROM auditlar a "
                "JOIN filiallar f ON a.filial_id = f.id "
                "WHERE a.filial_id = ? AND a.tugash_vaqti IS NOT NULL "
                "ORDER BY a.id DESC LIMIT ?",
                (filial_id, limit),
            ).fetchall()
        return conn.execute(
            "SELECT a.*, f.nomi as filial_nomi FROM auditlar a "
            "JOIN filiallar f ON a.filial_id = f.id "
            "WHERE a.tugash_vaqti IS NOT NULL "
            "ORDER BY a.id DESC LIMIT ?",
            (limit,),
        ).fetchall()


def audit_toliq(audit_id):
    with closing(get_conn()) as conn:
        audit = conn.execute(
            "SELECT a.*, f.nomi as filial_nomi FROM auditlar a "
            "JOIN filiallar f ON a.filial_id = f.id WHERE a.id = ?",
            (audit_id,),
        ).fetchone()
        javoblar = conn.execute(
            "SELECT j.*, b.matn as band_matni FROM javoblar j "
            "JOIN bandlar b ON j.band_id = b.id WHERE j.audit_id = ? ORDER BY j.id",
            (audit_id,),
        ).fetchall()
        return audit, javoblar
