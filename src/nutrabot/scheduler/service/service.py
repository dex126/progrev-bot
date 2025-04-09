from datetime import datetime

from aiogram import Bot, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from nutrabot.telegram.reminder.service.service import ReminderTelegramService
from nutrabot.telegram.template.template import RemindType


class SchedulerService:
    __reminder_telegram_service: ReminderTelegramService

    def __init__(
        self,
        bot: Bot,
        reminder_telegram_service: ReminderTelegramService,
    ) -> None:
        super().__init__()
        self.bot = bot
        self.__reminder_telegram_service = reminder_telegram_service

        self.__scheduler = AsyncIOScheduler()
        self.__scheduler.start()

    async def set_remind_message(
        self,
        user_id: int,
        run_date: datetime,
        text: str,
        remind_type: RemindType,
        markup: types.InlineKeyboardMarkup | None = None,
    ) -> None:
        self.__scheduler.add_job(
            func=self.__reminder_telegram_service.check_participation,
            trigger="date",
            run_date=run_date,
            args=(
                user_id,
                text,
                remind_type,
                markup,
            ),
        )

    def return_bot_init(self) -> Bot:  # нет времени
        return self.bot
