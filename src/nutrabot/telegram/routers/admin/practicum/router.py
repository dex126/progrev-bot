from datetime import datetime
from typing import Any

from aiogram import Bot, F, Router, types
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext

from nutrabot.practicum.service.schemas import PracticumAddSchema
from nutrabot.practicum.service.service import PracticumService
from nutrabot.telegram.middleware.admin import AdminAccessMiddleware
from nutrabot.telegram.routers.admin import keyboard
from nutrabot.telegram.routers.admin.practicum.state import (
    PracticumAddState,
    PracticumAddStateData,
)


class PracticumRouter(Router):  # нормальные стейты сделать
    __bot: Bot
    __practicum_service: PracticumService

    def __init__(
        self,
        bot: Bot,
        practicum_service: PracticumService,
        is_admin_middleware: AdminAccessMiddleware,
    ):
        super().__init__()
        self.__bot = bot
        self.__practicum_service = practicum_service
        self.message.middleware.register(is_admin_middleware)
        self.callback_query.register(
            self.handle_create_practicum_command,
            F.data == "create_practicum",
        )
        self.message.register(
            self.handle_date_first_question_answer,
            StateFilter(PracticumAddState.waiting_for_date_first_practicum),
        )
        self.message.register(
            self.handle_time_first_question_answer,
            F.text,
            StateFilter(PracticumAddState.waiting_for_time_first_practicum),
        )
        self.message.register(
            self.handle_link_first_question_answer,
            F.text,
            StateFilter(PracticumAddState.waiting_for_link_first_practicum),
        )
        self.message.register(
            self.handle_date_second_question_answer,
            F.text,
            StateFilter(PracticumAddState.waiting_for_date_second_practicum),
        )
        self.message.register(
            self.handle_time_second_question_answer,
            F.text,
            StateFilter(PracticumAddState.waiting_for_time_second_practicum),
        )
        self.message.register(
            self.handle_link_second_question_answer,
            F.text,
            StateFilter(PracticumAddState.waiting_for_link_second_practicum),
        )
        self.callback_query.register(
            self.handle_confirmation_question_answer,
            F.data,
            StateFilter(PracticumAddState.waiting_for_confirmation),
        )
        self.callback_query.register(
            self.understand,
            F.data == "delete",
        )
        self.callback_query.register(
            self.back,
            F.data == "back_admin",
        )

    async def handle_create_practicum_command(
        self,
        query: types.CallbackQuery,
        state: FSMContext,
    ) -> None:
        await state.clear()
        await self.send_date_first_question(
            user_telegram_id=query.message.chat.id,
            message_id=query.message.message_id,
            state=state,
        )

    async def send_date_first_question(
        self,
        user_telegram_id: int,
        message_id: int,
        state: FSMContext,
    ) -> None:
        await state.set_state(state=PracticumAddState.waiting_for_date_first_practicum)
        await self.__bot.edit_message_text(
            chat_id=user_telegram_id,
            message_id=message_id,
            text="Введите <b>дату</b> для первого дня практикума [01.02]:",
            reply_markup=keyboard.get_back_button(),
        )

    async def handle_date_first_question_answer(
        self,
        message: types.Message,
        state: FSMContext,
    ) -> None:
        try:
            date = datetime.strptime(
                f"{datetime.today().year}.{message.text}",  # noqa: DTZ002
                "%Y.%d.%m",
            ).date()

            await state.set_data(
                data=PracticumAddStateData(date_first_practicum=str(date)).as_dict(),
            )

            await self.send_time_first_question(
                user_telegram_id=message.from_user.id,
                state=state,
            )
        except ValueError:
            await self.__bot.send_message(
                chat_id=message.from_user.id,
                text="Введите <b>дату</b> в формате [01.02]:",
                reply_markup=keyboard.get_back_button(),
            )

    async def send_time_first_question(
        self,
        user_telegram_id: int,
        state: FSMContext,
    ) -> None:
        await state.set_state(state=PracticumAddState.waiting_for_time_first_practicum)
        await self.__bot.send_message(
            chat_id=user_telegram_id,
            text="Введите <b>время</b> для первого дня практикума [18:00]:",
            reply_markup=keyboard.get_back_button(),
        )

    async def handle_time_first_question_answer(
        self,
        message: types.Message,
        state: FSMContext,
    ) -> None:
        try:
            time = datetime.strptime(message.text, "%H:%M").time()

            state_data = PracticumAddStateData(**await state.get_data())
            state_data.time_first_practicum = str(time)
            await state.set_data(data=state_data.as_dict())
            await self.send_link_first_question(
                user_telegram_id=message.chat.id,
                state=state,
            )
        except ValueError:
            await self.__bot.send_message(
                chat_id=message.from_user.id,
                text="Введите <b>время</b> в формате [18:00]:",
                reply_markup=keyboard.get_back_button(),
            )

    async def send_link_first_question(
        self,
        user_telegram_id: int,
        state: FSMContext,
    ) -> None:
        await state.set_state(state=PracticumAddState.waiting_for_link_first_practicum)
        await self.__bot.send_message(
            chat_id=user_telegram_id,
            text="Введите ссылку на встречу для <b>первого</b> дня практикума:",
            reply_markup=keyboard.get_back_button(),
        )

    async def handle_link_first_question_answer(
        self,
        message: types.Message,
        state: FSMContext,
    ) -> None:
        state_data = PracticumAddStateData(**await state.get_data())
        state_data.link_first_practicum = message.text
        await state.set_data(data=state_data.as_dict())
        await self.send_date_second_question(
            user_telegram_id=message.chat.id,
            state=state,
        )

    async def send_date_second_question(
        self,
        user_telegram_id: int,
        state: FSMContext,
    ) -> None:
        await state.set_state(state=PracticumAddState.waiting_for_date_second_practicum)
        await self.__bot.send_message(
            chat_id=user_telegram_id,
            text="Введите <b>дату</b> для второго дня практикума [01.02]:",
            reply_markup=keyboard.get_back_button(),
        )

    async def handle_date_second_question_answer(
        self,
        message: types.Message,
        state: FSMContext,
    ) -> None:
        try:
            date = datetime.strptime(f"2025.{message.text}", "%Y.%d.%m").date()

            state_data = PracticumAddStateData(**await state.get_data())
            state_data.date_second_practicum = str(date)

            await state.set_data(data=state_data.as_dict())
            await self.send_time_second_question(
                user_telegram_id=message.chat.id,
                state=state,
            )

        except ValueError:
            await self.__bot.send_message(
                chat_id=message.from_user.id,
                text="Введите <b>дату</b> в формате [01.02]:",
                reply_markup=keyboard.get_back_button(),
            )

    async def send_time_second_question(
        self,
        user_telegram_id: int,
        state: FSMContext,
    ) -> None:
        await state.set_state(state=PracticumAddState.waiting_for_time_second_practicum)
        await self.__bot.send_message(
            chat_id=user_telegram_id,
            text="Введите <b>время</b> для второго дня практикума [18:00]:",
            reply_markup=keyboard.get_back_button(),
        )

    async def handle_time_second_question_answer(
        self,
        message: types.Message,
        state: FSMContext,
    ) -> None:
        try:
            time = datetime.strptime(message.text, "%H:%M").time()

            state_data = PracticumAddStateData(**await state.get_data())
            state_data.time_second_practicum = str(time)
            await state.set_data(data=state_data.as_dict())
            await self.send_link_second_question(
                user_telegram_id=message.chat.id,
                state=state,
            )
        except ValueError:
            await self.__bot.send_message(
                chat_id=message.from_user.id,
                text="Введите <b>время</b> в формате [18:00]:",
                reply_markup=keyboard.get_back_button(),
            )

    async def send_link_second_question(
        self,
        user_telegram_id: int,
        state: FSMContext,
    ) -> None:
        await state.set_state(state=PracticumAddState.waiting_for_link_second_practicum)
        await self.__bot.send_message(
            chat_id=user_telegram_id,
            text="Введите ссылку на встречу для <b>второго</b> дня практикума:",
            reply_markup=keyboard.get_back_button(),
        )

    async def handle_link_second_question_answer(
        self,
        message: types.Message,
        state: FSMContext,
    ) -> None:
        state_data = PracticumAddStateData(**await state.get_data())
        state_data.link_second_practicum = message.text
        await state.set_data(data=state_data.as_dict())
        await self.send_confirmation_question(
            user_telegram_id=message.chat.id,
            state=state,
        )

    async def send_confirmation_question(
        self,
        user_telegram_id: int,
        state: FSMContext,
    ) -> None:
        await state.set_state(state=PracticumAddState.waiting_for_confirmation)
        state_data = PracticumAddStateData(**(await state.get_data()))
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
            state_data = PracticumAddStateData(**await state.get_data())
            await self.__practicum_service.add(
                PracticumAddSchema(
                    first_practicum_date=state_data.date_first_practicum,
                    first_practicum_time=state_data.time_first_practicum,
                    first_practicum_link=state_data.link_first_practicum,
                    second_practicum_date=state_data.date_second_practicum,
                    second_practicum_time=state_data.time_second_practicum,
                    second_practicum_link=state_data.link_second_practicum,
                ),
            )

            bot_username = (await self.__bot.get_me()).username
            await query.message.edit_text(
                "<b>Практикум создан</b>\n\n"
                f"<code>t.me/{bot_username}?start=register_from_intensive</code>",
                reply_markup=keyboard.get_back_button(),
            )
            await query.message.answer(
                "Не забудьте поменять шаблоны, "
                "иначе пользователю выдаст некорректный ответ!",
                reply_markup=keyboard.get_delete_button(),
            )

        if query.data == "no":
            await query.message.edit_text(
                "📵 Создание практикума отменено",
                reply_markup=keyboard.get_back_button(),
            )

        await state.clear()

    async def send_post_message(
        self,
        destination_chat_id: int | str,
        state_data: dict[str, Any],
    ) -> None:
        await self.__bot.send_message(
            chat_id=destination_chat_id,
            text=f"1. {state_data.date_first_practicum} в "
            f"{(state_data.time_first_practicum)[:-3]}\n"
            f"2. {state_data.date_second_practicum} в "
            f"{(state_data.time_second_practicum)[:-3]}",
        )

    async def understand(self, query: types.CallbackQuery) -> None:
        await query.message.delete()

    async def back(self, query: types.CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        await query.message.edit_text(
            "Админ-панель\n\n",
            reply_markup=keyboard.get_admin_panel_keyboard(),
        )
