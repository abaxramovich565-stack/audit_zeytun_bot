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
                nomi TEXT NOT NULL UNIQUE,
                xodim_bolimi INTEGER DEFAULT 0
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
            CREATE TABLE IF NOT EXISTS bolimlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomi TEXT NOT NULL UNIQUE
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
                bolim_id INTEGER,
                xodim_ism TEXT,
                FOREIGN KEY (audit_id) REFERENCES auditlar(id),
                FOREIGN KEY (band_id) REFERENCES bandlar(id),
                FOREIGN KEY (bolim_id) REFERENCES bolimlar(id)
            )
        """)
        _eski_bazani_moslashtirish(conn)
        try:
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_javob_audit_band "
                "ON javoblar(audit_id, band_id)"
            )
        except sqlite3.IntegrityError:
            # Eski bazada bitta savolga bir nechta javob saqlangan bo'lishi mumkin.
            # Bunday holatda indeks o'rnatilmaydi, lekin bot ishlashda davom etadi.
            pass
    seed_default_data()


def _eski_bazani_moslashtirish(conn):
    """Avval yaratilgan bazalarga yangi ustunlarni xatosiz qo'shib qo'yadi."""
    javob_ustunlari = {row["name"] for row in conn.execute("PRAGMA table_info(javoblar)")}
    if "bolim_id" not in javob_ustunlari:
        conn.execute("ALTER TABLE javoblar ADD COLUMN bolim_id INTEGER")
    if "xodim_ism" not in javob_ustunlari:
        conn.execute("ALTER TABLE javoblar ADD COLUMN xodim_ism TEXT")

    kategoriya_ustunlari = {row["name"] for row in conn.execute("PRAGMA table_info(kategoriyalar)")}
    if "xodim_bolimi" not in kategoriya_ustunlari:
        conn.execute("ALTER TABLE kategoriyalar ADD COLUMN xodim_bolimi INTEGER DEFAULT 0")
        conn.execute(
            "UPDATE kategoriyalar SET xodim_bolimi = 1 WHERE LOWER(nomi) LIKE '%xodim%'"
        )


def seed_default_data():
    from checklist_seed import DEFAULT_CHECKLIST
    with closing(get_conn()) as conn, conn:
        cur = conn.execute("SELECT COUNT(*) as c FROM kategoriyalar")
        if cur.fetchone()["c"] > 0:
            return  # allaqachon to'ldirilgan
        for kategoriya_nomi, bandlar in DEFAULT_CHECKLIST.items():
            xodim_flag = 1 if "xodim" in kategoriya_nomi.lower() else 0
            cur = conn.execute(
                "INSERT INTO kategoriyalar (nomi, xodim_bolimi) VALUES (?, ?)",
                (kategoriya_nomi, xodim_flag),
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


def kategoriya_olish(kategoriya_id):
    with closing(get_conn()) as conn:
        return conn.execute(
            "SELECT * FROM kategoriyalar WHERE id = ?", (kategoriya_id,)
        ).fetchone()


def bandlar_royxati(kategoriya_id):
    with closing(get_conn()) as conn:
        return conn.execute(
            "SELECT * FROM bandlar WHERE kategoriya_id = ? AND faol = 1 ORDER BY id",
            (kategoriya_id,),
        ).fetchall()


def band_kategoriya_olish(band_id):
    """Bandni tegishli kategoriya ma'lumotlari (nomi, xodim_bolimi flag) bilan qaytaradi."""
    with closing(get_conn()) as conn:
        return conn.execute(
            "SELECT b.*, k.nomi as kategoriya_nomi, k.xodim_bolimi "
            "FROM bandlar b JOIN kategoriyalar k ON b.kategoriya_id = k.id "
            "WHERE b.id = ?",
            (band_id,),
        ).fetchone()


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


def barcha_bandlarni_yigish():
    """Barcha kategoriyalar bo'yicha bandlarni ketma-ket ro'yxat qilib qaytaradi."""
    natija = []
    for kat in kategoriyalar_royxati():
        for band in bandlar_royxati(kat["id"]):
            natija.append({"id": band["id"], "matn": band["matn"], "kategoriya": kat["nomi"]})
    return natija


