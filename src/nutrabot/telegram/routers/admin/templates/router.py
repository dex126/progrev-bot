from aiogram import F, Router, types
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext

from nutrabot.practicum.repository.repository import ModelNotFoundError
from nutrabot.practicum.service.schemas import PracticumAddSchema
from nutrabot.practicum.service.service import PracticumService
from nutrabot.telegram.middleware.admin import AdminAccessMiddleware
from nutrabot.telegram.routers.admin import keyboard as keyboard_main
from nutrabot.telegram.routers.admin.templates import keyboard as keyboard_templates
from nutrabot.telegram.routers.admin.templates.state import (
    PromocodeState,
    PromocodeStateData,
)


class TemplatesRouter(Router):
    __practicum_service: PracticumService

    def __init__(
        self,
        practicum_service: PracticumService,
        is_admin_middleware: AdminAccessMiddleware,
    ) -> None:
        super().__init__()
        self.__practicum_service = practicum_service
        self.callback_query.register(
            self.handle_templates_command,
            F.data.in_("templates"),
        )

        self.callback_query.register(
            self.handle_promocode_command,
            F.data.in_("promocode"),
        )

        self.message.register(
            self.handle_new_promocode,
            StateFilter(PromocodeState.waiting_for_new_promocode),
        )
        self.message.register(
            self.handle_new_discount_percent,
            StateFilter(PromocodeState.waiting_for_new_discount_percent),
        )
        self.message.register(
            self.handle_new_upper_cost,
            StateFilter(PromocodeState.waiting_for_new_cost),
        )
        self.callback_query.register(
            self.handle_confirmation_question_answer,
            F.data,
            StateFilter(PromocodeState.waiting_for_confirmation),
        )
        self.callback_query.middleware.register(is_admin_middleware)

    async def handle_templates_command(
        self,
        query: types.CallbackQuery,
        state: FSMContext,
    ) -> None:
        await state.clear()

        try:
            await self.__practicum_service.get()
            await query.message.edit_text(
                text="Выберите нужный шаблон для изменения",
                reply_markup=keyboard_templates.get_admin_templates_buttons(),
            )
        except ModelNotFoundError:
            await query.message.edit_text(
                text="Сначала создайте практикум!",
                reply_markup=keyboard_main.get_back_button(),
            )

    async def handle_promocode_command(
        self,
        query: types.CallbackQuery,
        state: FSMContext,
    ) -> None:
        await state.set_state(PromocodeState.waiting_for_new_promocode)
        await query.message.edit_text(
            text="<i>Этот шаблон меняет: промокод, процент скидки, цену.\n\n</i>"
            "Введите новый промокод (пример: <code>TEST01</code>)",
            reply_markup=keyboard_main.get_back_button(),
        )

    async def handle_new_promocode(
        self,
        message: types.Message,
        state: FSMContext,
    ) -> None:
        state_data = PromocodeStateData(**await state.get_data())
        state_data.promocode = message.text

        await state.set_data(
            data=state_data.as_dict(),
        )

        await state.set_state(PromocodeState.waiting_for_new_discount_percent)
        await message.answer(
            text="даю еще один шанс на промокод в [...]% скидки\n"
            "<b>Введите только число без процента</b>",
            reply_markup=keyboard_main.get_back_button(),
        )

    async def handle_new_discount_percent(
        self,
        message: types.Message,
        state: FSMContext,
    ) -> None:
        if not (message.text).isdigit():
            await message.answer(
                text="Только число без процента",
                reply_markup=keyboard_main.get_back_button(),
            )
            return

        state_data = PromocodeStateData(**await state.get_data())
        state_data.discount_percent = message.text

        await state.set_data(
            data=state_data.as_dict(),
        )

        await state.set_state(PromocodeState.waiting_for_new_cost)
        await message.answer(
            text="Через 1 день цена поднимется до [...] руб.\n"
            "<b>Введите только число</b>",
            reply_markup=keyboard_main.get_back_button(),
        )

    async def handle_new_upper_cost(
        self,
        message: types.Message,
        state: FSMContext,
    ) -> None:
        if not (message.text).isdigit():
            await message.answer(
                text="Только число",
                reply_markup=keyboard_main.get_back_button(),
            )
            return

        state_data = PromocodeStateData(**await state.get_data())
        state_data.upper_cost = message.text

        await state.set_data(data=state_data.as_dict())
        await message.answer(
            f"Промокод: <code>{state_data.promocode}</code>\n"
            f"Скидка: {state_data.discount_percent} процентов\n"
            f"Стоимость поднимется до: {state_data.upper_cost} руб.",
        )
        await message.answer(
            "Все верно?",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="Да", callback_data="yes")],
                    [types.InlineKeyboardButton(text="Нет", callback_data="no")],
                ],
                resize_keyboard=True,
            ),
        )
        await state.set_state(PromocodeState.waiting_for_confirmation)

    async def handle_confirmation_question_answer(
        self,
        query: types.CallbackQuery,
        state: FSMContext,
    ) -> None:
        if query.data == "yes":
            state_data = PromocodeStateData(**await state.get_data())
            existed_practicum_info = await self.__practicum_service.get()
            await self.__practicum_service.add(
                PracticumAddSchema(
                    first_practicum_date=existed_practicum_info.first_practicum_date,
                    first_practicum_time=existed_practicum_info.first_practicum_time,
                    first_practicum_link=existed_practicum_info.first_practicum_link,
                    second_practicum_date=existed_practicum_info.second_practicum_date,
                    second_practicum_time=existed_practicum_info.second_practicum_time,
                    second_practicum_link=existed_practicum_info.second_practicum_link,
                    promocode_text=state_data.promocode,
                    discount_percent=state_data.discount_percent,
                    upper_cost=state_data.upper_cost,
                ),
            )
            await query.message.edit_text(
                text="Шаблон отредактирован",
                reply_markup=keyboard_main.get_back_button(),
            )

        if query.data == "no":
            await query.message.edit_text(
                text="Редактирование шаблона отменено",
                reply_markup=keyboard_main.get_back_button(),
            )

        await state.clear()
