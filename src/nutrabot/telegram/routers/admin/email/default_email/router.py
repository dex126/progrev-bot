import contextlib
from typing import Any

from aiogram import Bot, F, Router, types
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext

from nutrabot.telegram.middleware.admin import AdminAccessMiddleware
from nutrabot.telegram.routers.admin import keyboard
from nutrabot.telegram.routers.admin.email import keyboard as choice_keyboard
from nutrabot.telegram.routers.admin.email.default_email import (
    keyboard as back_keyboard,
)
from nutrabot.telegram.routers.admin.email.default_email.state import (
    EmailState,
    EmailStateData,
)
from nutrabot.user.service.service import UserService


class EmailRouter(Router):
    __user_service: UserService
    __bot: Bot

    def __init__(
        self,
        bot: Bot,
        user_service: UserService,
        is_admin_middleware: AdminAccessMiddleware,
    ) -> None:
        super().__init__()
        self.__bot = bot
        self.__user_service = user_service
        self.callback_query.register(self.handle_email_command, F.data.in_("email"))
        self.callback_query.register(
            self.handle_default_email,
            F.data.in_("default_email"),
        )
        self.message.register(
            self.handle_question_answer,
            F.text,
            StateFilter(EmailState.waiting_for_email_text),
        )
        self.callback_query.register(
            self.handle_confirmation_question_answer,
            F.data,
            StateFilter(EmailState.waiting_for_confirmation),
        )
        self.callback_query.register(
            self.back,
            F.data.in_("back_email"),
        )
        self.callback_query.middleware.register(is_admin_middleware)

    async def back(self, query: types.CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        await self.handle_email_command(query=query)

    async def handle_email_command(
        self,
        query: types.CallbackQuery,
    ) -> None:
        await query.message.edit_text(
            "Выберите нужный вариант",
            reply_markup=choice_keyboard.get_email_buttons(),
        )

    async def handle_default_email(
        self,
        query: types.CallbackQuery,
        state: FSMContext,
    ) -> None:
        await state.clear()
        await self.send_question_message(
            user_id=query.message.chat.id,
            message_id=query.message.message_id,
            state=state,
        )

    async def send_question_message(
        self,
        user_id: int,
        message_id: int,
        state: FSMContext,
    ) -> None:
        await state.set_state(state=EmailState.waiting_for_email_text)
        await self.__bot.edit_message_text(
            text="Введите текст для рассылки",
            chat_id=user_id,
            message_id=message_id,
            reply_markup=back_keyboard.get_back_button(),
        )

    async def handle_question_answer(
        self,
        message: types.Message,
        state: FSMContext,
    ) -> None:
        await state.set_data(
            data=EmailStateData(email_text=message.html_text).as_dict(),
        )
        await self.send_confirmation_question(
            user_telegram_id=message.from_user.id,
            state=state,
        )

    async def send_confirmation_question(
        self,
        user_telegram_id: int,
        state: FSMContext,
    ) -> None:
        await state.set_state(state=EmailState.waiting_for_confirmation)
        state_data = EmailStateData(**(await state.get_data()))
        await self.send_post_message(
            destination_chat_id=user_telegram_id,
            state_data=state_data,
        )
        await self.__bot.send_message(
            chat_id=user_telegram_id,
            text="Все верно?",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="Да", callback_data="yes")],
                    [types.InlineKeyboardButton(text="Нет", callback_data="no")],
                ],
                resize_keyboard=True,
            ),
        )

    async def handle_confirmation_question_answer(
        self,
        query: types.CallbackQuery,
        state: FSMContext,
    ) -> None:
        if query.data == "yes":
            count = 0

            state_data = EmailStateData(**await state.get_data())
            users = await self.__user_service.get_and_add()
            async for user in users:
                if user["user_id"] is not None:
                    await self.send_post_message(
                        destination_chat_id=user["user_id"],
                        state_data=state_data,
                    )
                    count += 1

            await query.message.edit_text(
                f"<b>Сообщение разослано {count} юзерам</b>\n\n",
                reply_markup=keyboard.get_back_button(),
            )

        if query.data == "no":
            await query.message.edit_text(
                "Рассылка отменена",
                reply_markup=keyboard.get_back_button(),
            )

        await state.clear()

    async def send_post_message(
        self,
        destination_chat_id: int | str,
        state_data: dict[str, Any],
    ) -> None:
        with contextlib.suppress(TelegramForbiddenError):
            await self.__bot.send_message(
                chat_id=destination_chat_id,
                text=state_data.email_text,
                parse_mode="html",
            )
