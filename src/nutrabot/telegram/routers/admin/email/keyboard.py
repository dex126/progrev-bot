from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_email_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Обычная",
                    callback_data="default_email",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Оплата",
                    callback_data="payment_email",
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
