from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def get_deeplink_keyboard(bot: Bot) -> InlineKeyboardMarkup:
    bot_username = (await bot.get_me()).username

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Записаться",
                    url=f"https://t.me/{bot_username}?start=register_from_intensive",
                ),
            ],
        ],
    )
