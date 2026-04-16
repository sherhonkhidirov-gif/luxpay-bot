import asyncio
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.deep_linking import create_start_link

TOKEN = '8642617336:AAEtQc8o0YEqKRH7Rt8vedsP9G08dv4p0FY'
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Vaqtinchalik baza
users_db = {} 

class Order(StatesGroup):
    waiting_for_id = State()

def get_main_kb():
    buttons = [
        [types.KeyboardButton(text="💎 Almaz va Vaucherlar")],
        [types.KeyboardButton(text="👥 Referal"), types.KeyboardButton(text="💰 Balans")],
        [types.KeyboardButton(text="🆘 Yordam")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {'balance': 0, 'referals': 0}
        args = message.text.split()
        if len(args) > 1 and args[1].isdigit():
            referrer_id = int(args[1])
            if referrer_id in users_db and referrer_id != user_id:
                users_db[referrer_id]['balance'] += 2
                users_db[referrer_id]['referals'] += 1
                try:
                    await bot.send_message(referrer_id, "🎁 Referal uchun +2 almaz balansingizga qo'shildi!")
                except: pass
    await message.answer("🎮 **LuxPay - Free Fire Professional Shop**\n\nBarcha almaz va vaucherlar shu yerda!", reply_markup=get_main_kb(), parse_mode="Markdown")

@dp.message(F.text == "💎 Almaz va Vaucherlar")
async def all_products(message: types.Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💎 25 - 4 TJS", callback_data="buy_25"),
         types.InlineKeyboardButton(text="💎 50 - 8 TJS", callback_data="buy_50")],
        [types.InlineKeyboardButton(text="💎 100 - 14 TJS", callback_data="buy_100"),
         types.InlineKeyboardButton(text="💎 310 - 40 TJS", callback_data="buy_310")],
        [types.InlineKeyboardButton(text="💎 520 - 65 TJS", callback_data="buy_520"),
         types.InlineKeyboardButton(text="💎 1060 - 130 TJS", callback_data="buy_1060")],
        [types.InlineKeyboardButton(text="💎 2180 - 260 TJS", callback_data="buy_2180"),
         types.InlineKeyboardButton(text="💎 5600 - 650 TJS", callback_data="buy_5600")],
        [types.InlineKeyboardButton(text="📅 Haftalik (Weekly) - 25 TJS", callback_data="buy_Weekly")],
        [types.InlineKeyboardButton(text="🌙 Oylik (Monthly) - 110 TJS", callback_data="buy_Monthly")]
    ])
    await message.answer("🛒 Kerakli vaucher yoki almaz miqdorini tanlang:", reply_markup=kb)

@dp.message(F.text == "💰 Balans")
async def show_balance(message: types.Message):
    u_id = message.from_user.id
    bal = users_db.get(u_id, {}).get('balance', 0)
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💳 Hisobni to'ldirish", callback_data="refill")]
    ])
    await message.answer(f"📊 Balansingiz: **{bal} almaz**\nID: `{u_id}`", reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "refill")
async def refill_info(callback: types.CallbackQuery):
    text = (
        "💳 **To'lov usullari:**\n\n"
        "🔹 **Visa:** \`4444 8888 1215 6721\`\n"
        "🔹 **Alif mobi:** \`+992 906770462\`\n"
        "🔹 **Dc koshalok:** \`+992906770462\`\n"
        "🔹 **Eskhata:** \`+992907061220\`\n\n"
        "✅ To'lovdan so'ng chekni @Donaterbro_N1 ga yuboring."
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: types.CallbackQuery, state: FSMContext):
    item = callback.data.split("_")[1]
    await state.update_data(chosen_item=item)
    await callback.message.answer(f"🛒 Tanlandi: **{item}**\n\nIltimos, Free Fire **ID raqamingizni** yuboring:")
    await state.set_state(Order.waiting_for_id)
    await callback.answer()

@dp.message(Order.waiting_for_id)
async def get_id(message: types.Message, state: FSMContext):
    ff_id = message.text
    data = await state.get_data()
    item = data.get('chosen_item')
    
    msg = (
        f"📩 **Yangi Buyurtma!**\n\n"
        f"📦 Mahsulot: **{item}**\n"
        f"🆔 Free Fire ID: \`{ff_id}\`\n\n"
        f"💳 **To'lov ma'lumotlari:**\n"
        f"Visa: \`4444 8888 1215 6721\`\n"
        f"Alif/Dc: \`+992 906770462\`\n\n"
        f"✅ Chekni @Donaterbro_N1 ga yuboring!"
    )
    await message.answer(msg, parse_mode="Markdown")
    await state.clear()

@dp.message(F.text == "👥 Referal")
async def referral(message: types.Message):
    link = await create_start_link(bot, str(message.from_user.id), encode=False)
    await message.answer(f"🔗 Havolangizni do'stlarga yuboring va har biriga **2 almaz** oling:\n\n{link}")

@dp.message(F.text == "🆘 Yordam")
async def help_me(message: types.Message):
    await message.answer("🆘 Savollar bormi? Adminga yozing: @Donaterbro_N1")

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
EOF
