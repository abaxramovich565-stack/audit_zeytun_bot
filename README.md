# Supermarket Audit Boti

Telegram orqali do'kon tekshiruvlarini (audit) o'tkazish uchun bot.
Auditor telefonida botni ochib, checklist bo'yicha javob beradi, muammo
bo'lsa rasm yuboradi — bot hammasini saqlaydi va hisobot chiqaradi.

## Nima qila oladi

- **/audit** — filialni tanlab, checklist bo'yicha tekshiruv o'tkazish
  (Tovar zaxirasi, Do'kon standartlari, Xodimlar ishi)
- Har bir savolga 3 xil javob: ✅ Yaxshi / ⚠️ O'rtacha / ❌ Yomon
- Muammo topilsa — izoh yozish yoki **rasm yuborish** mumkin
- **/hisobot** — oxirgi tekshiruvlar ro'yxati va har birining batafsil
  natijasi (muammolar, izohlar, rasmlar)
- Admin uchun: yangi filial, yangi savol/kategoriya qo'shish — hammasi
  botning o'zidan, kod yozmasdan

---

## O'rnatish (bosqichma-bosqich)

### 1. Kompyuter yoki serverga Python o'rnatish

Python 3.10 yoki undan yuqori versiya kerak.
Tekshirish uchun terminalda yozing:
```
python3 --version
```
Agar yo'q bo'lsa, https://www.python.org/downloads/ dan yuklab oling.

### 2. Loyiha fayllarini joylashtirish

Ushbu papkani (`audit_bot`) kompyuteringiz yoki serveringizga nusxalang.

### 3. Kerakli kutubxonalarni o'rnatish

Terminalda loyiha papkasiga kirib:
```
cd audit_bot
pip install -r requirements.txt
```

### 4. Telegram botni yaratish (token olish)

1. Telegram'da **@BotFather** ni toping va yozing: `/newbot`
2. Bot uchun nom bering (masalan: "Supermarket Audit Bot")
3. Foydalanuvchi nomi bering — oxiri `bot` bilan tugashi kerak
   (masalan: `MeningAuditBotim_bot`)
4. BotFather sizga uzun bir **token** beradi, masalan:
   `7123456789:AAHkjahsdkjahsdKJHASDkjahsdkjahsd`
5. Shu tokenni nusxalab oling

### 5. Tokenni botga kiritish

`config.py` faylini oching va bu qatorni toping:
```python
BOT_TOKEN = os.getenv("BOT_TOKEN", "SIZNING_BOT_TOKENINGIZ_BU_YERGA")
```
`"SIZNING_BOT_TOKENINGIZ_BU_YERGA"` o'rniga BotFather bergan tokenni qo'ying.

### 6. O'zingizni admin qilib belgilash

1. Telegram'da **@userinfobot** ga `/start` yozing — u sizga ID raqamingizni beradi (masalan: `123456789`)
2. `config.py` faylida shu qatorni toping:
```python
ADMIN_IDS = [
    # BU YERGA O'Z ID RAQAMINGIZNI QO'SHING
]
```
va shunday qiling:
```python
ADMIN_IDS = [
    123456789,
]
```
(Bir nechta admin bo'lsa, vergul bilan qo'shishingiz mumkin: `[123456789, 987654321]`)

### 7. Botni ishga tushirish

Terminalda:
```
python3 bot.py
```
"Bot ishga tushdi..." degan yozuv chiqsa — tayyor! Endi Telegram'da
botingizni topib, `/start` bosing.

**Muhim:** Bot faqat kompyuter/server yoqiq va shu buyruq ishlab turgan
paytda javob beradi. Doimiy ishlashi uchun uni serverga (VPS) joylashtirish
va fonda (masalan `screen`, `tmux` yoki `systemd` orqali) ishga tushirish
tavsiya etiladi. Agar buni qanday qilishni bilmasangiz, menga ayting —
tayyorlab beraman.

---

## Botdan qanday foydalanish

### Auditor uchun
1. Botga `/audit` yozing
2. Filialni tanlang
3. Savollarga birma-bir javob bering (✅/⚠️/❌)
4. Muammo bo'lsa — izoh yozing yoki rasm yuboring (yoki `/otkazib_yuborish`)
5. Oxirida umumiy ball va muammolar soni chiqadi

### Menejer/admin uchun
- `/filial_qoshish <nomi>` — yangi filial qo'shish
- `/filiallar` — filiallar ro'yxati
- `/kategoriyalar` — checklist kategoriyalari va raqamlari
- `/kategoriya_qoshish <nomi>` — yangi bo'lim qo'shish
- `/band_qoshish <kategoriya raqami> <savol matni>` — yangi savol qo'shish
- `/hisobot` — barcha oxirgi tekshiruvlarni ko'rish, har birini bosib
  batafsil natija (muammolar, izohlar, rasmlar) olish

---

## Keyingi bosqichlar (xohlasangiz)

- **AI orqali rasm tahlili**: xodim yuborgan rasmni AI o'zi tekshirib,
  muammoni avtomatik aniqlaydi (bo'sh javon, tartibsizlik va h.k.)
- **Excel/PDF hisobot**: `/hisobot` natijalarini avtomatik fayl qilib berish
- **Kunlik avtomatik hisobot**: har kuni belgilangan vaqtda admin guruhiga
  statistika yuborish
- **Kameralar orqali avtomatik kuzatuv**: eng murakkab va qimmat bosqich

Shu funksiyalardan qaysi birini keyin qo'shishni xohlasangiz — ayting,
davom ettiramiz.
