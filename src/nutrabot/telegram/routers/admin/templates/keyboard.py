from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_admin_templates_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Промокоды",
                    callback_data="promocode",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data="back_admin",
                ),
            ],
        ],
    )
