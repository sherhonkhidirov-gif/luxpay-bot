import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# --- SOZLAMALAR --- 
API_TOKEN = "8642617336:AAEtQc8o0YEqKRH7Rt8vedsP9G08dv4p0FY"
ADMIN_ID = 8642617336 
ADMIN_USERNAME = "@khidirov_garand" # Sizning yangi usernameingiz

CHANNELS = ["@khidirov_garand1", "@freefireakkauntsavdokhidirov", "@khidirovotzif"] 
users_db = {} 

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

class FillBalance(StatesGroup):
    choosing_method = State()
    waiting_for_amount = State()
    waiting_for_photo = State()

# --- ASOSIY FUNKSIYALAR ---
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="💎 Olmaz sotib olish"))
    builder.row(types.KeyboardButton(text="💰 Balans"), types.KeyboardButton(text="👥 Referal"))
    builder.row(types.KeyboardButton(text="⚙️ Sozlamalar"), types.KeyboardButton(text="💳 Balansni to'ldirish"))
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {'balance': 0}
    await message.answer(f"Xush kelibsiz! @{ADMIN_USERNAME[1:]} botiga.", reply_markup=main_menu())

# Mini App dan kelgan buyurtmani qabul qilish
@dp.message(F.content_type == "web_app_data")
async def web_app_data_handler(message: types.Message):
    data = json.loads(message.web_app_data.data)
    item = data['item']
    cost = int(data['cost'])
    user_id = message.from_user.id
    
    if user_id not in users_db: users_db[user_id] = {'balance': 0}
    balans = users_db[user_id]['balance']

    if balans >= cost:
        users_db[user_id]['balance'] -= cost
        await message.answer(f"✅ Xarid qilindi: **{item}**\nBalansdan {cost} TJS yechildi.")
        await bot.send_message(ADMIN_ID, f"🛒 **Yangi Buyurtma!**\nUser: @{message.from_user.username}\nPaket: {item}")
    else:
        await message.answer(f"❌ Balans yetarli emas!\nKerak: {cost} TJS\nSizda: {balans} TJS\n\nIltimos, balansni to'ldiring.")

@dp.message(F.text == "💰 Balans")
async def show_bal(message: types.Message):
    b = users_db.get(message.from_user.id, {'balance': 0})['balance']
    await message.answer(f"💰 Sizning balansingiz: **{b} TJS**")

@dp.message(F.text == "⚙️ Sozlamalar")
async def settings(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="👨‍💻 Admin", url=f"https://t.me/{ADMIN_USERNAME[1:]}"))
    await message.answer("⚙️ **Sozlamalar:**", reply_markup=builder.as_markup())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
