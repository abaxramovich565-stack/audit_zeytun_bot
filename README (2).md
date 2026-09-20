# Supermarket Audit Boti — 0 dan o'rnatish

## 1. GitHub'da yangi, toza repo yarating
Eski `audit_zeytun_bot` repongizni **o'chirmang**, lekin undan foydalanmang.
GitHub'da yangi bo'sh repo oching, masalan: `audit-bot-v2`.

Shu papkadagi barcha fayllarni (bot.py, config.py, database.py,
checklist_seed.py, requirements.txt, Dockerfile, .dockerignore) o'sha
repo'ga yuklang (upload qiling yoki `git push` qiling).

## 2. Railway'da yangi service yarating
1. Railway'da eski `audit_zeytun_bot` service'ni **Settings > Delete Service**
   orqali o'chiring (loyihaning o'zini emas, faqat shu service'ni).
2. "+ New" > "GitHub Repo" > yangi `audit-bot-v2` repongizni tanlang.
3. Railway avtomatik ravishda `Dockerfile`ni topib, shu orqali build qiladi
   (nixpacks emas) — bu avvalgi "Build image" xatoligini bartaraf qiladi.

## 3. Muhit o'zgaruvchilarini (Variables) kiriting
Railway'da service ichida **Variables** bo'limiga o'ting va qo'shing:

| Nomi | Qiymati |
|---|---|
| `BOT_TOKEN` | BotFather bergan token |
| `ADMIN_IDS` | sizning Telegram ID raqamingiz, masalan `123456789` |

(Bir nechta admin bo'lsa: `123456789,987654321`)

Tokenni to'g'ridan-to'g'ri kodga yozish shart emas — Variables orqali
xavfsizroq.

## 4. Deploy va tekshirish
Variables saqlangach Railway avtomatik qayta deploy qiladi.
**Deploy Logs** bo'limida quyidagi yozuv chiqishi kerak:
```
Bot ishga tushdi...
```
Shundan keyin Telegram'da botga `/start` yozib sinab ko'ring.

## 5. Agar yana xato chiqsa
**Build Logs** yoki **Deploy Logs** ekranining skrinshotini yuboring —
aniq qaysi qatorda xato borligini shu yerdan ko'raman.

---

## Yangi imkoniyatlar (2-versiya)

### Erkin tartibda audit
`/audit` boshlaganda savollar endi ketma-ket avtomatik chiqmaydi.
Bosh menyuda kategoriyalar ro'yxati chiqadi (masalan "Tovar zaxirasi (2/5)"),
istalgan kategoriyani, istalgan savolni, istalgan tartibda tanlab
javob berish mumkin. Tugatganda "🏁 Auditni yakunlash" tugmasi bosiladi.

### Xodimlar ishi bo'limi — bo'lim va ism-familiya
"Xodimlar ishi" toifasidagi savolga javob berilganda rasm/izoh talab
qilinmaydi. Buning o'rniga:
1. Xodim qaysi bo'limda ishlashi so'raladi (ro'yxatdan tanlanadi)
2. Xodimning ism-familiyasi yoziladi

Bo'limlar ro'yxatini admin o'zi to'ldiradi:
- `/bolim_qoshish <nomi>` — masalan `/bolim_qoshish Kassa`
- `/bolimlar` — mavjud bo'limlar ro'yxati

**Muhim:** audit boshlashdan oldin kamida bitta bo'lim qo'shib qo'ying,
aks holda bot bo'lim/ism so'ramasdan javobni to'g'ridan-to'g'ri saqlaydi.

### Excel hisobotlar
Quyidagi buyruqlar (faqat adminlar uchun) professional formatlangan
Excel fayl chiqaradi — "Xulosa" (filiallar bo'yicha o'rtacha ball) va
"Tafsilot" (har bir muammoning batafsil ro'yxati, jumladan xodim ismi
va bo'limi) varaqlari bilan:

- `/kunlik-hisobot` — bugungi kun
- `/haftalik-hisobot` — oxirgi 7 kun
- `/oylik-hisobot` — oxirgi 30 kun

### Eski bazangiz bilan moslik
Agar Railway'da avvalgi `audit.db` fayli saqlanib qolgan bo'lsa ham,
bot ishga tushganda kerakli yangi ustunlarni avtomatik qo'shib oladi —
qo'lda hech narsa qilish shart emas.
