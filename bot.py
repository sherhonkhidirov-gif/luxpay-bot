import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode

# --- SOZLAMALAR --- 
API_TOKEN = "8642617336:AAEtQc8o0YEqKRH7Rt8vedsP9G08dv4p0FY"
ADMIN_ID = 8642617336 
ADMIN_USERNAME = "@khidirov_garand"

# Kanallar ro'yxati (Barcha kanallarda bot ADMIN bo'lishi shart!)
CHANNELS = ["@khidirov_garand1", "@freefireakkauntsavdokhidirov", "@khidirovotzif"] 
users_db = {} 

PRICES = {
    "💎 100+10": 10, "💎 310": 30, "💎 520": 55, "💎 1060": 106,
    "💎 2180": 220, "💎 5600": 550, "📅 Haftalik": 20, "🌕 Oylik": 100,
    "☀️ Kunlik": 5, "📈 Level Up": 30, "🎟 Booyah Pass": 30
}

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()

class FillBalance(StatesGroup):
    choosing_method = State()
    waiting_for_amount = State()
    waiting_for_photo = State()

# --- YORDAMCHI FUNKSIYALAR ---
async def check_sub(user_id):
    """Barcha kanallarga obunani tekshirish"""
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]: 
                return False
        except Exception: 
                return False
    return True

def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="💎 Olmaz sotib olish"))
    builder.row(types.KeyboardButton(text="💰 Balans"), types.KeyboardButton(text="👥 Referal"))
    builder.row(types.KeyboardButton(text="⚙️ Sozlamalar"), types.KeyboardButton(text="💳 Balansni to'ldirish"))
    return builder.as_markup(resize_keyboard=True)

async def send_sub_message(message: types.Message):
    """Obuna bo'lmaganlarga xabar yuborish"""
    builder = InlineKeyboardBuilder()
    # Har bir kanal uchun tugma yaratish
    for channel in CHANNELS:
        builder.row(types.InlineKeyboardButton(text=f"Obuna bo'lish {channel}", url=f"https://t.me/{channel[1:]}"))
    
    # Tekshirish tugmasi
    builder.row(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subs"))
    
    await message.answer("Botdan foydalanish uchun barcha kanallarga obuna bo'ling:", reply_markup=builder.as_markup())

# --- HANDLERS ---

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {'balance': 0}
    
    if not await check_sub(user_id):
        await send_sub_message(message)
    else:
        await message.answer("Xush kelibsiz!", reply_markup=main_menu())

@dp.callback_query(F.data == "check_subs")
async def check_callback(callback: types.CallbackQuery):
    if await check_sub(callback.from_user.id):
        await callback.message.delete()
        await callback.message.answer("Tabriklaymiz! Barcha kanallarga obuna bo'ldingiz.", reply_markup=main_menu())
    else:
        await callback.answer("❌ Hali hamma kanallarga obuna bo'lmagansiz!", show_alert=True)

# --- BALANS TO'LDIRISH ---
@dp.message(F.text == "💳 Balansni to'ldirish")
async def pay_start(message: types.Message, state: FSMContext):
    if not await check_sub(message.from_user.id):
        return await send_sub_message(message)
        
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Visa", callback_data="m_Visa"), types.InlineKeyboardButton(text="Alif", callback_data="m_Alif"))
    builder.row(types.InlineKeyboardButton(text="Eskhata", callback_data="m_Eskhata"), types.InlineKeyboardButton(text="DC", callback_data="m_DC"))
    await message.answer("💰 **Qaysi bank orqali to'lov qilasiz?**", reply_markup=builder.as_markup())
    await state.set_state(FillBalance.choosing_method)

@dp.callback_query(F.data.startswith("m_"), FillBalance.choosing_method)
async def pay_method(callback: types.CallbackQuery, state: FSMContext):
    m = callback.data.split("_")[1]
    nums = {"Visa": "4444 8888 1215 6721", "Alif": "+992 90 677 04 62", "Eskhata": "+992 90 706 12 20", "DC": "+992 706 12 20"}
    await state.update_data(method=m)
    await callback.message.answer(f"✅ Tanlandi: **{m}**\n💳 Raqam: `{nums[m]}`\n\n**Summani yozing (masalan: 10):**")
    await state.set_state(FillBalance.waiting_for_amount)
    await callback.answer()

@dp.message(FillBalance.waiting_for_amount)
async def pay_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Faqat raqam yozing!")
    
    await state.update_data(amount=message.text)
    await message.answer(f"✅ Summa: {message.text} TJS\nEndi to'lov chekini (rasmini) yuboring.")
    await state.set_state(FillBalance.waiting_for_photo)

@dp.message(FillBalance.waiting_for_photo, F.photo)
async def pay_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user = message.from_user
    
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"accept_{data['amount']}_{user.id}"),
        types.InlineKeyboardButton(text="❌ Rad etish", callback_data=f"deny_{user.id}")
    )

    caption = (
        f"🔔 **YANGI TO'LOV!**\n\n"
        f"👤 User: @{user.username or 'Nomalum'}\n"
        f"🆔 ID: `{user.id}`\n"
        f"🏦 Bank: **{data['method']}**\n"
        f"💰 Summa: **{data['amount']}** TJS"
    )
    
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=builder.as_markup())
    await message.answer("✅ Chek yuborildi! Admin tasdiqlashini kuting.")
    await state.clear()

