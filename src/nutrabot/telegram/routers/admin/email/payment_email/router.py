import contextlib

from aiogram import Bot, F, Router, types
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext

from nutrabot.practicum.repository.repository import ModelNotFoundError
from nutrabot.practicum.service.service import PracticumService
from nutrabot.reminder.service.service import ReminderService
from nutrabot.telegram.middleware.admin import AdminAccessMiddleware
from nutrabot.telegram.routers.admin import keyboard
from nutrabot.telegram.routers.admin.email.payment_email.state import (
    PaymentEmailState,
)
from nutrabot.telegram.template.template import RemindType, Template
from nutrabot.user.service.service import UserService


class PaymentEmailRouter(Router):
    __user_service: UserService
    __practicum_service: PracticumService
    __remind_service: ReminderService
    __bot: Bot

    def __init__(
        self,
        bot: Bot,
        user_service: UserService,
        practicum_service: PracticumService,
        remind_service: ReminderService,
        is_admin_middleware: AdminAccessMiddleware,
    ) -> None:
        super().__init__()
        self.__bot = bot
        self.__user_service = user_service
        self.__practicum_service = practicum_service
        self.__remind_service = remind_service
        self.callback_query.register(
            self.handle_payment_email,
            F.data.in_("payment_email"),
        )

        self.callback_query.register(
            self.handle_confirmation_question_answer,
            F.data,
            StateFilter(PaymentEmailState.waiting_for_confirmation),
        )
        self.callback_query.middleware.register(is_admin_middleware)

    async def handle_payment_email(
        self,
        query: types.CallbackQuery,
        state: FSMContext,
    ) -> None:
        await state.clear()
        await query.answer()

        try:
            practicum_data = await self.__practicum_service.get()
            if practicum_data.discount_percent is not None:
                await self.send_confirmation_question(
                    user_telegram_id=query.message.chat.id,
                    state=state,
                )
                return

            await query.message.edit_text(
                text="Сначала обновите шаблоны!",
                reply_markup=keyboard.get_back_button(),
            )

        except ModelNotFoundError:
            await query.message.edit_text(
                text="Сначала создайте практикум!",
                reply_markup=keyboard.get_back_button(),
            )

    async def send_confirmation_question(
        self,
        user_telegram_id: int,
        state: FSMContext,
    ) -> None:
        await state.set_state(state=PaymentEmailState.waiting_for_confirmation)

        await self.__bot.send_message(
            chat_id=user_telegram_id,
            text="Стартуем продажи?",
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
            users = await self.__user_service.get_and_add()
            async for user in users:
                if user["user_id"] is not None and user["is_intensive_registered"]:
                    await self.send_post_message(
                        destination_chat_id=user["user_id"],
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
    ) -> None:
        practicum_data = await self.__practicum_service.get()

        with contextlib.suppress(TelegramForbiddenError):
            await self.__bot.send_message(
                chat_id=destination_chat_id,
                text=Template.REMIND_TEXT.render(
                    type_=RemindType.PRACTICUM_PAYMENT_0D,
                    discount_percent=practicum_data.discount_percent,
                    promocode=practicum_data.promocode_text,
                ),
            )

            await self.__remind_service.set_practicum_payment_remind(
                user_id=destination_chat_id,
            )
