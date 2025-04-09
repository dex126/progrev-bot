from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Практикум",
                    callback_data="create_practicum",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Шаблоны",
                    callback_data="templates",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Рассылка",
                    callback_data="email",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Номера",
                    callback_data="numbers",
                ),
            ],
        ],
    )


def get_delete_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Понятно",
                    callback_data="delete",
                ),
            ],
        ],
    )


def get_back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data="back_admin",
                ),
            ],
        ],
    )