# ---------- Bo'limlar (xodimlar ishlaydigan bo'limlar) ----------

def bolim_qoshish(nomi):
    with closing(get_conn()) as conn, conn:
        cur = conn.execute("INSERT OR IGNORE INTO bolimlar (nomi) VALUES (?)", (nomi,))
        return cur.lastrowid


def bolimlar_royxati():
    with closing(get_conn()) as conn:
        return conn.execute("SELECT * FROM bolimlar ORDER BY nomi").fetchall()


def bolim_olish(bolim_id):
    with closing(get_conn()) as conn:
        return conn.execute("SELECT * FROM bolimlar WHERE id = ?", (bolim_id,)).fetchone()


# ---------- Audit ----------

def audit_boshlash(filial_id, auditor_id, auditor_ism, vaqt):
    with closing(get_conn()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO auditlar (filial_id, auditor_id, auditor_ism, boshlanish_vaqti) "
            "VALUES (?, ?, ?, ?)",
            (filial_id, auditor_id, auditor_ism, vaqt),
        )
        return cur.lastrowid


def javob_saqlash(audit_id, band_id, holat, izoh=None, rasm_file_id=None,
                   bolim_id=None, xodim_ism=None):
    """Javobni saqlaydi. Xuddi shu savolga qayta javob berilsa — yangilanadi (o'chirilib qayta yozilmaydi)."""
    with closing(get_conn()) as conn, conn:
        conn.execute(
            "INSERT INTO javoblar (audit_id, band_id, holat, izoh, rasm_file_id, bolim_id, xodim_ism) "
            "VALUES (?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(audit_id, band_id) DO UPDATE SET "
            "holat=excluded.holat, izoh=excluded.izoh, rasm_file_id=excluded.rasm_file_id, "
            "bolim_id=excluded.bolim_id, xodim_ism=excluded.xodim_ism",
            (audit_id, band_id, holat, izoh, rasm_file_id, bolim_id, xodim_ism),
        )


def audit_javoblari_xaritasi(audit_id):
    """{band_id: holat} — menyuda savol qaysi holatda javob berilganini ko'rsatish uchun."""
    with closing(get_conn()) as conn:
        rows = conn.execute(
            "SELECT band_id, holat FROM javoblar WHERE audit_id = ?", (audit_id,)
        ).fetchall()
        return {r["band_id"]: r["holat"] for r in rows}


def audit_holatlar_royxati(audit_id):
    with closing(get_conn()) as conn:
        rows = conn.execute(
            "SELECT holat FROM javoblar WHERE audit_id = ?", (audit_id,)
        ).fetchall()
        return [r["holat"] for r in rows]


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


def auditlar_oraliqda(boshlanish_iso, tugash_iso):
    """Berilgan vaqt oralig'ida yakunlangan barcha auditlar (hisobotlar uchun)."""
    with closing(get_conn()) as conn:
        return conn.execute(
            "SELECT a.*, f.nomi as filial_nomi FROM auditlar a "
            "JOIN filiallar f ON a.filial_id = f.id "
            "WHERE a.tugash_vaqti IS NOT NULL "
            "AND a.tugash_vaqti >= ? AND a.tugash_vaqti <= ? "
            "ORDER BY a.tugash_vaqti",
            (boshlanish_iso, tugash_iso),
        ).fetchall()


def audit_toliq(audit_id):
    with closing(get_conn()) as conn:
        audit = conn.execute(
            "SELECT a.*, f.nomi as filial_nomi FROM auditlar a "
            "JOIN filiallar f ON a.filial_id = f.id WHERE a.id = ?",
            (audit_id,),
        ).fetchone()
        javoblar = conn.execute(
            "SELECT j.*, b.matn as band_matni, k.nomi as kategoriya_nomi, "
            "bl.nomi as bolim_nomi "
            "FROM javoblar j "
            "JOIN bandlar b ON j.band_id = b.id "
            "JOIN kategoriyalar k ON b.kategoriya_id = k.id "
            "LEFT JOIN bolimlar bl ON j.bolim_id = bl.id "
            "WHERE j.audit_id = ? ORDER BY j.id",
            (audit_id,),
        ).fetchall()
        return audit, javoblar
