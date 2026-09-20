import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

import config
import database as db

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)


# ---------------- FSM holatlari ----------------

class AuditFSM(StatesGroup):
    javob_kutilmoqda = State()
    izoh_kutilmoqda = State()


def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS


# ---------------- Yordamchi funksiyalar ----------------

def filiallar_klaviaturasi():
    filiallar = db.filiallar_royxati()
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for f in filiallar:
        kb.inline_keyboard.append(
            [InlineKeyboardButton(text=f["nomi"], callback_data=f"filial:{f['id']}")]
        )
    return kb


def javob_klaviaturasi(band_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yaxshi", callback_data=f"javob:{band_id}:yaxshi"),
                InlineKeyboardButton(text="⚠️ O'rtacha", callback_data=f"javob:{band_id}:ortacha"),
                InlineKeyboardButton(text="❌ Yomon", callback_data=f"javob:{band_id}:yomon"),
            ]
        ]
    )


def barcha_bandlarni_yigish():
    """Barcha kategoriyalar bo'yicha bandlarni ketma-ket ro'yxat qilib qaytaradi."""
    natija = []
    for kat in db.kategoriyalar_royxati():
        for band in db.bandlar_royxati(kat["id"]):
            natija.append({"id": band["id"], "matn": band["matn"], "kategoriya": kat["nomi"]})
    return natija


def ball_hisoblash(holatlar):
    xarita = {"yaxshi": 100, "ortacha": 50, "yomon": 0}
    if not holatlar:
        return 0
    return round(sum(xarita[h] for h in holatlar) / len(holatlar), 1)


# ---------------- /start ----------------

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    matn = (
        "Assalomu alaykum! Men supermarket auditi uchun botman.\n\n"
        "Buyruqlar:\n"
        "/audit — yangi tekshiruv boshlash\n"
        "/hisobot — oxirgi tekshiruvlar hisobotini ko'rish\n"
    )
    if is_admin(message.from_user.id):
        matn += (
            "\nAdmin buyruqlari:\n"
            "/filial_qoshish <nomi> — yangi filial qo'shish\n"
            "/filiallar — filiallar ro'yxati\n"
            "/kategoriyalar — checklist kategoriyalari\n"
            "/kategoriya_qoshish <nomi> — yangi kategoriya\n"
            "/band_qoshish <kategoriya_raqami> <savol> — yangi savol\n"
        )
    await message.answer(matn)


# ---------------- Filial boshqaruvi (admin) ----------------

