from aiogram import Bot, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from nutrabot.telegram.template.template import RemindType
from nutrabot.user.service.service import UserService


class ReminderTelegramService:
    __user_service: UserService

    def __init__(self, bot: Bot, user_service: UserService) -> None:
        super().__init__()
        self.bot = bot
        self.__user_service = user_service
        self.__scheduler = AsyncIOScheduler()
        self.__scheduler.start()

    async def check_participation(
        self,
        user_id: int,
        text: str,
        remind_type: RemindType,
        markup: types.InlineKeyboardMarkup | None,
    ) -> None:
        if not remind_type.startswith("video") and not remind_type.startswith(
            "landing",
        ):
            await self.send_remind_message(
                user_id=user_id,
                text=text,
                markup=markup,
            )
            return

        user_info = await self.__user_service.get_and_add(
            id_=user_id,
            is_channel_subscriber=None,
        )

        if (
            remind_type == RemindType.VIDEO_1H
            and not user_info.is_clicked_watched_button
        ):
            await self.send_remind_message(
                user_id=user_id,
                text=text,
                markup=markup,
            )
            return

        if remind_type.startswith("landing") and not user_info.is_intensive_registered:
            await self.send_remind_message(
                user_id=user_id,
                text=text,
                markup=markup,
            )
            return

        return

    async def send_remind_message(
        self,
        user_id: int,
        text: str,
        markup: types.InlineKeyboardButton | None,
    ) -> None:
        await self.bot.send_message(chat_id=user_id, text=text, reply_markup=markup)
