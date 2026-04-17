from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode

# --- SOZLAMALAR --- 
API_TOKEN = "8642617336:AAEtQc8o0YEqKRH7Rt8vedsP9G08dv4p0FY"
ADMIN_ID = 8642617336 

CHANNELS = ["@khidirov_garand1", "@freefireakkauntsavdokhidirov", "@khidirovotzif"] 

# Ma'lumotlar bazasi
users_db = {} 

# FSM - Holatlarni boshqarish (summa va chekni ketma-ket so'rash uchun)
class FillBalance(StatesGroup):
    waiting_for_amount = State()
    waiting_for_photo = State()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher() 
PRICES = {
    "💎 100+10": 10, "💎 310": 30, "💎 520": 55, "💎 1060": 106,
    "💎 2180": 220, "💎 5600": 550, "📅 Haftalik": 20, "🌕 Oylik": 100,
    "☀️ Kunlik": 5, "📈 Level Up": 30, "🎟 Booyah Pass": 30
}

# --- YORDAMCHI FUNKSIYALAR ---
async def check_sub(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]: return False
        except: continue
    return True

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
    if user_id not in users_db: users_db[user_id] = 0
    if not await check_sub(user_id):
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="Obuna bo'lish", url="https://t.me/khidirov_garand1"))
        builder.row(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subs"))
        await message.answer("Botdan foydalanish uchun kanallarga obuna bo'ling:", reply_markup=builder.as_markup())
    else:
        await message.answer("Xush kelibsiz!", reply_markup=main_menu())

# --- BALANS TO'LDIRISH (KETMA-KETLIK) ---
@dp.message(F.text == "💳 Balansni to'ldirish")
async def start_payment(message: types.Message, state: FSMContext):
    await message.answer("💰 **Qancha to'ldirmoqchisiz?**\n(Summani raqam bilan yozing, masalan: 50)")
    await state.set_state(FillBalance.waiting_for_amount)

@dp.message(FillBalance.waiting_for_amount)
async def process_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqam yozing!")
        return
    
    await state.update_data(amount=message.text)
    text = (
        f"✅ Miqdor: {message.text} TJS\n\n"
        "💰 **To'lov usullari:**\n"
        "💳 **Visa:** `4444 8888 1215 6721`\n"
        "🟢 **Eskhata:** `+992 90 706 12 20`\n"
        "🔵 **Dushanbe City:** `+992 706 12 20`\n"
        "🟡 **Alif Mobi:** `+992 90 677 04 62`\n\n"
        "To'lovni amalga oshirib, **chekni (rasmni) yuboring!**"
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)
    await state.set_state(FillBalance.waiting_for_photo)

@dp.message(FillBalance.waiting_for_photo, F.photo)
async def handle_receipt(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    amount = user_data['amount']
    user_id = message.from_user.id
    username = message.from_user.username or "Noma'lum"

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=f"✅ Tasdiqlash ({amount} TJS)", callback_data=f"pay_{amount}_{user_id}"))
    builder.row(types.InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{user_id}"))

    caption = (
        f"🔔 **Yangi to'lov cheki!**\n\n"
        f"👤 Foydalanuvchi: @{username}\n"
        f"🆔 ID: `{user_id}`\n"
        f"💰 **To'ldirmoqchi:** {amount} TJS\n"
        f"💳 Joriy balans: {users_db.get(user_id, 0)} TJS"
    )
    
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=builder.as_markup(), parse_mode=ParseMode.MARKDOWN)
    await message.answer("✅ Rahmat! Chek adminga yuborildi. Tasdiqlanishini kuting.")
    await state.clear()

# --- ADMIN TASDIQLASHI ---
@dp.callback_query(F.data.startswith("pay_"))
async def approve_payment(callback: types.CallbackQuery):
    data = callback.data.split("_")
    amount = int(data[1])
    user_id = int(data[2])
    
    users_db[user_id] = users_db.get(user_id, 0) + amount
    await bot.send_message(user_id, f"✅ To'lovingiz tasdiqlandi! Balansingizga {amount} TJS qo'shildi.")
    await callback.message.edit_caption(caption=callback.message.caption + f"\n\n✅ **TASDIQLANDI (+{amount} TJS)**")
    await callback.answer("Tasdiqlandi")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_payment(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await bot.send_message(user_id, "❌ To'lovingiz bekor qilindi.")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ **RAD ETILDI**")
    await callback.answer("Rad etildi")

# --- OLMAZ SOTIB OLISH ---
@dp.message(F.text == "💎 Olmaz sotib olish")
async def shop(message: types.Message):
    builder = InlineKeyboardBuilder()
    for name, price in PRICES.items():
        builder.row(types.InlineKeyboardButton(text=f"{name} - {price} TJS", callback_data=f"buy_{price}_{name}"))
    bal = users_db.get(message.from_user.id, 0)
    await message.answer(f"💎 **Paketni tanlang:**\n💰 Balansingiz: {bal} TJS", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("buy_"))
async def buy_product(callback: types.CallbackQuery):
    data = callback.data.split("_")
    price, item_name, user_id = int(data[1]), data[2], callback.from_user.id
    if users_db.get(user_id, 0) >= price:
        users_db[user_id] -= price
        order_text = (f"🛒 **Yangi buyurtma!**\n\n👤 @{callback.from_user.username}\n🆔 `{user_id}`\n📦 Paket: **{item_name}**\n💰 Qolgan balans: {users_db[user_id]} TJS")
        await bot.send_message(ADMIN_ID, order_text, parse_mode=ParseMode.MARKDOWN)
        await callback.message.answer(f"✅ Xarid qilindi: **{item_name}**.")
    else:
        await callback.answer("❌ Mablag' yetarli emas!", show_alert=True)

# --- QOLGAN FUNKSIYALAR ---
@dp.message(F.text == "💰 Balans")
async def show_balance(message: types.Message):
    await message.answer(f"💰 Balansingiz: {users_db.get(message.from_user.id, 0)} TJS")

@dp.callback_query(F.data == "check_subs")
async def check_callback(callback: types.CallbackQuery):
    if await check_sub(callback.from_user.id):
        await callback.message.answer("Obuna tasdiqlandi.", reply_markup=main_menu())
    else:
        await callback.answer("Hali obuna bo'lmagansiz!", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
