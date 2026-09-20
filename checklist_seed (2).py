# Botni birinchi marta ishga tushirganda avtomatik yuklanadigan checklist.
# Keyinchalik botdan turib /kategoriya_qoshish va /band_qoshish orqali
# yangi savollar qo'shishingiz mumkin.

DEFAULT_CHECKLIST = {
    "Tovar zaxirasi": [
        "Barcha tovarlar javonlarda to'liq joylashtirilganmi?",
        "Bo'sh joylar (out-of-stock) mavjudmi?",
        "Muddati o'tgan yoki o'tish arafasidagi tovarlar bormi?",
        "Tovarlar FIFO tartibida joylashtirilganmi (eski tovar oldinda)?",
        "Ombordagi qoldiqlar hisobot bilan mos keladimi?",
    ],
    "Do'kon standartlari": [
        "Narx yorliqlari barcha tovarlarda mavjud va to'g'rimi?",
        "Savdo zali toza va tartiblimi?",
        "Yo'laklar bo'sh va o'tish qulaymi?",
        "Reklama va aksiya materiallari joyidami?",
        "Kassa zonasi tartibli va tozami?",
        "Yorug'lik va harorat me'yoridami?",
    ],
    "Xodimlar ishi": [
        "Xodimlar formada (dress-code) ishlayaptimi?",
        "Xodimlar mijozlarga xushmuomalami?",
        "Xodimlar o'z ish joyida, smenada vaqtidami?",
        "Xodimlar mahsulot haqidagi savollarga javob bera oladimi?",
        "Xizmat ko'rsatish tezligi qoniqarlimi?",
    ],
}
