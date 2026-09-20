import os

# Telegram bot tokeningiz. @BotFather dan olasiz.
# Eng oson yo'l: shu yerga to'g'ridan-to'g'ri qo'yib qo'ying (qo'shtirnoq ichida).
BOT_TOKEN = os.getenv("BOT_TOKEN", "SIZNING_BOT_TOKENINGIZ_BU_YERGA")

# Admin (menejer/rahbar) larning Telegram ID raqamlari.
# O'z ID raqamingizni @userinfobot ga /start yozib bilib olishingiz mumkin.
#
# Buni ikki xil usulda kiritish mumkin:
# 1) Shu yerga to'g'ridan-to'g'ri yozib qo'yish: ADMIN_IDS = [123456789, 987654321]
# 2) Yoki ADMIN_IDS nomli muhit o'zgaruvchisiga vergul bilan yozish
#    (masalan Railway kabi xizmatlarda): ADMIN_IDS=123456789,987654321
_admin_ids_env = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in _admin_ids_env.split(",") if x.strip()]

# Ma'lumotlar bazasi fayli (o'zgartirish shart emas)
DB_PATH = os.getenv("DB_PATH", "audit.db")
