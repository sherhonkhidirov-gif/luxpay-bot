import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- SOZLAMALAR ---
TOKEN = '8642617336:AAEtQc8o0YEqKRH7Rt...' # O'z tokeningizni yozing
ADMIN_ID = 8642617336 # O'z ID raqamingiz

# Yangilangan majburiy obuna kanallari
CHANNELS = [
    "@khidirov_garand1",
    "@freefireakkauntsavdokhidirov",
    "@khidirovotzif"
] 

users_db = {} 
referrals = {} 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- NARXLAR ---
PRICES = {
    "💎 100+10": 10, "💎 310": 30, "💎 520": 55, "💎 1060": 106,
    "💎 2180": 220, "💎 5600": 550, "📅 Haftalik": 20, "🌕 Oylik": 100,
    "☀️ Kunlik": 5, "📈 Level Up": 30, "🎟 Booyah Pass": 30
}

# --- OBUNANI TEKSHIRISH ---
async def check_sub(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status == "left":
                return False
        except:
            continue
    return True

# --- ASOSIY MENYU ---
def main_menu():
    kb = [
        [types.KeyboardButton(text="💎 Olmaz sotib olish")],
        [types.KeyboardButton(text="💰 Balans"), types.KeyboardButton(text="👥 Referal")],
        [types.KeyboardButton(text="⚙️ Sozlamalar"), types.KeyboardButton(text="💳 Balansni to'ldirish")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_db:
        users_db[user_id] = 0
        
    # Referal tizimi
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        inviter_id = int(args[1])
        if inviter_id != user_id and user_id not in referrals:
            referrals[user_id] = inviter_id
            users_db[inviter_id] = users_db.get(inviter_id, 0) + 1 
            await bot.send_message(inviter_id, "🔔 Do'stingiz qo'shildi! Sizga +1 TJS berildi.")

    if not await check_sub(user_id):
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="1-Kanal", url="https://t.me/khidirov_garand1"))
        builder.row(types.InlineKeyboardButton(text="Akkaunt Savdo", url="https://t.me/freefireakkauntsavdokhidirov"))
        builder.row(types.InlineKeyboardButton(text="Otziv Kanal", url="https://t.me/khidirovotzif"))
        builder.row(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subs"))
        await message.answer("Botdan foydalanish uchun hamma kanallarimizga obuna bo'ling:", reply_markup=builder.as_markup())
    else:
        await message.answer("Xush kelibsiz! Kerakli bo'limni tanlang:", reply_markup=main_menu())

# --- SOZLAMALAR BO'LIMI (YANGILANGAN) ---
@dp.message(F.text == "⚙️ Sozlamalar")
async def settings(message: types.Message):
    text = (
        "⚙️ **Bot sozlamalari va ma'lumotlar:**\n\n"
        "📢 **Asosiy kanal:** @khidirov_garand1\n"
        "🛒 **Akkaunt savdo:** @freefireakkauntsavdokhidirov\n"
        "💬 **Otzivlar:** @khidirovotzif\n"
        "👤 **Asosiy Admin:** @khidirov_garand\n\n"
        "Barcha xizmatlar kafolatlangan!"
    )
    await message.answer(text, disable_web_page_preview=True)

# --- REFERAL ---
@dp.message(F.text == "👥 Referal")
async def referral_link(message: types.Message):
    bot_me = await bot.get_me()
    link = f"https://t.me/{bot_me.username}?start={message.from_user.id}"
    await message.answer(f"👥 **Sizning referal silkangiz:**\n\n`{link}`\n\nHar bir taklif uchun 1 TJS balansga qo'shiladi!")

# --- BALANS VA TO'LOV ---
@dp.message(F.text == "💳 Balansni to'ldirish")
async def payment(message: types.Message):
    text = (
        "💰 **To'lov usullari:**\n\n"
        "🟡 **Alif:** (Karta raqamingizni yozing)\n"
        "🟢 **Eskhata:** (Karta raqamingizni yozing)\n"
        "🔵 **Dushanbe City:** (Karta raqamingizni yozing)\n"
        "💳 **Visa:** (Karta raqamingizni yozing)\n\n"
        "To'lovni amalga oshirib, chekni (rasmni) shu yerga yuboring!"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.photo)
async def handle_receipt(message: types.Message):
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                         caption=f"🔔 **Yangi chek keldi!**\n👤 User: @{message.from_user.username}\n🆔 ID: {message.from_user.id}")
    await message.answer("✅ Rahmat! Chek adminga yuborildi. Tasdiqlanishini kuting.")

# --- OLMAZ SOTIB OLISH ---
@dp.message(F.text == "💎 Olmaz sotib olish")
async def shop(message: types.Message):
    text = "💎 **Olmoslar va narxlar:**\n\n"
    for k, v in PRICES.items():
        text += f"🔹 {k} — {v} TJS\n"
    
    bal = users_db.get(message.from_user.id, 0)
    text += f"\n💰 Sizning balansingiz: {bal} TJS"
    if bal <= 0:
        text += "\n⚠️ Sotib olish uchun balans yetarli emas!"
    await message.answer(text)

@dp.callback_query(F.data == "check_subs")
async def check_callback(callback: types.CallbackQuery):
    if await check_sub(callback.from_user.id):
        await callback.message.answer("Tabriklaymiz! Obuna tasdiqlandi.", reply_markup=main_menu())
        await callback.answer()
    else:
        await callback.answer("Hamma kanallarga a'zo bo'lishingiz shart!", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
