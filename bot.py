import asyncio
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

# 3 ta majburiy kanal
CHANNELS = ["@khidirov_garand1", "@freefireakkauntsavdokhidirov", "@khidirovotzif"] 

# Ma'lumotlar (Vaqtincha RAMda saqlanadi)
users_db = {} 

PRICES = {
    "💎 100+10": 10, "💎 310": 30, "💎 520": 55, "💎 1060": 106,
    "💎 2180": 220, "💎 5600": 550, "📅 Haftalik": 20, "🌕 Oylik": 100,
    "☀️ Kunlik": 5, "📈 Level Up": 30, "🎟 Booyah Pass": 30
}

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class FillBalance(StatesGroup):
    choosing_method = State()
    waiting_for_amount = State()
    waiting_for_photo = State()

# --- YORDAMCHI FUNKSIYALAR ---
async def check_sub(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]: return False
        except: return False
    return True

def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="💎 Olmaz sotib olish"))
    builder.row(types.KeyboardButton(text="💰 Balans"), types.KeyboardButton(text="👥 Referal"))
    builder.row(types.KeyboardButton(text="⚙️ Sozlamalar"), types.KeyboardButton(text="💳 Balansni to'ldirish"))
    return builder.as_markup(resize_keyboard=True)

# --- START VA REFERAL ---
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if user_id not in users_db:
        ref_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
        users_db[user_id] = {'balance': 0, 'referrer': ref_id}
        if ref_id and ref_id in users_db and ref_id != user_id:
            users_db[ref_id]['balance'] += 0.30
            try: await bot.send_message(ref_id, "🔔 Yangi referal! Sizga 0.30 TJS berildi.")
            except: pass

    if not await check_sub(user_id):
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="1-kanal", url="https://t.me/khidirov_garand1"))
        builder.row(types.InlineKeyboardButton(text="2-kanal", url="https://t.me/freefireakkauntsavdokhidirov"))
        builder.row(types.InlineKeyboardButton(text="Isbotlar kanali 📢", url="https://t.me/khidirovotzif"))
        builder.row(types.InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subs"))
        await message.answer("Botdan foydalanish uchun 3 ta kanalga ham obuna bo'ling:", reply_markup=builder.as_markup())
    else:
        await message.answer("Xush kelibsiz!", reply_markup=main_menu())

# --- REFERAL VA SOZLAMALAR ---
@dp.message(F.text == "👥 Referal")
async def referal(message: types.Message):
    link = f"https://t.me/{(await bot.get_me()).username}?start={message.from_user.id}"
    await message.answer(f"🚀 **Referal dasturi**\n\nHar bir do'stingiz uchun **0.30 TJS** olasiz.\n\nSizning silkangiz:\n{link}")

@dp.message(F.text == "⚙️ Sozlamalar")
async def settings(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📢 Isbotlar kanali", url="https://t.me/khidirovotzif"))
    builder.row(types.InlineKeyboardButton(text="👨‍💻 Admin", url=f"https://t.me/{ADMIN_USERNAME[1:]}"))
    await message.answer("⚙️ **Sozlamalar va Aloqa bo'limi**", reply_markup=builder.as_markup())

# --- BALANS TO'LDIRISH ---
@dp.message(F.text == "💳 Balansni to'ldirish")
async def pay_start(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Visa", callback_data="m_Visa"), types.InlineKeyboardButton(text="Alif", callback_data="m_Alif"))
    builder.row(types.InlineKeyboardButton(text="Eskhata", callback_data="m_Eskhata"), types.InlineKeyboardButton(text="DC", callback_data="m_DC"))
    await message.answer("💰 **To'lov usulini tanlang:**", reply_markup=builder.as_markup())
    await state.set_state(FillBalance.choosing_method)

@dp.callback_query(F.data.startswith("m_"))
async def pay_method(callback: types.CallbackQuery, state: FSMContext):
    m = callback.data.split("_")[1]
    nums = {"Visa": "4444 8888 1215 6721", "Alif": "+992 90 677 04 62", "Eskhata": "+992 90 706 12 20", "DC": "+992 706 12 20"}
    await state.update_data(method=m)
    await callback.message.answer(f"✅ Usul: {m}\n💳 Raqam: `{nums[m]}`\n\nSummani yozing (masalan: 50):")
    await state.set_state(FillBalance.waiting_for_amount)
    await callback.answer()

@dp.message(FillBalance.waiting_for_amount)
async def pay_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Faqat raqam yozing!")
    await state.update_data(amount=message.text)
    await message.answer("To'lovni qiling va chekni (rasm) yuboring.")
    await state.set_state(FillBalance.waiting_for_photo)

@dp.message(FillBalance.waiting_for_photo, F.photo)
async def pay_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"ok_{data['amount']}_{message.from_user.id}"))
    builder.row(types.InlineKeyboardButton(text="❌ Rad etish", callback_data=f"no_{message.from_user.id}"))
    
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                         caption=f"💰 To'lov: {data['amount']} TJS\nUsul: {data['method']}\nID: `{message.from_user.id}`", 
                         reply_markup=builder.as_markup())
    await message.answer("✅ Chek yuborildi!")
    await state.clear()

# --- ADMIN TASDIQLASHI ---
@dp.callback_query(F.data.startswith("ok_"))
async def admin_ok(callback: types.CallbackQuery):
    _, am, uid = callback.data.split("_")
    uid = int(uid)
    users_db[uid]['balance'] += int(am)
    await bot.send_message(uid, f"✅ To'lovingiz tasdiqlandi! +{am} TJS")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ **TASDIQLANDI**")

# --- OLMAZ SOTIB OLISH ---
@dp.message(F.text == "💎 Olmaz sotib olish")
async def shop(message: types.Message):
    if not await check_sub(message.from_user.id): return
    builder = InlineKeyboardBuilder()
    for n, p in PRICES.items():
        builder.row(types.InlineKeyboardButton(text=f"{n} - {p} TJS", callback_data=f"buy_{p}_{n}"))
    await message.answer(f"💎 Paketni tanlang:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("buy_"))
async def buy(callback: types.CallbackQuery):
    _, p, n = callback.data.split("_")
    p = int(p)
    uid = callback.from_user.id
    if users_db.get(uid, {'balance':0})['balance'] >= p:
        users_db[uid]['balance'] -= p
        await bot.send_message(ADMIN_ID, f"🛒 Buyurtma!\nUser: @{callback.from_user.username}\nPaket: {n}")
        await callback.message.answer(f"✅ Xarid qilindi: {n}")
    else:
        await callback.answer("Mablag' yetarli emas!", show_alert=True)

@dp.message(F.text == "💰 Balans")
async def balance(message: types.Message):
    b = users_db.get(message.from_user.id, {'balance':0})['balance']
    await message.answer(f"💰 Balans: {b} TJS")

@dp.callback_query(F.data == "check_subs")
async def check_cb(callback: types.CallbackQuery):
    if await check_sub(callback.from_user.id):
        await callback.message.answer("Xush kelibsiz!", reply_markup=main_menu())
    else:
        await callback.answer("Hali obuna bo'lmadingiz!", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
            
