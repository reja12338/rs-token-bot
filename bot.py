"""
Official RS TOKEN Telegram Mining Bot
"""
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    MenuButtonWebApp,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8960410904:AAFprxOxrOO4ewr6F0ZvZi4nEJ88nEYwZsk")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://rs-token-bot.onrender.com")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user = message.from_user
    username = user.first_name if user else "Miner"

    # বট মেনু বাটন সেট
    try:
        await bot.set_chat_menu_button(
            chat_id=message.chat.id,
            menu_button=MenuButtonWebApp(
                text="🚀 Open RS Mining",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        )
    except Exception as e:
        print("Menu error:", e)

    # চ্যাটের ইনলাইন বাটন
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 ওপেন RS মাইনিং ড্যাশবোর্ড",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                InlineKeyboardButton(text="📢 টেলিগ্রাম চ্যানেল", url="https://t.me/RSTokenOfficial"),
                InlineKeyboardButton(text="👥 সাপোর্ট গ্রুপ", url="https://t.me/RSTokenChat")
            ]
        ]
    )

    text = (
        f"💎 স্বাগতম **{username}** RS TOKEN মাইনিং বটে!\n\n"
        "⚡ এটি **TON ব্লকচেইন** ভিত্তিক ক্রিপ্টো মাইনিং ও টোকেন প্ল্যাটফর্ম।\n\n"
        "• ফ্রিতে ক্লাউড মাইনিং চালু রাখুন (৬০ RS / ঘণ্টা)\n"
        "• অ্যাড দেখে ও টাস্ক করে টোকেন আর্ন করুন\n"
        "• অটো পেমেন্ট উইথড্র নিন!\n\n"
        "ড্যাশবোর্ড খুলতে নিচের বাটনে চাপুন 👇"
    )

    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)

async def main():
    print("🚀 RS TOKEN Bot running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
