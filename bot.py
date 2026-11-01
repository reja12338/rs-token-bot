"""
File: bot.py (Production Telegram Bot for Render.com)
Deploy on Render as a Web Service or Background Worker (Free Plan)
"""
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, MenuButtonWebApp

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-render-app.onrender.com")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user = message.from_user
    username = user.first_name if user else "Miner"

    # Set Telegram Menu Button to open RS TOKEN WebApp
    await bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=MenuButtonWebApp(
            text="🚀 Open RS Mining",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Open RS Mining Dashboard",
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}?uid={user.id if user else ''}")
                )
            ],
            [
                InlineKeyboardButton(text="📢 RS Official Channel", url="https://t.me/RSTokenOfficial"),
                InlineKeyboardButton(text="👥 Community Group", url="https://t.me/RSTokenChat")
            ]
        ]
    )

    notice = (
        f"💎 **Welcome {username} to RS TOKEN Mining Bot!**\n\n"
        "⚡ Built on the **TON Blockchain**.\n"
        "Mine $RS tokens for free, watch ads, join channels, and withdraw to your Tonkeeper wallet!\n\n"
        "Click the button below to launch your mining dashboard:"
    )

    await message.answer(notice, parse_mode="Markdown", reply_markup=keyboard)

async def main():
    print("🚀 RS TOKEN Telegram Bot is running on Render...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