@router.message(Command("filial_qoshish"))
async def cmd_filial_qoshish(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Bu buyruq faqat adminlar uchun.")
        return
    nomi = message.text.replace("/filial_qoshish", "").strip()
    if not nomi:
        await message.answer("Filial nomini yozing. Masalan:\n/filial_qoshish Chilonzor filiali")
        return
    db.filial_qoshish(nomi)
    await message.answer(f"✅ '{nomi}' filiali qo'shildi.")


@router.message(Command("filiallar"))
async def cmd_filiallar(message: Message):
    filiallar = db.filiallar_royxati()
    if not filiallar:
        await message.answer("Hozircha filiallar qo'shilmagan. /filial_qoshish buyrug'idan foydalaning.")
        return
    matn = "📍 Filiallar:\n" + "\n".join(f"- {f['nomi']}" for f in filiallar)
    await message.answer(matn)


# ---------------- Checklist boshqaruvi (admin) ----------------

@router.message(Command("kategoriyalar"))
async def cmd_kategoriyalar(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Bu buyruq faqat adminlar uchun.")
        return
    katlar = db.kategoriyalar_royxati()
    matn = "📂 Kategoriyalar:\n" + "\n".join(f"{k['id']}. {k['nomi']}" for k in katlar)
    matn += "\n\nYangi savol qo'shish uchun:\n/band_qoshish <kategoriya_raqami> <savol matni>"
    await message.answer(matn)


@router.message(Command("kategoriya_qoshish"))
async def cmd_kategoriya_qoshish(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Bu buyruq faqat adminlar uchun.")
        return
    nomi = message.text.replace("/kategoriya_qoshish", "").strip()
    if not nomi:
        await message.answer("Format: /kategoriya_qoshish <nomi>")
        return
    db.kategoriya_qoshish(nomi)
    await message.answer(f"✅ '{nomi}' kategoriyasi qo'shildi.")


@router.message(Command("band_qoshish"))
async def cmd_band_qoshish(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Bu buyruq faqat adminlar uchun.")
        return
    qism = message.text.split(maxsplit=2)
    if len(qism) < 3 or not qism[1].isdigit():
        await message.answer(
            "To'g'ri format:\n/band_qoshish <kategoriya_raqami> <savol matni>\n"
            "Kategoriyalar ro'yxatini /kategoriyalar orqali ko'ring."
        )
        return
    kategoriya_id, matn = int(qism[1]), qism[2]
    db.band_qoshish(kategoriya_id, matn)
    await message.answer("✅ Yangi savol qo'shildi.")


# ---------------- Audit jarayoni ----------------

@router.message(Command("audit"))
async def cmd_audit(message: Message, state: FSMContext):
    filiallar = db.filiallar_royxati()
    if not filiallar:
        await message.answer(
            "Hali birorta filial qo'shilmagan.\n"
            "Admin /filial_qoshish <nomi> buyrug'i orqali filial qo'shishi kerak."
        )
        return
    await message.answer("Qaysi filialni tekshiryapsiz?", reply_markup=filiallar_klaviaturasi())


@router.callback_query(F.data.startswith("filial:"))
async def filial_tanlandi(callback: CallbackQuery, state: FSMContext):
    filial_id = int(callback.data.split(":")[1])
    filial = db.filial_olish(filial_id)

    bandlar = barcha_bandlarni_yigish()
    if not bandlar:
        await callback.message.answer("Checklist bandlari topilmadi.")
        await callback.answer()
        return

    audit_id = db.audit_boshlash(
        filial_id=filial_id,
        auditor_id=callback.from_user.id,
        auditor_ism=callback.from_user.full_name,
        vaqt=datetime.now().isoformat(timespec="seconds"),
    )

    await state.update_data(
        audit_id=audit_id,
        bandlar=bandlar,
        indeks=0,
        holatlar=[],
    )

    await callback.message.answer(f"🏬 Filial: {filial['nomi']}\nTekshiruv boshlandi!")
    await keyingi_bandni_yuborish(callback.message, state)
    await callback.answer()


async def keyingi_bandni_yuborish(message: Message, state: FSMContext):
    data = await state.get_data()
    bandlar = data["bandlar"]
    indeks = data["indeks"]

    if indeks >= len(bandlar):
        await auditni_yakunlash(message, state)
        return

    band = bandlar[indeks]
    matn = f"[{band['kategoriya']}]\n\n{indeks + 1}/{len(bandlar)}. {band['matn']}"

    await message.answer(matn, reply_markup=javob_klaviaturasi(band["id"]))
    await state.set_state(AuditFSM.javob_kutilmoqda)


@router.callback_query(AuditFSM.javob_kutilmoqda, F.data.startswith("javob:"))
async def javob_qabul_qilindi(callback: CallbackQuery, state: FSMContext):
    _, band_id, holat = callback.data.split(":")
    band_id = int(band_id)
    data = await state.get_data()

    if holat == "yaxshi":
        db.javob_saqlash(audit_id=data["audit_id"], band_id=band_id, holat=holat)
        holatlar = data["holatlar"] + [holat]
        await state.update_data(indeks=data["indeks"] + 1, holatlar=holatlar)
        await callback.message.edit_reply_markup(reply_markup=None)
        await keyingi_bandni_yuborish(callback.message, state)
    else:
        await state.update_data(kutilayotgan_band=band_id, kutilayotgan_holat=holat)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            "📸 Muammo haqida izoh yozing yoki rasm yuboring.\n"
            "Izohsiz o'tkazmoqchi bo'lsangiz — /otkazib_yuborish deb yozing."
        )
        await state.set_state(AuditFSM.izoh_kutilmoqda)

    await callback.answer()


@router.message(AuditFSM.izoh_kutilmoqda, Command("otkazib_yuborish"))
async def izohsiz_otish(message: Message, state: FSMContext):
    await izohni_saqlash_va_davom_etish(message, state, izoh=None, rasm_file_id=None)


@router.message(AuditFSM.izoh_kutilmoqda, F.photo)
async def rasm_bilan_izoh(message: Message, state: FSMContext):
    rasm_file_id = message.photo[-1].file_id
    izoh = message.caption
    await izohni_saqlash_va_davom_etish(message, state, izoh=izoh, rasm_file_id=rasm_file_id)


@router.message(AuditFSM.izoh_kutilmoqda, F.text)
async def matn_bilan_izoh(message: Message, state: FSMContext):
    await izohni_saqlash_va_davom_etish(message, state, izoh=message.text, rasm_file_id=None)


async def izohni_saqlash_va_davom_etish(message: Message, state: FSMContext, izoh, rasm_file_id):
    data = await state.get_data()
    db.javob_saqlash(
        audit_id=data["audit_id"],
        band_id=data["kutilayotgan_band"],
        holat=data["kutilayotgan_holat"],
        izoh=izoh,
        rasm_file_id=rasm_file_id,
    )
    holatlar = data["holatlar"] + [data["kutilayotgan_holat"]]
    await state.update_data(indeks=data["indeks"] + 1, holatlar=holatlar)
    await message.answer("✅ Saqlandi.")
    await keyingi_bandni_yuborish(message, state)


async def auditni_yakunlash(message: Message, state: FSMContext):
    data = await state.get_data()
    umumiy_ball = ball_hisoblash(data["holatlar"])
    db.audit_yakunlash(
        audit_id=data["audit_id"],
        vaqt=datetime.now().isoformat(timespec="seconds"),
        umumiy_ball=umumiy_ball,
    )
    muammolar_soni = sum(1 for h in data["holatlar"] if h != "yaxshi")
    await message.answer(
        f"🏁 Tekshiruv yakunlandi!\n\n"
        f"📊 Umumiy ball: {umumiy_ball}%\n"
        f"⚠️ Aniqlangan muammolar: {muammolar_soni} ta\n\n"
        f"Rahmat! /hisobot orqali batafsil ko'rishingiz mumkin."
    )
    await state.clear()


# ---------------- Hisobot ----------------

@router.message(Command("hisobot"))
async def cmd_hisobot(message: Message):
    auditlar = db.oxirgi_auditlar(limit=10)
    if not auditlar:
        await message.answer("Hali yakunlangan tekshiruvlar yo'q.")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[])
    matn = "📋 Oxirgi tekshiruvlar:\n\n"
    for a in auditlar:
        sana = a["tugash_vaqti"][:16].replace("T", " ")
        matn += f"🏬 {a['filial_nomi']} — {sana} — {a['umumiy_ball']}%\n"
        kb.inline_keyboard.append(
            [InlineKeyboardButton(
                text=f"{a['filial_nomi']} ({sana})",
                callback_data=f"hisobot:{a['id']}",
            )]
        )
    await message.answer(matn, reply_markup=kb)


@router.callback_query(F.data.startswith("hisobot:"))
async def hisobot_batafsil(callback: CallbackQuery):
    audit_id = int(callback.data.split(":")[1])
    audit, javoblar = db.audit_toliq(audit_id)

    matn = (
        f"🏬 Filial: {audit['filial_nomi']}\n"
        f"👤 Auditor: {audit['auditor_ism']}\n"
        f"📅 Sana: {audit['tugash_vaqti'][:16].replace('T', ' ')}\n"
        f"📊 Umumiy ball: {audit['umumiy_ball']}%\n\n"
        f"Muammolar:"
    )
    await callback.message.answer(matn)

    muammolar = [j for j in javoblar if j["holat"] != "yaxshi"]
    if not muammolar:
        await callback.message.answer("Muammo aniqlanmadi. 🎉")
    else:
        for j in muammolar:
            belgi = "❌" if j["holat"] == "yomon" else "⚠️"
            izoh_matni = f"\nIzoh: {j['izoh']}" if j["izoh"] else ""
            javob_matni = f"{belgi} {j['band_matni']}{izoh_matni}"
            if j["rasm_file_id"]:
                await callback.message.answer_photo(j["rasm_file_id"], caption=javob_matni)
            else:
                await callback.message.answer(javob_matni)

    await callback.answer()


# ---------------- Ishga tushirish ----------------

async def main():
    db.init_db()
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