# --- ADMIN QABUL QILISH ---
@dp.callback_query(F.data.startswith("accept_"))
async def admin_accept(callback: types.CallbackQuery):
    _, am, uid = callback.data.split("_")
    uid, am = int(uid), int(am)
    
    if uid not in users_db: users_db[uid] = {'balance': 0}
    users_db[uid]['balance'] += am
    
    try:
        await bot.send_message(uid, f"✅ To'lovingiz tasdiqlandi!\n💰 Balansingizga **{am} TJS** qo'shildi.")
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ **TASDIQLANDI**")
    except:
        await callback.answer("Foydalanuvchiga xabar yuborib bo'lmadi.")
    
    await callback.answer("Muvaffaqiyatli tasdiqlandi")

@dp.callback_query(F.data.startswith("deny_"))
async def admin_deny(callback: types.CallbackQuery):
    uid = int(callback.data.split("_")[1])
    try:
        await bot.send_message(uid, "❌ To'lovingiz rad etildi. Chekda xatolik bo'lishi mumkin.")
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ **RAD ETILDI**")
    except:
        await callback.answer("Foydalanuvchiga xabar yuborib bo'lmadi.")
    await callback.answer("Rad etildi")

# --- OLMAZ XARID QILISH ---
@dp.message(F.text == "💎 Olmaz sotib olish")
async def shop_menu(message: types.Message):
    if not await check_sub(message.from_user.id): 
        return await send_sub_message(message)
        
    builder = InlineKeyboardBuilder()
    for n, p in PRICES.items():
        builder.row(types.InlineKeyboardButton(text=f"{n} - {p} TJS", callback_data=f"buy_{p}_{n}"))
    await message.answer("💎 **Paketni tanlang:**", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("buy_"))
async def buy_process(callback: types.CallbackQuery):
    data_parts = callback.data.split("_")
    p, n, uid = int(data_parts[1]), data_parts[2], callback.from_user.id
    
    if users_db.get(uid, {'balance':0})['balance'] >= p:
        users_db[uid]['balance'] -= p
        admin_msg = (
            f"🛒 **YANGI BUYURTMA!**\n\n"
            f"👤 User: @{callback.from_user.username or 'User'}\n"
            f"🆔 ID: `{uid}`\n"
            f"📦 Paket: **{n}**\n"
            f"💰 To'langan: {p} TJS"
        )
        await bot.send_message(ADMIN_ID, admin_msg)
        await callback.message.answer(f"✅ Xarid qilindi: **{n}**\nTez orada admin almazlarni yuboradi.")
    else:
        await callback.answer("❌ Balansda mablag' yetarli emas!", show_alert=True)

# --- BOSHQA TUGMALAR ---
@dp.message(F.text == "💰 Balans")
async def show_bal(message: types.Message):
    b = users_db.get(message.from_user.id, {'balance': 0})['balance']
    await message.answer(f"💰 Sizning balansingiz: **{b} TJS**")

@dp.message(F.text == "⚙️ Sozlamalar")
async def settings(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📢 Isbotlar", url="https://t.me/khidirovotzif"))
    builder.row(types.InlineKeyboardButton(text="👨‍💻 Admin", url=f"https://t.me/{ADMIN_USERNAME[1:]}"))
    await message.answer("⚙️ **Sozlamalar:**", reply_markup=builder.as_markup())

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
    
