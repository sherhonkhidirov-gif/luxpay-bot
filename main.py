import logging
import json
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup

# 1. BOT SOZLAMALARI
TOKEN = "8642617336:AAEtQc8o0YEqKRH7Rt8vedsP9G08dv4p0FY"
# DIQQAT: Quyidagi manzilni o'zingizning GitHub Pages manzilingizga almashtiring!
WEB_APP_URL = "https://username.github.io/repo-nomi/" 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 2. BARCHA MAHSULOTLAR VA NARXLAR (TJS)
PRICES = {
    # Olmoslar
    "25 💎": 4,
    "100+10 💎": 10,
    "310 💎": 30,
    "520 💎": 55,
    "1060 💎": 106,
    "2180 💎": 220,
    "5600 💎": 550,
    
    # Evo paketlar
    "Evo 3 DAY": 10,
    "Evo 7 DAY": 20,
    "Evo 30 DAY": 30,
    
    # Vaucherlar
    "Haftalik Vaucher": 20,
    "Oylik Vaucher": 110
}

# 3. /START BUYRUG'I
@dp.message(Command("start"))
async def start_command(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Do'konni ochish (Mini App)", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])
    
    welcome_text = (
        f"Assalomu alaykum, {message.from_user.full_name}!\n\n"
        "🎮 **Khidirov Shop** botiga xush kelibsiz.\n"
        "Bu yerda Free Fire olmoslarini eng arzon narxlarda olishingiz mumkin.\n\n"
        "Sotib olish uchun quyidagi tugmani bosing 👇"
    )
    await message.answer(welcome_text, reply_markup=markup)

# 4. MINI APP-DAN KELGAN MA'LUMOTLARNI QABUL QILISH
@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    try:
        # Mini App yuborgan JSON ma'lumotni yuklaymiz
        web_data = json.loads(message.web_app_data.data)
        action = web_data.get("action")
        user_id = message.from_user.id

        # AGAR SOTIB OLISH TUGMASI BOSILSA
        if action == "buy":
            item_name = web_data.get("item")
            item_price = PRICES.get(item_name, "Noma'lum")
            
            response = (
                f"🛒 **Yangi buyurtma qabul qilindi!**\n\n"
                f"👤 Xaridor: {message.from_user.full_name}\n"
                f"🆔 User ID: `{user_id}`\n"
                f"💎 Mahsulot: **{item_name}**\n"
                f"💰 Narxi: **{item_price} TJS**\n\n"
                "⚠️ To'lovni amalga oshirib, skrinshotni shu yerga yuboring. "
                "Admin tez orada olmoslarni hisobingizga tashlab beradi!"
            )
            await message.answer(response, parse_mode="Markdown")

        # AGAR BALANSNI TO'LDIRISH BOSILSA
        elif action == "topup":
            amount = web_data.get("amount")
            bank = web_data.get("bank")
            
            response = (
                f"💳 **Balansni to'ldirish so'rovi!**\n\n"
                f"🏦 Bank: **{bank}**\n"
                f"💵 Miqdor: **{amount} TJS**\n\n"
                "Iltimos, ko'rsatilgan raqamga to'lov qiling va chekni yuboring."
            )
            await message.answer(response, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Xato: {e}")
        await message.answer("Tizimda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

# 5. BOTNI ISHGA TUSHIRISH
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
