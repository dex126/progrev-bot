from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from nutrabot.telegram.template.template import CaseType


class SubscriptionCallbackInfo(CallbackData, prefix="sub_buttons_content"):
    case_type: CaseType


def get_link_inline_keyboard(
    target_channel: str,
    button_text: str,
    case_type: CaseType,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=button_text,
                    url=f"https://t.me/{target_channel[1:]}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Готово",
                    callback_data=SubscriptionCallbackInfo(case_type=case_type).pack(),
                ),
            ],
        ],
    )


def get_watched_button(case_type: CaseType) -> InlineKeyboardButton | None:
    return (
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Посмотрела",
                        callback_data="watched",
                    ),
                ],
            ],
        )
        if case_type == CaseType.VIDEO
        else None
    )
