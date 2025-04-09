from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery

from nutrabot.practicum.repository.repository import ModelNotFoundError
from nutrabot.practicum.service.service import PracticumService
from nutrabot.telegram.routers.watched import keyboard
from nutrabot.telegram.template.template import Template
from nutrabot.user.service.schemas import UserAddSchema
from nutrabot.user.service.service import UserService


class WatchedRouter(Router):
    __bot: Bot
    __user_service: UserService
    __practicum_service: PracticumService

    def __init__(
        self,
        bot: Bot,
        user_service: UserService,
        practicum_service: PracticumService,
    ) -> None:
        super().__init__()
        self.__bot = bot
        self.__user_service = user_service
        self.__practicum_service = practicum_service
        self.callback_query.register(
            self.send_watched_message,
            F.data.in_("watched"),
        )

    async def send_watched_message(
        self,
        query: CallbackQuery,
    ) -> None:
        await query.answer()
        user_info = await self.__user_service.get_and_add(
            id_=query.from_user.id,
            is_channel_subscriber=None,
        )

        try:
            practicum_data = await self.__practicum_service.get()
        except ModelNotFoundError:
            await query.message.answer("Практикум пока не создан")
            return

        if user_info:
            await self.__user_service.update_is_watched_button(
                UserAddSchema(
                    id_=query.from_user.id,
                    is_intensive_registered=user_info.is_intensive_registered,
                    is_clicked_watched_button=user_info.is_clicked_watched_button,
                ),
                is_watched=True,
            )

        first_practicum_datetime = datetime.strptime(
            f"{practicum_data.first_practicum_date}",
            "%Y-%m-%d",
        ).strftime("%d/%m/%Y")

        await query.message.answer(
            Template.WATCHED_TEXT.render(
                first_practicum_date=str(first_practicum_datetime),
                first_practicum_time=practicum_data.first_practicum_time[:-3],
            ),
            reply_markup=await keyboard.get_deeplink_keyboard(bot=self.__bot),
        )
